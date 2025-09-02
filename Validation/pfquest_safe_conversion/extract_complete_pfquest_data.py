#!/usr/bin/env python3
"""
Extract ALL available data from pfQuest converted quests
Including NPCs that need to be created and quest objectives
"""

import re
from typing import Dict, Set, List, Tuple
import json

def extract_all_quest_data(quest_file: str):
    """Extract comprehensive data from converted quests"""
    
    quests = {}
    all_npcs = {}
    all_items = set()
    all_objects = set()
    
    with open(quest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse each quest entry
    quest_pattern = r'\[(\d+)\]\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    
    for match in re.finditer(quest_pattern, content):
        quest_id = int(match.group(1))
        quest_data = match.group(2)
        
        # Split into fields
        fields = []
        current = ""
        depth = 0
        in_string = False
        
        for char in quest_data:
            if char == '"' and (not current or current[-1] != '\\'):
                in_string = not in_string
            
            if not in_string:
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                elif char == ',' and depth == 0:
                    fields.append(current.strip())
                    current = ""
                    continue
            
            current += char
        
        if current.strip():
            fields.append(current.strip())
        
        # Extract quest name
        quest_name = fields[0].strip('"') if fields else "Unknown Quest"
        
        # Extract NPCs from startedBy (field 2)
        start_npcs = []
        if len(fields) > 1 and fields[1] != 'nil':
            npc_matches = re.findall(r'\{(\d+)\}', fields[1])
            start_npcs = [int(npc) for npc in npc_matches]
            
            # Add to NPC list
            for npc_id in start_npcs:
                if npc_id not in all_npcs:
                    all_npcs[npc_id] = {
                        'id': npc_id,
                        'name': f"Quest Giver {npc_id}",  # Placeholder
                        'quests_start': [],
                        'quests_end': []
                    }
                all_npcs[npc_id]['quests_start'].append(quest_id)
        
        # Extract NPCs from finishedBy (field 3)
        end_npcs = []
        if len(fields) > 2 and fields[2] != 'nil':
            npc_matches = re.findall(r'\{(\d+)\}', fields[2])
            end_npcs = [int(npc) for npc in npc_matches]
            
            # Add to NPC list
            for npc_id in end_npcs:
                if npc_id not in all_npcs:
                    all_npcs[npc_id] = {
                        'id': npc_id,
                        'name': f"Quest Turn-in {npc_id}",  # Placeholder
                        'quests_start': [],
                        'quests_end': []
                    }
                all_npcs[npc_id]['quests_end'].append(quest_id)
        
        # Extract quest text (field 8) to look for objective hints
        quest_text = ""
        if len(fields) > 7:
            quest_text = fields[7].strip('"')
        
        # Try to extract objectives from quest text
        objectives_hints = {
            'kill': [],
            'collect': [],
            'explore': []
        }
        
        # Look for kill patterns
        kill_patterns = [
            r'[Kk]ill (\d+) ([A-Z][a-z]+ ?[A-Z]?[a-z]*)',
            r'[Ss]lay (\d+) ([A-Z][a-z]+ ?[A-Z]?[a-z]*)',
            r'[Dd]efeat (\d+) ([A-Z][a-z]+ ?[A-Z]?[a-z]*)',
        ]
        
        for pattern in kill_patterns:
            matches = re.findall(pattern, quest_text)
            for count, mob in matches:
                objectives_hints['kill'].append(f"{count} {mob}")
        
        # Look for collect patterns
        collect_patterns = [
            r'[Cc]ollect (\d+) ([A-Z][a-z]+ ?[A-Z]?[a-z]*)',
            r'[Gg]ather (\d+) ([A-Z][a-z]+ ?[A-Z]?[a-z]*)',
            r'[Bb]ring.* (\d+) ([A-Z][a-z]+ ?[A-Z]?[a-z]*)',
        ]
        
        for pattern in collect_patterns:
            matches = re.findall(pattern, quest_text)
            for count, item in matches:
                objectives_hints['collect'].append(f"{count} {item}")
        
        quests[quest_id] = {
            'id': quest_id,
            'name': quest_name,
            'start_npcs': start_npcs,
            'end_npcs': end_npcs,
            'text': quest_text,
            'objective_hints': objectives_hints,
            'level': fields[4] if len(fields) > 4 else 'nil',
            'min_level': fields[3] if len(fields) > 3 else 'nil'
        }
    
    return quests, all_npcs

def create_npc_stubs(npcs: Dict, existing_npc_file: str):
    """Create NPC stub entries for missing NPCs"""
    
    # Load existing NPCs
    existing_npcs = set()
    with open(existing_npc_file, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'\s*\[(\d+)\]', line)
            if match:
                existing_npcs.add(int(match.group(1)))
    
    # Filter to only missing NPCs
    missing_npcs = {npc_id: data for npc_id, data in npcs.items() 
                   if npc_id not in existing_npcs}
    
    print(f"\nCreating stubs for {len(missing_npcs)} missing NPCs")
    
    # Generate NPC stub entries
    npc_stubs = []
    for npc_id, data in sorted(missing_npcs.items()):
        # Determine NPC type based on quests
        npc_type = ""
        if data['quests_start'] and data['quests_end']:
            npc_type = "Quest Giver & Turn-in"
        elif data['quests_start']:
            npc_type = "Quest Giver"
        elif data['quests_end']:
            npc_type = "Quest Turn-in"
        
        # Build the NPC entry (15 fields)
        npc_entry = f'[{npc_id}] = {{'
        npc_entry += f'"{npc_type} {npc_id}",'  # Name
        npc_entry += 'nil,'  # minLevelHealth
        npc_entry += 'nil,'  # maxLevelHealth  
        npc_entry += '1,'    # minLevel
        npc_entry += '60,'   # maxLevel
        npc_entry += '0,'    # rank (0=normal)
        npc_entry += 'nil,'  # spawns (no coordinates yet)
        npc_entry += 'nil,'  # waypoints
        npc_entry += '0,'    # zoneID (unknown)
        
        # questStarts
        if data['quests_start']:
            npc_entry += '{' + ','.join(str(q) for q in data['quests_start']) + '},'
        else:
            npc_entry += 'nil,'
        
        # questEnds
        if data['quests_end']:
            npc_entry += '{' + ','.join(str(q) for q in data['quests_end']) + '},'
        else:
            npc_entry += 'nil,'
        
        npc_entry += 'nil,'  # factionID
        npc_entry += '"AH",' # friendlyToFaction (both for now)
        npc_entry += f'"{npc_type}",' # subName
        npc_entry += '2'     # npcFlags (2=questgiver)
        npc_entry += f'}}, -- pfQuest stub'
        
        npc_stubs.append(npc_entry)
    
    return npc_stubs

def analyze_objective_patterns(quests: Dict):
    """Analyze quest text to find objective patterns"""
    
    print("\n=== OBJECTIVE PATTERN ANALYSIS ===")
    
    quests_with_kill = 0
    quests_with_collect = 0
    quests_with_hints = 0
    
    for quest_id, quest in quests.items():
        if quest['objective_hints']['kill']:
            quests_with_kill += 1
        if quest['objective_hints']['collect']:
            quests_with_collect += 1
        if quest['objective_hints']['kill'] or quest['objective_hints']['collect']:
            quests_with_hints += 1
    
    print(f"Quests with kill objectives detected: {quests_with_kill}")
    print(f"Quests with collect objectives detected: {quests_with_collect}")
    print(f"Total quests with objective hints: {quests_with_hints}/{len(quests)}")
    
    # Show some examples
    print("\nExample objective hints found:")
    count = 0
    for quest_id, quest in quests.items():
        if quest['objective_hints']['kill'] or quest['objective_hints']['collect']:
            print(f"\nQuest {quest_id}: {quest['name']}")
            if quest['objective_hints']['kill']:
                print(f"  Kill: {quest['objective_hints']['kill']}")
            if quest['objective_hints']['collect']:
                print(f"  Collect: {quest['objective_hints']['collect']}")
            count += 1
            if count >= 5:
                break

def main():
    print("="*70)
    print("EXTRACTING COMPLETE PFQUEST DATA")
    print("="*70)
    
    # Extract all data
    quests, npcs = extract_all_quest_data('pfquest_properly_converted_FIXED.lua')
    
    print(f"\nExtracted data:")
    print(f"  Quests: {len(quests)}")
    print(f"  NPCs referenced: {len(npcs)}")
    
    # Create NPC stubs
    npc_stubs = create_npc_stubs(npcs, 'epochNpcDB.lua')
    
    # Write NPC stubs to file
    with open('pfquest_npcs_to_add.lua', 'w', encoding='utf-8') as f:
        f.write('-- Missing NPCs from pfQuest quests\n')
        f.write('-- These are stub entries that need coordinates\n\n')
        f.write('pfQuestNPCs = {\n')
        for stub in npc_stubs:
            f.write(f'  {stub}\n')
        f.write('}\n')
    
    print(f"\nWrote {len(npc_stubs)} NPC stubs to: pfquest_npcs_to_add.lua")
    
    # Analyze objective patterns
    analyze_objective_patterns(quests)
    
    # Write quest analysis
    with open('pfquest_quest_analysis.json', 'w') as f:
        json.dump({
            'total_quests': len(quests),
            'total_npcs': len(npcs),
            'missing_npcs': len(npc_stubs),
            'sample_quests': dict(list(quests.items())[:10])
        }, f, indent=2)
    
    print("\nQuest analysis written to: pfquest_quest_analysis.json")
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"""
✅ Extracted from pfQuest:
  - {len(quests)} quest entries with names and NPCs
  - {len(npcs)} unique NPCs referenced
  - {len(npc_stubs)} NPCs need to be added to our database

📝 Files created:
  - pfquest_npcs_to_add.lua - NPC stubs ready to merge
  - pfquest_quest_analysis.json - Detailed analysis

⚠️ Limitations:
  - NPC coordinates unknown (need in-game collection)
  - Objective mob/item IDs missing (need manual mapping)
  - Quest text hints found but not actionable without IDs
""")

if __name__ == "__main__":
    main()