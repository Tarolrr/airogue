# Modularization Plan

## Current State Analysis

### Problems with Current Structure:
- `llm/world.py` is 12KB+ with multiple responsibilities
- Mixed concerns: generation, parsing, validation, orchestration
- Hard for LLMs to modify safely (too many moving parts)
- Difficult to test individual components
- No clear separation between different content types

### Current `llm/world.py` Breakdown:
- Theme generation (lines ~50-80)
- Title generation (lines ~80-110) 
- Plot generation (lines ~110-150)
- Game mechanics generation (lines ~150-200)
- Item generation (lines ~200-240)
- World orchestration (lines ~240-280)
- Output formatting (lines ~280-320)

## Target Modular Structure

```
llm/
├── __init__.py
├── models.py                    # Pydantic models (existing)
├── orchestrator.py              # Coordinates all generation
├── generators/
│   ├── __init__.py
│   ├── base_generator.py        # Abstract base class
│   ├── theme_generator.py       # Theme generation only
│   ├── title_generator.py       # Title generation only
│   ├── plot_generator.py        # Plot generation only
│   ├── mechanics_generator.py   # Game mechanics only
│   └── item_generator.py        # Item generation only
├── parsers/
│   ├── __init__.py
│   ├── base_parser.py           # Common parsing logic
│   ├── theme_parser.py          # Theme-specific parsing
│   ├── mechanics_parser.py      # Mechanics parsing
│   └── item_parser.py           # Item parsing
├── validators/
│   ├── __init__.py
│   ├── content_validator.py     # Content validation
│   └── contract_validator.py    # Contract compliance
└── providers/                   # Existing LLM providers
    ├── __init__.py
    └── openai_provider.py
```

## Migration Strategy

### Phase 1: Extract Generators (High Priority)
1. Create `llm/generators/base_generator.py` with common interface
2. Extract theme generation → `theme_generator.py`
3. Extract plot generation → `plot_generator.py`
4. Extract mechanics generation → `mechanics_generator.py`
5. Extract item generation → `item_generator.py`

### Phase 2: Create Orchestrator
1. Create `llm/orchestrator.py` to coordinate generators
2. Move world generation logic from `world.py` to orchestrator
3. Update `world.py` to use orchestrator (backward compatibility)

### Phase 3: Add Validation Layer
1. Create `llm/validators/content_validator.py`
2. Add validation to each generator
3. Implement fallback mechanisms

### Phase 4: Improve Parsing
1. Extract parsing logic to `llm/parsers/`
2. Create specialized parsers for each content type
3. Add better error handling

## Implementation Details

### Base Generator Contract
```python
# llm/generators/base_generator.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from llm.models import GenerationContext

T = TypeVar('T')

class BaseGenerator(ABC, Generic[T]):
    """Base class for all LLM content generators"""
    
    def __init__(self, llm_provider, parser, validator):
        self.llm = llm_provider
        self.parser = parser
        self.validator = validator
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def generate(self, context: GenerationContext, **kwargs) -> T:
        """Generate content of type T"""
        pass
    
    @abstractmethod
    def _create_prompt(self, context: GenerationContext, **kwargs) -> str:
        """Create LLM prompt for this generator"""
        pass
    
    @abstractmethod
    def _get_fallback(self, context: GenerationContext, **kwargs) -> T:
        """Return fallback content if generation fails"""
        pass
    
    def _generate_safely(self, prompt: str, context: GenerationContext, **kwargs) -> T:
        """Generate with error handling and validation"""
        try:
            raw_output = self.llm.generate(prompt)
            parsed_output = self.parser.parse(raw_output)
            
            validation_result = self.validator.validate(parsed_output)
            if not validation_result.is_valid:
                self.logger.warning(f"Invalid output: {validation_result.errors}")
                return self._get_fallback(context, **kwargs)
            
            return parsed_output
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            return self._get_fallback(context, **kwargs)
```

