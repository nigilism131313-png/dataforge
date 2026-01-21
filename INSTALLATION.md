# DataForge Installation Guide

## 🚨 Problem: ModuleNotFoundError: No module named 'yaml'

This error means **PyYAML is not installed**. Let's fix it!

---

## ✅ Solution 1: Install All Dependencies (RECOMMENDED)

### Step 1: Activate Virtual Environment
```powershell
# Windows PowerShell
D:\DataForge> .venv\Scripts\Activate.ps1

# Or if using Command Prompt
D:\DataForge> .venv\Scripts\activate.bat

# Or if using Git Bash / Linux / Mac
$ source .venv/bin/activate
```

### Step 2: Install All Dependencies
```powershell
# Make sure you're in the DataForge directory
(D:\DataForge) $ pip install -r requirements.txt
```

This will install:
- mcp>=0.1.0
- sqlalchemy>=2.0.0
- faker>=20.0.0
- pydantic>=2.0.0
- pyyaml>=6.0.0  ← This is what's missing!
- tqdm>=4.65.0

### Step 3: Verify Installation
```powershell
# Check if PyYAML is installed
(D:\DataForge) $ python -c "import yaml; print('PyYAML installed successfully!')"

# Expected output:
# PyYAML installed successfully!
```

### Step 4: Run Tests Again
```powershell
# Now run the test suite
(D:\DataForge) $ python test_dataforge.py
```

---

## ✅ Solution 2: Install PyYAML Directly (ALTERNATIVE)

If Solution 1 doesn't work, try installing PyYAML directly:

```powershell
# Activate virtual environment
D:\DataForge> .venv\Scripts\Activate.ps1

# Install PyYAML directly
(D:\DataForge) $ pip install pyyaml

# Verify installation
(D:\DataForge) $ python -c "import yaml; print('PyYAML installed!')"

# Run tests
(D:\DataForge) $ python test_dataforge.py
```

---

## ✅ Solution 3: Recreate Virtual Environment (LAST RESORT)

If the above solutions don't work, recreate the virtual environment:

### Step 1: Delete Old Virtual Environment
```powershell
# Deactivate first (if activated)
(D:\DataForge) $ deactivate

# Delete the old virtual environment
D:\DataForge> Remove-Item -Recurse -Force .venv
```

### Step 2: Create New Virtual Environment
```powershell
# Create new virtual environment
D:\DataForge> python -m venv .venv

# Activate it
D:\DataForge> .venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
# Install all dependencies
(D:\DataForge) $ pip install -r requirements.txt
```

### Step 4: Run Tests
```powershell
# Run the test suite
(D:\DataForge) $ python test_dataforge.py
```

---

## 🐛 Common Installation Issues

### Issue 1: "pip not recognized"
**Error:**
```
'pip' is not recognized as an internal or external command
```

**Solution:**
```powershell
# Use python -m pip instead
D:\DataForge> python -m pip install -r requirements.txt
```

### Issue 2: "Access denied" on Windows
**Error:**
```
Access denied: '.venv'
```

**Solution:**
```powershell
# Run PowerShell as Administrator
# Right-click PowerShell → "Run as administrator"
```

### Issue 3: "SSL certificate error"
**Error:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solution:**
```powershell
# Use trusted hosts
D:\DataForge> pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

### Issue 4: "Module not found" for other modules
**Error:**
```
ModuleNotFoundError: No module named 'mcp'
```

**Solution:**
```powershell
# Install all dependencies again
D:\DataForge> pip install -r requirements.txt
```

---

## ✅ Quick Installation Checklist

Before running tests, ensure:

- [ ] Virtual environment is activated
- [ ] All dependencies are installed (`pip list`)
- [ ] PyYAML is installed (`python -c "import yaml"`)
- [ ] Faker is installed (`python -c "import faker"`)
- [ ] SQLAlchemy is installed (`python -c "import sqlalchemy"`)
- [ ] MCP is installed (`python -c "import mcp"`)
- [ ] Pydantic is installed (`python -c "import pydantic"`)
- [ ] tqdm is installed (`python -c "import tqdm"`)

---

## 🎯 Complete Installation Steps (Copy & Paste)

```powershell
# 1. Activate virtual environment
D:\DataForge> .venv\Scripts\Activate.ps1

# 2. Install all dependencies
D:\DataForge> pip install -r requirements.txt

# 3. Verify PyYAML installation
D:\DataForge> python -c "import yaml; print('PyYAML installed successfully!')"

# 4. Run tests
D:\DataForge> python test_dataforge.py
```

---

## 📊 What Each Dependency Does

| Package | Version | Purpose |
|----------|---------|---------|
| mcp | >=0.1.0 | Model Context Protocol (MCP) server |
| sqlalchemy | >=2.0.0 | Database abstraction and ORM |
| faker | >=20.0.0 | Generate fake data (names, emails, etc.) |
| pydantic | >=2.0.0 | Data validation and settings |
| pyyaml | >=6.0.0 | Parse YAML configuration files |
| tqdm | >=4.65.0 | Progress bars for long operations |

---

## 💡 Tips

### 1. Always Use Virtual Environments
```powershell
# Create virtual environment for each project
python -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate  # Linux/Mac
```

### 2. Upgrade pip First
```powershell
# Upgrade pip to latest version
D:\DataForge> python -m pip install --upgrade pip
```

### 3. Use Requirements.txt
```powershell
# Always install from requirements.txt
pip install -r requirements.txt

# NOT individual packages (unless necessary)
pip install pyyaml  # Only if you need just one
```

### 4. Check Installed Packages
```powershell
# List all installed packages
pip list

# Search for specific package
pip list | findstr pyyaml
```

---

## 🔍 Troubleshooting

### If PyYAML Still Not Found:

1. **Check Python Version:**
   ```powershell
   python --version
   # Should be 3.8 or higher
   ```

2. **Check pip Version:**
   ```powershell
   pip --version
   # Should be 20.0 or higher
   ```

3. **Check Installation:**
   ```powershell
   pip show pyyaml
   # Should show package details
   ```

4. **Reinstall PyYAML:**
   ```powershell
   pip uninstall pyyaml
   pip install pyyaml
   ```

---

## ✅ Success Indicators

You know installation is successful when:

1. ✅ No errors during `pip install -r requirements.txt`
2. ✅ `python -c "import yaml"` prints success message
3. ✅ `python test_dataforge.py` runs without import errors
4. ✅ All 14 tests execute (even if some fail)

---

## 🚀 After Successful Installation

Once PyYAML is installed and tests pass:

1. ✅ Read [`START_HERE.md`](START_HERE.md) for next steps
2. ✅ Follow the step-by-step guide
3. ✅ Publish to GitHub
4. ✅ Publish to PyPI
5. ✅ Start marketing
6. ✅ Make money! 💰

---

## 📞 Need More Help?

### Check These Files:
- [`TESTING_GUIDE.md`](TESTING_GUIDE.md) - Detailed testing instructions
- [`START_HERE.md`](START_HERE.md) - Step-by-step launch guide
- [`README.md`](README.md) - Main documentation

### Common Issues:
- **Module not found** → Install missing package
- **Permission denied** → Run as administrator
- **SSL error** → Use --trusted-host flag
- **Version conflict** → Upgrade pip first

---

**Quick Fix (Copy & Paste):**
```powershell
D:\DataForge> .venv\Scripts\Activate.ps1
D:\DataForge> pip install -r requirements.txt
D:\DataForge> python test_dataforge.py
```

**Good luck!** 🚀
