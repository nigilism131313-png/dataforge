import json
from mcp.server.fastmcp import FastMCP
from .database import DatabaseManager

# Ініціалізація менеджера бази та MCP сервера
db_manager = DatabaseManager()
mcp = FastMCP("dataforge")

@mcp.tool()
async def connect_db(db_url: str) -> str:
    """Connect to the database using the provided URL."""
    return db_manager.connect(db_url)

@mcp.tool()
async def get_schema_summary() -> str:
    """Get a summary of the database schema, including table names."""
    summary = db_manager.get_schema_summary()
    return json.dumps(summary, indent=2)

@mcp.tool()
async def seed_table(table_name: str, count: int = 10, locale: str = "en_US", custom_values: dict = None) -> str:
    """Seed the specified table with generated data, maintaining referential integrity."""
    return db_manager.seed_table(table_name, count, locale, custom_values)

@mcp.tool()
async def seed_all_tables(count: int = 10, locale: str = "en_US", custom_values: dict = None) -> str:
    """Seed all tables in dependency order, maintaining referential integrity."""
    return db_manager.seed_all_tables(count, locale, custom_values)

@mcp.tool()
async def get_table_order() -> str:
    """Get tables in dependency order (parents before children)."""
    import json
    order = db_manager.get_table_order()
    return json.dumps({"tables": order}, indent=2)

@mcp.tool()
async def get_dependency_tree() -> str:
    """Get a visualization of the database dependency tree."""
    return db_manager.get_dependency_tree()

if __name__ == "__main__":
    # Запуск сервера (FastMCP сам керує асинхронністю)
    mcp.run()