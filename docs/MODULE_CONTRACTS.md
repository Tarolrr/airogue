# Module Contracts

This document defines the explicit interfaces and contracts between modules. **LLMs must respect these contracts** - breaking them will cause system failures.

## 🎯 Core Principle
Each module has a **contract** - a promise about what it provides and what it expects. Breaking these contracts breaks the system.

## 📋 Contract Format

For each module, we define:
- **Purpose**: What this module does
- **Inputs**: What it expects to receive
- **Outputs**: What it promises to provide
- **Dependencies**: What other modules it uses
- **Guarantees**: What it promises to maintain
- **Constraints**: What it will never do

---

## `llm/` Module Contracts

### `llm/generators/world_generator.py`
**Purpose**: Generate all world content using LLM (themes, plots, mechanics, items)
**Status**: ✅ Implemented

```python
# CONTRACT
class WorldGenerator:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", temperature: float = 1.0):
        """
        INPUT CONTRACT:
        - api_key: Optional OpenAI API key
        - model: LLM model to use
        - temperature: Float between 0.0 and 2.0
        
        GUARANTEES:
        - Initializes LLM client lazily (only when needed)
        - Handles API key management
        - Creates parsers for different content types
        
        CONSTRAINTS:
        - Does not make API calls during initialization
        """
    
    def generate_themes(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, List[str]]:
        """
        INPUT CONTRACT:
        - context: Optional dictionary with generation context
        
        OUTPUT CONTRACT:
        - Returns: Dictionary with 'themes' key containing list of theme strings
        - Each theme is a coherent game theme
        
        GUARANTEES:
        - Always returns at least one theme
        - Validates output before returning
        
        CONSTRAINTS:
        - ONLY generates themes
        - Does not modify global state
        - Thread-safe
        """
    
    def generate_title(self, theme: str) -> str:
        """
        INPUT CONTRACT:
        - theme: Non-empty string representing the game theme
        
        OUTPUT CONTRACT:
        - Returns: String containing the game title
        
        GUARANTEES:
        - Title is consistent with provided theme
        - Always returns a non-empty string
        
        CONSTRAINTS:
        - ONLY generates a title based on theme
        """

    def generate_plot(self, theme: str, title: str) -> Dict[str, Any]:
        """
        INPUT CONTRACT:
        - theme: Non-empty string representing the game theme
        - title: Non-empty string representing the game title
        
        OUTPUT CONTRACT:
        - Returns: Dictionary with plot details
        - Contains 'setting', 'plot_summary', 'core_mechanics' keys
        
        GUARANTEES:
        - Plot is consistent with provided theme and title
        - Always returns a valid dictionary
        
        CONSTRAINTS:
        - ONLY generates plot based on theme and title
        """
        
    def generate_mechanics(self, theme: str, setting: str, plot: str) -> List[Dict[str, Any]]:
        """
        INPUT CONTRACT:
        - theme: Non-empty string representing the game theme
        - setting: Non-empty string representing the game setting
        - plot: Non-empty string representing the plot summary
        
        OUTPUT CONTRACT:
        - Returns: List of dictionaries representing game mechanics
        - Each mechanic has 'name', 'description', and 'rules' keys
        
        GUARANTEES:
        - Mechanics are consistent with theme, setting, and plot
        - No duplicate mechanics
        - All mechanics are implementable in ASCII roguelike
        
        CONSTRAINTS:
        - Max number of mechanics limited for game balance
        - No mechanics requiring sound (engine limitation)
        """

    def generate_items(self, mechanics: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        INPUT CONTRACT:
        - mechanics: List of dictionaries representing game mechanics
        
        OUTPUT CONTRACT:
        - Returns: Dictionary with 'items' key containing a list of item dictionaries
        - Each item has 'name', 'description', 'mechanics_link' keys
        
        GUARANTEES:
        - Items are balanced for the given mechanics
        - Items have valid ASCII symbols
        - No duplicate items
        
        CONSTRAINTS:
        - ONLY generates items for mechanics
        - 1-5 items per mechanic
        - Items must be representable in ASCII
        """
```

