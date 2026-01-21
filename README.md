[![PyPI version](https://badge.fury.io/py/dataforge-mcp.svg)](https://badge.fury.io/py/dataforge-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)


# DataForge MCP Server

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)

**DataForge** is a production-ready MCP (Model Context Protocol) server that enables AI agents, such as Claude and Cursor, to generate realistic test data and seed databases while maintaining referential integrity. It supports PostgreSQL, MySQL, and SQLite databases.

## 🚀 Quick Start

### Installation

1. Clone or download this repository:
```bash
git clone https://github.com/yourusername/dataforge.git
cd dataforge
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. For database drivers, install the appropriate packages:
- PostgreSQL: `pip install psycopg2-binary`
- MySQL: `pip install pymysql`
- SQLite: Already included with Python

### Basic Usage

#### Using MCP (Claude Desktop, Cursor)

Add the following to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "dataforge": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/dataforge"
    }
  }
}
```

Replace `/path/to/dataforge` with the actual path to the directory containing `server.py`.

#### Using CLI

```bash
# Connect to database
python cli.py connect sqlite:///test.db

# Show database schema
python cli.py schema

# Seed a table with 50 rows
python cli.py seed users 50

# Seed with Russian locale
python cli.py seed users 100 --locale ru_RU

# Seed all tables
python cli.py seed-all 20

# List supported locales
python cli.py locales

# Create example configuration file
python cli.py init

# Apply configuration from YAML file
python cli.py apply dataforge.yml
```

#### Using YAML Configuration

Create a `dataforge.yml` file:

```yaml
database:
  url: "sqlite:///test.db"

tables:
  users:
    count: 100
    locale: "en_US"
    custom_values:
      role: ["admin", "user", "moderator"]
      status: ["active", "inactive"]

  products:
    count: 500
    locale: "en_US"

  orders:
    count: 1000
    locale: "en_US"
    depends_on: ["users", "products"]
```

Then apply the configuration:

```bash
python cli.py apply dataforge.yml
```

## ✨ Features

- **Smart Relations**: Automatically detects foreign keys and ensures referential integrity by selecting valid primary keys from parent tables.
- **Context-Aware Mapping**: Uses intelligent heuristics to generate appropriate fake data based on column names and types (e.g., emails, names, addresses, dates).
- **Bulk Inserts**: Efficiently inserts large amounts of data using SQLAlchemy's bulk operations.
- **Safety Limits**: Maximum of 1000 rows per request to prevent timeouts and performance issues.
- **Error Handling**: Provides clear, understandable error messages instead of stack traces.
- **Multi-Locale Support**: Generate data in 15+ languages including English, Russian, German, French, Spanish, Japanese, Chinese, and more.
- **CLI Interface**: Full-featured command-line interface for standalone use.
- **YAML Configuration**: Define your data generation strategy in reusable YAML files.
- **Custom Values**: Specify custom value sets for specific columns.

## 📚 Documentation

### MCP Tools

Once configured, the AI agent can use the following tools:

#### `connect_db(db_url: str)`
Connects to the database using the provided URL.

**Example:**
```
connect_db("sqlite:///test.db")
```

#### `get_schema_summary()`
Returns a list of tables in the database.

**Example:**
```
get_schema_summary()
```

#### `seed_table(table_name: str, count: int = 10, locale: str = 'en_US', custom_values: dict = None)`
Seeds the specified table with generated data.

**Parameters:**
- `table_name`: The name of the table to seed
- `count`: Number of rows to generate (max 1000)
- `locale`: Faker locale for data generation (default: 'en_US')
- `custom_values`: Dictionary mapping column names to lists of custom values

**Example:**
```
seed_table("users", 50, "en_US", {"role": ["admin", "user"]})
```

### CLI Commands

```bash
# Connect to database
python cli.py connect <url>

# Show database schema
python cli.py schema [--format table|json]

# Seed a table
python cli.py seed <table> [count] [--locale <locale>] [--custom <json>]

# Seed all tables
python cli.py seed-all [count] [--locale <locale>]

# List supported locales
python cli.py locales

# Create example configuration
python cli.py init [--output <path>]

# Apply configuration
python cli.py apply <config_path>
```

### Supported Locales

DataForge supports 15+ locales for generating realistic localized data:

- `en_US` - English (United States)
- `ru_RU` - Russian (Russia)
- `de_DE` - German (Germany)
- `fr_FR` - French (France)
- `es_ES` - Spanish (Spain)
- `uk_UA` - Ukrainian (Ukraine)
- `ja_JP` - Japanese (Japan)
- `zh_CN` - Chinese (China)
- `pt_BR` - Portuguese (Brazil)
- `it_IT` - Italian (Italy)
- `pl_PL` - Polish (Poland)
- `nl_NL` - Dutch (Netherlands)
- `ko_KR` - Korean (Korea)
- `tr_TR` - Turkish (Turkey)
- `ar_SA` - Arabic (Saudi Arabia)

## 🔧 Data Generation Heuristics

DataForge uses context-aware mapping to generate appropriate fake data:

- `email` columns: Random email addresses
- `phone`/`tel` columns: Phone numbers
- `name`/`user`/`author` columns: Names
- `address` columns: Full addresses
- `city` columns: City names
- `country` columns: Country names
- `company` columns: Company names
- `created_at`/`updated_at` columns: Recent dates
- `price`/`amount`/`total` columns: Decimal values
- `is_active`/`status` columns: Booleans or status values
- JSON columns: Dummy JSON objects
- Integer columns: Random integers
- Text columns: Random text

### Table-Specific Logic

DataForge applies table-specific heuristics for common table patterns:

**Users table:**
- `name`/`user` columns: Person names
- `email` columns: Email addresses

**Orders table:**
- `amount`/`total`/`price` columns: Decimal values (100.0 - 5000.0)
- `date` columns: Dates within the current year
- `status` columns: Order statuses (pending, completed, cancelled, processing, shipped)

## 🔗 Referential Integrity

For foreign key columns, DataForge:
1. Queries the parent table for existing primary keys (limited to 100)
2. Randomly selects a valid key
3. Raises an error if the parent table is empty

**Important:** Ensure parent tables are seeded before child tables, or use the `seed-all` command which handles dependencies automatically.

## ⚠️ Error Handling

Common error messages:
- "Not connected to database": Call `connect_db` first
- "Parent table X is empty. Please seed it first.": Seed referenced tables first
- "Max 1000 rows per request": Reduce the count parameter
- "Unsupported locale": Use one of the supported locales

## 📖 Use Cases

### 1. Quick Testing

Generate test data for development:

```bash
python cli.py connect sqlite:///test.db
python cli.py seed-all 50
```

### 2. Localization Testing

Test your application with different locales:

```bash
python cli.py seed users 100 --locale ru_RU
python cli.py seed users 100 --locale ja_JP
```

### 3. CI/CD Integration

Use YAML configuration for reproducible test data:

```yaml
database:
  url: "postgresql://test:test@localhost/test_db"

tables:
  users:
    count: 100
    locale: "en_US"
  orders:
    count: 500
    locale: "en_US"
```

```bash
python cli.py apply test_config.yml
```

### 4. Custom Business Logic

Define custom values for specific business scenarios:

```bash
python cli.py seed users 50 --custom '{"role": ["admin", "moderator"], "status": ["active"]}'
```

## 🆚 Comparison with Alternatives

| Feature | DataForge | Factory Boy | Faker | Mockaroo |
|---------|-----------|-------------|-------|----------|
| MCP Integration | ✅ | ❌ | ❌ | ❌ |
| Automatic FK Handling | ✅ | ❌ | ❌ | ✅ |
| Multiple Database Support | ✅ | ✅ | ❌ | ✅ |
| CLI Interface | ✅ | ❌ | ✅ | ✅ |
| YAML Configuration | ✅ | ❌ | ❌ | ✅ |
| Multi-Locale Support | 15+ | 1 | 100+ | 200+ |
| Open Source | ✅ | ✅ | ✅ | ❌ |
| AI Agent Integration | ✅ | ❌ | ❌ | ❌ |

**DataForge's unique advantage:** Seamless integration with AI agents through MCP protocol while maintaining referential integrity and providing a powerful CLI.

## 🔮 Roadmap

- [x] ✅ Automatic table dependency resolution (Topological Sort)
- [x] ✅ Data templates for common domains (E-commerce, CRM, HR)
- [x] ✅ Support for complex data types (UUID, JSON, Arrays)
- [x] ✅ Multi-locale support (15+ languages)
- [ ] Data validation against constraints
- [ ] Parallel data generation for large datasets
- [ ] Docker support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open-source and licensed under the MIT License.

## 📞 Support

If you encounter any issues or have questions, please use the GitHub Issues system:

* 🐛 **Report a Bug:** [GitHub Issues](https://github.com/nigilism131313-png/dataforge/issues)
* 💡 **Request a Feature:** [GitHub Issues](https://github.com/nigilism131313-png/dataforge/issues)

If you find this tool useful, please give it a ⭐️ on GitHub!

---

Made with ❤️ by the DataForge Team