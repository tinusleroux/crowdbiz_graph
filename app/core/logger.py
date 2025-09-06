#!/usr/bin/env python3
"""
Logging and monitoring system for CrowdBiz Graph
Provides structured logging, metrics tracking, and import monitoring
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import os

@dataclass
class ImportMetrics:
    """Metrics for import operations"""
    source: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_records: int = 0
    success_count: int = 0
    error_count: int = 0
    warnings_count: int = 0
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
    
    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def success_rate(self) -> float:
        if self.total_records == 0:
            return 0.0
        return self.success_count / self.total_records
    
    def finish(self):
        """Mark the import as finished"""
        self.end_time = datetime.now()
    
    def add_success(self):
        """Record a successful import"""
        self.success_count += 1
        self.total_records += 1
    
    def add_error(self, error: str):
        """Record an error"""
        self.error_count += 1
        self.total_records += 1
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Record a warning"""
        self.warnings_count += 1
        self.warnings.append(warning)

class CrowdBizLogger:
    """Enhanced logger for CrowdBiz operations"""
    
    def __init__(self, name: str, log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Set up structured logging
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # File handler for all logs
        log_file = self.log_dir / f"{name}.log"
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler for important messages
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)
        
        # Metrics tracking
        self.metrics: List[ImportMetrics] = []
        self.current_import: Optional[ImportMetrics] = None
    
    def start_import(self, source: str) -> ImportMetrics:
        """Start tracking an import operation"""
        metrics = ImportMetrics(
            source=source,
            start_time=datetime.now()
        )
        self.current_import = metrics
        self.metrics.append(metrics)
        
        self.info(f"🚀 Starting import from source: {source}")
        return metrics
    
    def finish_import(self) -> Optional[ImportMetrics]:
        """Finish the current import operation"""
        if self.current_import:
            self.current_import.finish()
            
            # Log summary
            metrics = self.current_import
            self.info(f"✅ Import completed: {metrics.source}")
            self.info(f"  Duration: {metrics.duration_seconds:.2f}s")
            self.info(f"  Success: {metrics.success_count}/{metrics.total_records} ({metrics.success_rate:.1%})")
            self.info(f"  Errors: {metrics.error_count}")
            self.info(f"  Warnings: {metrics.warnings_count}")
            
            # Save metrics to file
            self._save_metrics_to_file(metrics)
            
            result = self.current_import
            self.current_import = None
            return result
        
        return None
    
    def log_import_success(self, message: str = "Record imported successfully"):
        """Log a successful import"""
        if self.current_import:
            self.current_import.add_success()
        self.debug(message)
    
    def log_import_error(self, error: str):
        """Log an import error"""
        if self.current_import:
            self.current_import.add_error(error)
        self.error(f"Import error: {error}")
    
    def log_import_warning(self, warning: str):
        """Log an import warning"""
        if self.current_import:
            self.current_import.add_warning(warning)
        self.warning(f"Import warning: {warning}")
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info=False):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info)
    
    def _save_metrics_to_file(self, metrics: ImportMetrics):
        """Save metrics to JSON file"""
        metrics_file = self.log_dir / "import_metrics.jsonl"
        
        # Convert to dict and make it JSON serializable
        metrics_dict = asdict(metrics)
        metrics_dict['start_time'] = metrics.start_time.isoformat()
        if metrics.end_time:
            metrics_dict['end_time'] = metrics.end_time.isoformat()
        
        # Append to JSONL file
        with open(metrics_file, 'a') as f:
            f.write(json.dumps(metrics_dict) + '\n')
    
    def get_import_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get import summary for the last N days"""
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        recent_metrics = [
            m for m in self.metrics 
            if m.start_time.timestamp() > cutoff_time and m.end_time
        ]
        
        if not recent_metrics:
            return {
                'period_days': days,
                'total_imports': 0,
                'total_records': 0,
                'success_rate': 0.0,
                'avg_duration': 0.0,
                'sources': []
            }
        
        total_records = sum(m.total_records for m in recent_metrics)
        total_success = sum(m.success_count for m in recent_metrics)
        total_duration = sum(m.duration_seconds for m in recent_metrics)
        
        # Group by source
        source_stats = {}
        for m in recent_metrics:
            if m.source not in source_stats:
                source_stats[m.source] = {
                    'imports': 0,
                    'records': 0,
                    'success': 0,
                    'errors': 0
                }
            
            stats = source_stats[m.source]
            stats['imports'] += 1
            stats['records'] += m.total_records
            stats['success'] += m.success_count
            stats['errors'] += m.error_count
        
        return {
            'period_days': days,
            'total_imports': len(recent_metrics),
            'total_records': total_records,
            'success_rate': total_success / max(1, total_records),
            'avg_duration': total_duration / len(recent_metrics),
            'sources': source_stats
        }

# Global logger instances
_loggers: Dict[str, CrowdBizLogger] = {}

def get_logger(name: str) -> CrowdBizLogger:
    """Get or create a logger instance"""
    if name not in _loggers:
        _loggers[name] = CrowdBizLogger(name)
    return _loggers[name]

def setup_logging(log_level: str = "INFO"):
    """Setup global logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

class ImportLogger:
    """Context manager for import operations"""
    
    def __init__(self, source: str, logger_name: str = "import"):
        self.source = source
        self.logger = get_logger(logger_name)
        self.metrics: Optional[ImportMetrics] = None
    
    def __enter__(self) -> 'ImportLogger':
        self.metrics = self.logger.start_import(self.source)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.logger.log_import_error(f"Import failed with exception: {exc_val}")
        
        final_metrics = self.logger.finish_import()
        self.metrics = final_metrics
    
    def success(self, message: str = "Record imported successfully"):
        """Log a successful import"""
        self.logger.log_import_success(message)
    
    def error(self, error: str):
        """Log an import error"""
        self.logger.log_import_error(error)
    
    def warning(self, warning: str):
        """Log an import warning"""
        self.logger.log_import_warning(warning)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

def main():
    """Demo the logging system"""
    setup_logging("INFO")
    
    # Demo import logging
    with ImportLogger("demo_source.csv") as import_logger:
        import_logger.info("Processing demo data...")
        
        # Simulate some imports
        for i in range(10):
            if i == 7:
                import_logger.error(f"Failed to process record {i}")
            elif i == 3:
                import_logger.warning(f"Warning for record {i}")
            else:
                import_logger.success(f"Processed record {i}")
            
            time.sleep(0.1)  # Simulate processing time
    
    # Show summary
    logger = get_logger("import")
    summary = logger.get_import_summary(days=1)
    print("\n📊 Import Summary:")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
