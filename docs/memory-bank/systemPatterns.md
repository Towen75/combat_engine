# System Patterns

## System Architecture

The Combat Engine follows a modular, layered architecture designed for maintainability, testability, and extensibility. The system is built around three core principles: data-driven design, event-driven communication, and clear separation of concerns.

### Core Architecture Layers

```
┌─────────────────┐
│  Simulation     │ ← Testing & Balancing Tools
│  Framework      │
└─────────────────┘
        │
┌─────────────────┐
│  Game Systems   │ ← Skills, Items, Progression
│  Layer          │
└─────────────────┘
        │
┌─────────────────┐
│  Combat Logic   │ ← Damage, Events, Effects
│  Layer          │
└─────────────────┘
        │
┌─────────────────┐
│  Data Models    │ ← Entities, Stats, Configuration
│  Layer          │
└─────────────────┘
```

## Key Technical Decisions

### Data-Driven Design
- **Decision**: All game content (characters, items, skills, affixes) defined in external data files (JSON/Godot resources)
- **Rationale**: Enables rapid iteration, balancing, and content creation without code changes
- **Implementation**: DataModels module provides base classes and validation for all game objects

### Event-Driven Communication
- **Decision**: EventBus as central dispatcher for all combat events (OnHit, OnCrit, OnKill, etc.)
- **Rationale**: Decouples effect systems from core combat logic, allowing modular feature development
- **Implementation**: Publisher-subscriber pattern with typed event objects containing context data

### Engine Agnostic Core
- **Decision**: Core combat logic developed independently of game engine specifics
- **Rationale**: Enables prototyping, testing, and potential multi-platform deployment
- **Implementation**: Python prototype with clear interfaces for Godot integration

## Design Patterns in Use

### ACTION/RESULT PATTERN (PR1 - Production Architecture)
- **Context**: Combat calculations and execution need complete separation for testing and Godot compatibility
- **Implementation**: SkillUseResult + Action hierarchy (ApplyDamageAction, DispatchEventAction, ApplyEffectAction)
- **Benefits**: Zero side effects in calculation, decoupled execution via CombatOrchestrator
- **Godot Fit**: Direct mapping to Godot's signal/event system

### CENTRALIZED TICK PATTERN (PR4 - Time-Based Processing)
- **Context**: Time-based effects (DoTs, cooldowns, modifiers) need unified processing for consistency
- **Implementation**: StateManager.tick() method as single entry point for all time-based updates
- **Benefits**: Predictable timing, event-driven effects, performance optimization through batching
- **Integration**: Seamless event dispatching with DamageTickEvent for effect notifications

### PUBLISHER-SUBSCRIBER ENHANCED PATTERN (PR3 - Event Bus Robustness)
- **Context**: Event system needs robustness for production use with error handling and performance
- **Implementation**: EventBus.unsubscribe(), exception isolation, safe iteration, logging infrastructure
- **Benefits**: System stability, debugging capabilities, listener management, priority support preparation
- **Performance**: Async-safe dispatching prevents modification issues during event processing

### TEMPLATE METHOD + CONFIGURATION PATTERN (PR2 - Generic Effect Framework)
- **Context**: DoT effects share common mechanics but need data-driven variation
- **Implementation**: DamageOnHitHandler template with DamageOnHitConfig for effect parameters
- **Benefits**: No code changes for new effects, centralized validation, consistent behavior
- **Extensibility**: JSON-only additions for new effect types (Burn, Freeze, etc.)

### SINGLETON PATTERN (Code Review Implementation - GameDataProvider)
- **Context**: Centralized data access for all JSON game data across the application
- **Implementation**: GameDataProvider singleton with error resilience and reload capabilities
- **Benefits**: Efficient memory usage, consistent data access, graceful failure handling
- **Methods**: get_affixes(), get_items(), get_quality_tiers() for specific sections

### TEMPLATE METHOD PATTERN (Code Review Implementation - Generic Effect Framework)
- **Context**: All DoT effects share common application logic but have different configurations
- **Implementation**: DamageOnHitHandler provides template, DamageOnHitConfig provides data variation
- **Benefits**: Zero code changes needed for new effects, comprehensive validation and error handling

### DEPENDENCY INJECTION PATTERN (Code Review Implementation - Orchestrator Architecture)
- **Context**: Combat execution depends on external services (StateManager, EventBus) for testability
- **Implementation**: CombatOrchestrator constructor injects all dependencies
- **Benefits**: Complete test isolation, Godot scene node integration support

