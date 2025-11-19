# Technical Context: Combat Engine

## Technology Stack

### Core Runtime Environment
- **Language**: Python 3.8+ (type hints, dataclasses, modern syntax)
- **Package Manager**: pip with `requirements.txt`
- **Virtual Environment**: venv (Windows: `venv\Scripts\activate`)
- **Platform Support**: Cross-platform (Windows/macOS/Linux via Godot target)

### Testing & Validation
- **Test Framework**: pytest with coverage reporting (`--cov=src --cov-report=html`)
- **Deterministic RNG**: Custom fixtures for seeded random number generation
- **CI/CD**: Designed for integration with GitHub Actions or similar
- **Performance Benchmarking**: Simulation-based testing with 6993 events/sec target

### Data Processing
- **Tabular Data**: pandas for CSV parsing and manipulation
- **Schema Validation**: Pydantic V2 for runtime type checking and model validation
- **Configuration**: JSON for complex relationships, CSV for bulk data
- **Data Integrity**: Custom validation layers for cross-reference checking

### Development Tools
- **Code Quality**: black (formatting), ruff (linting), mypy (static type checking)
- **IDE**: Visual Studio Code with Python extensions
- **Version Control**: Git with conventional commit message standards
- **Documentation**: Markdown-based docs with Mermaid diagrams

## Development Setup Requirements

### System Prerequisites
```bash
# Python 3.8 or higher
python --version  # Must be 3.8+

# Git for version control
git --version

# Virtual environment support (usually included)
python -m venv --help
```

### Dependency Installation
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Core Dependencies Breakdown
```
pandas>=1.3.0         # CSV processing, data manipulation
pydantic>=2.0.0       # Runtime validation, type enforcement
pytest>=7.0.0         # Test framework with fixtures
pytest-cov>=4.0.0     # Coverage reporting
mypy>=1.0.0           # Static type checking
black>=22.0.0         # Code formatting
ruff>=0.1.0           # Fast linting
```

## Technical Constraints

### Performance Requirements
- **Simulation Speed**: 6993 events/second minimum for balance validation
- **Memory Usage**: Must support thousands of entity simulations simultaneously
- **Startup Time**: Data loading and validation under 5 seconds for development iteration
- **Real-time Combat**: Support 60+ combat calculations per second for live gameplay

### Determinism Requirements
- **Test Reproducibility**: Same inputs always produce identical outputs
- **No Global State**: RNG must be injected, no global random seeding
- **Order Independence**: Event processing order must not affect final results
- **Seed Management**: Support for replayable combat scenarios

### Data Integrity Constraints
- **Schema Enforcement**: All data structures validated at load time
- **Cross-Reference Validation**: IDs must resolve to valid objects
- **Type Safety**: Runtime type checking prevents invalid data combinations
- **Backward Compatibility**: New versions must support existing data formats

### Code Quality Standards
- **Type Hints**: Required on all public functions and complex logic
- **Documentation**: Comprehensive docstrings with examples
- **Test Coverage**: >95% on critical systems, full integration coverage
- **Linting Compliance**: Zero ruff/black violations in CI

## Development Workflow Patterns

### Testing Patterns
```python
# Deterministic unit test
def test_damage_calculation(make_rng):
    engine = CombatEngine(rng=make_rng(42))
    result = engine.calculate_damage(attacker, defender)
    assert result == expected_value  # Always reproducible

# Integration test with fixtures
def test_full_combat_flow(make_attacker, make_defender, make_rng):
    # Set up full combat scenario
    # Verify end-to-end behavior
```

### Data Loading Pattern
```python
# Always validate data at load time
def load_game_data():
    data = GameDataLoader.load_from_files()
    validator = DataValidator()
    validator.validate_structure(data)
    validator.check_cross_references(data)
    return data
```

### RNG Usage Pattern
```python
# Never use global random
def roll_critical_hit(crit_chance: float, rng: Callable[[], float]) -> bool:
    return rng() < crit_chance

# Allow default for production
def __init__(self, rng: Optional[Callable[[], float]] = None):
    self.rng = rng or random.random
```

### State Management Pattern
```python
# Centralized state mutations
def apply_damage(entity_id: str, damage: float, state_manager: StateManager):
    current_health = state_manager.get_health(entity_id)
    new_health = max(0, current_health - damage)
    state_manager.update_health(entity_id, new_health)
    # All state changes go through manager
```

## Key Tool Usage Patterns

### pytest Testing Patterns
- **Unit Tests**: Focused on individual functions, heavy use of fixtures
- **Integration Tests**: Full system behavior, deterministic RNG throughout
- **Performance Tests**: Time budgeted assertions, simulation batch testing
- **Data Tests**: CSV/JSON validation, cross-reference integrity

### pandas Data Processing Patterns
- **CSV Loading**: `pd.read_csv()` with dtype specification for memory efficiency
- **Data Validation**: Custom validation functions applied to DataFrames
- **Lookup Tables**: Dictionary-based caching for runtime performance
- **Data Transformation**: Vectorized operations where possible

### Pydantic Model Patterns
- **Validation Models**: Strict typing with custom validators where needed
- **Serialization**: JSON-compatible models for configuration files
- **Error Messages**: Descriptive validation errors for debugging
- **Nested Models**: Complex relationships represented hierarchically

### Event System Patterns
- **Event Registration**: Handlers register interest in specific event types
- **Event Dispatch**: Batch processing to prevent re-entrancy issues
- **Handler Isolation**: Each handler receives immutable event data
- **Cleanup**: Event listener removal when objects are destroyed

## Known Technical Challenges

### Current Workarounds
- **Pydantic Performance**: Large data files may require streaming validation
- **Event Overhead**: High-frequency events batched to reduce function call overhead
- **Memory Usage**: Data structures optimized for simulation workloads

### Future Considerations
- **Godot Port**: GDScript translation maintaining same architecture patterns
- **Multi-threaded Simulation**: Parallel combat simulation for faster balancing
- **Network Play**: Deterministic combat for multiplayer synchronization
- **Save/Load**: Serializable state for persistent game sessions

### Performance Optimizations Applied
- **Data Caching**: Pre-computed lookup tables for runtime speed
- **Lazy Evaluation**: Expensive calculations deferred until needed
- **Batch Processing**: Group similar operations for vectorization
- **Memory Pooling**: Reuse allocated objects in simulation loops

## Integration Points

### Data Pipeline Integration
- External CSV/JSON files loaded through `game_data_provider.py`
- Validation occurs at application startup
- Runtime data access through typed interfaces

### Engine Integration
- Combat calculations accessible through `CombatEngine` API
- Event system integration through `EventBus` interfaces
- State management through `StateManager` for persistence

### Testing Integration
- Test fixtures provide consistent data for all test scenarios
- RNG injection enables deterministic behavior in CI/CD
- Coverage reporting integrated with development workflow