### `llm/generators/theme_generator.py`
**Purpose**: Generate game theme
**Status**: 🔄 Future implementation (currently part of WorldGenerator)

```python
# CONTRACT
class ThemeGenerator:
    def generate(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate theme based on optional context.
        
        GUARANTEES: 
        - Theme is implementable in ASCII roguelike
        - Theme has appropriate depth for short game experience
        
        CONSTRAINTS:
        - ONLY generates theme, never plots/mechanics/items
        - No themes requiring complex graphics
        """
```

### `llm/generators/plot_generator.py`
**Purpose**: Generate game plot based on theme
**Status**: 🔄 Future implementation (currently part of WorldGenerator)

```python
# CONTRACT
class PlotGenerator:
    def generate(self, theme: str, title: str) -> str:
        """Generate plot based on theme and title.
        
        GUARANTEES:
        - Plot complements theme and title
        - Plot has proper narrative arc for roguelike
        
        CONSTRAINTS:
        - ONLY generates plot, never themes/mechanics/items
        - Plot must be completable in < 1 hour gameplay
        - No complex branching narratives (engine limitation)
        """
```

### `llm/generators/mechanics_generator.py`
**Purpose**: Generate gameplay mechanics based on theme and plot
**Status**: 🔄 Future implementation (currently part of WorldGenerator)

```python
# CONTRACT
class MechanicsGenerator:
    def generate(self, theme: str, title: str, plot: str) -> List[Dict[str, str]]:
        """Generate gameplay mechanics based on theme, title and plot.
        
        GUARANTEES:
        - Mechanics are consistent with theme and plot
        - No duplicate mechanics
        - All implementable in ASCII roguelike
        
        CONSTRAINTS:
        - ONLY generates mechanics, never themes/plots/items
        - 2-7 mechanics (game balance requirement)
        - No mechanics requiring sound (engine limitation)
        """
```

### `llm/generators/item_generator.py`
**Purpose**: Generate items for specific game mechanics
**Status**: 🔄 Future implementation (currently part of WorldGenerator)

```python
# CONTRACT
class ItemGenerator:
    def generate(self, mechanics: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Generate items supporting the provided mechanics.
        
        GUARANTEES:
        - Items are balanced for mechanics
        - Items have valid ASCII symbols
        - No duplicate items
        
        CONSTRAINTS:
        - ONLY generates items for mechanics
        - 1-5 items per mechanic
        - Items must be representable in ASCII
        """
```

### `llm/generators/base.py`
**Purpose**: Provide base generator functionality and LLM initialization
**Status**: ✅ Implemented

```python
# CONTRACT
class BaseGenerator(ABC):
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-nano-2025-04-14", temperature: float = 1.0):
        """Initialize generator with LLM settings.
        
        GUARANTEES:
        - Safe API key handling
        - Consistent LLM interface
        
        CONSTRAINTS:
        - API keys handled securely
        """
    
    @abstractmethod
    def generate(self, *args, **kwargs):
        """Abstract method all generators must implement.
        
        CONSTRAINTS:
        - Must validate inputs
        - Must handle LLM errors gracefully
        """
```

### `llm/generators/cli.py`
**Purpose**: Provide command-line interface for running generators
**Status**: ✅ Implemented

```python
# CONTRACT
def main():
    """
    INPUT CONTRACT:
    - Command line arguments
    
    OUTPUT CONTRACT:
    - Generates world content based on arguments
    - Outputs content to console or file
    
    GUARANTEES:
    - Provides help text and argument handling
    - Creates WorldGenerator with appropriate settings
    
    CONSTRAINTS:
    - Command-line tool only, not for import
    """
```

---

## `game/` Module Contracts

### `game/world_tools.py`
**Purpose**: Convert LLM-generated content into game entities
**Status**: ✅ Exists, needs contract definition

