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

### Observer Pattern (Event System)
- **Context**: Combat events need to trigger multiple independent systems
- **Implementation**: EventBus manages subscriptions, EffectHandlers listen for relevant events
- **Benefits**: Loose coupling between damage calculation and effect application

### Component Pattern (Entity Composition)
- **Context**: Characters and items have variable combinations of stats and effects
- **Implementation**: Entity base class with modular stat components and equipment slots
- **Benefits**: Flexible character/item building without inheritance hierarchies

### State Pattern (Entity States)
- **Context**: Entities have different states (healthy, stunned, buffed) affecting behavior
- **Implementation**: StateManager tracks current stats, active effects, and state transitions
- **Benefits**: Clean handling of temporary modifications and effect stacking

### Factory Pattern (Object Creation)
- **Context**: Complex object creation with validation and initialization
- **Implementation**: Factories for characters, items, and skills with data validation
- **Benefits**: Centralized object creation logic and error handling

### Strategy Pattern (Damage Calculation)
- **Context**: Different damage calculation strategies based on crit tiers and effect types
- **Implementation**: CombatEngine uses strategy objects for different calculation paths
- **Benefits**: Extensible damage formulas without modifying core logic

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
