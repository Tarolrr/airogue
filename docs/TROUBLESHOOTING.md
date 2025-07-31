# Troubleshooting Guide

## 🚨 Common LLM Development Issues

This guide helps diagnose and fix common problems when working with LLMs on the AiRogue project.

## 🔍 Diagnostic Questions

When something breaks, ask these questions first:

1. **What exactly broke?** (Error message, unexpected behavior, test failure)
2. **What was the last change made?** (Which file, what modification)
3. **Do the tests pass?** (Run `pytest tests/ -v`)
4. **Are the contracts being followed?** (Check `MODULE_CONTRACTS.md`)

---

## 🐛 Common Issues & Solutions

### Issue: "Module not found" or Import Errors

**Symptoms:**
```
ImportError: No module named 'llm.generators'
ModuleNotFoundError: No module named 'game.components'
```

**Likely Causes:**
- Missing `__init__.py` files
- Incorrect import paths
- Circular imports

**Solutions:**
```bash
# 1. Check for missing __init__.py files
find . -name "*.py" -exec dirname {} \; | sort -u | xargs -I {} test -f {}/__init__.py || echo "Missing __init__.py in {}"

# 2. Fix import paths - use absolute imports
# ❌ BAD
from generators.theme_generator import ThemeGenerator

# ✅ GOOD  
from llm.generators.theme_generator import ThemeGenerator

# 3. Check for circular imports
python -c "import sys; sys.path.append('.'); import llm.world"
```

### Issue: LLM Generation Fails or Returns Invalid Data

**Symptoms:**
```
ValidationError: Theme name cannot be empty
TypeError: Expected Theme object, got str
```

**Likely Causes:**
- LLM output doesn't match expected format
- Missing validation
- Prompt engineering issues

**Solutions:**
```python
# 1. Add comprehensive validation
def generate_theme(self, context: GenerationContext) -> Theme:
    try:
        raw_output = self.llm.generate(prompt)
        parsed_output = self.parser.parse(raw_output)
        
        # Validate before returning
        validation_result = ContentValidator.validate_theme(parsed_output)
        if not validation_result.is_valid:
            logger.error(f"Invalid theme: {validation_result.errors}")
            return self._get_fallback_theme()
            
        return parsed_output
    except Exception as e:
        logger.error(f"Theme generation failed: {e}")
        return self._get_fallback_theme()

# 2. Add fallback mechanisms
def _get_fallback_theme(self) -> Theme:
    return Theme(
        name="Generic Fantasy",
        description="A classic fantasy adventure",
        mood="neutral"
    )
```

### Issue: Tests Failing After Code Changes

**Symptoms:**
```
FAILED tests/test_theme_generator.py::test_generate_valid_theme
AssertionError: Expected Theme object, got None
```

**Diagnostic Steps:**
```bash
# 1. Run specific failing test with verbose output
pytest tests/test_theme_generator.py::test_generate_valid_theme -v -s

# 2. Check if contract was broken
# Look at the test - what contract does it expect?
# Compare with your implementation

# 3. Run all tests to see scope of breakage
pytest tests/ -v
```

**Common Fixes:**
- **Return type mismatch**: Check function signature matches contract
- **Missing validation**: Add proper input/output validation
- **Changed interface**: Update all callers when changing function signatures

### Issue: Game Won't Start or Crashes

**Symptoms:**
```
AttributeError: 'NoneType' object has no attribute 'render'
KeyError: 'player'
```

**Likely Causes:**
- World generation failed
- Missing required entities
- TCOD initialization issues

**Diagnostic Steps:**
```python
# 1. Test world generation in isolation
python -c "
from llm.world import World
world = World('fantasy')
try:
    result = world.generate_world()
    print('World generation: SUCCESS')
    print(f'Generated: {type(result)}')
except Exception as e:
    print(f'World generation: FAILED - {e}')
"

# 2. Check entity creation
python -c "
from game.world_tools import WorldTools
# Test with minimal data
tools = WorldTools()
# ... test entity creation
"
```

### Issue: Performance Problems or Timeouts

**Symptoms:**
- LLM calls taking too long
- Application freezing
- Timeout errors

