# Testing Guide for AiRogue

## 🚨 CRITICAL - READ FIRST

**TESTING BASELINE STATUS: ✅ ESTABLISHED**
- All dependencies resolved
- Contract tests passing (4 passed, 4 skipped)
- Foundation ready for test-driven development

## 🚨 MANDATORY WORKFLOW FOR ALL DEVELOPMENT

### **BEFORE ANY CODE CHANGES:**
```bash
# 1. ACTIVATE VIRTUAL ENVIRONMENT (CRITICAL!)
venv\Scripts\activate

# 2. Run existing tests to establish baseline
pytest tests/ -v
# Expected: 4 passed, 4 skipped, 2 warnings

# 3. Identify which tests cover the area you're changing
pytest tests/ -k "your_module_name" -v
```

### **DURING DEVELOPMENT (TDD):**
```bash
# 1. Write failing test first
# 2. Run the specific test to confirm it fails
pytest tests/test_your_module.py::test_your_function -v

# 3. Implement minimal code to make test pass
# 4. Run test again to confirm it passes
# 5. Run full test suite to check for regressions
pytest tests/ -v
```

### **BEFORE COMMITTING CHANGES:**
```bash
# 1. Run all tests - MUST PASS
pytest tests/ -v

# 2. Run integration tests
pytest tests/ -v -m integration

# 3. If ANY test fails, investigate and fix before proceeding
```

## Current Test Structure

```
tests/
├── conftest.py              # ✅ Pytest configuration and shared fixtures
├── test_integration.py      # ✅ Contract tests (4 passing, 4 skipped)
├── test_llm_generators.py   # 🚧 TODO: Create for modular generators
├── test_game_components.py  # 🚧 TODO: Create for game components
├── test_validation.py       # 🚧 TODO: Create for content validation
└── README.md               # 📖 This file
```

## Test Commands Reference

### **Basic Commands (Use These)**
```bash
# Run all tests (standard command)
pytest tests/ -v

# Run specific test file
pytest tests/test_integration.py -v

# Run only passing tests (skip integration placeholders)
pytest tests/ -v -k "not SKIPPED"

# Run with coverage (when available)
pytest tests/ --cov=. --cov-report=html
```

### **Test Markers**
- `@pytest.mark.integration` - Full pipeline tests (may be slow)
- `@pytest.mark.llm` - Tests requiring actual LLM API calls
- `@pytest.mark.slow` - Tests that take significant time

### **Environment Setup**
```bash
# Dependencies are installed via pip in venv
# langchain-core and other required packages are available

# Optional: Set environment variables for LLM tests
set OPENAI_API_KEY=your-key-here
```

## Test Categories

### 1. Unit Tests
Test individual components in isolation:
- LLM generators (theme, plot, mechanics, items)
- Content validators
- Game components
- Utility functions

### 2. Integration Tests
Test component interactions:
- Full world generation pipeline
- LLM content to game entity conversion
- Error handling and recovery

### 3. Contract Tests
Verify modules follow their defined contracts:
- Input/output type validation
- Error handling behavior
- Interface compliance

## Writing Tests

### Test Naming Convention
```python
def test_[component]_[scenario]_[expected_result]():
    """
    Clear description of what this test verifies.
    
    This test ensures that [component] correctly handles [scenario]
    and produces [expected_result].
    """
```

### Using Fixtures
```python
def test_theme_generator_with_valid_context(sample_generation_context, mock_llm):
    """Test theme generation with valid input"""
    generator = ThemeGenerator(llm=mock_llm)
    result = generator.generate(sample_generation_context)
    
    assert isinstance(result, Theme)
    assert result.name is not None
    assert len(result.name) <= 50
```

### Mocking LLM Calls
```python
@patch('llm.generators.theme_generator.ChatOpenAI')
def test_theme_generator_without_api_calls(mock_openai):
    """Test theme generation without making actual API calls"""
    mock_openai.return_value.generate.return_value = "Mock theme response"
    
    generator = ThemeGenerator()
    # Test logic here
```

## Test Data

### Fixtures Available
- `sample_generation_context` - Valid GenerationContext
- `sample_theme` - Valid Theme object
- `sample_plot` - Valid Plot object
- `sample_game_mechanic` - Valid GameMechanic
- `sample_item` - Valid Item
- `mock_llm` - Mocked LLM for testing
- `content_validator` - ContentValidator instance

### Creating Test Data
```python
# In your test file
def test_with_custom_data():
    custom_theme = Theme(
        name="Test Theme",
        description="Theme for testing",
        mood="neutral"
    )
    # Use custom_theme in test
```

## Common Test Patterns

### Testing LLM Generators
```python
def test_generator_contract_compliance():
    """Ensure generator follows its contract"""
    generator = SomeGenerator()
    
    # Test with valid input
    result = generator.generate(valid_input)
    assert isinstance(result, ExpectedType)
    
    # Test with invalid input
    with pytest.raises(ValidationError):
        generator.generate(invalid_input)
    
    # Test output validation
    assert validator.validate(result).is_valid
```

### Testing Error Handling
```python
def test_graceful_error_handling():
    """Test that errors are handled gracefully"""
    generator = SomeGenerator()
    
    with patch.object(generator, '_llm_call', side_effect=Exception("API Error")):
        result = generator.generate(valid_input)
        
        # Should return fallback, not crash
        assert result is not None
        assert isinstance(result, ExpectedType)
```

### Testing Validation
```python
def test_validation_catches_invalid_data():
    """Test that validation catches all invalid cases"""
    validator = ContentValidator()
    
    invalid_cases = [
        Theme(name="", description="valid"),  # Empty name
        Theme(name="x" * 100, description="valid"),  # Too long
        Theme(name="valid", description=""),  # Empty description
    ]
    
    for invalid_theme in invalid_cases:
        result = validator.validate_theme(invalid_theme)
        assert not result.is_valid
        assert len(result.errors) > 0
```

## Debugging Failed Tests

### 1. Read the Error Message
```bash
# Run with verbose output
pytest tests/test_failing.py::test_name -v -s

# Show local variables on failure
pytest tests/test_failing.py::test_name -v -s --tb=long
```

### 2. Use Print Debugging
```python
def test_debugging_example():
    result = some_function(input_data)
    print(f"DEBUG: result = {result}")
    print(f"DEBUG: type = {type(result)}")
    assert result.is_valid
```

### 3. Use Pytest's Built-in Debugging
```bash
# Drop into debugger on failure
pytest tests/test_failing.py::test_name --pdb
```

## Continuous Integration

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Test Coverage Requirements
- Minimum 80% code coverage
- All public functions must have tests
- All error paths must be tested

## Best Practices

### DO:
- ✅ Write tests before implementing features (TDD)
- ✅ Use descriptive test names
- ✅ Test both success and failure cases
- ✅ Mock external dependencies (LLM APIs)
- ✅ Use fixtures for common test data
- ✅ Keep tests focused and independent

### DON'T:
- ❌ Write tests that depend on external services
- ❌ Make tests depend on each other
- ❌ Test implementation details, test behavior
- ❌ Skip writing tests for "simple" functions
- ❌ Leave failing tests in the codebase

## Troubleshooting

### Common Issues:
1. **Import errors**: Check `__init__.py` files exist
2. **Fixture not found**: Check `conftest.py` imports
3. **Tests pass individually but fail together**: Check for shared state
4. **Slow tests**: Use mocks instead of real LLM calls

### Getting Help:
- Check `docs/TROUBLESHOOTING.md` for common issues
- Look at existing tests for patterns
- Use `pytest --collect-only` to see test discovery issues

Remember: Good tests are your safety net for LLM-driven development!
