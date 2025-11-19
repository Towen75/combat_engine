"""Script to update all imports to reflect the new modular structure."""

import os
import re
from pathlib import Path

# Define the import mapping from old to new structure
IMPORT_MAPPINGS = {
    # Combat package
    r'from src\.combat_math import': 'from src.combat.combat_math import',
    r'from src\.engine\.core import': 'from src.combat.engine import',
    r'from src\.engine import': 'from src.combat import',
    r'from src\.combat_orchestrator import': 'from src.combat.orchestrator import',
    r'from \.\.combat_math import': 'from src.combat.combat_math import',
    r'from \.\.engine\.core import': 'from src.combat.engine import',
    r'from \.\.combat_orchestrator import': 'from src.combat.orchestrator import',
    r'from \.engine\.core import': 'from src.combat.engine import',
    r'from \.engine\.hit_context import': 'from src.combat.hit_context import',
    
    # Core package
    r'from src\.events import': 'from src.core.events import',
    r'from src\.models import': 'from src.core.models import',
    r'from src\.skills import': 'from src.core.skills import',
    r'from src\.state import': 'from src.core.state import',
    r'from \.\.events import': 'from src.core.events import',
    r'from \.\.models import': 'from src.core.models import',
    r'from \.\.skills import': 'from src.core.skills import',
    r'from \.\.state import': 'from src.core.state import',
    
    # Data package (already in src.data, but update relative imports)
    r'from \.\.data\.': 'from src.data.',
    r'from src\.game_data_provider import': 'from src.data.game_data_provider import',
    r'from \.\.game_data_provider import': 'from src.data.game_data_provider import',
    
    # Handlers package
    r'from src\.effect_handlers import': 'from src.handlers.effect_handlers import',
    r'from \.\.effect_handlers import': 'from src.handlers.effect_handlers import',
    
    # Simulation package
    r'from src\.simulation import': 'from src.simulation.combat_simulation import',
    r'from src\.batch_simulation\.batch_runner import': 'from src.simulation.batch_runner import',
    r'from src\.batch_simulation\.aggregators import': 'from src.simulation.aggregators import',
    r'from src\.batch_simulation\.exporters import': 'from src.simulation.exporters import',
    r'from src\.batch_simulation\.telemetry import': 'from src.simulation.telemetry import',
    r'from src\.batch_simulation import': 'from src.simulation import',
    r'from \.\.simulation import': 'from src.simulation.combat_simulation import',
    r'from \.\.batch_simulation\.': 'from src.simulation.',
    
    # Utils package
    r'from src\.item_generator import': 'from src.utils.item_generator import',
    r'from \.\.item_generator import': 'from src.utils.item_generator import',
}

def update_imports_in_file(file_path):
    """Update imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all import mappings
        for old_pattern, new_import in IMPORT_MAPPINGS.items():
            content = re.sub(old_pattern, new_import, content)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Update all Python files in src/ and tests/."""
    base_path = Path(__file__).parent
    
    updated_count = 0
    
    # Update all files in src/
    for py_file in base_path.glob('src/**/*.py'):
        if update_imports_in_file(py_file):
            updated_count += 1
    
    # Update all files in tests/
    for py_file in base_path.glob('tests/**/*.py'):
        if update_imports_in_file(py_file):
            updated_count += 1
    
    # Update root-level scripts
    for py_file in base_path.glob('*.py'):
        if py_file.name != 'update_imports.py':  # Don't update this script
            if update_imports_in_file(py_file):
                updated_count += 1
    
    # Update scripts/ directory
    for py_file in base_path.glob('scripts/**/*.py'):
        if update_imports_in_file(py_file):
            updated_count += 1
    
    print(f"\nTotal files updated: {updated_count}")

if __name__ == '__main__':
    main()