**Solutions:**
```python
# 1. Add timeouts to LLM calls
from functools import timeout

@timeout(30)  # 30 second timeout
def generate_with_timeout(self, prompt):
    return self.llm.generate(prompt)

# 2. Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=100)
def generate_theme(self, theme_type: str) -> Theme:
    # Expensive LLM call cached by input
    pass

# 3. Use async for multiple LLM calls
import asyncio

async def generate_all_content(self, context):
    tasks = [
        self.generate_theme_async(context),
        self.generate_plot_async(context),
        # ... other generators
    ]
    return await asyncio.gather(*tasks)
```

---

## 🔧 Debugging Workflow

### Step 1: Isolate the Problem
```bash
# Test each component individually
python -c "from llm.generators.theme_generator import ThemeGenerator; print('Theme generator imports OK')"
python -c "from game.components import Position; print('Game components import OK')"
python -c "from utils.validation import ContentValidator; print('Validation imports OK')"
```

### Step 2: Check Contracts
1. Open `docs/MODULE_CONTRACTS.md`
2. Find the relevant module contract
3. Verify your code follows the contract exactly
4. Check input/output types match

### Step 3: Run Tests
```bash
# Run tests in order of specificity
pytest tests/test_[specific_module].py -v    # Unit tests
pytest tests/test_integration.py -v         # Integration tests
pytest tests/ -v                           # All tests
```

### Step 4: Add Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

def problematic_function(self, input_data):
    logger.debug(f"Input: {input_data}")
    logger.debug(f"Input type: {type(input_data)}")
    
    result = self.process(input_data)
    
    logger.debug(f"Output: {result}")
    logger.debug(f"Output type: {type(result)}")
    
    return result
```

---

## 🆘 Emergency Procedures

### If You've Broken Everything:
```bash
# 1. Don't panic - Windsurf UI has your back
# The user can see all your changes as diffs in the Windsurf UI
# They can revert specific changes without affecting other work

# 2. Ask the user to review your changes
# "I've made several changes to improve the codebase. Could you please
#  review the diffs in the Windsurf UI and approve or revert any changes
#  that don't look correct?"

# 3. If you need to revert programmatically (last resort):
git status                    # See what changed
git checkout -- [filename]   # Revert specific file
```

### If Tests Won't Pass:
```bash
# 1. Find the last working commit
git bisect start
git bisect bad                # Current commit is bad
git bisect good [commit-hash] # Last known good commit
# Git will help you find the breaking commit

# 2. Understand what broke
git show [breaking-commit]    # See exactly what changed
```

### If LLM Keeps Making Same Mistakes:
1. **Update the guidelines** - Add the specific issue to `LLM_GUIDELINES.md`
2. **Add validation** - Prevent the mistake at the code level
3. **Add tests** - Catch the mistake automatically
4. **Improve contracts** - Make expectations clearer

---

## 📞 Getting Help

### Before Asking for Help:
1. **Read the error message** completely
2. **Check this troubleshooting guide**
3. **Run the diagnostic steps** above
4. **Document what you tried** and what happened

### Asking User to Review Changes:
When you've made significant changes, always ask the user to review:
```
"I've made several changes to [describe changes]. Could you please review 
the diffs in the Windsurf UI and approve or revert any changes that don't 
look correct? The UI allows you to revert specific changes without affecting 
other work."
```

### Getting Help:
Include this information:
- **Exact error message** (copy-paste, don't paraphrase)
- **What you were trying to do**
- **What you expected to happen**
- **What actually happened**
- **Steps to reproduce**
- **Your environment** (Python version, OS, etc.)

### Self-Help Resources:
- `docs/ARCHITECTURE.md` - System overview
- `docs/MODULE_CONTRACTS.md` - Interface specifications  
- `docs/LLM_GUIDELINES.md` - Development rules
- `tests/` - Examples of correct usage
- Git history - See how similar problems were solved

---

## 🎯 Prevention Tips

### Before Making Changes:
- [ ] Read the relevant module's docstring
- [ ] Check the contract in `MODULE_CONTRACTS.md`
- [ ] Look for similar existing implementations
- [ ] Run tests to establish baseline

### While Making Changes:
- [ ] Make small, incremental changes
- [ ] Test frequently (`pytest tests/test_[module].py`)
- [ ] Add logging to understand data flow
- [ ] Validate inputs and outputs

### After Making Changes:
- [ ] Run full test suite (`pytest tests/ -v`)
- [ ] Test the actual game (`python main.py`)
- [ ] Check for performance regressions
- [ ] Update documentation if needed

**Remember**: Prevention is better than debugging. Follow the guidelines, respect the contracts, and test thoroughly.
