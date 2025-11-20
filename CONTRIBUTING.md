# Contributing to Combat Engine

Welcome! This guide will help you get set up for development and explain the contribution workflow.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Running Tests](#running-tests)
3. [Code Standards](#code-standards)
4. [Adding New Content](#adding-new-content)
5. [Pull Request Process](#pull-request-process)
6. [Project Structure](#project-structure)

## Development Setup

### Prerequisites

- **Python**: 3.10 or higher
- **Git**: For version control
- **pip**: Python package manager

### Initial Setup

1. **Clone the repository:**

```bash
git clone <repository-url>
cd combat_engine
```

2. **Create a virtual environment:**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Verify installation:**

```bash
# Run the test suite
python -m pytest

# Expected output: All tests passing
```

### Development Tools

The project uses modern Python development tools configured in `pyproject.toml`:

- **pytest**: Testing framework
- **black**: Code formatting (optional, configured but not mandatory)
- **ruff**: Linting (optional)
- **mypy**: Static type checking (optional)

## Running Tests

### Full Test Suite

```bash
# Run all 276 tests
python -m pytest

# With coverage report
python -m pytest --cov=src --cov-report=html

# View coverage in browser
open htmlcov/index.html  # Linux/Mac
start htmlcov\index.html  # Windows
```

### Specific Test Files

```bash
# Run specific test file
python -m pytest tests/test_engine.py

# Run specific test function
python -m pytest tests/test_engine.py::test_basic_hit_calculation

# Run tests matching a pattern
python -m pytest -k "damage"
```

### Test Categories

- **Unit Tests**: `tests/test_*.py` - Test individual components
- **Integration Tests**: `tests/test_integration.py` - End-to-end scenarios
- **Data Tests**: `tests/test_data_parser.py`, `tests/test_cross_reference_validation.py` - Data pipeline validation

### Writing Tests

**All tests must use deterministic RNG:**

```python
from tests.fixtures import make_rng, make_attacker, make_defender

def test_my_feature():
    # Use seeded RNG for reproducibility
    engine = CombatEngine(rng=make_rng(42))
    
    # Use test fixtures for common entities
    attacker = make_attacker(base_damage=100.0)
    defender = make_defender(armor=50.0)
    
    # Test your feature
    result = engine.resolve_hit(attacker, defender, state_manager)
    
    # Make assertions
    assert result.final_damage > 0
```

**Key principles:**
- ✅ Use `make_rng(seed)` for deterministic randomness
- ✅ Use test fixtures from `tests/fixtures.py`
- ✅ Test edge cases (zero damage, max values, etc.)
- ✅ Use descriptive test names
- ❌ Never use `random.random()` directly
- ❌ Never rely on global state between tests

## Code Standards

### Type Hints

**All public functions must have type hints:**

```python
# ✅ Good
def apply_damage(entity_id: str, damage: float) -> float:
    """Apply damage and return actual damage dealt."""
    ...

# ❌ Bad
def apply_damage(entity_id, damage):
    ...
```

### Docstrings

**All public classes and methods must have docstrings:**

```python
def process_skill_use(
    self,
    attacker: Entity,
    defender: Entity,
    skill: Skill,
    event_bus: EventBus,
    state_manager: StateManager
) -> bool:
    """Process a full skill use with resource checks and event dispatching.

    Args:
        attacker: The entity using the skill
        defender: The target of the skill  
        skill: The skill being used
        event_bus: Event bus for dispatching events
        state_manager: State manager for damage/effects/resources

    Returns:
        True if skill was successfully used, False if unable (cooldown/resource issues)
    """
    ...
```

**Docstring style**: Google Style (as shown above)

### RNG Injection

**All random behavior must accept injectable RNG:**

```python
class CombatEngine:
    def __init__(self, rng=None):
        """Initialize with optional RNG for testing."""
        self.rng = rng
    
    def _roll_chance(self) -> float:
        """Roll random number using injected or system RNG."""
        if self.rng:
            return self.rng.random()
        return random.random()
```

**Why?** Enables deterministic testing and reproducible bug reports.

### Code Organization

- **Pure functions**: Separate calculation from execution (see `CombatEngine.calculate_skill_use()`)
- **Dependency injection**: Accept dependencies through constructors (see `CombatOrchestrator`)
- **Single responsibility**: Each class/module has one clear purpose
- **Avoid global state**: No module-level mutable state

## Adding New Content

The engine is data-driven - add new content via CSV files, not code.

### Adding a New Skill

1. **Edit `data/skills.csv`:**

```csv
skill_id,name,hits,resource_cost,cooldown,trigger_event,proc_rate,trigger_result,trigger_duration,stacks_max
my_skill,My Awesome Skill,2,20.0,6.0,OnHit,0.5,Bleed,10.0,5
```

2. **Rebuild data:**

```bash
python scripts/update_game_data.py  # If you have this script
# Or manually: Re-run data parser to regenerate game_data.json
```

3. **Test your skill:**

```python
from src.data.game_data_provider import GameDataProvider

provider = GameDataProvider()
skill_data = provider.get_skills()['my_skill']

# skill_data is now available for use
```

### Adding a New Effect

1. **Edit `data/effects.csv`:**

```csv
effect_id,name,duration,tick_interval,damage_per_tick,stacks_to_add,description
burn,Burn,12.0,2.0,8.0,1,Fire damage over time
```

2. **Reference in skills:**

```csv
fireball,Fireball,1,25.0,8.0,OnHit,0.8,burn,12.0,5
```

3. **Data validation ensures the reference exists!**

### Adding a New Item

1. **Edit `data/items.csv`:**

```csv
item_id,name,slot,rarity,affix_pool,description
fire_sword,Sword of Flames,Weapon,Epic,weapon;fire,Burning blade
```

2. **Generate procedural items:**

```python
from src.utils.item_generator import ItemGenerator

generator = ItemGenerator()
item = generator.generate_item('fire_sword', quality_tier='Epic')
```

### cross-reference Validation

The data pipeline automatically validates:

- Skills → Effects (trigger_result must exist)
- Items → Affixes (affix_pool must contain valid affixes)
- Affixes → Stats (stat_affected must be valid EntityStats field)

**Invalid data will fail on load with helpful error messages.**

## Pull Request Process

### Before Submitting

1. **Run the full test suite:**

```bash
python -m pytest
```

All 276 tests must pass.

2. **Test your changes manually:**

```bash
# Run integration tests
python run_simulation.py  # If applicable
```

3. **Check code quality** (optional but encouraged):

```bash
# Format code
black src/ tests/

# Check types
mypy src/

# Lint
ruff check src/
```

### PR Guidelines

**Commit Messages:**
- Use present tense ("Add feature" not "Added feature")
- Be descriptive but concise
- Reference issues if applicable

**PR Description:**
- Explain what changed and why
- Include test results
- Note any breaking changes
- Link to related issues

**Example PR Description:**

```markdown
## Changes
- Added new "Cleave" skill with AoE mechanics
- Updated skill data pipeline to support multi-target skills
- Added 5 new tests for AoE functionality

## Testing
- All 281 tests passing (5 new tests added)
- Manually tested in simulation: works as expected

## Breaking Changes
None

## Related Issues
Closes #42
```

### Review Process

1. **Automated checks**: Tests must pass
2. **Code review**: Maintainer reviews code quality, adherence to standards
3. **Feedback**: Address any requested changes
4. **Merge**: Once approved, your PR will be merged

## Project Structure

```
combat_engine/
├── src/                    # Source code
│   ├── combat/            # Combat calculation and orchestration
│   ├── core/              # Core models and systems
│   ├── data/              # Data loading and validation
│   ├── handlers/          # Effect and event handlers
│   ├── simulation/        # Batch simulation framework
│   └── utils/             # Utility modules
├── tests/                 # Test suite
├── data/                  # Game content (CSV files)
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
└── pyproject.toml        # Project configuration
```

**Key directories:**

- **`src/combat/`**: Damage calculation, hit resolution, action/result pattern
- **`src/core/`**: Entity models, StateManager, EventBus, Skills
- **`src/data/`**: CSV parsing, GameDataProvider singleton, validation
- **`tests/`**: Comprehensive test suite with fixtures

## Architecture Overview

Before contributing, familiarize yourself with the architecture:

- **[Architecture Overview](docs/architecture.md)**: Core patterns and module structure
- **[Damage Pipeline](docs/damage_pipeline.md)**: 9-step combat calculation
- **[State & Lifecycle](docs/state_and_lifecycle.md)**: StateManager and entity lifecycle
- **[Data Pipeline](docs/data_pipeline.md)**: CSV to runtime flow

## Getting Help

**Questions?**

- Check the [README.md](README.md) for usage examples
- Review the [docs/](docs/) for architectural details
- Look at existing tests in `tests/` for patterns
- Review similar existing features for reference

**Found a bug?**

- Check if it's already reported in Issues
- If not, open a new issue with:
  - Steps to reproduce
  - Expected behavior
  - Actual behavior
  - Test case that demonstrates the issue (if possible)

## Code of Conduct

- Be respectful and professional
- Focus on constructive feedback
- Help others learn and improve
- Follow the established patterns and conventions

---

Thank you for contributing to Combat Engine! 🎮⚔️
