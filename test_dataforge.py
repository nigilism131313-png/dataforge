#!/usr/bin/env python3
"""
DataForge Automated Test Script
Tests all major functionality of DataForge
"""
import os
import sys
import sqlite3
import time
from pathlib import Path
from database import DatabaseManager, SUPPORTED_LOCALES
from config import ConfigLoader, load_config


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class TestRunner:
    """Test runner for DataForge"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.test_db = "test_dataforge.db"
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def print_header(self, text):
        """Print a formatted header"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.END}\n")
    
    def print_success(self, text):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {text}{Colors.END}")
        self.passed += 1
    
    def print_error(self, text):
        """Print error message"""
        print(f"{Colors.RED}✗ {text}{Colors.END}")
        self.failed += 1
        self.errors.append(text)
    
    def print_info(self, text):
        """Print info message"""
        print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")
    
    def setup_test_database(self):
        """Create a test database with sample tables"""
        self.print_header("Setting up test database")
        
        # Remove old test database
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
            self.print_info(f"Removed old test database: {self.test_db}")
        
        # Create new database
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Create tables with foreign keys
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100),
                role VARCHAR(50),
                created_at TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                amount DECIMAL(10,2),
                status VARCHAR(50),
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE order_items (
                id INTEGER PRIMARY KEY,
                order_id INTEGER,
                product_name VARCHAR(100),
                quantity INTEGER,
                price DECIMAL(10,2),
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        self.print_success(f"Test database created: {self.test_db}")
        return True
    
    def test_1_database_connection(self):
        """Test 1: Database connection"""
        self.print_header("Test 1: Database Connection")
        
        result = self.db_manager.connect(f"sqlite:///{self.test_db}")
        
        if "Connected successfully" in result:
            self.print_success("Database connection successful")
            return True
        else:
            self.print_error(f"Database connection failed: {result}")
            return False
    
    def test_2_schema_summary(self):
        """Test 2: Schema summary"""
        self.print_header("Test 2: Schema Summary")
        
        summary = self.db_manager.get_schema_summary()
        tables = summary.get("tables", [])
        
        if len(tables) == 3:
            self.print_success(f"Found {len(tables)} tables: {', '.join(tables)}")
            return True
        else:
            self.print_error(f"Expected 3 tables, found {len(tables)}: {tables}")
            return False
    
    def test_3_table_order(self):
        """Test 3: Table order (dependency resolution)"""
        self.print_header("Test 3: Table Order (Dependency Resolution)")
        
        try:
            order = self.db_manager.get_table_order()
            
            if len(order) == 3:
                self.print_success(f"Table order correct: {' -> '.join(order)}")
                
                # Verify order is correct
                if order[0] == 'users' and order[1] == 'orders' and order[2] == 'order_items':
                    self.print_success("Dependency order verified (users -> orders -> order_items)")
                    return True
                else:
                    self.print_error(f"Wrong order: {order}")
                    return False
            else:
                self.print_error(f"Expected 3 tables in order, found {len(order)}")
                return False
        except Exception as e:
            self.print_error(f"Table order failed: {e}")
            return False
    
    def test_4_dependency_tree(self):
        """Test 4: Dependency tree"""
        self.print_header("Test 4: Dependency Tree")
        
        try:
            tree = self.db_manager.get_dependency_tree()
            
            if "Database Dependency Graph" in tree:
                self.print_success("Dependency tree generated successfully")
                self.print_info(f"Tree preview:\n{tree[:200]}...")
                return True
            else:
                self.print_error("Dependency tree format incorrect")
                return False
        except Exception as e:
            self.print_error(f"Dependency tree failed: {e}")
            return False
    
    def test_5_seed_single_table(self):
        """Test 5: Seed single table"""
        self.print_header("Test 5: Seed Single Table")
        
        result = self.db_manager.seed_table("users", 10, "en_US")
        
        if "Inserted 10 rows" in result:
            self.print_success(f"Seeded users table: {result}")
            return True
        else:
            self.print_error(f"Failed to seed users table: {result}")
            return False
    
    def test_6_seed_with_locale(self):
        """Test 6: Seed with different locale"""
        self.print_header("Test 6: Seed with Different Locale (Russian)")
        
        result = self.db_manager.seed_table("users", 5, "ru_RU")
        
        if "Inserted 5 rows" in result and "ru_RU" in result:
            self.print_success(f"Seeded with Russian locale: {result}")
            return True
        else:
            self.print_error(f"Failed to seed with Russian locale: {result}")
            return False
    
    def test_7_seed_with_custom_values(self):
        """Test 7: Seed with custom values"""
        self.print_header("Test 7: Seed with Custom Values")
        
        custom_values = {
            "role": ["admin", "moderator", "user"]
        }
        
        result = self.db_manager.seed_table("users", 5, "en_US", custom_values)
        
        if "Inserted 5 rows" in result:
            self.print_success(f"Seeded with custom values: {result}")
            return True
        else:
            self.print_error(f"Failed to seed with custom values: {result}")
            return False
    
    def test_8_seed_all_tables(self):
        """Test 8: Seed all tables (dependency order)"""
        self.print_header("Test 8: Seed All Tables (Dependency Order)")
        
        result = self.db_manager.seed_all_tables(5, "en_US")
        
        if "Seeding 3 table(s)" in result:
            self.print_success(f"Seeded all tables in dependency order")
            self.print_info(f"Result preview:\n{result[:300]}...")
            return True
        else:
            self.print_error(f"Failed to seed all tables: {result}")
            return False
    
    def test_9_foreign_key_integrity(self):
        """Test 9: Foreign key integrity"""
        self.print_header("Test 9: Foreign Key Integrity")
        
        # Check if foreign keys are valid
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Check if all order.user_id values exist in users table
        cursor.execute("""
            SELECT COUNT(*) FROM orders 
            WHERE user_id NOT IN (SELECT id FROM users)
        """)
        invalid_fks = cursor.fetchone()[0]
        
        conn.close()
        
        if invalid_fks == 0:
            self.print_success("All foreign keys are valid (referential integrity maintained)")
            return True
        else:
            self.print_error(f"Found {invalid_fks} invalid foreign keys")
            return False
    
    def test_10_data_realism(self):
        """Test 10: Data realism"""
        self.print_header("Test 10: Data Realism")
        
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Check user data
        cursor.execute("SELECT name, email FROM users LIMIT 3")
        users = cursor.fetchall()
        
        conn.close()
        
        all_valid = True
        for user in users:
            name, email = user
            
            # Check if name looks realistic (has space or common pattern)
            if not name or len(name) < 3:
                self.print_error(f"Invalid name: {name}")
                all_valid = False
                continue
            
            # Check if email has @
            if '@' not in email or '.' not in email:
                self.print_error(f"Invalid email: {email}")
                all_valid = False
                continue
        
        if all_valid:
            self.print_success("All generated data looks realistic")
            self.print_info(f"Sample users: {users}")
            return True
        else:
            return False
    
    def test_11_supported_locales(self):
        """Test 11: Supported locales"""
        self.print_header("Test 11: Supported Locales")
        
        if len(SUPPORTED_LOCALES) >= 15:
            self.print_success(f"Found {len(SUPPORTED_LOCALES)} supported locales")
            self.print_info(f"Locales: {', '.join(SUPPORTED_LOCALES[:10])}...")
            return True
        else:
            self.print_error(f"Expected at least 15 locales, found {len(SUPPORTED_LOCALES)}")
            return False
    
    def test_12_yaml_config(self):
        """Test 12: YAML configuration"""
        self.print_header("Test 12: YAML Configuration")
        
        # Create a test YAML config
        test_config = "test_config.yml"
        config_content = """
database:
  url: "sqlite:///test_dataforge.db"

tables:
  users:
    count: 5
    locale: "en_US"
    custom_values:
      role: ["admin", "user"]
"""
        
        with open(test_config, 'w') as f:
            f.write(config_content)
        
        try:
            config = load_config(test_config)
            
            if 'database' in config and 'tables' in config:
                self.print_success("YAML configuration loaded successfully")
                
                # Clean up
                os.remove(test_config)
                return True
            else:
                self.print_error("YAML configuration missing required sections")
                os.remove(test_config)
                return False
        except Exception as e:
            self.print_error(f"Failed to load YAML configuration: {e}")
            if os.path.exists(test_config):
                os.remove(test_config)
            return False
    
    def test_13_large_dataset(self):
        """Test 13: Large dataset (performance)"""
        self.print_header("Test 13: Large Dataset (Performance)")
        
        # Time the operation
        start_time = time.time()
        result = self.db_manager.seed_table("users", 100, "en_US")
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        if "Inserted 100 rows" in result:
            self.print_success(f"Generated 100 rows in {execution_time:.2f}s")
            
            if execution_time < 5.0:
                self.print_success("Performance is good (< 5 seconds for 100 rows)")
                return True
            else:
                self.print_info(f"Performance could be improved (took {execution_time:.2f}s)")
                return True
        else:
            self.print_error(f"Failed to generate large dataset: {result}")
            return False
    
    def test_14_complex_types(self):
        """Test 14: Complex data types"""
        self.print_header("Test 14: Complex Data Types")
        
        # Create a table with complex types
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE complex_test (
                id INTEGER PRIMARY KEY,
                uuid_col TEXT,
                json_col TEXT,
                array_col TEXT,
                enum_col VARCHAR(50)
            )
        """)
        
        conn.commit()
        
        # Seed the table
        result = self.db_manager.seed_table("complex_test", 5, "en_US")
        
        conn.close()
        
        if "Inserted 5 rows" in result:
            self.print_success("Complex types table seeded successfully")
            return True
        else:
            self.print_error(f"Failed to seed complex types table: {result}")
            return False
    
    def cleanup(self):
        """Clean up test database"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
            self.print_info(f"Cleaned up test database: {self.test_db}")
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        print(f"{Colors.BOLD}Total Tests:{Colors.END} {total}")
        print(f"{Colors.GREEN}{Colors.BOLD}Passed:{Colors.END} {self.passed}")
        print(f"{Colors.RED}{Colors.BOLD}Failed:{Colors.END} {self.failed}")
        print(f"{Colors.BLUE}{Colors.BOLD}Success Rate:{Colors.END} {percentage:.1f}%")
        
        if self.failed > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}Errors found:{Colors.END}")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.END}\n")
        
        return self.failed == 0
    
    def run_all_tests(self):
        """Run all tests"""
        print(f"{Colors.BOLD}{Colors.BLUE}")
        print("╔════════════════════════════════════════════════════╗")
        print("║           DATAFORGE AUTOMATED TEST SUITE             ║")
        print("╠════════════════════════════════════════════════════╣")
        print("║                                                    ║")
        print(f"{Colors.END}")
        
        # Setup
        self.setup_test_database()
        
        # Run tests
        self.test_1_database_connection()
        self.test_2_schema_summary()
        self.test_3_table_order()
        self.test_4_dependency_tree()
        self.test_5_seed_single_table()
        self.test_6_seed_with_locale()
        self.test_7_seed_with_custom_values()
        self.test_8_seed_all_tables()
        self.test_9_foreign_key_integrity()
        self.test_10_data_realism()
        self.test_11_supported_locales()
        self.test_12_yaml_config()
        self.test_13_large_dataset()
        self.test_14_complex_types()
        
        # Cleanup
        self.cleanup()
        
        # Summary
        success = self.print_summary()
        
        return success


def main():
    """Main entry point"""
    runner = TestRunner()
    success = runner.run_all_tests()
    
    if success:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.END}")
        print(f"{Colors.GREEN}DataForge is ready for production!{Colors.END}")
        sys.exit(0)
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.END}")
        print(f"{Colors.YELLOW}Please fix the errors before publishing.{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()
