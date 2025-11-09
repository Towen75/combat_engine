# Active Context

## Current Work Focus

### Immediate Priority: Phase 1 Implementation
The project is currently in the initial setup phase, establishing the foundational memory bank and preparing for core combat system development. The focus is on implementing Phase 1 of the implementation plan: "The Foundation - Core Damage & State".

**Active Development Tasks:**
- Complete memory bank documentation setup
- Begin Python prototyping of core damage calculation
- Establish testing framework for combat mechanics
- Create initial data models and validation

### Key Current Objectives
1. **Memory Bank Completion**: Finish documenting all core project knowledge
2. **Foundation Systems**: Implement basic Entity class and StateManager
3. **Damage Formula**: Build and test the core damage calculation: `MAX((Attack Damage - Defences), (Attack Damage * Pierce Ratio))`
4. **Unit Testing**: Establish comprehensive test coverage for all core functions

## Recent Changes

### Memory Bank Establishment
- **Created projectbrief.md**: Defined core requirements, scope, and success criteria
- **Created productContext.md**: Established user experience goals and problem-solution framework
- **Created systemPatterns.md**: Documented architecture decisions and design patterns
- **Created techContext.md**: Specified technology stack and development constraints

### Design Document Analysis
- **Damage System Review**: Confirmed comprehensive design covering damage formulas, critical hits, secondary effects, and itemization
- **Progression Loop Analysis**: Validated the interlocking level/rarity progression system
- **Implementation Plan Review**: Approved phased approach with clear milestones

## Next Steps

### Short Term (Next 1-2 Weeks)
1. **Complete Memory Bank**: Finish progress.md and any additional context files
2. **Python Environment Setup**: Initialize virtual environment and install dependencies
3. **Data Models Implementation**: Create base Entity class with core stats
4. **Combat Engine Foundation**: Implement basic ResolveHit function
5. **Initial Testing**: Set up pytest framework and write first unit tests

### Medium Term (Next 1-2 Months)
1. **Phase 1 Completion**: Full core damage and state management system
2. **Phase 2 Beginning**: Add critical hit system and event framework
3. **Simulation Framework**: Build basic combat simulation tools
4. **Balance Analysis**: Run initial simulations to validate damage formula

### Long Term (3+ Months)
1. **Phase 3-4 Completion**: Full game systems integration
2. **Godot Port**: Transition from Python prototype to GDScript implementation
3. **Content Creation**: Develop sample characters, items, and skills
4. **Playtesting**: Balance pass and user experience validation

## Active Decisions and Considerations

### Architecture Decisions
- **Python Prototyping**: Confirmed as primary development approach before Godot implementation
- **Data-Driven Design**: All game content will be JSON-defined for easy balancing
- **Event-Driven Effects**: EventBus system approved for decoupling combat logic from effects

### Design Considerations
- **Pierce Ratio Balance**: Need to ensure pierce provides meaningful counterplay without dominating
- **Critical Hit Tiers**: Rarity-based crit scope creates clear progression incentives
- **DoT Stacking**: Combined refresh model prevents spam while rewarding skill

### Technical Considerations
- **Performance Targets**: Combat calculations must complete in < 1ms per hit
- **Memory Management**: StateManager needs efficient handling of effect stacks
- **Testing Coverage**: Aim for 80%+ coverage on critical combat systems

## Important Patterns and Preferences

### Code Style Preferences
- **Clear Naming**: Descriptive variable and function names (e.g., `attack_damage` not `atk_dmg`)
- **Type Hints**: Full Python type annotations for maintainability
- **Docstrings**: Comprehensive documentation for all public functions
- **Modular Functions**: Single responsibility principle for all methods

### Data Structure Preferences
- **Immutable Core Stats**: Base stats treated as immutable, modifications through modifiers
- **Typed Enums**: Use enums for categories (damage types, effect types, rarity tiers)
- **Validation**: All data structures validated on creation/load
- **Serialization**: JSON-compatible structures for save/load functionality

### Development Preferences
- **Test-First**: Write tests before implementation where possible
- **Incremental Development**: Build and test small pieces before integration
- **Documentation Priority**: Update memory bank with significant decisions/changes
- **Simulation-Driven**: Use simulation tools to validate design decisions

## Learnings and Project Insights

### Design Strengths Identified
- **Interlocking Progression**: Level caps tied to rarity creates natural long-term goals
- **Event System Flexibility**: Allows complex skill/item interactions without hardcoded logic
- **Phased Implementation**: Clear roadmap prevents scope creep and maintains momentum

### Potential Challenges Anticipated
- **Balance Complexity**: Multiple interacting systems (pierce, crits, DoTs) require careful tuning
- **Performance Scaling**: Effect stacking and event dispatching must scale to 50+ entities
- **Data Management**: Large item/affix databases need efficient loading and querying

### Key Insights from Design Review
- **Player Agency**: Choice-based rewards on level-up add significant replay value
- **Rarity Meaningfulness**: Higher rarity providing deeper mechanical access (not just stats) is innovative
- **Boss Pacing**: Every 3 floors structure creates satisfying rhythm and milestone density

### Risk Mitigation Strategies
- **Prototyping First**: Python implementation allows rapid iteration and testing before Godot commitment
- **Modular Architecture**: Independent systems can be developed and tested separately
- **Comprehensive Testing**: Automated tests will catch regressions and validate balance changes
- **Documentation Discipline**: Memory bank ensures knowledge persistence across development sessions

## Current Project State

### Completed
- ✅ Design document analysis and synthesis
- ✅ Memory bank structure established
- ✅ Core project documentation (4/6 files)
- ✅ Technology and architecture decisions documented

### In Progress
- 🔄 Memory bank completion (progress.md remaining)
- 🔄 Development environment preparation
- 🔄 Initial prototyping setup

### Planned
- 📋 Phase 1 implementation (core damage system)
- 📋 Event system foundation
- 📋 Basic simulation framework
- 📋 Initial balance validation

## Communication and Collaboration Notes

### Documentation Standards
- All significant decisions documented in activeContext.md
- Code changes accompanied by updated memory bank entries
- Design rationale captured for future reference

### Review and Validation
- Regular simulation runs to validate balance assumptions
- Peer review of critical systems before integration
- User testing feedback incorporated into design iterations
