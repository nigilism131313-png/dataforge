"""
DataForge Configuration Module - YAML configuration support
"""
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from database import SUPPORTED_LOCALES


class ConfigLoader:
    """Load and validate DataForge YAML configurations"""
    
    @staticmethod
    def load(config_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Dictionary with configuration
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML is invalid
            ValueError: If configuration is invalid
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate configuration
        ConfigLoader.validate(config)
        
        return config
    
    @staticmethod
    def validate(config: Dict[str, Any]) -> None:
        """
        Validate configuration structure
        
        Args:
            config: Configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        # Validate database section
        if 'database' not in config:
            raise ValueError("Configuration must contain 'database' section")
        
        if 'url' not in config['database']:
            raise ValueError("Database configuration must contain 'url'")
        
        # Validate tables section if present
        if 'tables' in config:
            if not isinstance(config['tables'], dict):
                raise ValueError("'tables' section must be a dictionary")
            
            for table_name, table_config in config['tables'].items():
                ConfigLoader.validate_table_config(table_name, table_config)
    
    @staticmethod
    def validate_table_config(table_name: str, config: Dict[str, Any]) -> None:
        """
        Validate table-specific configuration
        
        Args:
            table_name: Name of the table
            config: Table configuration
            
        Raises:
            ValueError: If table configuration is invalid
        """
        if not isinstance(config, dict):
            raise ValueError(f"Configuration for table '{table_name}' must be a dictionary")
        
        # Validate count
        if 'count' in config:
            if not isinstance(config['count'], int) or config['count'] <= 0:
                raise ValueError(f"'count' for table '{table_name}' must be a positive integer")
            if config['count'] > 1000:
                raise ValueError(f"'count' for table '{table_name}' cannot exceed 1000")
        
        # Validate locale
        if 'locale' in config:
            if config['locale'] not in SUPPORTED_LOCALES:
                raise ValueError(
                    f"Unsupported locale '{config['locale']}' for table '{table_name}'. "
                    f"Supported: {', '.join(SUPPORTED_LOCALES)}"
                )
        
        # Validate custom_values
        if 'custom_values' in config:
            if not isinstance(config['custom_values'], dict):
                raise ValueError(f"'custom_values' for table '{table_name}' must be a dictionary")
            
            for col_name, values in config['custom_values'].items():
                if not isinstance(values, list):
                    raise ValueError(
                        f"Custom values for column '{col_name}' in table '{table_name}' "
                        f"must be a list"
                    )
                if len(values) == 0:
                    raise ValueError(
                        f"Custom values for column '{col_name}' in table '{table_name}' "
                        f"cannot be empty"
                    )
    
    @staticmethod
    def get_database_url(config: Dict[str, Any]) -> str:
        """Get database URL from configuration"""
        return config['database']['url']
    
    @staticmethod
    def get_table_configs(config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Get all table configurations"""
        return config.get('tables', {})
    
    @staticmethod
    def get_table_config(config: Dict[str, Any], table_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific table"""
        tables = config.get('tables', {})
        return tables.get(table_name)
    
    @staticmethod
    def create_example_config(output_path: str = "dataforge.yml") -> None:
        """
        Create an example configuration file
        
        Args:
            output_path: Path where to save the example config
        """
        example_config = {
            'database': {
                'url': 'sqlite:///test.db',
                'comment': 'Supports: sqlite:///, postgresql://, mysql://'
            },
            'tables': {
                'users': {
                    'count': 100,
                    'locale': 'en_US',
                    'custom_values': {
                        'role': ['admin', 'user', 'moderator'],
                        'status': ['active', 'inactive']
                    },
                    'comment': 'User accounts table'
                },
                'products': {
                    'count': 500,
                    'locale': 'en_US',
                    'comment': 'Products catalog'
                },
                'orders': {
                    'count': 1000,
                    'locale': 'en_US',
                    'depends_on': ['users', 'products'],
                    'comment': 'Customer orders'
                },
                'order_items': {
                    'count': 5000,
                    'locale': 'en_US',
                    'depends_on': ['orders', 'products'],
                    'comment': 'Order line items'
                }
            },
            'global_settings': {
                'default_locale': 'en_US',
                'default_count': 10,
                'max_count': 1000
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(example_config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        print(f"Example configuration created: {output_path}")


def load_config(config_path: str) -> Dict[str, Any]:
    """Convenience function to load configuration"""
    return ConfigLoader.load(config_path)
