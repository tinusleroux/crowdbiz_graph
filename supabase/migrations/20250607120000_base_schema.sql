
-- Enable extensions
create extension if not exists "uuid-ossp";
create extension if not exists "vector";

-- PERSON
create table person (
  id           uuid primary key default uuid_generate_v4(),
  full_name    text not null,
  first_name   text,
  last_name    text,
  email        text unique,
  linkedin_url text unique,
  embedding    vector(384),            -- optional semantic search on bio snippets
  created_at   timestamptz default now(),
  updated_at   timestamptz default now()
);
create index person_name_idx on person using gin (to_tsvector('simple', full_name));

-- ORGANIZATION
create table organization (
  id         uuid primary key default uuid_generate_v4(),
  name       text not null,
  org_type   text check (org_type in ('Team','League','Brand','Agency','Vendor')),
  sport      text,
  parent_org_id uuid references organization(id)
);
create unique index org_name_unique on organization(lower(name));

-- SOURCE
create table source (
  id            uuid primary key default uuid_generate_v4(),
  url           text not null,
  license       text,
  confidence    numeric check (confidence between 0 and 1),
  fetched_at    timestamptz,
  checksum_sha256 text,
  raw_blob_path text
);

-- ROLE  (historical job titles)
create table role (
  id          uuid primary key default uuid_generate_v4(),
  person_id   uuid references person(id),
  org_id      uuid references organization(id),
  job_title   text not null,
  dept        text,
  start_date  date not null,
  end_date    date,
  source_id   uuid references source(id),
  ingested_at timestamptz default now(),
  constraint uniq_active_role unique (person_id, org_id, start_date)
);
create index role_active_idx on role(person_id) where end_date is null;

-- MATERIALISED VIEW for “current” snapshot
create materialized view v_role_current as
select distinct on (person_id, org_id)
       id, person_id, org_id, job_title, dept, start_date
from   role
where  end_date is null
order by person_id, org_id, start_date desc;
create index v_role_current_person_idx on v_role_current(person_id);
