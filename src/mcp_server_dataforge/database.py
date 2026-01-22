from sqlalchemy import create_engine, inspect, MetaData, text
from sqlalchemy.orm import sessionmaker
from faker import Faker
import random
import uuid
import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from decimal import Decimal
from .topology import TopologySorter, get_table_order

# Supported locales
SUPPORTED_LOCALES = [
    'uk_UA', 'en_US', 'ru_RU', 'de_DE', 'fr_FR', 
    'es_ES', 'ja_JP', 'zh_CN', 'pt_BR', 'it_IT',
    'pl_PL', 'nl_NL', 'ko_KR', 'tr_TR', 'ar_SA'
]

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.metadata = MetaData()
        self.inspector = None
        self.session_factory = None

    def connect(self, db_url: str) -> str:
        try:
            self.engine = create_engine(db_url)
            self.metadata.reflect(bind=self.engine)
            self.inspector = inspect(self.engine)
            self.session_factory = sessionmaker(bind=self.engine)
            return "Connected successfully"
        except Exception as e:
            return f"Connection failed: {str(e)}"

    def get_schema_summary(self) -> Dict[str, Any]:
        if not self.inspector:
            return {"error": "Not connected to database"}
        tables = self.inspector.get_table_names()
        # For simplicity, return list of tables. Topological sort can be added later.
        return {"tables": tables}

    def seed_table(self, table_name: str, count: int = 10, locale: str = 'en_US', custom_values: Optional[Dict[str, List[Any]]] = None) -> str:
        if not self.engine:
            return "Not connected to database"
        if count > 1000:
            return "Max 1000 rows per request"
        if locale not in SUPPORTED_LOCALES:
            return f"Unsupported locale '{locale}'. Supported: {SUPPORTED_LOCALES}"
        try:
            table = self.metadata.tables[table_name]
            columns = self.inspector.get_columns(table_name)
            fks = self.inspector.get_foreign_keys(table_name)
            fk_dict = {fk['constrained_columns'][0]: (fk['referred_table'], fk['referred_columns'][0]) for fk in fks}
            faker = Faker(locale)
            data = []
            with self.engine.connect() as conn:
                # Get parent PKs for foreign keys
                parent_pks_cache = {}
                for fk_col, (parent_table, parent_col) in fk_dict.items():
                    result = conn.execute(text(f"SELECT {parent_col} FROM {parent_table} LIMIT 100"))
                    parent_pks_cache[fk_col] = [r[0] for r in result.fetchall()]
                    if not parent_pks_cache[fk_col]:
                        return f"Parent table {parent_table} is empty. Please seed it first."
                
                for _ in range(count):
                    row = {}
                    for col in columns:
                        col_name = col['name']
                        if col_name in fk_dict:
                            row[col_name] = random.choice(parent_pks_cache[col_name])
                        else:
                            value = self.generate_value(col, faker, table_name, custom_values)
                            if value is not None:
                                row[col_name] = value
                    data.append(row)
                conn.execute(table.insert(), data)
                conn.commit()
                ids = [i+1 for i in range(count)]
                return f"Inserted {count} rows into '{table_name}' with locale '{locale}'. IDs: {ids[:10]}..."
        except Exception as e:
            return f"Error seeding table: {str(e)}"

    def seed_all_tables(self, count: int = 10, locale: str = 'en_US', 
                       custom_values: Optional[Dict[str, List[Any]]] = None) -> str:
        """
        Seed all tables in dependency order
        
        Args:
            count: Number of rows to generate per table (max 1000)
            locale: Faker locale for data generation
            custom_values: Dictionary mapping table names to custom value dictionaries
            
        Returns:
            Result message with summary of seeded tables
        """
        if not self.engine:
            return "Not connected to database"
        if count > 1000:
            return "Max 1000 rows per request"
        if locale not in SUPPORTED_LOCALES:
            return f"Unsupported locale '{locale}'. Supported: {SUPPORTED_LOCALES}"
        
        try:
            # Get tables in dependency order
            table_order = get_table_order(self.inspector)
            
            results = []
            results.append(f"Seeding {len(table_order)} table(s) in dependency order...")
            results.append("=" * 60)
            
            for table_name in table_order:
                table_custom_values = custom_values.get(table_name) if custom_values else None
                result = self.seed_table(table_name, count, locale, table_custom_values)
                results.append(f"\n{table_name}:")
                results.append(result)
            
            return "\n".join(results)
            
        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error seeding all tables: {str(e)}"
    
    def get_table_order(self) -> List[str]:
        """
        Get tables in dependency order
        
        Returns:
            List of table names in dependency order
        """
        if not self.inspector:
            return []
        return get_table_order(self.inspector)
    
    def get_dependency_tree(self) -> str:
        """
        Get dependency tree visualization
        
        Returns:
            String representation of dependency tree
        """
        if not self.inspector:
            return "Not connected to database"
        
        try:
            sorter = TopologySorter(self.inspector)
            return sorter.visualize_dependencies()
        except Exception as e:
            return f"Error getting dependency tree: {str(e)}"
    
    def generate_value(self, col: Dict[str, Any], faker: Faker, table_name: Optional[str] = None, custom_values: Optional[Dict[str, List[Any]]] = None) -> Any:
        col_name = col['name'].lower()
        col_type = str(col['type']).lower()
        
        # Check for custom values first
        if custom_values:
            # Check both original and lowercase column name
            original_col_name = col['name']
            if original_col_name in custom_values:
                return random.choice(custom_values[original_col_name])
            if col_name in custom_values:
                return random.choice(custom_values[col_name])
        
        # Skip auto-increment primary keys
        if col.get('autoincrement') or (col_name == 'id' and col.get('primary_key')):
            return None
        
        # UUID support
        if 'uuid' in col_name or 'guid' in col_name or 'uuid' in col_type:
            return str(uuid.uuid4())
        
        # Table-specific logic for users
        if table_name and table_name.lower() in ['users', 'user']:
            if 'name' in col_name or 'user' in col_name:
                return faker.name()
            elif 'email' in col_name:
                return faker.email()
        
        # Table-specific logic for orders
        if table_name and table_name.lower() in ['orders', 'order']:
            if 'amount' in col_name or 'total' in col_name or 'price' in col_name:
                return Decimal(str(round(random.uniform(100.0, 5000.0), 2)))
            elif 'date' in col_name:
                return faker.date_this_year()
            elif 'status' in col_name:
                return random.choice(['pending', 'completed', 'cancelled', 'processing', 'shipped'])
        
        # General column name matching
        if 'email' in col_name:
            return faker.email()
        elif 'phone' in col_name or 'tel' in col_name:
            return faker.phone_number()
        elif 'name' in col_name or 'user' in col_name or 'author' in col_name:
            return faker.name()
        elif 'address' in col_name:
            return faker.address()
        elif 'city' in col_name:
            return faker.city()
        elif 'country' in col_name:
            return faker.country()
        elif 'company' in col_name:
            return faker.company()
        elif 'created_at' in col_name or 'updated_at' in col_name:
            return faker.date_time_between(start_date='-1y', end_date='now')
        elif 'price' in col_name or 'amount' in col_name or 'total' in col_name:
            return Decimal(str(round(random.uniform(100.0, 5000.0), 2)))
        elif 'status' in col_name:
            return random.choice(['active', 'inactive', 'pending'])
        elif 'description' in col_name or 'bio' in col_name:
            return faker.paragraph()
        # JSON/JSONB support
        elif 'json' in col_type or 'jsonb' in col_type:
            return self._generate_json_value(faker)
        # Array support
        elif 'array' in col_type or 'text[]' in col_type or 'integer[]' in col_type:
            return self._generate_array_value(col_type, faker)
        # Enum support
        elif 'enum' in col_type:
            # Try to extract enum values from column type
            enum_values = self._extract_enum_values(col_type)
            if enum_values:
                return random.choice(enum_values)
            return faker.word()
        # Spatial data support (basic)
        elif 'point' in col_type or 'geometry' in col_type:
            return self._generate_point_value()
        # Basic types
        elif 'int' in col_type:
            return faker.random_int(min=1, max=1000)
        elif 'varchar' in col_type or 'text' in col_type:
            return faker.text(max_nb_chars=50)
        elif 'bool' in col_type:
            return faker.boolean()
        elif 'decimal' in col_type or 'float' in col_type or 'double' in col_type:
            return Decimal(str(round(random.uniform(10.0, 1000.0), 2)))
        elif 'date' in col_type or 'time' in col_type:
            return faker.date_this_year()
        else:
            return faker.word()
    
    def _generate_json_value(self, faker: Faker) -> Dict[str, Any]:
        """Generate a realistic JSON value"""
        json_types = ['object', 'array', 'simple']
        json_type = random.choice(json_types)
        
        if json_type == 'object':
            return {
                "id": faker.random_int(min=1, max=1000),
                "name": faker.word(),
                "value": faker.random_int(min=1, max=100),
                "active": faker.boolean(),
                "created_at": faker.date_time_between(start_date='-1y', end_date='now').isoformat(),
                "tags": [faker.word() for _ in range(random.randint(1, 5))]
            }
        elif json_type == 'array':
            return [
                {
                    "id": i,
                    "name": faker.word(),
                    "value": faker.random_int(min=1, max=100)
                }
                for i in range(random.randint(1, 5))
            ]
        else:  # simple
            return {
                "data": faker.word(),
                "value": faker.random_int()
            }
    
    def _generate_array_value(self, col_type: str, faker: Faker) -> List[Any]:
        """Generate an array value based on column type"""
        array_length = random.randint(1, 5)
        
        if 'integer[]' in col_type or 'int[]' in col_type:
            return [faker.random_int(min=1, max=100) for _ in range(array_length)]
        elif 'text[]' in col_type or 'varchar[]' in col_type:
            return [faker.word() for _ in range(array_length)]
        elif 'bool[]' in col_type:
            return [faker.boolean() for _ in range(array_length)]
        else:
            # Default to string array
            return [faker.word() for _ in range(array_length)]
    
    def _extract_enum_values(self, col_type: str) -> List[str]:
        """Extract enum values from column type string"""
        # Try to parse enum values from type string
        # Example: "enum('active','inactive','pending')"
        import re
        enum_pattern = r"enum\((.*?)\)"
        match = re.search(enum_pattern, col_type, re.IGNORECASE)
        if match:
            values_str = match.group(1)
            # Split by comma and clean up quotes
            values = [v.strip().strip("'\"") for v in values_str.split(',')]
            return values
        return []
    
    def _generate_point_value(self) -> str:
        """Generate a spatial point value (PostGIS format)"""
        # Generate random coordinates
        lat = round(random.uniform(-90, 90), 6)
        lon = round(random.uniform(-180, 180), 6)
        return f"POINT({lon} {lat})"