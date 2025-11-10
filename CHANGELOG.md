# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
