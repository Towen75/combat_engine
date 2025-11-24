# # [2.11.0](https://github.com/Towen75/combat_engine/compare/v2.10.0...v2.11.0) (2025-11-24)


### Bug Fixes

* correct changelog links and format v2.10.0 release ([35d31e0](https://github.com/Towen75/combat_engine/commit/35d31e0a2775f461324bdbce80ce764dfaf0ff2b))



# [2.10.0](https://github.com/Towen75/combat_engine/compare/v2.9.0...v2.10.0) (2025-11-23)

### Added
- **Major Architectural Refactoring**: GameDataProvider converted from singleton to explicit dependency injection
  - **Explicit Data Ownership**: Removed singleton pattern, requires explicit instantiation at application boundaries
  - **Clean Data Dependencies**: Constructor injection pattern establishes clear data ownership and boundaries
  - **Path Resolution**: Robust cross-platform path handling with environment variable fallback
  - **Type Safety Maintained**: Full type annotation preservation with enhanced error handling

### Technical Details
- **Dependency Injection**: GameDataProvider now requires explicit instantiation with optional data directory parameter
- **Cross-Platform Paths**: pathlib.Path usage with COMBAT_ENGINE_DATA_DIR environment variable support
- **File Existence Validation**: Pre-load validation ensures data directory exists before initialization
- **Backward Compatibility**: ItemGenerator maintains emergency fallback to auto-create provider when needed
- **Code Hygiene**: Removed deprecated convenience functions that exposed singleton usage pattern

### Breaking Changes
- **GameDataProvider API**: No longer a singleton - consumers must instantiate explicitly at application startup
- **Data Ownership**: Applications now explicitly declare and manage their data requirements through constructor injection

# [2.9.0](https://github.com/Towen75/combat_engine/compare/v2.8.0...v2.9.0) (2025-11-19)

### Added
- **RNG Rollout Completion**: Implemented tiered critical hits with rarity-based scaling
  - **Tiered Critical System**: Different crit damage multipliers by rarity (Normal 1.5x, Magic 1.5x/2x, Mythic 1.5x/2x/3x)
  - **Deterministic Combat**: Full RNG integration enabling perfectly reproducible combat simulations
  - **Status Proc System**: DoT ticks, on-damage triggers, and status effect probabilities all using injected RNG
  - **Multi-Hit Support**: Complex skills with proper RNG propagation for all damage instances
  - **Weighted Random Selection**: Helper functions for deterministic weighted choices in item generation

### Technical Details
- **Central RNG Architecture**: Single RNG instance injected through component constructors
- **Tiered Probability System**: Probability arrays define crit multiplier selection per rarity
- **Event-Driven Effects**: Full integration with existing effect and skill trigger systems
- **Deterministic Testing**: Seeded RNG enables reproducible testing for all probabilistic features
- **Performance**: Zero overhead RNG propagation with sub-millisecond execution times

### Breaking Changes
- **RNG Policy Enforcement**: All random calls must use injected RNG instance, no global seeding
- **Critical Hit Mechanics**: Crit damage calculation now uses tiered probabilities instead of fixed multipliers

# [2.8.0](https://github.com/Towen75/combat_engine/compare/v2.7.0...v2.8.0) (2025-11-19)

### Added
- **Central Deterministic RNG**: Complete rewrite of random number generation system
  - **Single RNG Wrapper**: Unified RNG class replacing all Python random calls with deterministic instances
  - **Roll Helpers**: Convenience methods (roll(), roll_tiered(), weighted_choice()) for common probabilistic operations
  - **Explicit Injection**: Constructor-based RNG injection throughout combat system components
  - **Seeded Determinism**: Configurable seeding for reproducible simulations and testing

### Technical Details
- **RNG Injection Pattern**: All components accepted RNG parameter, defaulting to random.random() for production
- **No Global State**: Eliminated dependency on Python's global random module for testing capabilities
- **Backward Compatibility**: Default parameters maintain production unpredictability while enabling testing
- **Architecture**: Clean separation between deterministic testing and live gameplay randomness



# [2.7.0](https://github.com/Towen75/combat_engine/compare/v2.6.0...v2.7.0) (2025-11-21)

### Added
- **Interactive Combat Dashboard**: Complete Streamlit web application for combat simulation and analysis
  - **Dashboard Structure**: Modular page-based navigation (Forge, Arena, Coliseum)
  - **Entity Management**: Drag-and-drop entity configuration with real-time stat feedback
  - **Combat Visualization**: Live battle logs, DPS tracking, and performance metrics
  - **Forge System**: Equipment generation with quality tiers and affix selection
  - **Simulation Engine**: Real-time combat simulation with detailed result analysis
- **DPS Tracking**: Enhanced simulation batch runner with damage-per-second calculations
- **Dashboard Components**: Reusable Streamlit components for entities, items, and battle logs

### Technical Details
- **Dashboard Architecture**: Multi-page Streamlit app with component-based design
- **Data Integration**: Full integration with existing combat engine and data providers
- **Performance Monitoring**: Added DPS calculations to simulation aggregators
- **Test Coverage**: Added dashboard import verification tests

# [2.6.0](https://github.com/Towen75/combat_engine/compare/v2.5.0...v2.6.0) (2025-11-20)

### Added
- **PR-P3S8 Complete**: Final Documentation and Project Polish
  - **Architectural Documentation**: Comprehensive guides for all major systems
    - `docs/architecture.md`: Complete architectural overview with package structure and patterns
    - `docs/damage_pipeline.md`: Detailed 9-step combat calculation walkthrough with examples
    - `docs/state_and_lifecycle.md`: StateManager and entity lifecycle documentation
    - `docs/data_pipeline.md`: CSV to runtime data flow and validation pipeline
  - **Contributor Guide**: Professional `CONTRIBUTING.md` with development setup and standards
  - **Enhanced README**: Updated with links to architectural docs and improved structure

### Technical Details
- **Documentation Completeness**: All major systems now have comprehensive architectural guides
- **Code-Level Docs**: Verified existing docstring coverage across all modules
- **Developer Experience**: CONTRIBUTING.md enables independent developer onboarding
- **Knowledge Transfer**: Complete architectural knowledge documented for future maintainers

# [2.5.0](https://github.com/Towen75/combat_engine/compare/v2.4.0...v2.5.0) (2025-11-19)

### Added
- **Major Code Restructuring**: Consolidation of batch simulation functionality into unified simulation package
  - **Package Consolidation**: Merged `batch_simulation` module into `simulation/` package for better organization
  - **Improved Architecture**: Streamlined imports and eliminated package naming conflicts
  - **Maintained Functionality**: All batch processing, aggregation, telemetry, and export capabilities preserved

### Technical Details
- **Code Organization**: Unified simulation API with cleaner package structure
- **Backward Compatibility**: All existing simulation and batch runner functionality maintained
- **Testing Integrity**: 276 tests passing with complete functional coverage
- **Performance**: Maintained high-throughput simulation capabilities (6993 events/sec)

### Breaking Changes
- **Package Structure**: `src/batch_simulation/` module consolidated into `src/simulation/`
- **Import Paths**: Updated imports to reflect new module organization



# [2.3.0](https://github.com/Towen75/combat_engine/compare/v2.2.2...v2.3.0) (2025-11-19)

### Added
- **PR-P2S5 Complete**: Simulation Batching API and Telemetry Expansion
  - **SimulationBatchRunner**: High-volume deterministic combat testing with RNG injection
  - **Statistical Aggregators**: DPS and win rate analysis with mean/median/stdev calculations
  - **Telemetry Modes**: Developer (DEBUG), Designer (INFO), and Player (narrative) logging modes
  - **Data Exporters**: JSON and CSV export for analysis and spreadsheet balancing
  - **HitContext Expansion**: Added `simulation_id` and `batch_id` fields for batch tracking

### Technical Details
- **Determinism**: Bit-identical results across repeated runs with same seed (base_seed + iteration)
- **RNG Injection**: Proper RNG propagation to CombatEngine and ItemGenerator
- **Cleanup**: Mandatory StateManager.reset_system() prevents state leakage between simulations
- **Test Coverage**: 33 comprehensive tests covering determinism, aggregation, telemetry, and export
- **Performance**: Sub-second batch execution for 100+ simulations

### Breaking Changes
- **Package Structure**: New `batch_simulation` package to avoid naming conflicts
- **HitContext**: Added optional `simulation_id` and `batch_id` fields (backward compatible)


# [2.2.0](https://github.com/Towen75/combat_engine/compare/v2.1.0...v2.2.0) (2025-11-18)

### Added
- **PR-P1S3 Complete**: Data Pipeline Hardening with Strict Typing and Cross-Reference Validation
  - **Typed Data Models**: Complete enum definitions and TypedDict models for all game data structures
  - **Cross-Reference Validation**: Runtime validation ensures skills reference existing effects, items reference valid affixes
  - **Static Type Checking**: mypy integration ensures compile-time type safety for data layer
  - **Triple Validation Layer**: Schema enforcement + cross-reference checks + type safety validation
  - **Enhanced EntityStats**: Added `life_steal`, `damage_multiplier`, and `movement_speed` for comprehensive stat support
  - **Production-Ready Data Provider**: GameDataProvider with singleton pattern and comprehensive error resilience

### Technical Details
- **Data Integrity**: 69 items, 63 affixes, 35 effects, 28 skills all validated at load time
- **Type Safety**: Full mypy coverage on data access layer with strict error checking
- **Performance**: Sub-millisecond data loading and validation with hot-reload capability
- **Architecture**: Progressive validation (parse → validate → hydrate → cross-reference) catches errors at appropriate stages
- **Testing**: Comprehensive validation tests ensure data integrity in all scenarios

### Breaking Changes
- **Data Model Enhancement**: Enhanced EntityStats requires stat validation on existing equippable items
- **Type Requirements**: Data access layer now requires full type annotations and validation

## [2.2.1] - 2025-11-19

### Fixed
- **Data Corrections**: Fixed multiple typos in CSV data files (e.g., "Posion" → "Poison", "daamge" → "damage")
- **Test Suite Stability**: Corrected test property names (`is_crit` → `was_crit`), added missing StateManager entity registrations
- **Engine Code Quality**: Fixed tier 3 crit calculation returning int instead of float, improved type consistency
- **Repository Maintenance**: Added node_Modules to .gitignore, updated changelog formatting

### Technical Details
- **Test Coverage**: All 25 engine unit tests now passing (100% success rate)
- **Data Integrity**: CSV files validated with corrected effect and skill references
- **Critical Hit Mechanics**: Fixed tier 3 critical hit damage multipliers for Legendary/Mythic rarities
- **Type Safety**: Consistent float handling throughout hit context and damage calculations

## [2.2.2] - 2025-11-19

### Fixed
- **Code Cleanup**: Removed deprecated `data_loader.py` module (consolidated into `game_data_provider.py`)
- **Test Consolidation**: Removed legacy `test_strict_mode.py` test file
- **Test Coverage**: Added `test_roll_dual_stat_affix` test for dual-stat affix validation
- **System Simplification**: Streamlined data loading with centralized provider pattern
- **Print Statement Fixes**: Updated success messages to reflect new architecture

### Technical Details
- **Refactoring**: Eliminated redundant data loading code (320 lines removed)
- **Test Maintenance**: Consolidated validation testing into modern patterns
- **Dual-Stat Testing**: Added deterministic testing for dual-value affix rolling
- **Code Quality**: Removed deprecated modules, improved import organization
- **Architecture**: Simplified CSV loading with singleton provider pattern


## [1.0.0](https://github.com/Towen75/combat_engine/compare/v0.7.0...v1.0.0) (2025-11-15)

### Added
- **COMPLETE GDD v4.0 Combat Engine Implementation**: Full system delivery exceeding original IP scope
  - **9-Step Unified Combat Pipeline**: Complete evasion→dodge→crit→defense→block→final damage resolution
  - **Advanced Dual-Stat Affixes**: Single affixes affecting multiple stats simultaneously (damage + crit)
  - **Scaling AffixSystem**: Power-level logarithmic scaling based on character strength
  - **Complex Reactive Effects**: Advanced trigger parsing for "reflect_damage:0.3", "apply_crit_bonus:0.25"
  - **Master Rule Data System**: Complete CSV-driven content creation (skills.csv, effects.csv, affixes.csv)
- **Phase 3 Advanced Systems**: Beyond-IP implementation of complex trigger effects and handlers
  - **FocusedRageHandler**: Crit bonus on special skill use
  - **BlindingRebukeHandler**: Evasion penalty to blocked attackers
  - **Complex Trigger Parsing**: "effect_name:number" → proper effect execution
- **Phase 4 Data Master System**: Complete content creation framework
  - **MasterRuleData Loader**: Centralized CSV loading with validation and consistency checking
  - **EffectDefinition System**: Complete buff/debuff/dot mechanics (16 different effect types)
  - **LoadedSkill Objects**: Runtime skill generation with trigger parsing and metadata
  - **Data Integrity**: Query methods and cross-reference validation
- **Phase 5 Production Validation**: Complete end-to-end testing and verification
  - **run_full_test.py**: 10-second simulation with cooldowns and resource management
  - **Combat Verification**: Real skill execution, damage calculation, effect triggering
  - **Test Suite Expansion**: 16 skills loading successfully, functional trigger effects

### Technical Details
- **Architecture Excellence**: Event-driven design with 96+ unit tests (100% pass rate)
- **Data-Driven Mechanics**: Zero hardcoded skills/effects - all CSV configurable
- **Performance Validation**: Sub-millisecond execution with production simulation throughput
- **Godot Port Ready**: Complete Python prototype providing technical specification for GDScript implementation
- **Documentation Complete**: Updated memory bank reflecting full advanced system implementation
- **Quality Assurance**: Comprehensive testing with battle-tested combat validation

### Breaking Changes
- **Major Feature Expansion**: System scope far exceeds original specification (all remaining phases completed)
- **Advanced Affix System**: Dual-stat and scaling mechanics add complexity to stat calculations
- **CSV Data Requirements**: Core mechanics now depend on properly formatted CSV data files

## [0.7.0] - 2025-11-14

### Added
- **Code Review Implementation**: Major architectural overhaul transforming prototype to production-ready system
  - **Phase 1 - Action/Result Pattern**: Implemented `SkillUseResult` + `Action` hierarchy for decoupled execution
  - **CombatOrchestrator**: Dependency injection pattern for clean separation between calculation and execution
  - **Pure Functions**: Zero side effects in `calculate_skill_use()` with complete test coverage
- **Phase 2 - Effect System Generalization**: Generic `DamageOnHitHandler` with configurable `DamageOnHitConfig`
  - **Data-Driven Effects**: Add new DoT effects without code changes (css Burn, Freeze, Life Drain)
  - **Template Method Pattern**: Reusable effect framework with `create_bleed_handler()` and `create_poison_handler()`
  - **Zero-Code Extensibility**: Future effects defined entirely in configuration
- **Phase 3 - Data Integrity & Access**: Centralized data management with comprehensive validation
  - **GameDataProvider Singleton**: Centralized JSON data loading with error resilience and reload capability
  - **Stat Validation**: Entity.calculate_final_stats() validates affix stat names with helpful logging
  - **ItemGenerator Integration**: Refactored to use centralized provider with full backward compatibility

### Technical Details
- **Testing**: 129 unit tests (up from 96), 100% pass rate with comprehensive action-based validation
- **Architecture**: Production-ready with proper separation of concerns, dependency injection, and Godot compatibility
- **Performance**: All architectural improvements maintain sub-millisecond execution times
- **Error Resilience**: Input validation prevents runtime crashes while providing clear error messages
- **Godot Port Readiness**: Action/Result and dependency injection patterns translate directly to GDScript signals

### Breaking Changes
- **Architectural Refactoring**: Pure calculation functions and orchestrator execution pattern
- **Effect Framework Overhaul**: Generic configurable handlers replace hardcoded implementations
- **Data Access Centralization**: GameDataProvider singleton for all JSON loading
- **Enhanced Validation**: Stat name validation in final stat calculations

## [0.6.0] - 2025-11-14

### Added
- **Phase 5 Complete**: Procedural Item Generator system implementation
  - **ItemGenerator**: Two-phase quality rolls with sub-quality variation preventing identical items
  - **Data Pipeline**: CSV-to-JSON parsing system for affixes, items, and quality tiers
  - **Sub-Quality Variation**: Each affix rolls 0-X% where X = item's quality ceiling for unique characteristics
  - **Content Library**: 17 items × 9 affixes covering all equipment slots and rarities
  - **Data-Driven Design**: Add new content without code changes using CSV files
  - **Display Formatting**: Smart percentage formatting for multiplier stats (crits, pierce, resistance)

### Technical Details
- **Performance**: 93 unit tests with 100% pass rate, sub-millisecond item generation
- **Architecture**: Data-driven item generation with quality ceilings preventing overpowered items
- **Testing**: Comprehensive unit tests with RNG seeding for deterministic validation
- **Extensibility**: CSV-based content system supporting unlimited item/affix additions
- **Integration**: Full compatibility with existing Entity equipment system

### Breaking Changes
- **Item Model Update**: New Item dataclass with procedural generation mechanics
- **Affix System Refactor**: RolledAffix replaces static Affix with rolled values
- **Entity Integration**: Updated stat calculation for percentage-formatted multipliers

## [0.5.0] - 2025-11-11



# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-11-11

### Added
- **Phase 4 Complete**: Simulation & Balancing framework implementation
  - **CombatLogger System**: Comprehensive event recording and analysis with damage breakdown and effect uptime tracking
  - **SimulationRunner**: Time-based combat simulation with delta-time processing and automated scenario testing
  - **ReportGenerator**: Automated balance analysis with actionable recommendations and performance metrics
  - **Integration Testing**: Full system validation with seeded combat scenarios and reproducible results
- **Testing Expansion**: 22 unit tests with 100% pass rate (total 92 tests across all phases)
  - CombatLogger functionality tests
  - SimulationRunner time-based processing tests
  - ReportGenerator balance analysis tests
  - Integration scenario validation
- **Performance Achievements**: 6993 events/second simulation throughput with excellent scalability
- **Documentation**: Attack speed design document and comprehensive memory bank updates

### Technical Details
- **Performance**: Simulation framework achieves 6993 events/second with sub-millisecond execution times
- **Architecture**: Event-driven simulation with time-based processing and automated balance analysis
- **Testing**: Comprehensive unit test coverage with complex mocking for interdependent systems
- **Integration**: Full end-to-end validation with seeded random scenarios for reproducible testing

## [0.3.0] - 2025-11-10

### Added
- **Phase 3 Complete**: Game systems implementation - Items, Skills & Equipment
  - **Item System**: Affix and Item data models with stat modification logic
  - **Equipment System**: Dynamic stat calculation with flat/multiplier bonuses
  - **Skill System**: Multi-hit skills with configurable triggers and effects
  - **Effect Framework**: EffectHandler base class with Bleed and Poison implementations
  - **Integration Testing**: Complete end-to-end validation ("Phase 3 Test" script)
- **Testing Expansion**: 70 unit tests with 100% pass rate (17 new tests added)
  - Equipment and affix model tests
  - Skill processing and trigger tests
  - Effect handler functionality tests
  - Integration scenario validation
- **Dynamic Stat Calculation**: Real-time equipment bonus computation
  - Flat bonuses (e.g., +20 damage)
  - Multiplier bonuses (e.g., 1.5x pierce ratio)
  - Combined stat stacking and validation

### Technical Details
- **Performance**: All systems maintain sub-millisecond execution times
- **Architecture**: Event-driven skill effects integrated with existing EventBus
- **Extensibility**: Modular effect system for easy addition of new effects
- **Validation**: Comprehensive testing with 100% coverage on new functionality

## [0.2.0] - 2025-11-09

### Added
- **Phase 1 Complete**: Full combat foundation implementation
  - Core damage formula with pierce mechanics: `MAX((Attack Damage - Defences), (Attack Damage * Pierce Ratio))`
  - Entity and EntityStats data models with comprehensive validation
  - StateManager for dynamic entity state tracking (health, alive status)
  - CombatEngine with damage calculation and analysis tools
  - Complete integration test ("First Hit" demo script)
- **Testing Infrastructure**: 53 unit tests with 100% pass rate
  - Entity model validation tests
  - State management tests
  - Damage calculation tests
  - Integration validation
- **Development Setup**: Complete Python development environment
  - Virtual environment configuration
  - pytest testing framework
  - Git version control with proper ignore rules
  - Requirements management

### Technical Details
- **Performance**: Combat calculations complete in < 1ms per hit
- **Validation**: Input validation on all data models and operations
- **Architecture**: Modular design with clear separation of concerns
- **Documentation**: Complete memory bank with project knowledge base

## [0.1.0] - 2025-11-09

### Added
- **Project Initialization**: Combat Engine project setup
- **Memory Bank**: Documentation framework established
- **Design Documents**: Core combat system specifications
- **Development Infrastructure**: Git repository and basic structure

### Technical Details
- **Python Environment**: 3.12.10 with virtual environment
- **Dependencies**: NumPy, Pandas, pytest, pydantic configured
- **Documentation**: Project brief, context, and technical specifications
