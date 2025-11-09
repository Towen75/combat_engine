# Project Brief: Combat Engine

## Project Overview
This project is the development of a modular combat engine for a dungeon crawler RPG game. The engine implements a sophisticated damage calculation system, character progression mechanics, and itemization framework that enables deep strategic gameplay through player choices in skills, equipment, and character development.

## Core Requirements

### Combat System
- **Damage Calculation**: Implement the core formula `Damage Dealt = MAX((Attack Damage - Defences), (Attack Damage * Pierce Ratio))` with support for flat and multiplier modifiers
- **Critical Hits**: Multi-tier critical system where rarity determines crit scope (Base, Pre-Pierce, Post-Pierce, Full)
- **Secondary Effects**: Event-driven system for DoTs (Bleed, Poison, Burn, Life Drain) and status effects with stacking mechanics
- **Defensive Mechanics**: Armour reduction for physical damage, resistances for elemental damage

### Character Systems
- **Skills**: Three unique skills per character (Passive, Special, Ultimate) plus normal attack, all upgradeable
- **Progression**: Level-based stat increases and skill upgrades through experience from combat
- **Rarity System**: Character rarity tiers (Common→Mythic) with star progression (every 3 stars = rarity rank up)

### Itemization
- **Equipment Slots**: Head, Chest, Hands, Feet, Arms, Pants, Shoulders, Belt, Amulet, Ring(x2), Weapon, Off-Hand
- **Weapon Types**: Fists, Swords, Daggers, Axes, Maces, Bows, Staffs, Throwing Weapons
- **Affix System**: Thematic affix pools by slot/type with exclusivity rules and rarity scaling

### Progression Loop
- **Core Loop**: Kill mobs → Gain XP → Level up (with reward choices) → Clear floors → Fight bosses → Gain stars → Rarity upgrade → Higher level cap
- **Reward System**: Small rewards on level-up (items, upgrades, boosts), major rewards on floor/boss completion

## Technical Goals
- **Modular Architecture**: Data-driven and event-driven design for easy content creation and balancing
- **Simulation Framework**: Built-in tools for combat testing, reporting, and balancing
- **Engine Agnostic**: Core logic designed for portability (initially prototyped in Python, final implementation in Godot/GDScript)

## Success Criteria
- Fully functional damage calculation engine with all formula components
- Complete character progression system with leveling and rarity
- Comprehensive itemization system with balanced affixes
- Working simulation framework for testing and balancing
- Clear documentation and data structures for content creation

## Scope Limitations
- Single-player focused (no multiplayer considerations)
- Dungeon crawler mechanics (no open world)
- Combat-focused (exploration mechanics minimal)
- PC platform target (Godot engine)

## Key Stakeholders
- Game Designer: Combat balance and player experience
- Technical Lead: System architecture and performance
- Content Creator: Item/skill data and balancing
