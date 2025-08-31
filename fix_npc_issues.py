#!/usr/bin/env python3
"""
Fix NPC database issues:
1. Find duplicate NPC IDs
2. Fix coordinate format issues (triple-nested braces)
"""

import re
from collections import defaultdict

def analyze_npc_database():
    """Analyze NPC database for issues."""
    
    print("="*60)
    print("Analyzing NPC Database Issues")
    print("="*60)
    
    with open('Database/Epoch/epochNpcDB.lua', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Track NPCs
    npcs = {}
    duplicates = defaultdict(list)
    coord_issues = []
    
    for i, line in enumerate(lines, 1):
        # Find NPC entries
        match = re.match(r'^\[(\d+)\] = \{(.+)\}', line.strip())
        if match:
            npc_id = int(match.group(1))
            data = match.group(2)
            
            # Check for duplicate IDs
            if npc_id in npcs:
                duplicates[npc_id].append((i, line.strip()[:100]))
                duplicates[npc_id].append((npcs[npc_id][0], npcs[npc_id][1][:100]))
            else:
                npcs[npc_id] = (i, line.strip())
            
            # Check for triple-nested coordinate braces {{{x,y}}}
            if '{{{' in data:
                coord_issues.append((i, npc_id, line.strip()[:100]))
    
    # Report duplicates
    if duplicates:
        print(f"\n❌ Found {len(duplicates)} duplicate NPC IDs:")
        for npc_id, occurrences in sorted(duplicates.items()):
            print(f"\n  NPC ID {npc_id} appears {len(occurrences)} times:")
            seen = set()
            for line_num, content in occurrences:
                if line_num not in seen:
                    print(f"    Line {line_num}: {content}...")
                    seen.add(line_num)
    
    # Report coordinate issues
    if coord_issues:
        print(f"\n⚠️  Found {len(coord_issues)} NPCs with triple-nested coordinates:")
        for line_num, npc_id, content in coord_issues[:10]:
            print(f"  Line {line_num} (NPC {npc_id}): {content}...")
        if len(coord_issues) > 10:
            print(f"  ... and {len(coord_issues) - 10} more")
    
    return duplicates, coord_issues

def fix_coordinate_format():
    """Fix triple-nested coordinate braces."""
    
    print("\n" + "="*60)
    print("Fixing Coordinate Format Issues")
    print("="*60)
    
    with open('Database/Epoch/epochNpcDB.lua', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes = 0
    for i, line in enumerate(lines):
        # Fix triple-nested braces in coordinates
        # Change {[zone]={{{x,y}}}} to {[zone]={{x,y}}}
        if '{{{' in line:
            original = line
            # Replace {{{ with {{
            line = re.sub(r'\{\{\{(\d+\.?\d*),(\d+\.?\d*)\}\}\}', r'{{\1,\2}}', line)
            if line != original:
                lines[i] = line
                fixes += 1
    
    if fixes > 0:
        with open('Database/Epoch/epochNpcDB.lua', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"✅ Fixed {fixes} coordinate format issues")
    else:
        print("✅ No coordinate format issues found")
    
    return fixes

def suggest_new_ids(duplicates):
    """Suggest new IDs for duplicates."""
    
    print("\n" + "="*60)
    print("Suggested Fixes for Duplicate NPCs")
    print("="*60)
    
    # Find highest NPC ID to suggest new ones
    with open('Database/Epoch/epochNpcDB.lua', 'r', encoding='utf-8') as f:
        content = f.read()
    
    max_id = 0
    for match in re.finditer(r'\[(\d+)\]', content):
        npc_id = int(match.group(1))
        if 45000 <= npc_id <= 50000:  # Epoch range
            max_id = max(max_id, npc_id)
    
    next_id = max_id + 1
    
    print(f"\nHighest Epoch NPC ID found: {max_id}")
    print(f"Suggesting new IDs starting from: {next_id}")
    
    for npc_id in sorted(duplicates.keys()):
        print(f"\n  NPC {npc_id} duplicates:")
        print(f"    Keep first occurrence, change others to {next_id}, {next_id+1}, etc.")
        next_id += len(duplicates[npc_id]) - 1

def main():
    # Analyze issues
    duplicates, coord_issues = analyze_npc_database()
    
    # Fix coordinate issues automatically
    if coord_issues:
        fix_coordinate_format()
    
    # Suggest fixes for duplicates
    if duplicates:
        suggest_new_ids(duplicates)
        print("\n⚠️  Duplicate IDs need manual fixing:")
        print("  1. Decide which NPC should keep the ID")
        print("  2. Assign new IDs to the others")
        print("  3. Update any quest references to those NPCs")
    
    print("\n" + "="*60)
    if not duplicates and not coord_issues:
        print("✅ NPC database is clean!")
    else:
        print("⚠️  Issues found - see above for details")
    print("="*60)

if __name__ == "__main__":
    main()