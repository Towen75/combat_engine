# Product Context

## Why This Project Exists

The Combat Engine project addresses the need for a sophisticated, modular combat system in modern dungeon crawler RPGs. Traditional combat systems often feel shallow, with player choices having minimal impact on overall effectiveness. This engine creates a layered combat experience where every decision - from skill selection to equipment choices to character progression paths - meaningfully affects gameplay outcomes.

## Problems Solved

### Shallow Combat Depth
- **Problem**: Many games have simple damage formulas that don't reward strategic thinking
- **Solution**: Multi-layered damage calculation with pierce ratios, critical hit tiers, and secondary effects that create meaningful trade-offs and synergies

### Linear Progression
- **Problem**: Character growth feels predetermined with little player agency
- **Solution**: Branching progression paths through skill upgrades, rarity tiers, and choice-based reward systems

### Poor Itemization
- **Problem**: Equipment feels interchangeable with no distinct identities
- **Solution**: Thematic affix pools and exclusivity rules that give each item slot and weapon type unique strategic roles

### Lack of Build Diversity
- **Problem**: Limited viable strategies due to imbalanced mechanics
- **Solution**: Event-driven system allowing complex interactions between skills, items, and character abilities

## How It Should Work

### Core Gameplay Loop
1. **Combat Engagement**: Players enter dungeons with procedurally generated floors
2. **Strategic Decision Making**: Choose skills, position, and timing based on enemy types and player build
3. **Damage Resolution**: Complex calculations determine hit effectiveness, with pierce bypassing armor and crits amplifying damage based on rarity
4. **Secondary Effects**: DoTs and status effects create ongoing tactical considerations
5. **Progression Milestones**: Level-ups provide choice rewards, boss fights unlock rarity upgrades

### Combat Flow
- **Initiation**: Player selects target and activates skill
- **Calculation**: Engine resolves damage using attacker stats, defender defenses, and skill properties
- **Events**: Triggers fire based on outcomes (OnHit, OnCrit, OnKill)
- **Effects**: Secondary systems apply DoTs, buffs, or status effects
- **Feedback**: Clear visual/audio indicators of damage, crits, and effect applications

## User Experience Goals

### Strategic Depth
- Players should feel that understanding the damage formula and effect interactions leads to superior performance
- Build diversity should encourage experimentation and replayability
- Rare items and high-rarity characters should feel meaningfully more powerful

### Satisfying Progression
- Level-ups should feel like meaningful milestones with tangible power increases
- Rarity upgrades should be rare, memorable events that unlock new potential
- Reward choices should create branching paths and build identity

### Clear Feedback
- Combat should provide immediate, understandable feedback on what's happening
- Build effectiveness should be visible through damage numbers, effect uptimes, and performance metrics
- Simulation tools should help players understand and optimize their builds

### Accessibility
- Complex systems should be approachable for casual players
- Tooltips and UI should explain mechanics without overwhelming
- Auto-balancing should prevent extreme power disparities

### Emotional Experience
- Combat should feel impactful and responsive
- Critical moments (big crits, boss kills) should be exciting
- Progression should create a sense of growing mastery and capability

## Target Audience
- **Core Players**: Strategy-focused gamers who enjoy optimizing builds and mastering complex systems
- **Casual Players**: Those who want engaging combat without overwhelming complexity
- **Content Creators**: Game designers who need flexible systems for creating balanced, interesting content

## Success Metrics
- Player engagement with different build strategies
- Time spent in combat vs exploration
- Completion rates for high-difficulty content
- Positive feedback on combat satisfaction and depth
