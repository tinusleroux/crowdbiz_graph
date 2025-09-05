-- Add news_item table for article imports
create table news_item (
  id           uuid primary key default uuid_generate_v4(),
  title        text not null,
  url          text,
  published_at timestamptz,
  article_text text,
  source_id    uuid references source(id),
  created_at   timestamptz default now(),
  updated_at   timestamptz default now()
);

-- Add unique constraint on url to prevent duplicates
create unique index news_item_url_unique on news_item(url) where url is not null;

-- Add index for searching articles
create index news_item_title_idx on news_item using gin (to_tsvector('english', title));
create index news_item_content_idx on news_item using gin (to_tsvector('english', article_text));
create index news_item_published_idx on news_item(published_at);
