---
trigger: always_on
---

# LLM Development Guidelines

## 🚨 CRITICAL SETUP - ACTIVATE VIRTUAL ENVIRONMENT FIRST! 🚨

**⚠️ BEFORE DOING ANYTHING ELSE, ALWAYS ACTIVATE THE VIRTUAL ENVIRONMENT:**

```bash
# Windows (Command Prompt)
venv\Scripts\activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

**🔥 YOU MUST ACTIVATE THE VENV BEFORE EVERY DEVELOPMENT SESSION! 🔥**

---

## 🚨 CRITICAL RULES - READ FIRST

### ⚠️ NEVER MODIFY THESE FILES/FOLDERS:
- `config/` - Contains immutable game rules
- `main.py` - TCOD lifecycle management (modify only with extreme care)
- `pyproject.toml` - Dependencies (discuss changes first)

### 🎯 GOLDEN RULES:
1. **🚨 ACTIVATE VENV FIRST** - Always activate the virtual environment before any work (`venv\Scripts\activate`)
2. **ONE MODULE AT A TIME** - Never modify multiple unrelated files simultaneously
3. **READ BEFORE WRITE** - Always examine existing code and documentation first
4. **TEST BEFORE COMMIT** - Run tests after every change
5. **VALIDATE CONTRACTS** - Check `MODULE_CONTRACTS.md` for interface requirements

## 📋 Pre-Development Checklist

Before making ANY changes:

- [ ] **🚨 ACTIVATE VIRTUAL ENVIRONMENT** (`venv\Scripts\activate` on Windows, `source venv/bin/activate` on Linux/Mac)
- [ ] Read the module's docstring and purpose
- [ ] Check `docs/MODULE_CONTRACTS.md` for interface requirements
- [ ] Look for existing similar implementations
- [ ] Identify which tests cover this area
- [ ] Understand the module's dependencies

## 🧪 Testing Process (MANDATORY)

### 🚨 FIRST: ACTIVATE VIRTUAL ENVIRONMENT! 🚨
```bash
# ALWAYS START WITH THIS:
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### Before Any Code Changes:
```bash
# 1. Run existing tests to establish baseline
pytest tests/ -v

# 2. Run specific module tests if they exist
pytest tests/test_[module_name].py -v
```

### After Making Changes:
```bash
# 1. Run all tests
pytest tests/ -v

# 2. Run integration tests
pytest tests/test_integration.py -v

# 3. Validate the full pipeline still works
python -m pytest tests/test_world_generation.py -v
```

### If Tests Fail:
1. **DO NOT** modify unrelated code to "fix" tests
2. **DO NOT** disable or skip failing tests
3. **REVERT** your changes and analyze the root cause
4. Fix the actual issue, not the symptoms

## 🏗️ Module-Specific Guidelines

### `llm/` Directory
**Purpose**: LLM content generation with clear boundaries

#### When working on generators (`llm/generators/`):
- Each generator has ONE responsibility (theme, plot, mechanics, items)
- Input: Well-defined context object
- Output: Validated Pydantic model
- Never mix generation logic between generators

#### Example - Good vs Bad:
```python
# ✅ GOOD - Single responsibility
class ThemeGenerator:
    def generate(self, context: GenerationContext) -> Theme:
        """Generate ONLY theme. Nothing else."""
        pass

# ❌ BAD - Mixed responsibilities  
class ThemeGenerator:
    def generate_theme_and_plot(self, context):  # DON'T DO THIS
        pass
```

### `game/` Directory
**Purpose**: Core game engine using ECS pattern

#### When modifying components (`game/components.py`):
- Components are pure data structures
- No business logic in components
- Follow existing naming conventions
- Test component serialization/deserialization

#### When modifying world tools (`game/world_tools.py`):
- This bridges LLM content to game entities
- Always validate LLM content before creating entities
- Use defensive programming - assume LLM output might be malformed

### `tests/` Directory
**Purpose**: Comprehensive test coverage

#### Test Writing Rules:
- One test file per module: `test_[module_name].py`
- Test both success and failure cases
- Use descriptive test names: `test_theme_generator_with_invalid_context_raises_error`
- Mock LLM calls in unit tests, use real LLM in integration tests

## 🔍 Common LLM Development Pitfalls

### ❌ What LLMs Often Do Wrong:
1. **Ignore existing patterns** - Always check how similar functionality is implemented
2. **Break interfaces** - Changing function signatures without updating callers
3. **Add unnecessary complexity** - Keep solutions simple and focused
4. **Skip validation** - Always validate inputs and outputs
5. **Modify multiple files** - Focus on one module at a time

### ✅ How to Avoid These Issues:
1. **Study existing code** before making changes
2. **Follow established patterns** in the codebase
3. **Use type hints** and validate inputs/outputs
4. **Write tests first** (TDD approach when possible)
5. **Make minimal changes** to achieve the goal

## 🚀 Development Workflow

### 🚨 ALWAYS START BY ACTIVATING VENV: `venv\Scripts\activate` 🚨

### For New Features:
1. **Plan**: Update `docs/ARCHITECTURE.md` if adding new modules
2. **Design**: Define interfaces in `docs/MODULE_CONTRACTS.md`
3. **Test**: Write tests first (TDD)
4. **Implement**: Write minimal code to pass tests
5. **Validate**: Run full test suite
6. **Document**: Update relevant documentation

### For Bug Fixes:
1. **Reproduce**: Write a test that demonstrates the bug
2. **Analyze**: Understand root cause (don't guess)
3. **Fix**: Make minimal change to fix the actual issue
4. **Verify**: Ensure the test now passes
5. **Regression**: Run full test suite to ensure no new bugs

## 📚 Required Reading

Before contributing to specific areas:

- **LLM Integration**: Read `llm/README.md` (when created)
- **Game Engine**: Read `game/README.md` (when created)  
- **Testing**: Read `tests/README.md` (when created)
- **Architecture**: Read `docs/ARCHITECTURE.md`

## 🆘 When Things Go Wrong

### 🚨 REMINDER: Make sure you have the virtual environment activated! 🚨
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### If You Break Something:
1. **Analyze the issue** - What exactly broke?
2. **Try to fix it** - You can try to fix it yourself
3. **Ask for help to revert changes** - User is able to revert specific changes you made through Windsurf UI

### If Tests Are Failing:
1. **Read the error message** carefully
2. **Check if your changes broke the contract** (see `MODULE_CONTRACTS.md`)
3. **Look for similar test patterns** in the codebase
4. **Fix the root cause**, not the symptoms

## 🎯 Success Metrics

A good LLM contribution:
- ✅ Passes all existing tests
- ✅ Follows established patterns
- ✅ Has clear, single responsibility
- ✅ Includes appropriate tests
- ✅ Updates documentation if needed
- ✅ Doesn't break module contracts

Remember: **Quality over speed**. It's better to make one solid, well-tested change than multiple rushed changes that introduce bugs.