### Example Generator Implementation
```python
# llm/generators/theme_generator.py
from .base_generator import BaseGenerator
from llm.models import Theme, GenerationContext

class ThemeGenerator(BaseGenerator[Theme]):
    """Generates game themes using LLM"""
    
    def generate(self, context: GenerationContext) -> Theme:
        """Generate theme based on user context"""
        prompt = self._create_prompt(context)
        return self._generate_safely(prompt, context)
    
    def _create_prompt(self, context: GenerationContext) -> str:
        return f"""
        Generate a unique theme for a roguelike game.
        User preference: {context.user_input or 'any'}
        
        Requirements:
        - Name: 1-50 characters
        - Description: 1-200 characters  
        - Mood: dark, light, or neutral
        
        Return JSON format: {{"name": "...", "description": "...", "mood": "..."}}
        """
    
    def _get_fallback(self, context: GenerationContext) -> Theme:
        return Theme(
            name="Generic Adventure",
            description="A classic adventure in an unknown land",
            mood="neutral"
        )
```

### Orchestrator Design
```python
# llm/orchestrator.py
class WorldOrchestrator:
    """Coordinates all content generation for world building"""
    
    def __init__(self):
        self.theme_gen = ThemeGenerator(...)
        self.plot_gen = PlotGenerator(...)
        self.mechanics_gen = MechanicsGenerator(...)
        self.item_gen = ItemGenerator(...)
    
    def generate_complete_world(self, context: GenerationContext) -> CompleteWorld:
        """Generate all world content in correct order"""
        
        # Generate in dependency order
        theme = self.theme_gen.generate(context)
        plot = self.plot_gen.generate(context, theme=theme)
        mechanics = self.mechanics_gen.generate(context, theme=theme, plot=plot)
        
        # Generate items for each mechanic
        all_items = []
        for mechanic in mechanics:
            items = self.item_gen.generate(context, mechanic=mechanic)
            all_items.extend(items)
        
        return CompleteWorld(
            theme=theme,
            plot=plot,
            mechanics=mechanics,
            items=all_items
        )
```

## Migration Steps

### Step 1: Create Base Structure
```bash
mkdir -p llm/generators llm/parsers llm/validators
touch llm/generators/__init__.py
touch llm/parsers/__init__.py  
touch llm/validators/__init__.py
```

### Step 2: Extract First Generator
1. Create `base_generator.py`
2. Extract theme generation from `world.py`
3. Create `theme_generator.py`
4. Add tests for theme generator
5. Update `world.py` to use new generator

### Step 3: Repeat for Other Generators
- Follow same pattern for plot, mechanics, items
- Each generator gets its own file and tests
- Update world.py incrementally

### Step 4: Create Orchestrator
- Move coordination logic to orchestrator
- Keep world.py as thin wrapper for backward compatibility

## Testing Strategy

### Each Generator Gets:
- Unit tests with mocked LLM
- Contract compliance tests
- Error handling tests
- Fallback mechanism tests

### Integration Tests:
- Full pipeline through orchestrator
- Error recovery scenarios
- Performance tests

## Benefits of This Structure

### For LLM Development:
- **Single Responsibility**: Each file has one clear purpose
- **Clear Contracts**: Explicit interfaces reduce confusion
- **Safe Modifications**: Changes isolated to specific generators
- **Better Testing**: Each component tested independently
- **Easier Debugging**: Problems isolated to specific generators

### For Maintainability:
- **Modular**: Easy to add new content types
- **Extensible**: New generators follow same pattern
- **Testable**: Each component independently testable
- **Documented**: Clear contracts and responsibilities

## Risk Mitigation

### Backward Compatibility:
- Keep existing `world.py` interface working
- Gradual migration, not big bang
- Extensive testing during transition

### LLM Safety:
- Clear documentation of what each file does
- Contracts prevent interface breaking
- Comprehensive tests catch regressions
- Fallback mechanisms prevent total failures

## Success Metrics

- [ ] `world.py` reduced from 12KB to <2KB (orchestrator wrapper)
- [ ] Each generator file <200 lines
- [ ] 100% test coverage on new modules
- [ ] All existing functionality preserved
- [ ] LLM development guidelines followed
- [ ] Documentation complete and accurate
