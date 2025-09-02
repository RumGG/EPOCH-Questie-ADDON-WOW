#!/usr/bin/env python3

"""
Script to find duplicate quests in Questie database
Identifies quests with identical names and compares their data
"""

import re
import json
from collections import defaultdict

def parse_lua_table(text):
    """Parse a Lua table into a Python structure."""
    # This is a simplified parser for the specific format we have
    result = {}
    
    # Find all quest entries like [questId] = {data}
    pattern = r'\[(\d+)\]\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    
    for match in re.finditer(pattern, text):
        quest_id = int(match.group(1))
        quest_data_str = match.group(2)
        
        # Parse the quest data (simplified - just extract what we need)
        # Extract the quest name (first quoted string)
        name_match = re.search(r'"([^"]*)"', quest_data_str)
        quest_name = name_match.group(1) if name_match else f"Quest {quest_id}"
        
        # Store the raw data for comparison
        result[quest_id] = {
            'name': quest_name,
            'raw_data': quest_data_str
        }
    
    return result

def extract_quest_details(raw_data):
    """Extract key details from quest data string."""
    details = {}
    
    # Split by commas but be careful with nested structures
    parts = []
    current = ""
    depth = 0
    
    for char in raw_data:
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
        elif char == ',' and depth == 0:
            parts.append(current.strip())
            current = ""
            continue
        current += char
    if current:
        parts.append(current.strip())
    
    # Field 23 is questFlags (0-indexed would be 22)
    if len(parts) > 22:
        # Extract questFlags value
        flags_str = parts[22].strip()
        try:
            details['questFlags'] = int(flags_str) if flags_str and flags_str != 'nil' else None
        except:
            details['questFlags'] = flags_str
    
    # Field 17 is zone
    if len(parts) > 16:
        zone_str = parts[16].strip()
        try:
            details['zone'] = int(zone_str) if zone_str and zone_str != 'nil' else None
        except:
            details['zone'] = zone_str
            
    return details

def find_duplicates():
    """Main function to find duplicate quests."""
    
    print("Loading quest database...")
    
    # Read the quest database file
    with open("Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse quests
    quests = parse_lua_table(content)
    print(f"Analyzed {len(quests)} quests")
    
    # Build a map of quest names to IDs
    name_to_ids = defaultdict(list)
    
    for quest_id, quest_data in quests.items():
        name = quest_data['name']
        # Skip placeholder entries
        if not name.startswith("[Epoch] Quest "):
            name_to_ids[name].append(quest_id)
    
    # Find duplicates
    duplicate_groups = []
    exact_duplicates = []
    
    for name, ids in name_to_ids.items():
        if len(ids) > 1:
            duplicate_groups.append((name, ids))
    
    # Sort by name for consistent output
    duplicate_groups.sort(key=lambda x: x[0])
    
    print("\n" + "=" * 80)
    print("QUESTS WITH DUPLICATE NAMES:")
    print("=" * 80)
    
    for name, ids in duplicate_groups:
        print(f"\n\"{name}\" - {len(ids)} instances:")
        print("-" * 78)
        
        # Check if raw data is identical
        quest_data_list = []
        for quest_id in ids:
            raw_data = quests[quest_id]['raw_data']
            details = extract_quest_details(raw_data)
            quest_data_list.append({
                'id': quest_id,
                'raw': raw_data,
                'details': details
            })
        
        # Check for exact duplicates
        found_exact = False
        for i in range(len(quest_data_list)):
            for j in range(i + 1, len(quest_data_list)):
                # Compare raw data (ignoring whitespace differences)
                data1 = re.sub(r'\s+', ' ', quest_data_list[i]['raw']).strip()
                data2 = re.sub(r'\s+', ' ', quest_data_list[j]['raw']).strip()
                
                if data1 == data2:
                    if not found_exact:
                        print("  ⚠️  EXACT DUPLICATES FOUND:")
                    found_exact = True
                    id1 = quest_data_list[i]['id']
                    id2 = quest_data_list[j]['id']
                    print(f"      Quest {id1} and {id2} are IDENTICAL - one can be purged")
                    exact_duplicates.append((name, id1, id2))
        
        # Display quest IDs and details
        for data in quest_data_list:
            quest_id = data['id']
            details = data['details']
            print(f"  Quest {quest_id}:")
            if 'questFlags' in details:
                print(f"    questFlags: {details['questFlags']}")
            if 'zone' in details:
                print(f"    Zone: {details['zone']}")
        
        # Check if sequential (likely a quest chain)
        sorted_ids = sorted(ids)
        sequential = all(sorted_ids[i] == sorted_ids[i-1] + 1 for i in range(1, len(sorted_ids)))
        
        if sequential and not found_exact:
            print("  ℹ️  Note: Sequential IDs - likely a quest chain, should be preserved")
    
    # Summary report
    print("\n" + "=" * 80)
    print("SUMMARY REPORT")
    print("=" * 80)
    print(f"Total quests analyzed: {len(quests)}")
    print(f"Quest names with duplicates: {len(duplicate_groups)}")
    print(f"Exact duplicates to purge: {len(exact_duplicates)}")
    
    # List quests to purge
    if exact_duplicates:
        print("\n" + "=" * 80)
        print("RECOMMENDED PURGE LIST:")
        print("=" * 80)
        print("The following quest IDs can be safely removed (keeping the lower ID):")
        
        for name, id1, id2 in exact_duplicates:
            keep_id = min(id1, id2)
            remove_id = max(id1, id2)
            print(f"  REMOVE Quest {remove_id} (duplicate of {keep_id}) - \"{name}\"")
    
    # Special case: Check for our known duplicate
    print("\n" + "=" * 80)
    print("SPECIFIC CASE: Shift into G.E.A.R.")
    print("=" * 80)
    
    if 28725 in quests and 28901 in quests:
        print(f"Quest 28725 exists: {quests[28725]['name']}")
        print(f"Quest 28901 exists: {quests[28901]['name']}")
        
        # Compare raw data
        data1 = re.sub(r'\s+', ' ', quests[28725]['raw_data']).strip()
        data2 = re.sub(r'\s+', ' ', quests[28901]['raw_data']).strip()
        
        if data1 == data2:
            print("✅ Confirmed: 28725 and 28901 are EXACT duplicates")
            print("Recommendation: Remove 28901, keep 28725 (actual quest ID)")
        else:
            print("⚠️  Warning: 28725 and 28901 have the same name but different data")
            print("Further investigation needed")

if __name__ == "__main__":
    find_duplicates()