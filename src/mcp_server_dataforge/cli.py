#!/usr/bin/env python3
"""
DataForge CLI - Command Line Interface for DataForge MCP Server
"""
import argparse
import sys
import json
from .database import DatabaseManager, SUPPORTED_LOCALES
from .config import ConfigLoader, load_config
from typing import Optional


class DataForgeCLI:
    """Command Line Interface for DataForge"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.connected = False
        self.db_url = None
    
    def connect(self, db_url: str) -> str:
        """Connect to database"""
        result = self.db_manager.connect(db_url)
        if "Connected successfully" in result:
            self.connected = True
            self.db_url = db_url
        return result
    
    def schema(self, format: str = "table") -> str:
        """Get database schema"""
        if not self.connected:
            return "Error: Not connected to database. Use 'connect' command first."
        
        summary = self.db_manager.get_schema_summary()
        
        if format == "json":
            return json.dumps(summary, indent=2)
        elif format == "table":
            tables = summary.get("tables", [])
            if not tables:
                return "No tables found in database."
            
            output = ["Database Schema:", "=" * 50]
            for i, table in enumerate(tables, 1):
                output.append(f"{i}. {table}")
            return "\n".join(output)
        else:
            return f"Error: Unsupported format '{format}'. Use 'table' or 'json'."
    
    def seed(self, table_name: str, count: int = 10, locale: str = "en_US", 
             custom_values: Optional[str] = None) -> str:
        """Seed a table with generated data"""
        if not self.connected:
            return "Error: Not connected to database. Use 'connect' command first."
        
        if locale not in SUPPORTED_LOCALES:
            return f"Error: Unsupported locale '{locale}'. Supported: {', '.join(SUPPORTED_LOCALES)}"
        
        custom_dict = None
        if custom_values:
            try:
                custom_dict = json.loads(custom_values)
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON in custom_values: {e}"
        
        return self.db_manager.seed_table(table_name, count, locale, custom_dict)
    
    def seed_all(self, count: int = 10, locale: str = "en_US", 
                 custom_values: Optional[str] = None) -> str:
        """Seed all tables with generated data in dependency order"""
        if not self.connected:
            return "Error: Not connected to database. Use 'connect' command first."
        
        if locale not in SUPPORTED_LOCALES:
            return f"Error: Unsupported locale '{locale}'. Supported: {', '.join(SUPPORTED_LOCALES)}"
        
        custom_dict = None
        if custom_values:
            try:
                custom_dict = json.loads(custom_values)
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON in custom_values: {e}"
        
        return self.db_manager.seed_all_tables(count, locale, custom_dict)
    
    def get_table_order(self) -> str:
        """Get tables in dependency order"""
        if not self.connected:
            return "Error: Not connected to database. Use 'connect' command first."
        
        order = self.db_manager.get_table_order()
        if not order:
            return "No tables found in database."
        
        output = ["Table Dependency Order:", "=" * 50]
        for i, table in enumerate(order, 1):
            output.append(f"{i}. {table}")
        return "\n".join(output)
    
    def get_dependency_tree(self) -> str:
        """Get dependency tree visualization"""
        if not self.connected:
            return "Error: Not connected to database. Use 'connect' command first."
        
        return self.db_manager.get_dependency_tree()
    
    def list_locales(self) -> str:
        """List all supported locales"""
        output = ["Supported Locales:", "=" * 40]
        for locale in SUPPORTED_LOCALES:
            output.append(f"  - {locale}")
        return "\n".join(output)
    
    def init_config(self, config_path: str = "dataforge.yml") -> str:
        """Create an example configuration file"""
        try:
            ConfigLoader.create_example_config(config_path)
            return f"Example configuration created: {config_path}\n\nEdit this file and run 'dataforge apply {config_path}' to use it."
        except Exception as e:
            return f"Error creating configuration: {e}"
    
    def list_templates(self) -> str:
        """List available data templates"""
        from pathlib import Path
        
        templates_dir = Path(__file__).parent / "templates"
        
        if not templates_dir.exists():
            return "No templates directory found."
        
        templates = list(templates_dir.glob("*.yml"))
        
        if not templates:
            return "No templates found."
        
        output = ["Available Data Templates:", "=" * 50]
        for template in sorted(templates):
            template_name = template.stem
            output.append(f"  - {template_name}")
        
        output.append("\nUsage:")
        output.append("  dataforge init-template <template_name> [output_path]")
        
        return "\n".join(output)
    
    def init_template(self, template_name: str, output_path: Optional[str] = None) -> str:
        """Initialize a specific template"""
        from pathlib import Path
        
        templates_dir = Path(__file__).parent / "templates"
        template_file = templates_dir / f"{template_name}.yml"
        
        if not template_file.exists():
            available = [t.stem for t in templates_dir.glob("*.yml")]
            return f"Template '{template_name}' not found. Available templates: {', '.join(available)}"
        
        if output_path is None:
            output_path = f"{template_name}.yml"
        
        import shutil
        shutil.copy(template_file, output_path)
        
        return f"Template '{template_name}' initialized: {output_path}\n\nEdit this file and run 'dataforge apply {output_path}' to use it."
    
    def apply_config(self, config_path: str) -> str:
        """Apply configuration from YAML file"""
        try:
            config = load_config(config_path)
            
            # Connect to database
            db_url = ConfigLoader.get_database_url(config)
            connect_result = self.connect(db_url)
            if "Connected successfully" not in connect_result:
                return f"Error connecting to database: {connect_result}"
            
            # Get table configurations
            table_configs = ConfigLoader.get_table_configs(config)
            
            if not table_configs:
                return "No tables configured in configuration file."
            
            results = []
            results.append(f"Applying configuration from: {config_path}")
            results.append(f"Database: {db_url}")
            results.append(f"Tables to seed: {len(table_configs)}")
            results.append("=" * 60)
            
            # Seed each table
            for table_name, table_config in table_configs.items():
                count = table_config.get('count', 10)
                locale = table_config.get('locale', 'en_US')
                custom_values = table_config.get('custom_values')
                
                results.append(f"\nSeeding table: {table_name}")
                results.append(f"  Count: {count}")
                results.append(f"  Locale: {locale}")
                if custom_values:
                    results.append(f"  Custom values: {list(custom_values.keys())}")
                
                result = self.seed(table_name, count, locale, 
                                  json.dumps(custom_values) if custom_values else None)
                results.append(f"  Result: {result}")
            
            return "\n".join(results)
            
        except FileNotFoundError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error applying configuration: {e}"


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description="DataForge CLI - Generate realistic test data for databases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Connect to SQLite database
  dataforge connect sqlite:///test.db
  
  # Show database schema
  dataforge schema
  
  # Show tables in dependency order
  dataforge order
  
  # Show dependency tree
  dataforge deps
  
  # Seed a table with 50 rows
  dataforge seed users 50
  
  # Seed with Russian locale
  dataforge seed users 100 --locale ru_RU
  
  # Seed all tables in dependency order
  dataforge seed-all 20
  
  # List supported locales
  dataforge locales
  
  # Create example configuration file
  dataforge init
  
  # Apply configuration from YAML file
  dataforge apply dataforge.yml
  
  # List available templates
  dataforge templates
  
  # Initialize a specific template
  dataforge init-template ecommerce
  
  # Initialize template with custom output path
  dataforge init-template crm my_crm.yml
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Connect command
    connect_parser = subparsers.add_parser("connect", help="Connect to database")
    connect_parser.add_argument("url", help="Database URL (e.g., sqlite:///test.db, postgresql://user:pass@localhost/db)")
    
    # Schema command
    schema_parser = subparsers.add_parser("schema", help="Show database schema")
    schema_parser.add_argument("--format", choices=["table", "json"], default="table", 
                               help="Output format (default: table)")
    
    # Seed command
    seed_parser = subparsers.add_parser("seed", help="Seed a table with generated data")
    seed_parser.add_argument("table", help="Table name to seed")
    seed_parser.add_argument("count", type=int, nargs="?", default=10, 
                            help="Number of rows to generate (default: 10, max: 1000)")
    seed_parser.add_argument("--locale", default="en_US", 
                           help=f"Faker locale (default: en_US)")
    seed_parser.add_argument("--custom", help="Custom values as JSON string")
    
    # Seed-all command
    seed_all_parser = subparsers.add_parser("seed-all", help="Seed all tables with generated data in dependency order")
    seed_all_parser.add_argument("count", type=int, nargs="?", default=10,
                                 help="Number of rows per table (default: 10, max: 1000)")
    seed_all_parser.add_argument("--locale", default="en_US",
                                help=f"Faker locale (default: en_US)")
    seed_all_parser.add_argument("--custom", help="Custom values as JSON string")
    
    # Table order command
    subparsers.add_parser("order", help="Show tables in dependency order")
    
    # Dependency tree command
    subparsers.add_parser("deps", help="Show database dependency tree")
    
    # Locales command
    subparsers.add_parser("locales", help="List all supported locales")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Create an example configuration file")
    init_parser.add_argument("--output", "-o", default="dataforge.yml",
                           help="Output path for configuration file (default: dataforge.yml)")
    
    # List templates command
    subparsers.add_parser("templates", help="List available data templates")
    
    # Init template command
    init_template_parser = subparsers.add_parser("init-template", help="Initialize a specific data template")
    init_template_parser.add_argument("template", help="Template name (e.g., ecommerce, crm, hr, healthcare)")
    init_template_parser.add_argument("output", nargs="?", help="Output path (default: <template_name>.yml)")
    
    # Apply command
    apply_parser = subparsers.add_parser("apply", help="Apply configuration from YAML file")
    apply_parser.add_argument("config", help="Path to YAML configuration file")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = DataForgeCLI()
    
    if args.command == "connect":
        result = cli.connect(args.url)
        print(result)
        if "Connected successfully" in result:
            print(f"\nNext steps:")
            print(f"  dataforge schema          # Show database schema")
            print(f"  dataforge seed users 50   # Seed 'users' table")
            print(f"  dataforge seed-all 20     # Seed all tables")
    
    elif args.command == "schema":
        result = cli.schema(args.format)
        print(result)
    
    elif args.command == "seed":
        result = cli.seed(args.table, args.count, args.locale, args.custom)
        print(result)
    
    elif args.command == "seed-all":
        result = cli.seed_all(args.count, args.locale, args.custom)
        print(result)
    
    elif args.command == "order":
        result = cli.get_table_order()
        print(result)
    
    elif args.command == "deps":
        result = cli.get_dependency_tree()
        print(result)
    
    elif args.command == "locales":
        result = cli.list_locales()
        print(result)
    
    elif args.command == "init":
        result = cli.init_config(args.output)
        print(result)
    
    elif args.command == "apply":
        result = cli.apply_config(args.config)
        print(result)
    
    elif args.command == "templates":
        result = cli.list_templates()
        print(result)
    
    elif args.command == "init-template":
        result = cli.init_template(args.template, args.output)
        print(result)


if __name__ == "__main__":
    main()