### OBSERVER PATTERN (Original Implementation - Event System)
- **Context**: Combat events need to trigger multiple independent systems
- **Implementation**: EventBus manages subscriptions, EffectHandlers listen for relevant events
- **Benefits**: Loose coupling between damage calculation and effect application
- **Enhanced**: Now integrates seamlessly with new Action/Result pattern

### COMPONENT PATTERN (Original Implementation - Entity Composition)
- **Context**: Characters and items have variable combinations of stats and effects
- **Implementation**: Entity base class with modular stat components and equipment slots
- **Benefits**: Flexible character/item building without inheritance hierarchies
- **Enhanced**: Added stat validation to prevent invalid affix configurations

### STATE PATTERN (Original Implementation - Entity States)
- **Context**: Entities have different states (healthy, stunned, buffed) affecting behavior
- **Implementation**: StateManager tracks current stats, active effects, and state transitions
- **Benefits**: Clean handling of temporary modifications and effect stacking

### FACTORY PATTERN (Enhanced - Object Creation with Validation)
- **Context**: Complex object creation with validation and initialization
- **Implementation**: ItemGenerator refactored to use GameDataProvider, all creation includes comprehensive validation
- **Benefits**: Centralized object creation logic and error handling, data integrity guaranteed

### STRATEGY PATTERN (Original Implementation - Damage Calculation)
- **Context**: Different damage calculation strategies based on crit tiers and effect types
- **Implementation**: CombatEngine uses strategy objects for different calculation paths
- **Benefits**: Extensible damage formulas without modifying core logic
- **Enhanced**: Now pure functions within Action/Result architecture

## Component Relationships

### Core Components
- **DataModels**: Defines structure for all game objects
- **CombatEngine**: Pure functions for damage calculations
- **StateManager**: Manages entity state mutations
- **EventBus**: Central event dispatcher
- **EffectHandlers**: Subscribed listeners for specific events
- **SimulationFramework**: Testing and analysis tools

### Critical Implementation Paths

#### Damage Resolution Path
```
Skill Activation → CombatEngine.ResolveHit() → EventBus.Dispatch(OnHit) → EffectHandlers → StateManager.Update()
```

#### Character Progression Path
```
Combat Results → Experience Calculation → Level Up Check → Reward Selection → Stat Updates → Skill Unlocks
```

#### Itemization Path
```
Item Generation → Affix Selection → Stat Calculation → Equipment Application → Entity Updates
```

## Data Flow Patterns

### Combat Turn Flow
1. **Input**: Player selects skill and target
2. **Validation**: Check resource costs and cooldowns
3. **Calculation**: CombatEngine processes hits with full formula
4. **Events**: EventBus dispatches relevant events
5. **Effects**: Handlers apply secondary effects
6. **Updates**: StateManager updates all affected entities
7. **Feedback**: UI updates with results

### Progression Flow
1. **Trigger**: Combat completion or milestone reached
2. **Calculation**: Experience and reward determination
3. **Choice**: Player selects from reward options
4. **Application**: Stats, items, or unlocks applied
5. **Persistence**: Changes saved to character data

## Error Handling Patterns

### Validation Layer
- **Input Validation**: All external data validated on load
- **Runtime Checks**: Combat calculations include bounds checking
- **Graceful Degradation**: Invalid states handled without crashes

### Logging and Debugging
- **Combat Logger**: Records all combat events for analysis
- **Simulation Reports**: Detailed performance metrics
- **Error Recovery**: State rollback on critical failures

## Performance Considerations

### Computational Efficiency
- **Damage Calculations**: Optimized math operations, cached stat lookups
- **Event System**: Efficient subscription management, batched updates
- **Memory Management**: Object pooling for frequent combat objects

### Scalability Patterns
- **Modular Loading**: Systems load independently
- **Data Chunking**: Large datasets loaded on demand
- **Caching Strategy**: Frequently accessed data cached in memory

## Testing Patterns

### Unit Testing
- **Pure Functions**: CombatEngine methods tested in isolation
- **Mock Objects**: External dependencies mocked for component testing
- **Data Validation**: All data models tested for correctness

### Integration Testing
- **Simulation Runs**: Full combat scenarios tested automatically
- **Balance Verification**: Statistical analysis of simulation results
- **Regression Testing**: Changes validated against baseline metrics
