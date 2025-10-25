"""
Configuration Management for CSIT Timetable Generator
Centralized configuration for all system settings
"""

import os
import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from pathlib import Path


@dataclass
class SolverConfig:
    """Configuration for CSP solver parameters"""
    max_iterations: int = 5000
    timeout_seconds: int = 300
    hard_constraint_weight: float = 5.0
    soft_constraint_weight: float = 1.0
    enable_constraint_propagation: bool = True
    enable_forward_checking: bool = True
    randomization_factor: float = 0.1


@dataclass
class DataConfig:
    """Configuration for data management"""
    data_directory: str = "."
    database_path: str = "timetable.db"
    backup_directory: str = "backups"
    auto_backup: bool = True
    backup_retention_days: int = 30
    csv_encoding: str = "utf-8-sig"
    validate_on_load: bool = True


@dataclass
class UIConfig:
    """Configuration for user interface"""
    theme: str = "light"
    chart_height: int = 400
    max_display_rows: int = 1000
    enable_animations: bool = True
    show_debug_info: bool = False


@dataclass
class SystemConfig:
    """Main system configuration"""
    version: str = "1.0.0"
    debug_mode: bool = False
    log_level: str = "INFO"
    log_file: str = "timetable_generator.log"
    enable_performance_monitoring: bool = True
    max_log_size_mb: int = 10
    log_retention_days: int = 7


class ConfigManager:
    """Manages system configuration"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.solver = SolverConfig()
        self.data = DataConfig()
        self.ui = UIConfig()
        self.system = SystemConfig()
        
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Update configurations
                if 'solver' in config_data:
                    self.solver = SolverConfig(**config_data['solver'])
                if 'data' in config_data:
                    self.data = DataConfig(**config_data['data'])
                if 'ui' in config_data:
                    self.ui = UIConfig(**config_data['ui'])
                if 'system' in config_data:
                    self.system = SystemConfig(**config_data['system'])
                
                return True
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            config_data = {
                'solver': asdict(self.solver),
                'data': asdict(self.data),
                'ui': asdict(self.ui),
                'system': asdict(self.system)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return {
            'solver': asdict(self.solver),
            'data': asdict(self.data),
            'ui': asdict(self.ui),
            'system': asdict(self.system)
        }
    
    def validate_config(self) -> bool:
        """Validate configuration values"""
        try:
            # Validate solver config
            assert self.solver.max_iterations > 0, "Max iterations must be positive"
            assert 0 <= self.solver.timeout_seconds <= 3600, "Timeout must be 0-3600 seconds"
            assert self.solver.hard_constraint_weight > 0, "Hard constraint weight must be positive"
            assert self.solver.soft_constraint_weight >= 0, "Soft constraint weight must be non-negative"
            
            # Validate data config
            assert Path(self.data.data_directory).exists(), "Data directory must exist"
            assert self.data.backup_retention_days > 0, "Backup retention must be positive"
            
            # Validate system config
            assert self.system.log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR'], "Invalid log level"
            
            return True
        except AssertionError as e:
            print(f"Configuration validation failed: {e}")
            return False


# Global configuration instance
config = ConfigManager()
config.load_config()
