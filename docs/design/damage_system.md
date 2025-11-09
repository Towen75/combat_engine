# **Game Design Document: Core Combat & Damage Systems**
**Version:** 3.0
**Date:** November 7, 2025

---

### **1.0 Overview**
This document outlines the core design for the damage calculation, character skills, and itemization systems. The primary goal is to create a layered and engaging combat system where player choices in skills, equipment, and character development have a meaningful impact on performance. The system is built upon several key dimensions that combine to determine overall combat effectiveness.

---

### **2.0 Core Damage Calculation**
The foundation of the combat system is the calculation of damage applied with each successful attack. Damage is resolved on a per-hit basis.

#### **2.1 Damage Formula**
For each individual hit that lands on a target, the damage dealt is calculated as follows:

`Damage Dealt = MAX( (Attack Damage - Defences), (Attack Damage * Pierce Ratio) )`

where the pierce ratio is a fractional value between 0.01 and 1.
With respect to modifiers, additive or 'flat' modifiers are applied to the attack damage prior to pierce, whilst multiplier modifiers are applied to the damage dealt after pierce.
For example:
Attack Damage = 100 + FlatBonus(20) = 120  
Armour = 80  
Pierce = 0.3  
→ PrePierceDamage = 120 - 80 = 40  
→ PiercedDamage = 120 * 0.3 = 36  
→ Damage = max(40, 36)  
→ AfterPierceMultiplier(1.3) = 52

The 'Defences' is take as amour for physical attacks and the relevant resistances for non-physical attacks. Resistances will be calculated using a formula based on percent of armour and other stats with exact details tbd. 

This ensures that attacks with a high `Pierce Ratio` remain effective against heavily armoured targets, providing a strategic layer to combat encounters.

#### **2.2 Critical Hits**
Each hit has a chance to be a critical hit, based on the attacker's `Critical Hit Chance` statistic. A critical hit multiplies the attack damage by the attacker's `Critical Hit Damage` modifier.

By default critical Hits only affect the attack damage pre modifier and pre-pierce.  Item of skill modifiers and/or effects are required for critical hits to affect other parts of the damage formula so that with the right set up it is possible crits may multiply post-pierce or even secondary effects. 

Consider having an "crit tier" system (e.g. ) (normal crit → empowered crit → super-crit) driven by overcapping crit chance or specific affixes.

Can we link crits to an overkill mechanic (overkill is where you deal twice the require damage to kill in one attack whilst enemy is above x% health)

---

### **3.0 Dimensions of Damage**
The "Attack Damage" value is influenced by a combination of factors inherent to the character, their weapon, and the specific attack being used.

*   **3.1 Base Damage:** An intrinsic statistic of the player character.
*   **3.2 Hits:** The number of times a single attack execution strikes the target.
*   **3.3 Attack Speed:** Determines the frequency at which attacks are performed.
*   **3.4 Attack Targets:** Defines the application area of an attack (Single-Target, Multi-Target, Area of Effect, Vector-Based).
*   **3.5 Damage Type:** Each attack possesses a damage type which dictates its core properties, including `Pierce Ratio` and potential Secondary Effects.

#### **3.6 Secondary Effects & Multi-Hit Resolution**
Secondary effects (DoTs, debuffs, status effects) are resolved on a **per-hit basis**. For a multi-hit attack, each hit is an independent event with its own damage calculation, critical hit check, and secondary effect proc check. Stacks are not bundled.

---

### **4.0 The Event Trigger System**
The system for applying secondary effects is governed by a universal "Event Trigger System." This provides a consistent framework for all conditional effects in the game.

#### **4.1 The Core Model**
Every conditional effect is defined by three components:
1.  **The Trigger (The "On-Event"):** The specific gameplay event that initiates the logic (e.g., On-Hit, On-Crit, On-Kill, On-Dodge).
2.  **The Check (The Condition):** An optional set of conditions, most commonly a `Proc Rate` percentage, but can also be a state check (e.g., target is below 20% health).
3.  **The Result (The Consequence):** The outcome that occurs if the trigger fires and the check is passed (e.g., apply a debuff, deal damage, restore health).

#### **4.2 Application Methods for Secondary Effects**
The "Result" of a trigger is handled by one of two primary systems:

*   **4.2.1 Stacking System (for DoTs, Buffs, Debuffs):** These effects are applied in stacks and are governed by `Proc Rate`. This model is designed for effects that can overlap and accumulate.
*   **4.2.2 Empower System (for Status Effects):** Hard control effects like Stun or powerful slows are governed by this system. The magnitude or duration of the effect scales with the pre-mitigation damage of the single hit that applies it, rewarding slower, more powerful attacks over rapid, light ones.

