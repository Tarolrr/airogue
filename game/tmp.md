Documentation Analysis & Reorganization Plan
Based on my review, here's my assessment of the current documentation:

Current Documentation Assessment:
ARCHITECTURE.md (3.9KB) - KEEP & REFINE
Rationale: Core architectural overview, but needs updating for your new vision
Issues: Missing your new concepts (components, pipelines, attributes)
IMPROVEMENT_POINTS.md (2.9KB) - MERGE INTO ARCHITECTURE
Rationale: These are implementation tasks, not standalone documentation
Action: Move priority items to a "Roadmap" section in ARCHITECTURE.md
MODULARIZATION_PLAN.md (9.1KB) - SPLIT & REORGANIZE
Rationale: Too detailed for a single file, mixes planning with implementation
Action: Split into "Design Patterns" and "Migration Guide"
MODULE_CONTRACTS.md (14.8KB) - KEEP BUT RESTRUCTURE
Rationale: Critical for LLM safety, but too verbose
Action: Create concise contract summaries with detailed specs in separate files
TROUBLESHOOTING.md (9.1KB) - KEEP AS-IS
Rationale: Operational knowledge, good reference
Your New Vision - Let's Work Through This Together
I see you want to add three major concepts after world generation:

Components (not game.components) - Objects with pipelines and attributes
Pipelines - LangChain Runnables for entity behavior
Attributes - LLM-generated properties for entities
Questions to Refine Your Vision:
1. Components Architecture:

Should these "components" be attached to specific game entities (items, NPCs, locations)?
What's the relationship between these components and the ECS components in game/components.py?
Do you envision a hierarchy (e.g., ItemComponent, NPCComponent, LocationComponent)?
2. Pipeline Integration:

You mentioned subclassing RunnableSerializable - are you thinking of pipelines like "when_attacked", "on_use", "dialogue_flow"?
Should pipelines be composable (can one pipeline call another)?
How do pipelines interact with the game's ECS system and the slot functions?
3. Attribute System:

Are attributes like "magical_power: 5" or more complex like "backstory: 'A sword forged in dragon fire'"?
Should attributes affect game mechanics directly or through pipelines?
How do we ensure LLM-generated attributes are consistent with game balance?
4. Data Flow: Let me propose a rough diagram of how I understand your vision:

World Generation → Entity Descriptions
       ↓
Component Generation → {pipelines: [...], attributes: {...}}
       ↓
Pipeline Serialization → LangChain Runnables
       ↓
Game Runtime → Execute pipelines based on game events
Is this the right flow? What am I missing?

Next Steps:

Let's refine these concepts together through discussion
Create a new "ENTITY_SYSTEM.md" document for this vision
Update ARCHITECTURE.md to include the new system
Reorganize existing docs as proposed above
What aspects would you like to dive into first? The component model structure, the pipeline execution flow, or the attribute generation system?