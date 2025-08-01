# AiRogue Improvement Points

## Priority 1: Critical Stability & Testing

1. **Fix Pydantic Deprecation Warnings**
   - Replace `min_items` with `min_length` and `max_items` with `max_length` in model definitions
   - Document in code why we're using these specific validators

2. **Complete Mocking Framework for Tests**
   - Create dedicated mock generators/fixtures in `conftest.py` for all LLM-dependent components
   - Ensure all unit tests can run without real API keys

3. **Decouple Game Logic from LLM Implementation**
   - Create abstraction layer for LLM operations in `llm/providers/`
   - Implement factory pattern to swap between real/mock LLM clients

## Priority 2: Architecture Alignment

4. **Implement Modular Generator Structure**
   - Create `llm/generators/` directory as mentioned in architecture docs
   - Split content generation into specialized modules (theme, plot, mechanics, items)

5. **Validate World Model Schema**
   - Add comprehensive validation for world models
   - Create proper error handling for invalid LLM responses

6. **Implement Clean Parser Modules**
   - Create `llm/parsers/` directory for output parsing logic
   - Move parsing logic from `world.py` into dedicated parser classes

## Priority 3: Code Quality & Documentation

7. **Remove Commented-Out Code**
   - Clean up unused imports and commented-out code in `llm/world.py`
   - Document why certain approaches were abandoned if relevant

8. **Document LLM Prompting Strategy**
   - Create documentation for prompt engineering patterns used
   - Explain reasoning behind temperature settings and model choices

9. **Add Code Documentation**
   - Add docstrings to all classes and important methods
   - Document contract expectations between modules

## Priority 4: Feature Improvements

10. **Implement Adaptive Difficulty**
    - Create generation parameters for difficulty adjustment
    - Add progression mechanics based on player performance

11. **Enhance Theme Variety**
    - Expand theme prompts to generate more diverse game experiences
    - Implement theme consistency checks across generated elements

12. **Create Testing UI**
    - Implement simple debugging UI for testing generated worlds
    - Add ability to regenerate specific components

## Implementation Approach

For each improvement point:

1. **Write tests first** - Define expected behavior with tests
2. **Document contract** - Update MODULE_CONTRACTS.md with interface requirements
3. **Implement solution** - Follow the established patterns in codebase
4. **Validate with tests** - Ensure all tests pass
5. **Document changes** - Update relevant documentation

## Critical Path Dependencies

The improvement points should be addressed in this order:
1. Fix stability issues (1-3)
2. Align with architecture (4-6)
3. Improve code quality (7-9)
4. Add new features (10-12)