#### **4.3 Damage over Time (DoT) Implementations**
DoTs are a common "Result" of an On-Hit trigger. The following are base implementations. By default and without modification all DoTs cannot themselves crit or proc or trigger secondary effects and have their own damage damage and/or coefficients.


*   **4.3.1 Bleed (Sustained Physical Pressure)**
    *   **Formula:** `Total Damage = Base Damage * Stacks`
    *   **Niche:** A straightforward and dependable source of physical damage.

*   **4.3.2 Poison (High-Health Shredder)**
    *   **Formula:** `Total Damage = (x% of Target's Current Health * Base % Damage) * Stacks`
    *   **Niche:** An anti-tank and boss-killing debuff, most effective at the start of a fight.

*   **4.3.3 Burn (Intensifying Elemental Damage)**
    *   **Formula:** `Total Damage = (Base Damage * Stacks) * 2^(Stacks / 30)`
    *   **Niche:** A high-skill, high-reward effect that ramps up exponentially, doubling its effectiveness every 20 stacks. Capped at 100 stacks. 

*   **4.3.4 Life Drain (Sustaining Finisher)**
    *   **Formula:** `Total Damage = (Target's Missing Health * Base % Damage) * Stacks`
    *   **Siphon:** The attacker is healed for x% of the Life Drain damage dealt.
    *   **Niche:** An "execute" DoT that becomes stronger as the target weakens.

#### **4.4 DoT Stack Management: Combined Refresh Model**
All stacking DoTs use this model for efficiency and clarity.
1.  **Single Debuff Instance:** All stacks of a specific DoT are treated as one debuff on the target.
2.  **Application Refreshes Duration:** When a new stack is successfully applied, the stack count increases, and the duration of the entire debuff is refreshed to its maximum value.
3. **Internal Cooldown** stack application has an internal cooldown of say half or quarter of a tick for balance purpose to prevent high-speed attacks dominating the meta.
4.  **Removal:** If the duration expires, the entire debuff and all its stacks are removed.

---

### **5.0 Defensive Mechanics**
*   **5.1 Armor:** Primarily reduces incoming **physical** damage.
*   **5.2 Resistances:** Reduce incoming **non-physical** (e.g., elemental) damage.
*   **5.3 Base Resistance:** Armour provides a small universal resistance unless an effect specifies otherwise.

---

### **6.0 Character Skills**
Each character has a unique set of three skills that define their combat identity.
*   **6.1 Passive Skill:** An intrinsic, always-active ability.
*   **6.2 Special Skill:** An activatable ability that consumes a character-specific resource.
*   **6.3 Ultimate Skill:** A powerful, high-impact ability with a significant cooldown.

---

### **7.0 Itemization**
Items are a primary vector for character customization and progression.

#### **7.1 Equipment Slots**
Head, Chest, Hands, Feet, Arms, Pants, Shoulders, Belt, Amulet, Ring (x2), Weapon, Off-Hand.

#### **7.2 Weapon Types**
Fists/Unarmed, Swords, Daggers/Knives, Axes, Maces/Hammers, Bows/Arrows, Staffs, Throwing Weapons.

#### **7.3 Item Tiers & Rarity**
*   **Item Design:** Basic, Special, and Unique items determine the complexity of their effects.
*   **Affix Tiers:** Low (Normal Rarity), Mid (Magic Rarity), and High (Mystic Rarity) tier affixes determine the power and nature of item bonuses.

#### **7.4 Affix Exclusivity**
To ensure balance, certain powerful affixes are mutually exclusive and cannot appear on the same item.

#### **7.5 Thematic Affix Distribution**
Affixes are sorted into "Affix Pools" based on item slot and type to give each piece of gear a distinct strategic identity.

*   **7.5.1 Distribution by Armor/Accessory Slot**
    *   **Primary Slots:**
        *   **Head:** Mind/Command (Cooldowns, Resource Mgt, AoE).
        *   **Chest:** Vitality/Resilience (Health, Armor, Resistances).
        *   **Hands:** Dexterity/Application (Attack Speed, Crit Chance, Proc Rate).
        *   **Feet:** Mobility/Evasion (Movement Speed, Dodge).
    *   **Supporting Slots:**
        *   **Arms:** Supports the Hands (Flat Damage, Life on Hit, secondary speed/crit).
        *   **Pants:** Supports the Feet (Health, Armor, secondary move/dodge, CC resist).
        *   **Shoulders:** Hybrid Offense/Defense (Cooldowns, Thorns, general stats).
        *   **Belt:** Utility/Resourcefulness (Potion effects, Resource Generation).
    *   **Specialized Slots:**
        *   **Jewelry (Amulet/Rings):** Potent & Unique Effects (Crit Damage, +All Skills, powerful Event Triggers).

