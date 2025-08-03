# AiRogue Architecture

## Overview

AiRogue is a roguelike game that uses Large Language Models (LLMs) to dynamically generate game content. The architecture is designed to be LLM-friendly, modular, and resilient to AI-assisted development.

## Core Principles

1. **Single Responsibility**: Each module has one clear purpose
2. **Explicit Contracts**: Clear interfaces between components
3. **Defensive Programming**: Validation and error handling at boundaries
4. **LLM-Safe**: Resistant to common LLM development pitfalls

## System Architecture

```text
AiRogue/
├── main.py                 # Entry point, TCOD setup
├── g.py                   # Global state (minimal)
├── game/                  # Game engine components
│   ├── states.py         # Game state management
│   ├── components.py     # ECS components
│   ├── tags.py          # Entity tags
│   ├── slots.py         # Action handlers
│   └── world_tools.py   # World-to-game bridge
├── llm/                  # LLM content generation
│   ├── generators/      # Focused content generators
│   │   ├── base.py     # Base generator class
│   │   ├── world_generator.py # World content generator
│   │   └── cli.py      # Command-line interface for generators
│   ├── models.py       # Pydantic data models
│   ├── components.py   # LLM Component system
│   ├── world.py        # Backward-compatible world generator
│   └── providers/      # LLM provider implementations
├── utils/               # Shared utilities
├── tests/              # Comprehensive test suite
└── docs/               # Documentation
```

## Module Responsibilities

### `main.py`

- **Purpose**: Application entry point
- **Responsibilities**: TCOD initialization, main game loop
- **Dependencies**: `game.states`, `g`
- **LLM Safety**: ⚠️ **CRITICAL** - Do not modify without understanding TCOD lifecycle

### `game/`

- **Purpose**: Core game engine using ECS pattern
- **Key Files**:
  - `states.py`: Game state machine
  - `components.py`: Entity components (Position, Graphic, etc.)
  - `world_tools.py`: Converts LLM content to game entities
- **LLM Safety**: Modify components carefully - breaking ECS breaks the game

### `llm/`

- **Purpose**: LLM-based content generation
- **Architecture**: Modular generators with clear contracts
- **Key Principle**: Each generator is independent and testable
- **LLM Safety**: Always validate LLM outputs before use

### `llm/generators/`

- **Purpose**: Modular, focused content generators
- **Key Files**:
  - `base.py`: Base generator class with LLM initialization
  - `world_generator.py`: World generation (theme, plot, mechanics, items)
  - `cli.py`: Command-line tools for running generators independently
- **LLM Safety**: All generators follow the same pattern and validation

## Component System Architecture

### System Overview

The Component System extends the basic ECS with LLM-powered behaviors through pipelines and attributes. It functions similar to prefabs in Unity, where components with specific behaviors are generated and attached to game entities.

### Components

- **Purpose**: Provide LLM-generated behaviors and attributes for game entities
- **Structure**:

  ```text
  Component
  ├── pipelines: Dict[str, RunnableSerializable]
  │   └── [event_name]: [pipeline_instance]
  └── attributes: Dict[str, Attribute]
      └── [attribute_name]: Attribute
  ```

- **Location**: Components are defined in `llm/components.py`
- **Types**: ItemComponent, NPCComponent, LocationComponent, etc.

### Attributes

- **Purpose**: LLM-generated properties that define entity characteristics
- **Structure**:

  ```python
  {
    "name": "damage",
    "description": "Amount of damage dealt when attacking",
    "value": 4
  }
  ```

- **Usage**: Referenced by pipelines and game mechanics
- **Examples**:
  - Simple attributes: "damage": 4, "weight": 2
  - Complex attributes: "backstory": "A sword forged in dragon fire"

### Pipelines

- **Purpose**: Define behavior logic for components using LangChain Runnables
- **Structure**: LangChain RunnableSerializable subclasses
- **Events**: "on_use", "when_attacked", "on_interact", etc.
- **Behavior**: Pipelines can reference component attributes and affect game state
- **Example**: A sword's "on_attack" pipeline would subtract its "damage" value from target's "health"

## Data Flow

1. **World Generation**: `llm/generators/world_generator.py` handles content generation
2. **Component Generation**: LLM generates components with pipelines and attributes
3. **Content Validation**: Each component, pipeline, and attribute is validated
4. **Game Integration**: `game/world_tools.py` converts LLM content to game entities
5. **Runtime Execution**: Pipelines execute when triggered by game events
6. **Rendering**: TCOD renders the game world

## Error Handling Strategy

1. **Validation at Boundaries**: All LLM outputs are validated
2. **Graceful Degradation**: Fallback content when LLM fails
3. **Rollback Capability**: Can revert to last known good state
4. **Comprehensive Logging**: Track all LLM operations

## Testing Strategy

- **Unit Tests**: Each generator/parser tested independently
- **Integration Tests**: Full pipeline from LLM to game
- **Validation Tests**: Ensure all content meets game requirements
- **Regression Tests**: Prevent LLM-introduced bugs

## Development Guidelines

See `LLM_GUIDELINES.md` for detailed contribution rules.

## Roadmap

### Priority 1: Critical Stability & Testing

1. **Complete Mocking Framework for Tests**
   - Create dedicated mock generators/fixtures in `conftest.py` for all LLM-dependent components
   - Ensure all unit tests can run without real API keys

2. **Decouple Game Logic from LLM Implementation**
   - Create abstraction layer for LLM operations in `llm/providers/`
   - Implement factory pattern to swap between real/mock LLM clients

### Priority 2: Architecture Alignment

1. **Validate World Model Schema**
   - Create proper error handling for invalid LLM responses

2. **Implement Clean Parser Modules**
   - Create `llm/parsers/` directory for output parsing logic
   - Move parsing logic from `world.py` into dedicated parser classes

### Priority 3: Component System Implementation

1. **Create Component Base Classes**
   - Implement `llm/components.py` with base Component structure
   - Define the relationship between Components and ECS entities

2. **Implement Pipeline Framework**
   - Create pipeline base classes using LangChain RunnableSerializable
   - Define serialization/deserialization for pipelines

3. **Develop Attribute System**
   - Design attribute schema with validation
   - Create attribute generation prompts for LLM

4. **Integrate with ECS**
    - Update `game/world_tools.py` to handle Components
    - Create runtime hooks for pipeline execution

### Priority 4: Feature Improvements

1. **Implement Adaptive Difficulty**
    - Create generation parameters for difficulty adjustment
    - Add progression mechanics based on player performance

2. **Enhance Theme Variety**
    - Expand theme prompts to generate more diverse game experiences
    - Implement theme consistency checks across generated elements

3. **Create Testing UI**
    - Implement simple debugging UI for testing generated worlds
    - Add ability to regenerate specific components

## Implementation Approach

For each improvement point:

1. **Write tests first** - Define expected behavior with tests
2. **Document contract** - Update MODULE_CONTRACTS.md with interface requirements
3. **Implement solution** - Follow the established patterns in codebase
4. **Validate with tests** - Ensure all tests pass
5. **Document changes** - Update relevant documentation
