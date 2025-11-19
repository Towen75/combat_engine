#!/usr/bin/env python3
from src.data.data_parser import parse_all_csvs

try:
    data = parse_all_csvs()
    print(f"Data parsed successfully. Affixes: {len(data['affixes'])}")
    if 'swiftslayer' in data['affixes']:
        print("Swiftslayer affix:", data['affixes']['swiftslayer'])
except Exception as e:
    print(f"Error: {e}")