*   **7.5.2 Distribution by Weapon Type**
    *   **Swords:** Versatility (Flat Damage, Attack Speed).
    *   **Axes:** Brutality (% Physical Damage, Crit Damage, Bleed).
    *   **Maces & Hammers:** Control (Armor Pierce, Empowered Stun).
    *   **Daggers / Knives:** Precision & Cunning (Crit Chance, Attack Speed, Poison).
    *   **Bows & Arrows:** Ranged Superiority (+Projectiles, Pierce, Slow).
    *   **Staffs:** Magical Conduit (Elemental Damage, Burn/Life Drain, Cooldowns).
    *   **Fists / Throwing:** Rapid Application (High Attack Speed, Proc Rate, Life on Hit).

---

### **8.0 Rarity System**
A universal rarity scale applies to characters, items, and affixes.
*   **Tiers:** Common, Uncommon, Rare, Epic, Legendary, Mythic.
*   **Categories:** Normal (Common/Uncommon), Magic (Rare/Epic), Mystic (Legendary/Mythic).
*   **Application:** For characters, rarity limits their max level. For items, it determines the power and quantity of affixes.

---

### **9.0 Internal Balancing: "Power Score"**
For internal design and balancing, an abstract "Power Score" metric will be used to evaluate the theoretical effectiveness of an attack or item.
*   **Conceptual Formula:** `Power Score ≈ (Damage * Hits) *  (1 + EffectModifier) * TargetFactor`

Where TargetFactor is based from a combination of pierceRatio and TargetCount 
---

### **10.0 Progression Systems**
*   **Character Leveling:** Characters gain experience to increase their base level and core stats.
*   **Skill Leveling:** Each of the three main skills has its own level that can be increased.

---

### **11.0 To Be Determined (TBD) During Development**
The following systems and values require further design, prototyping, and balancing:
*   Specific numerical values for all base stats, damage effects, proc rates, and empowerment scaling.
*   Detailed character archetypes and their unique skill sets.
*   The complete list of item affixes and their value ranges per rarity tier.
*   The experience curve for character and skill progression.
*   Specific mechanics for character resource regeneration.
*   Enemy statistics, abilities, and AI.

** In Depth Critical Hit System Design **

⚔️ Critical Hit System — Integrated Design (with Rarity Scaling)

🧩 1. Core Concept
Critical hits represent moments of exceptional precision or power, temporarily amplifying a unit’s damage.
 In your system, the rarity of the attacker’s equipment or skill determines how deeply the critical strike penetrates the damage formula — a layered design that rewards progression and synergy building.
This is governed by Critical Hit Tiers, which define how far the crit multiplier propagates through the calculation.

⚙️ 2. Critical Hit Flow Overview
Below is a narrative + visual breakdown of the damage calculation process, showing when and where critical hits are applied at each rarity tier.

Damage Calculation Flow (Base System)
1. Base Damage
    ↓
2. Flat Modifiers (e.g., +20 from buffs)
    ↓
3. Multipliers (e.g., ability or faction bonus)
    ↓
4. Defense / Armor Reduction
    ↓
5. Pierce (bypasses some armor)
    ↓
6. Final Damage Modifiers (e.g., elemental, situational)
    ↓
7. Secondary Effects (e.g., burn, bleed)


Critical Hit Application by Tier
Crit Tier
Source
Critical Multiplier Applies After:
Scope Description
Formula Section
Tier 1 — Base Crit
Normal (Common/Uncommon)
Step 1
Affects only base attack damage before modifiers or pierce.
base_damage × crit_mult
Tier 2 — Enhanced Crit
Magic (Rare/Epic)
Step 3
Affects all pre-pierce damage (base + flat + ability modifiers).
(base + flat) × mult × crit_mult
Tier 3 — True Crit
Mystic (Legendary/Mythic)
Step 6
Affects full final damage, post-pierce and post-defense.
final_damage × crit_mult
Tier 4 — Transcendent Crit (special)
Mythic+ or unique passives
Step 7
Affects final damage and secondary effects (DoTs, procs).
final_damage × crit_mult + enhanced DoTs


📊 Visual Summary (Flow Diagram)
       ┌─────────────────────────────────────────────┐
        │            BASE DAMAGE CALCULATION           │
        └─────────────────────────────────────────────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
         Tier 1         Tier 2         Tier 3+
        (Normal)        (Magic)        (Mystic+)
          │               │               │
     [Apply crit]   [Apply crit]   [Apply crit + secondary]
     to base only    pre-pierce     post-pierce & effects
          │               │               │
          └────→ Continue Damage Flow →───┘


💥 3. Step-by-Step Calculation Example
Let’s walk through an example to illustrate how crit scope changes by rarity.
Base Parameters:
Base Damage: 100
Flat Bonus: +30
Ability Multiplier: ×1.2
Armor Reduction: 20%
Pierce: 50%
Crit Multiplier: ×2.0


