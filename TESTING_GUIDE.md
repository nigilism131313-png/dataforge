# DataForge Testing Guide

## 🧪 Quick Start - Run All Tests

```bash
# Make sure you're in the DataForge directory
cd d:/DataForge

# Run the automated test suite
python test_dataforge.py
```

---

## 📋 What the Tests Check

The automated test suite checks **14 critical aspects** of DataForge:

### ✅ Test 1: Database Connection
- Verifies that DataForge can connect to SQLite databases
- Checks for proper error handling

### ✅ Test 2: Schema Summary
- Confirms that table detection works
- Validates schema inspection

### ✅ Test 3: Table Order (Dependency Resolution)
- Tests topological sorting
- Verifies foreign key dependencies
- Ensures correct order: users → orders → order_items

### ✅ Test 4: Dependency Tree
- Checks dependency tree generation
- Validates visualization output

### ✅ Test 5: Seed Single Table
- Tests basic data generation
- Verifies row count

### ✅ Test 6: Seed with Different Locale (Russian)
- Tests locale support
- Validates Russian data generation

### ✅ Test 7: Seed with Custom Values
- Tests custom value functionality
- Verifies role assignment

### ✅ Test 8: Seed All Tables (Dependency Order)
- Tests automatic dependency resolution
- Verifies all tables are seeded in correct order

### ✅ Test 9: Foreign Key Integrity
- **CRITICAL TEST** - Validates referential integrity
- Ensures all foreign keys reference existing records
- Prevents orphaned records

### ✅ Test 10: Data Realism
- Validates generated data quality
- Checks email format
- Checks name patterns

### ✅ Test 11: Supported Locales
- Confirms 15+ locales are available
- Lists supported locales

### ✅ Test 12: YAML Configuration
- Tests YAML config loading
- Validates configuration structure

### ✅ Test 13: Large Dataset (Performance)
- Tests performance with 100 rows
- Measures execution time
- Validates performance is acceptable (< 5 seconds)

### ✅ Test 14: Complex Data Types
- Tests UUID generation
- Tests JSON generation
- Tests array generation
- Tests enum support

---

## 🎯 Expected Output

### Success Case:
```
╔════════════════════════════════════════════════════╗
║           DATAFORGE AUTOMATED TEST SUITE             ║
╠════════════════════════════════════════════════════╣
║                                                    ║

============================================================
Setting up test database
ℹ Removed old test database: test_dataforge.db
✓ Test database created: test_dataforge.db

============================================================
Test 1: Database Connection
✓ Database connection successful

============================================================
Test 2: Schema Summary
✓ Found 3 tables: users, orders, order_items

... (all 14 tests) ...

============================================================
TEST SUMMARY
============================================================
Total Tests: 14
Passed: 14
Failed: 0
Success Rate: 100.0%

============================================================

✓ ALL TESTS PASSED!
DataForge is ready for production!
```

### Failure Case:
```
... (some tests pass, some fail) ...

============================================================
TEST SUMMARY
============================================================
Total Tests: 14
Passed: 12
Failed: 2
Success Rate: 85.7%

Errors found:
  1. Failed to seed with Russian locale: ...
  2. Foreign key integrity check failed: ...

============================================================

✗ SOME TESTS FAILED
Please fix the errors before publishing.
```

---

## 🐛 Common Issues and Solutions

### Issue 1: "Module not found"
**Error:**
```
ModuleNotFoundError: No module named 'mcp'
```

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue 2: "Not connected to database"
**Error:**
```
Error: Not connected to database
```

**Solution:**
The test script handles this automatically. If you see this error, it's a bug in the code.

### Issue 3: "Parent table is empty"
**Error:**
```
Parent table users is empty. Please seed it first.
```

**Solution:**
The test script seeds tables in the correct order. If you see this error, it's a bug in the dependency resolution.

### Issue 4: "Unsupported locale"
**Error:**
```
Unsupported locale 'ru_RU'
```

