# AiRogue Architecture

## Overview
AiRogue is a roguelike game that uses Large Language Models (LLMs) to dynamically generate game content. The architecture is designed to be LLM-friendly, modular, and resilient to AI-assisted development.

## Core Principles
1. **Single Responsibility**: Each module has one clear purpose
2. **Explicit Contracts**: Clear interfaces between components
3. **Defensive Programming**: Validation and error handling at boundaries
4. **LLM-Safe**: Resistant to common LLM development pitfalls

## System Architecture

```
AiRogue/
├── main.py                 # Entry point, TCOD setup
├── g.py                   # Global state (minimal)
├── config/                # Immutable game rules
├── game/                  # Game engine components
│   ├── states.py         # Game state management
│   ├── components.py     # ECS components
│   ├── tags.py          # Entity tags
│   ├── slots.py         # Action handlers
│   └── world_tools.py   # World-to-game bridge
├── llm/                  # LLM content generation
│   ├── generators/      # Focused content generators
│   ├── parsers/         # Output parsing
│   ├── validators/      # Content validation
│   └── orchestrator.py  # Generation coordination
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

### `config/`
- **Purpose**: Immutable game rules and constants
- **LLM Safety**: 🚫 **NEVER MODIFY** - These define core game behavior

## Data Flow

1. **World Generation**: `llm/orchestrator.py` coordinates content generation
2. **Content Validation**: Each piece of content is validated before use
3. **Game Integration**: `game/world_tools.py` converts LLM content to game entities
4. **Rendering**: TCOD renders the game world

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