Rarity
Calculation Path
Final Damage
Normal (Tier 1)
Crit(100) × 1.2 = 240 × (1 - 0.2 × (1 - 0.5)) = 216
216
Magic (Tier 2)
Crit((100 + 30) × 1.2) = 312 × (1 - 0.2 × (1 - 0.5)) = 280.8
281
Mystic (Tier 3)
(100 + 30) × 1.2 × (1 - 0.2 × (1 - 0.5)) = 187.2 → Crit(×2) = 374.4
374
Mythic+ (Tier 4)
Same as Tier 3 + DoT/Secondary doubled
≈374 + effect

This shows the clear scaling: higher rarity pushes crit further downstream, giving greater multiplicative leverage.

🧠 4. Design Rationale
Design Goal
Mechanic
Outcome
Make rarity feel meaningful.
Higher-tier crits apply later in the formula.
Rare gear delivers real mechanical depth, not just bigger numbers.
Reward build synergy.
Skills or items can extend crit scope or unlock higher tiers.
Allows hybrid builds to feel unique.
Keep balance under control.
Limit crit tier access, apply soft caps beyond Tier 2.
Prevent exponential crit stacking.
Support future scaling.
Crit scope can be extended via traits or special affixes.
Easy to expand system later.


🔧 5. Implementation Notes (Python)
5.1 Define Critical Scope per Rarity
from enum import Enum, auto

class CritScope(Enum):
    BASE = auto()
    PRE_PIERCE = auto()
    POST_PIERCE = auto()
    FULL = auto()

5.2 Link Rarity to Scope
RARITY_CRIT_SCOPE = {
    "Normal": CritScope.BASE,
    "Magic": CritScope.PRE_PIERCE,
    "Mystic": CritScope.POST_PIERCE,
    "Mythic": CritScope.FULL
}

5.3 Apply in Hit Resolution
def apply_critical(hit, rarity_scope: CritScope):
    if not hit.is_crit:
        return hit

    if rarity_scope == CritScope.BASE:
        hit.base_damage *= hit.crit_mult

    elif rarity_scope == CritScope.PRE_PIERCE:
        hit.pre_pierce_damage *= hit.crit_mult

    elif rarity_scope == CritScope.POST_PIERCE:
        hit.final_damage *= hit.crit_mult

    elif rarity_scope == CritScope.FULL:
        hit.final_damage *= hit.crit_mult
        hit.apply_secondary_crit_effects()

    return hit

You can store the maximum scope available on both item and ability, then apply the most permissive one:
scope = max(item.scope, ability.scope, key=lambda s: s.value)
hit = apply_critical(hit, scope)


⚖️ 6. Balancing Guidelines
Area
Risk
Mitigation
Tier 3/4 double-dipping
Pierce or elemental modifiers stacking too efficiently.
Introduce diminishing scaling on crit damage above 200%.
Early tier boredom
Tier 1 crits feel weak.
Use higher crit chance or visual flair to keep them satisfying.
DoT abuse (Tier 4)
Infinite loop of secondary crits.
Restrict to 1 stack or CD gating.
Rarity disparity
Huge jump between Magic → Mystic.
Offer partial “scope extension” via skill passives or affixes.


🌟 7. Optional Extensions
Affix Example:
 “Critical Precision” — Your critical hits apply post-pierce (1 tier higher).


Skill Synergy Example:
 “Lethal Focus” — When at full energy, your next hit uses True Crit scope.


Faction Identity:


Assassins favour Enhanced Crits (Tier 2).


Demons unlock True Crits (Tier 3).


Celestials may manipulate Transcendent Crits (Tier 4).



🧾 8. Summary (for Documentation)
Critical Hits (Rarity-Linked System)
 Critical hits multiply damage, but their scope depends on rarity.
 Normal-tier crits enhance base attack damage only, while Mystic-tier crits apply across the full formula, including post-pierce modifiers.
This progression turns rarity into a structural combat mechanic, ensuring that higher-quality items don’t just increase stats — they deepen mechanics.




Next Prompt
Ok thanks.  For the game and character itself I think I have a good design. 
Each character has normal attack, passive skill, special skill and ultimate skill.  All of these are upgraded ( increased effect , extend effect etc)  characters rank up in rarity. Rarity ranks up every 3 stars and increases max level. Level up increases base stats. 

Characters gain levels via experience and experience is gained by kills mobs and completing dungeon floors, and every 3rd floor has a dungeon boss that also rewards a rarity upgrade upon death.  When a level is gain an offering of 3 small rewards is presented to the player (e.g. new item, random item upgrade, exp, temporary boost boost, etc) with bigger rewards offered at floor compilation.