**Solution:**
Check that `SUPPORTED_LOCALES` in `database.py` includes the locale.

---

## 🔍 Manual Testing

If automated tests pass, you may want to do manual testing:

### Test CLI Commands:
```bash
# Connect to database
python cli.py connect sqlite:///test.db

# Show schema
python cli.py schema

# Show table order
python cli.py order

# Show dependency tree
python cli.py deps

# List locales
python cli.py locales

# List templates
python cli.py templates

# Seed a table
python cli.py seed users 10

# Seed with Russian locale
python cli.py seed users 10 --locale ru_RU

# Seed all tables
python cli.py seed-all 10

# Create example config
python cli.py init

# Initialize template
python cli.py init-template ecommerce
```

### Test MCP Server:
```bash
# Start MCP server
python server.py

# The server should run without errors
# Press Ctrl+C to stop
```

### Verify Generated Data:
```bash
# Open database
sqlite3 test_dataforge.db

# Check users table
SELECT * FROM users LIMIT 5;

# Check orders table
SELECT * FROM orders LIMIT 5;

# Check foreign key integrity
SELECT COUNT(*) FROM orders WHERE user_id NOT IN (SELECT id FROM users);
# Should return 0
```

---

## ✅ Pre-Publication Checklist

Before publishing DataForge, ensure:

- [ ] All 14 automated tests pass
- [ ] Manual CLI testing works
- [ ] MCP server starts without errors
- [ ] Generated data is realistic
- [ ] Foreign keys maintain integrity
- [ ] All 15+ locales work
- [ ] YAML configs load correctly
- [ ] Templates initialize successfully
- [ ] Performance is acceptable (< 5s for 100 rows)
- [ ] Complex types (UUID, JSON, Arrays) work
- [ ] Documentation is up to date
- [ ] LICENSE file exists
- [ ] .gitignore exists

---

## 🚀 Next Steps After Testing

### If All Tests Pass ✅:
1. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: DataForge v1.0.0"
   git branch -M main
   git remote add origin https://github.com/yourusername/dataforge.git
   git push -u origin main
   ```

2. **Publish to PyPI**
   ```bash
   pip install build twine
   python -m build
   twine upload dist/*
   ```

3. **Create First Release**
   - Go to GitHub Releases
   - Create new release: v1.0.0
   - Add release notes from CHANGELOG.md

4. **Start Marketing**
   - Post on Reddit (r/Python, r/Database)
   - Post on Hacker News
   - Post on Twitter/X
   - Post on LinkedIn
   - Create Upwork profile

### If Tests Fail ❌:
1. **Review Errors**
   - Check which tests failed
   - Read error messages carefully

2. **Fix Issues**
   - Fix bugs in code
   - Update logic if needed
   - Add missing features

3. **Re-run Tests**
   ```bash
   python test_dataforge.py
   ```

4. **Repeat Until All Pass**
   - Keep fixing and testing
   - Don't publish until 100% pass rate

---

## 💡 Tips

1. **Run tests after every code change**
   ```bash
   python test_dataforge.py
   ```

2. **Test with different databases**
   - SQLite (default in tests)
   - PostgreSQL (if available)
   - MySQL (if available)

3. **Test with different locales**
   ```bash
   python cli.py seed users 10 --locale ru_RU
   python cli.py seed users 10 --locale ja_JP
   python cli.py seed users 10 --locale zh_CN
   ```

4. **Test edge cases**
   - Empty tables
   - Large datasets (1000+ rows)
   - Complex foreign key relationships
   - Custom values with special characters

---

## 📞 Support

If you encounter issues:

1. Check the error message carefully
2. Review the relevant code section
3. Search for similar issues online
4. Ask for help in:
   - GitHub Issues (after publishing)
   - Discord server (after creating)
   - Stack Overflow
   - Python forums

---

**Good luck with testing!** 🧪
