# Combat Engine Project Brief

## Overview
A modular combat system for dungeon crawler RPGs featuring sophisticated damage calculations, character progression, and itemization systems.

## Core Mission
To implement a complete RPG combat system with pierce-based damage calculation, multi-tier critical hits, event-driven effects, dynamic itemization, and time-based simulation for DoTs, duration management, and temporal effects.

## Key Features
- Pierce-based damage formula: `MAX((Attack Damage - Defense), (Attack Damage × Pierce Ratio))`
- Rarity-based critical hit scaling (Common→Mythic)
- Event-driven effects system for DoTs, buffs, and skill interactions
- Thematic affix pools with equipment mechanics
- DoT ticks, duration management, and temporal effects

## Architecture Principles
- Data-driven design with all game content in external data structures
- Event-driven architecture with loose coupling through observer pattern
- Deterministic results for testing and balance validation
- Modular systems for easy maintenance and extension

## Development Status
- Python prototype: Complete and fully tested (96 unit tests)
- Godot port: Ready for implementation
- Test coverage: >95% on critical systems
- Performance: 6993 events/second in simulation

## Project Goals
1. Transform into production-ready, maintainable library through 8-phase plan
2. Port core systems to GDScript
3. Implement UI and visual feedback
4. Add content creation tools
5. Optimize performance for target platforms

## Critical Requirements
- **RNG Policy**: All combat RNG must be deterministic in tests and injectable in production. No global seeding permitted.
- **Test Determinism**: Same inputs always produce same outputs for reproducible tests and balance validation
- **Code Quality**: Type hints, comprehensive docstrings, unit tests for all functionality
- **Data Integrity**: Strict typing and validation with logical cross-reference checks
