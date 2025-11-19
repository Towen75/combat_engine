"""Data exporters for batch simulation results.

Provides JSON and CSV export functionality for analysis and spreadsheet balancing.
"""

import json
import csv
from pathlib import Path
from typing import Any, Dict
from .batch_runner import BatchResult


def export_to_json(batch_result: BatchResult, filepath: str) -> None:
    """Export batch results to JSON format.
    
    Creates a structured JSON file with full hit contexts and statistics
    for programmatic analysis.
    
    Args:
        batch_result: BatchResult to export
        filepath: Output file path
        
    Raises:
        IOError: If file cannot be written
    """
    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = batch_result.to_dict()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)


def export_to_csv(batch_result: BatchResult, filepath: str) -> None:
    """Export batch results to CSV format.
    
    Creates a spreadsheet-friendly CSV file with one row per simulation
    for easy balance analysis in Excel/Google Sheets.
    
    Args:
        batch_result: BatchResult to export
        filepath: Output file path
        
    Raises:
        IOError: If file cannot be written
    """
    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Define CSV columns
    fieldnames = [
        'batch_id',
        'simulation_id',
        'base_seed',
        'winner',
        'remaining_hp',
        'duration',
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Write one row per simulation
        for i in range(batch_result.iterations):
            row = {
                'batch_id': batch_result.batch_id,
                'simulation_id': i,
                'base_seed': batch_result.base_seed + i,
                'winner': batch_result.winners[i] if i < len(batch_result.winners) else '',
                'remaining_hp': batch_result.remaining_hps[i] if i < len(batch_result.remaining_hps) else 0,
                'duration': batch_result.durations[i] if i < len(batch_result.durations) else 0,
            }
            writer.writerow(row)


def export_summary_to_csv(batch_result: BatchResult, filepath: str) -> None:
    """Export aggregated statistics to CSV format.
    
    Creates a summary CSV with DPS and win rate statistics.
    
    Args:
        batch_result: BatchResult to export
        filepath: Output file path
        
    Raises:
        IOError: If file cannot be written
    """
    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write batch metadata
        writer.writerow(['Batch Summary'])
        writer.writerow(['Batch ID', batch_result.batch_id])
        writer.writerow(['Iterations', batch_result.iterations])
        writer.writerow(['Base Seed', batch_result.base_seed])
        writer.writerow([])
        
        # Write DPS statistics
        writer.writerow(['DPS Statistics'])
        writer.writerow(['Metric', 'Value'])
        for key, value in batch_result.dps_stats.items():
            writer.writerow([key, value])
        writer.writerow([])
        
        # Write win rate statistics
        writer.writerow(['Win Rate Statistics'])
        
        # Entity-level stats
        if 'entities' in batch_result.win_rate_stats:
            writer.writerow(['Entity', 'Wins', 'Losses', 'Total Fights', 'Win Rate'])
            for entity_id, stats in batch_result.win_rate_stats['entities'].items():
                writer.writerow([
                    entity_id,
                    stats.get('wins', 0),
                    stats.get('losses', 0),
                    stats.get('total_fights', 0),
                    f"{stats.get('win_rate', 0):.2%}"
                ])
        
        writer.writerow([])
        writer.writerow(['Mean Victory Margin', batch_result.win_rate_stats.get('mean_victory_margin', 0)])
        writer.writerow(['Median Victory Margin', batch_result.win_rate_stats.get('median_victory_margin', 0)])
