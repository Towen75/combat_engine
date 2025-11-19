# Project Spec: Gladiator Engine Dashboard

This specification outlines a **Streamlit-based Control Center** for your Combat Engine. This approach treats your Python library as the "backend" and Streamlit as the immediate "frontend," allowing you to visualize, edit, and balance your game without writing game-client code.

**Goal:** Create a professional, web-based interface to manage game data, validate content relationships, and simulate combat scenarios using the existing Python engine.

**Tech Stack:**
*   **Frontend:** Streamlit (Rapid UI development)
*   **Charting:** Altair or Plotly (Native to Streamlit)
*   **Backend:** Your existing `src/` package (Direct import)
*   **Data:** Direct CSV manipulation via `pandas`

---

## 1. Information Architecture (Layout)

The application will use a **Sidebar Navigation** layout with three primary "Workspaces" (Pages).

### Sidebar (Global Context)
*   **Engine Status:** Indicator showing if `GameDataProvider` loaded successfully.
*   **Hot Reload:** Button to force reload CSV data without restarting the server.
*   **Global Settings:**
    *   RNG Seed (Input box for deterministic debugging).
    *   Logging Level (Dropdown: INFO/DEBUG).

---

## 2. Workspace A: The Forge (Content Manager)

This is the "Editor" you requested. It enforces data integrity by using your strict Enums and existing IDs as constraints.

**Layout:**
*   **Selector:** Radio button to choose Data Type: `Affixes` | `Items` | `Skills` | `Effects`.
*   **Action Bar:** `Create New` | `Edit Selected`.

**Feature: Smart Forms (The "Strict Order" Logic)**
Instead of typing strings, the UI generates inputs based on your `src/data/typed_models.py`.

*   **Editing an Item:**
    *   **Name/ID:** Text Input.
    *   **Slot:** Dropdown populated by `ItemSlot` Enum (Weapon, Chest, etc.).
    *   **Rarity:** Dropdown populated by `Rarity` Enum.
    *   **Implicit Affixes:** Multi-select Dropdown populated by **keys from `affixes.csv`**.
        *   *Constraint:* You cannot type a made-up affix. You must select an existing one.
    *   **Validation:** A "Validate" button runs `src/data/schemas.py`. If it passes, the "Save to CSV" button becomes enabled.

**Feature: Dependency Graph**
*   **Visualizer:** A simple readout showing "This Affix is used by 3 Items."
*   **Safety:** Prevents deleting an Affix if an Item is currently referencing it.

---

## 3. Workspace B: The Arena (Combat Debugger)

A 1-on-1 battle simulator for testing specific interactions and edge cases.

**Layout:** Two columns (Attacker vs. Defender).

*   **Entity Builder (Left & Right Columns):**
    *   **Base Stats:** Number inputs for Health, Damage, Speed (pre-filled with defaults).
    *   **Equipment Rack:** Dropdowns for Main Hand, Chest, Head, etc. (Populated from `items.csv`).
    *   **Active Buffs:** Multi-select to force-start the fight with buffs (e.g., "Test how hitting a target with *Thornmail* works").

*   **Control Panel (Center):**
    *   **Action:** Dropdown (Basic Attack, or Select a Skill from `skills.csv`).
    *   **Execute:** Big "FIGHT" button.

*   **The Battle Log (Output):**
    *   Instead of a raw console print, a formatted list of events.
    *   **Visuals:**
        *   🔴 Damage (Red)
        *   🟡 Crit (Gold)
        *   🛡️ Block (Blue)
        *   🟢 Heal (Green)
    *   **State Inspector:** An `st.expander` below the log showing the exact JSON state of `EntityStats` before and after the hit.

---

## 4. Workspace C: The Coliseum (Batch Simulation)

Leverages your **Phase 2** work (`BatchRunner`) to visualize balance data.

**Layout:**
*   **Configuration:**
    *   **Iterations:** Slider (100 - 10,000 simulations).
    *   **Matchup:** Select "Warrior Archetype" vs "Tank Archetype" (Saved presets).

*   **Dashboard Output (Visuals):**
    1.  **Win Rate:** A simple Pie Chart (Attacker Wins / Defender Wins / Timeouts).
    2.  **Time-To-Kill (TTK):** A Histogram showing how long matches last.
        *   *Insight:* If the peak is at 2 seconds, damage is too high. If it's at 5 minutes, damage is too low.
    3.  **DPS Distribution:** Box plot showing the min/max/median damage per second.
    4.  **Effect Uptime:** Bar chart showing what % of the fight "Bleed" was active.

---

## 5. Directory Structure

We will keep this separate from your engine core (`src`) to keep the library clean.

```text
combat_engine/
├── data/                 # Your CSVs
├── src/                  # Your Game Engine
├── dashboard/            # NEW DIRECTORY
│   ├── app.py            # Main Streamlit entry point
│   ├── pages/
│   │   ├── 1_The_Forge.py    # Content Editor
│   │   ├── 2_The_Arena.py    # Single Combat
│   │   └── 3_The_Coliseum.py # Batch Sim
│   ├── components/       # Reusable UI bits
│   │   ├── entity_card.py
│   │   └── battle_log.py
│   └── utils.py          # Helpers to bridge Streamlit <-> Engine
├── run_dashboard.sh      # Shortcut to launch
└── requirements.txt      # Add streamlit, altair, pandas
```

## 6. Implementation Roadmap

This looks complex, but because your engine is **Strictly Typed**, 80% of the UI code is just auto-generating forms from your Class definitions.

1.  **Setup:** Install Streamlit, create the folder structure.
2.  **Data Connector:** Write a helper to wrap `GameDataProvider` and expose Lists for Dropdowns.
3.  **The Arena (MVP):** Build the Single Combat page first. It validates that your Engine is working and provides immediate visual feedback.
4.  **The Forge:** Build the Item Editor next. This solves your content creation bottleneck.
5.  **The Coliseum:** Build this last, as it depends on the Batch Runner logic we haven't fully merged yet.

### Why this is "Professional"
*   **Type Safety in UI:** Users literally cannot enter "Pyhsical" damage. The UI only offers "Physical".
*   **Immediate Feedback:** You see the math happen in real-time.
*   **Data Persistence:** It saves directly to your CSVs, which are version-controlled by Git.

Do you want to proceed with setting up the **Dashboard Skeleton**?