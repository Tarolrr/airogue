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

### `llm/generators/theme_generator.py`
**Purpose**: Generate game themes using LLM
**Status**: 🔄 To be implemented

```python
# CONTRACT
class ThemeGenerator:
    def generate(self, context: GenerationContext) -> Theme:
        """
        INPUT CONTRACT:
        - context: GenerationContext with user preferences
        - context.user_input: Optional string with user theme preference
        
        OUTPUT CONTRACT:
        - Returns: Theme object (see llm/models.py)
        - Theme.name: Non-empty string, max 50 chars
        - Theme.description: Non-empty string, max 200 chars
        - Theme.mood: One of ["dark", "light", "neutral"]
        
        GUARANTEES:
        - Always returns valid Theme object
        - Never returns None
        - Validates output before returning
        
        CONSTRAINTS:
        - ONLY generates themes, never plots/mechanics/items
        - Does not modify global state
        - Thread-safe
        """
```

### `llm/generators/plot_generator.py`
**Purpose**: Generate game plots based on theme
**Status**: 🔄 To be implemented

```python
# CONTRACT
class PlotGenerator:
    def generate(self, theme: Theme, context: GenerationContext) -> Plot:
        """
        INPUT CONTRACT:
        - theme: Valid Theme object from ThemeGenerator
        - context: GenerationContext with additional preferences
        
        OUTPUT CONTRACT:
        - Returns: Plot object (see llm/models.py)
        - Plot.summary: Non-empty string, max 300 chars
        - Plot.objectives: List of 1-3 objective strings
        - Plot.setting_details: Non-empty string, max 500 chars
        
        GUARANTEES:
        - Plot is consistent with provided theme
        - Always returns valid Plot object
        - Validates theme input
        
        CONSTRAINTS:
        - ONLY generates plots, never themes/mechanics/items
        - Must use provided theme, not generate new one
        """
```

### `llm/generators/mechanics_generator.py`
**Purpose**: Generate game mechanics based on theme and plot
**Status**: 🔄 To be implemented

```python
# CONTRACT
class MechanicsGenerator:
    def generate(self, theme: Theme, plot: Plot, context: GenerationContext) -> List[GameMechanic]:
        """
        INPUT CONTRACT:
        - theme: Valid Theme object
        - plot: Valid Plot object
        - context: GenerationContext
        
        OUTPUT CONTRACT:
        - Returns: List of GameMechanic objects
        - Length: 3-7 mechanics
        - Each mechanic has valid name, description, rules
        
        GUARANTEES:
        - Mechanics are consistent with theme and plot
        - No duplicate mechanics
        - All mechanics are implementable in ASCII roguelike
        
        CONSTRAINTS:
        - ONLY generates mechanics, never themes/plots/items
        - Max 7 mechanics (game balance requirement)
        - No mechanics requiring sound (engine limitation)
        """
```

### `llm/generators/item_generator.py`
**Purpose**: Generate items for specific game mechanics
**Status**: 🔄 To be implemented

```python
# CONTRACT
class ItemGenerator:
    def generate(self, mechanic: GameMechanic, context: GenerationContext) -> List[Item]:
        """
        INPUT CONTRACT:
        - mechanic: Valid GameMechanic object
        - context: GenerationContext
        
        OUTPUT CONTRACT:
        - Returns: List of Item objects
        - Length: 1-5 items per mechanic
        - Each item supports the given mechanic
        
        GUARANTEES:
        - Items are balanced for the mechanic
        - Items have valid ASCII symbols
        - No duplicate items within mechanic
        
        CONSTRAINTS:
        - ONLY generates items for ONE mechanic
        - Max 5 items per mechanic call
        - Items must be representable in ASCII
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
