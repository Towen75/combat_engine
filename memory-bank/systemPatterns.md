# System Patterns: Combat Engine Architecture

## Core Architecture Overview

The Combat Engine follows a modular, event-driven architecture with clear separation of concerns and deterministic behavior for testing and simulation.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Game Data     │───▶│   State         │◀──▶│   Engine        │
│   (External)    │    │   Management    │    │   (Combat)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       ▲                       │
         ▼                       │                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Event Bus     │◀──▶│   Effect        │◀──▶│   Combat        │
│   (Decoupling)  │    │   Handlers      │    │   Resolution    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Key Design Patterns

### 1. Data-Driven Architecture Pattern
- **Pattern**: All game content defined externally in structured data files
- **Implementation**: CSV for tabular data, JSON for complex relationships
- **Benefits**: Easy content iteration, no code changes for balance tweaks
- **Critical Path**: `src/data/schemas.py` enforces structure, `src/game_data_provider.py` loads and validates

### 2. Event-Driven Observer Pattern
- **Pattern**: Loose coupling through publish-subscribe event system
- **Implementation**: `EventBus` class with event types and handler registration
- **Benefits**: Effects can interact without direct dependencies, easy testing
- **Critical Path**: Events like `OnHit`, `OnDamage`, `OnTick` drive DoTs and skill triggers

### 3. State Manager Pattern
- **Pattern**: Centralized state tracking with controlled mutations
- **Implementation**: `StateManager` class tracks entity health, active effects
- **Benefits**: Predictable state changes, easy rollback for testing
- **Critical Path**: Prevents race conditions in multi-effect scenarios

### 4. RNG Injection Pattern
- **Pattern**: Deterministic random number generation with external control
- **Implementation**: All random calls use injected `rng` parameter, defaults to `random.random`
- **Benefits**: Perfect test reproducibility, seeded simulations
- **Critical Path**: Every `random()` call must be injected, no global `random.seed()`

### 5. Hit Resolution Pipeline Pattern
- **Pattern**: Modular damage calculation through chained computations
- **Implementation**: `CombatEngine.resolve_hit()` orchestrates stat gathering, formula application, effect application
- **Benefits**: Clear separation of calculation phases, easy debugging
- **Critical Path**: Pierce formula, crit calculation, defensive calculations in sequence

## Component Relationships

### Core Combat Flow
```
Entity Stats ──▶ Combat Math ──▶ Hit Context ──▶ Effect Application
     │                │                │                │
     ▼                ▼                ▼                ▼
Entity Base ──▶ Damage Formula ─▶ Crit Scaling ──▶ State Updates
```

### Data Pipeline
```
Raw CSV ──▶ Data Parser ──▶ Typed Models ──▶ Validation ──▶ Game Data Provider
     │           │              │              │              │
     ▼           ▼              ▼              ▼              ▼
Effects ──▶ Schema ──▶ Pydantic ──▶ Cross-Ref ──▶ Runtime Access
```

## Critical Implementation Paths

### 1. Combat Resolution Path
**Purpose**: Calculate final damage from attacker to defender with all modifiers
```
resolve_hit(attacker, defender, state_manager)
├── gather_combat_stats()           # Combine entity + equipment stats
├── calculate_raw_damage()          # Base damage + pierce formula
├── apply_critical_hit()           # Rarity-based crit scaling
├── apply_defensive_calcs()        # Armor reduction + thresholds
├── create_hit_context()           # Bundle results for effects
└── apply_effects()                # Event-driven effect application
```

### 2. Effect Processing Path
**Purpose**: Handle DoTs, buffs, and triggered abilities
```
process_effect_application(hit_context, event_bus)
├── dispatch_hit_events()           # OnHit, OnDamage, etc.
├── evaluate_triggers()            # Check proc conditions
├── calculate_effect_strength()    # Stack scaling, duration
├── update_entity_state()          # Apply to StateManager
└── schedule_cleanup()             # Tick timers, removal
```

### 3. Skill Execution Path
**Purpose**: Multi-hit skills with complex trigger conditions
```
process_skill_use(attacker, defender, skill)
├── validate_skill_requirements()   # Cooldowns, resources
├── execute_hit_sequence()         # Multiple resolve_hit() calls
├── aggregate_damage()             # Total damage tracking
├── apply_skill_effects()          # Unique skill abilities
└── update_cooldowns()             # Prevent spam usage
```

### 4. Data Loading Path
**Purpose**: Load and validate all game content at startup
```
initialize_game_data()
├── load_csv_files()               # pandas/csv parsing
├── validate_structure()           # Schema enforcement
├── cross_reference_check()        # ID integrity validation
├── build_derived_data()           # Computed relationships
└── cache_for_runtime()            # Fast lookup structures
```

## Key Technical Decisions

### Damage Formula Choice
**Decision**: `MAX((Attack - Defense), (Attack × Pierce))` over linear reduction
**Rationale**: Allows weapons to "punch through" defense without ignoring investment
**Trade-offs**: More complex than simple subtraction, but richer gameplay
**Implementation**: `src/combat_math.py::calculate_damage()`

### Event Bus vs Direct Calls
**Decision**: Observer pattern over method chaining for effects
**Rationale**: Enables buffs/debuffs to interact without tight coupling
**Trade-offs**: Indirect control flow harder to debug, but flexible composition
**Implementation**: `src/events.py::EventBus`

### Pydantic vs Plain Classes
**Decision**: Runtime type validation over simple dataclasses
**Rationale**: Catches data errors early, provides clear error messages
**Trade-offs**: Slight performance cost, but critical for data integrity
**Implementation**: `src/data/typed_models.py`

### Simulation vs Real-time Balance
**Decision**: Support both deterministic testing and live randomization
**Rationale**: Balance requires reproducible testing, gameplay needs unpredictability
**Trade-offs**: Dual code paths increase complexity, but necessary for quality
**Implementation**: RNG injection pattern throughout codebase

## Critical Failure Points

### RNG Non-Determinism
**Risk**: Hard-to-reproduce bugs caused by unseeded random calls
**Mitigation**: Static analysis to find bare `random()` calls, injected RNG requirement
**Detection**: Test failures that don't reproduce locally

### State Mutation Race Conditions
**Risk**: Multiple effects modifying entity state simultaneously
**Mitigation**: All state changes through StateManager, event ordering preserved
**Detection**: Integration tests with complex multi-effect scenarios

### Data Reference Invalidity
**Risk**: Skills referencing non-existent effects, items using invalid stats
**Mitigation**: Schema validation + cross-reference checking at load time
**Detection**: Data loading failures with detailed error messages

### Performance Degradation
**Risk**: Event system overhead in high-frequency combat scenarios
**Mitigation**: Event batching, efficient lookups, profiling-driven optimization
**Detection**: Performance benchmarks in simulation runs
