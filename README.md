# Combat Engine

A modular combat system for dungeon crawler RPGs, featuring sophisticated damage calculations, character progression, and itemization systems.

## Overview

The Combat Engine implements a complete RPG combat system with:
- **Pierce-based damage calculation**: `MAX((Attack Damage - Defense), (Attack Damage × Pierce Ratio))`
- **Multi-tier critical hits**: Rarity-based crit scaling (Common→Mythic)
- **Event-driven effects**: DoTs, buffs, and complex skill interactions
- **Dynamic itemization**: Thematic affix pools with equipment mechanics
- **Time-based simulation**: DoT ticks, duration management, and temporal effects

## Architecture

### Core Components
- **`src/engine.py`**: CombatEngine with damage calculation and hit resolution
- **`src/models.py`**: Entity, EntityStats, Affix, Item data models
- **`src/state.py`**: StateManager for entity state tracking
- **`src/events.py`**: EventBus for decoupled effect triggering
- **`src/effect_handlers.py`**: DoT and effect application logic
- **`src/skills.py`**: Multi-hit skills with configurable triggers

### Design Principles
- **Data-driven**: All game content defined in external data structures
- **Event-driven**: Loose coupling through observer pattern
- **Deterministic**: Reproducible results for testing and balance
- **Modular**: Independent systems for easy maintenance and extension

## Testing & Determinism

### RNG Policy
**All combat RNG must be deterministic in tests and injectable in production. No global seeding permitted.**

This ensures:
- **Reproducible tests**: Same inputs always produce same outputs
- **Balance validation**: Simulation results are consistent and verifiable
- **Debugging**: Issues can be reproduced with specific RNG states
- **Production safety**: No hidden randomness affecting game state

### Testing Conventions

#### RNG Injection
```python
from tests.fixtures import make_rng

# For deterministic tests
engine = CombatEngine(rng=make_rng(42))
handler = BleedHandler(event_bus, state_manager, rng=make_rng(123))

# For production (uses random.random() internally)
engine = CombatEngine()  # rng=None uses system random
```

#### Test Fixtures
Common test entities are available through fixtures:
```python
from tests.fixtures import make_attacker, make_defender, make_rng

attacker = make_attacker(base_damage=100.0, crit_chance=0.25)
defender = make_defender(armor=50.0, max_health=1000.0)
```

#### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_engine.py

# Run integration tests
python run_phase1_test.py  # Basic combat
python run_phase2_test.py  # Crits & events
python run_phase3_test.py  # Items & skills
```

## Installation & Setup

### Requirements
```bash
pip install -r requirements.txt
```

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd combat_engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest
```

## Usage Examples

### Basic Combat
```python
from src.engine import CombatEngine
from src.models import Entity, EntityStats

# Create entities
attacker_stats = EntityStats(base_damage=100.0, pierce_ratio=0.2)
attacker = Entity(id="hero", base_stats=attacker_stats)

defender_stats = EntityStats(armor=50.0, max_health=1000.0)
defender = Entity(id="monster", base_stats=defender_stats)

# Resolve hit
engine = CombatEngine()
hit_context = engine.resolve_hit(attacker, defender, state_manager)

print(f"Damage dealt: {hit_context.final_damage}")
print(f"Was critical: {hit_context.is_crit}")
```

### Skills with Effects
```python
from src.skills import Skill, Trigger
from src.events import EventBus
from src.state import StateManager
from src.effect_handlers import BleedHandler

# Set up systems
event_bus = EventBus()
state_manager = StateManager()
bleed_handler = BleedHandler(event_bus, state_manager)

# Create multi-hit skill
skill = Skill(
    id="whirlwind",
    name="Whirlwind Strike",
    hits=3,
    triggers=[{
        "event": "OnHit",
        "check": {"proc_rate": 0.5},
        "result": {"apply_debuff": "Bleed", "stacks": 1}
    }]
)

# Execute skill
engine.process_skill_use(attacker, defender, skill, event_bus, state_manager)
```

## Development Status

### Completed Phases ✅
- **Phase 1**: Core combat foundation (damage formulas, entity management)
- **Phase 2**: Enhanced combat (crits, events, DoTs)
- **Phase 3**: Game systems (items, skills, equipment)
- **Phase 4**: Simulation & balancing (time-based effects, comprehensive testing)

### Current Status
- **Python Prototype**: Complete and fully tested (96 unit tests)
- **Godot Port**: Ready for implementation
- **Test Coverage**: >95% on critical systems
- **Performance**: 6993 events/second in simulation

### Next Steps
- Port core systems to GDScript
- Implement UI and visual feedback
- Add content creation tools
- Performance optimization for target platforms

## API Reference

### CombatEngine
- `resolve_hit(attacker, defender, state_manager)`: Calculate single hit damage
- `calculate_effective_damage(attacker, defender)`: Get detailed breakdown
- `validate_damage_calculation(attacker, defender)`: Check calculation validity
- `process_skill_use(attacker, defender, skill, event_bus, state_manager)`: Execute skill

### Key Classes
- `Entity`: Combat participant with stats and equipment
- `EntityStats`: Base stats (damage, armor, crit chance, etc.)
- `Skill`: Multi-hit ability with triggers
- `StateManager`: Tracks entity health and active effects
- `EventBus`: Decoupled event dispatching system

## Contributing

### Code Standards
- Type hints required for all public functions
- Comprehensive docstrings
- Unit tests for all new functionality
- RNG injection for any random behavior

### Testing Requirements
- All tests must pass with `python -m pytest`
- New features require corresponding tests
- Deterministic RNG usage in tests
- Integration tests for complex interactions

### Documentation
- Update memory bank for significant changes
- Keep API examples current
- Document any new RNG usage patterns

## License

[License information here]

## Contact

[Contact information here]
