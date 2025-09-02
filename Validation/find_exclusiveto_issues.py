#!/usr/bin/env python3

"""
Find quests with numbers in the exclusiveTo field (position 16)
"""

import re

def find_exclusiveto_issues():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    issues = []
    
    for i, line in enumerate(lines, 1):
        if not line.strip().startswith('[') or '=' not in line:
            continue
            
        # Skip comments and empty lines
        if line.strip().startswith('--'):
            continue
            
        # Look for quest entries
        quest_match = re.search(r'\[(\d+)\]', line)
        if quest_match:
            quest_id = quest_match.group(1)
            
            # Split by commas to count fields
            # We need to be careful with nested structures
            parts = line.split('=', 1)[1]
            
            # Check if position 16 (exclusiveTo) has a number instead of nil or array
            # Pattern: 5 nils, then a number, then nil
            if re.search(r',nil,nil,nil,nil,nil,(\d+),nil,', parts):
                match = re.search(r',nil,nil,nil,nil,nil,(\d+),nil,', parts)
                zone_id = match.group(1)
                issues.append((quest_id, i, zone_id))
                print(f"Quest {quest_id} (line {i}): exclusiveTo has zone ID {zone_id} instead of nil")
    
    print(f"\n✅ Found {len(issues)} quests with exclusiveTo issues")
    return issues

if __name__ == "__main__":
    find_exclusiveto_issues()