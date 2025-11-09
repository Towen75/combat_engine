### **Core Progression Loop Analysis**

You have successfully designed a classic and highly effective core loop. It can be visualized like this:

1.  **Engage in Core Gameplay** → *(Kill Mobs, Clear Dungeon Floors)*
2.  **Gain Primary Resource** → *(Gain Experience)*
3.  **Achieve Micro-Milestone** → *(Level Up)*
4.  **Receive Immediate Rewards** → *(Increase Base Stats + Get a Choice of 3 Small Rewards)*
5.  **Engage in Macro-Gameplay** → *(Fight a Dungeon Boss every 3 floors)*
6.  **Achieve Macro-Milestone** → *(Defeat the Boss)*
7.  **Receive Major Rewards** → *(Gain a "Star" for Rarity Upgrade + Bigger Rewards)*
8.  **Unlock Further Progression** → *(3 Stars lead to Rarity Rank Up, which increases Max Level Cap)*
9.  **Loop Repeats** → *(The higher level cap allows the player to continue the core loop at a higher difficulty/power level)*

This is a fantastic structure because the two main loops (Leveling and Rarity) directly feed into each other, ensuring the player never hits a hard wall without a clear objective to overcome it.

---

### **Detailed Breakdown of Progression Systems**

#### **1. Character Progression**

This is the vertical progression axis, making a single character more powerful over time.

*   **Leveling (Short-Term Goal):**
    *   **Mechanic:** Gain XP from combat and exploration.
    *   **Reward:** Increased base stats. This provides a constant, tangible sense of growing stronger with every level.
    *   **Player Choice:** The "offering of 3 small rewards" is a brilliant rogue-lite mechanic. It gives players agency and makes each level-up feel unique and exciting.
        *   *Examples:* new item, random item upgrade, bonus XP, temporary boost (e.g., +20% Crit Chance for the next floor).

*   **Rarity & Stars (Long-Term Goal):**
    *   **Mechanic:** Rarity (e.g., Common, Uncommon, Rare) is the major tier. It sounds like "Stars" are the intermediate steps (1-Star, 2-Star, 3-Star) within a rarity. This is a great way to break up the long-term goal into smaller, achievable chunks.
    *   **Reward:** The primary reward for ranking up rarity is an **increased max level**. This is the key that unlocks the next phase of the leveling loop.
    *   **Acquisition:** Earning a "star" by defeating a dungeon boss is a powerful and memorable milestone. It makes boss fights the central focus of a player's long-term progression.

*   **Skill Upgrades:**
    *   **Mechanic:** All four ability slots (Normal Attack, Passive, Special, Ultimate) can be upgraded.
    *   **Effect:** Upgrades can "increase effect" (e.g., +10% damage, +5% crit chance on the skill) or "extend effect" (e.g., Bleed duration +1 second, Stun duration +0.2 seconds). This provides depth and allows for build customization.

#### **2. Dungeon Structure & Rewards**

This is the horizontal progression axis, defining the gameplay environment where character progression occurs.

*   **Pacing:** The "3 floors then a boss" structure is excellent. It creates a predictable and satisfying rhythm for gameplay sessions. Players know they are always working towards a meaningful confrontation.
*   **Reward Pacing:**
    *   **Micro-Rewards (Level Ups):** Happen frequently during gameplay, keeping the player engaged moment-to-moment.
    *   **Macro-Rewards (Floor/Boss Completion):** These are the "jackpot" moments that punctuate the end of a gameplay segment. They should feel significantly more impactful than the level-up rewards.
        *   *Examples for "Bigger Rewards":* Guaranteed high-rarity item, a Skill Upgrade Point, a large amount of a special currency, or unlocking a new system.

---

### **Strengths of This Design**

*   **Interlocking Systems:** The level cap being tied to rarity is the linchpin that makes the entire system work. Players have a clear reason to pursue both leveling and rarity.
*   **Clear Player Goals:** At any point, the player knows exactly what they need to do to get stronger: gain XP to level up, or beat the next boss to increase their rarity potential.
*   **Multiple Vectors of Power:** Players feel progress on many fronts simultaneously: their character's level, rarity, individual skill power, and equipped items.
*   **High Player Agency:** The choice-based rewards on level-up prevent the progression from feeling linear and pre-determined, adding replayability and build diversity.

---

### **Next Steps & Design Considerations**

You have a solid blueprint. The next step is to start defining the specific numbers and rules that will govern these systems. Here are some key questions to consider for your design document:

1.  **The Experience Curve:**
    *   How much XP does it take to get from level 1 to 2, versus 49 to 50? Will it be a steep curve or a gentle one?
    *   How much XP do mobs give? How much for a floor clear? This will determine the overall pace of the game.

2.  **Skill Upgrade Mechanics:**
    *   **How does a player upgrade a skill?** Do they earn "Skill Points" on level-up or from boss kills? Or do they need to find/craft specific items (like "Tomes of Strength")?
    *   Define a clear upgrade path for a few sample skills. For example:
        *   **Fireball Lvl 1:** Deals 100 damage.
        *   **Fireball Lvl 2:** Deals 115 damage.
        *   **Fireball Lvl 3:** Deals 130 damage and applies a small Burn DoT.

3.  **The "Star" System:**
    *   What benefit, if any, does a character get for being 1-Star or 2-Star? Is it just a step towards the rarity rank-up, or does each star provide a small stat bonus? (e.g., +5% to all base stats per star).

4.  **The "Normal Attack":**
    *   Is the "Normal Attack" considered a skill that can be upgraded with points, or does its damage only scale from the character's `base_damage` stat and item affixes?

5.  **Prototyping with Your Combat Framework:**
    *   You can now use the simulation framework from Phase 4 to test this progression. Create a Level 5 character and a Level 10 character (with appropriately scaled stats) and run them against the same enemy. Does the power increase *feel* right based on the DPS numbers?
    *   Simulate a character before and after a Rarity upgrade (e.g., at level 30, then again at level 30 but with the higher base stats they would have earned on the path to a new cap of 60). This will help you balance the impact of each major milestone.