```python
# CONTRACT
class WorldTools:
    def create_world_from_llm_content(
        self, 
        theme: Theme, 
        plot: Plot, 
        mechanics: List[GameMechanic], 
        items: List[Item]
    ) -> World:
        """
        INPUT CONTRACT:
        - All inputs must be validated LLM content
        - theme, plot: Non-null objects
        - mechanics: 3-7 mechanics
        - items: Non-empty list
        
        OUTPUT CONTRACT:
        - Returns: Playable World object
        - World contains all necessary entities
        - Player entity is created and positioned
        
        GUARANTEES:
        - World is immediately playable
        - All items are placed in world
        - Game mechanics are active
        
        CONSTRAINTS:
        - Does not modify input objects
        - Creates new entities, doesn't reuse existing
        """
```

### `game/components.py`
**Purpose**: Define ECS components for game entities
**Status**: ✅ Exists

```python
# CONTRACT - Components are pure data structures
# CONSTRAINTS:
# - No business logic in components
# - All components must be serializable
# - Follow naming convention: PascalCase
# - Use type hints for all fields
```

---

## `utils/` Module Contracts

### `utils/validation.py`
**Purpose**: Validate LLM-generated content
**Status**: 🔄 To be implemented

```python
# CONTRACT
class ContentValidator:
    @staticmethod
    def validate_theme(theme: Theme) -> ValidationResult:
        """
        INPUT CONTRACT:
        - theme: Any object (may be invalid)
        
        OUTPUT CONTRACT:
        - Returns: ValidationResult with is_valid and errors
        - If is_valid=False, errors list is non-empty
        
        GUARANTEES:
        - Never raises exceptions
        - Always returns ValidationResult
        """
    
    @staticmethod
    def validate_plot(plot: Plot, theme: Theme) -> ValidationResult:
        """Validates plot is consistent with theme"""
    
    @staticmethod
    def validate_mechanics(mechanics: List[GameMechanic]) -> ValidationResult:
        """Validates mechanics list meets game requirements"""
    
    @staticmethod
    def validate_items(items: List[Item]) -> ValidationResult:
        """Validates items are game-compatible"""
```

---

## 🚨 Contract Violation Examples

### ❌ BAD - Breaking Input Contract
```python
# ThemeGenerator expecting GenerationContext, getting string
theme_gen = ThemeGenerator()
theme = theme_gen.generate("fantasy")  # WRONG! Breaks contract
```

### ❌ BAD - Breaking Output Contract
```python
# Returning None instead of Theme object
def generate(self, context: GenerationContext) -> Theme:
    if some_condition:
        return None  # WRONG! Contract says never return None
```

### ❌ BAD - Breaking Responsibility Contract
```python
# ThemeGenerator doing plot generation
class ThemeGenerator:
    def generate(self, context: GenerationContext) -> Theme:
        theme = self._generate_theme(context)
        plot = self._generate_plot(theme)  # WRONG! Not theme generator's job
        return theme
```

### ✅ GOOD - Respecting Contracts
```python
# Proper contract usage
context = GenerationContext(user_input="fantasy")
theme_gen = ThemeGenerator()
theme = theme_gen.generate(context)  # Correct input type

# Validate before using
validator = ContentValidator()
result = validator.validate_theme(theme)
if not result.is_valid:
    handle_validation_errors(result.errors)
```

---

## 🔄 Contract Evolution

### When You Need to Change a Contract:
1. **Document the change** in this file first
2. **Update all callers** before changing the implementation
3. **Update tests** to reflect new contract
4. **Consider backward compatibility** if possible

### Adding New Contracts:
1. **Define the contract** in this file first
2. **Get agreement** on the interface design
3. **Implement** following the defined contract
4. **Test** the contract thoroughly

---

## 📝 Contract Checklist

Before implementing any module:
- [ ] Contract is documented in this file
- [ ] Input/output types are clearly defined
- [ ] Guarantees and constraints are explicit
- [ ] Error handling approach is specified
- [ ] Dependencies are listed
- [ ] Tests will verify contract compliance

**Remember**: Contracts are promises. Breaking them breaks the system. When in doubt, follow the contract exactly as written.
