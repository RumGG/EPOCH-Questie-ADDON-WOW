#!/usr/bin/env python3
"""
Enhanced pfQuest to Questie conversion that properly extracts objective data
Fixes the missing mob/item/object requirements
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Any

def parse_lua_table(text: str) -> Any:
    """Parse a Lua table into Python structure"""
    # Convert Lua table to JSON-like format
    text = text.strip()
    if text == 'nil':
        return None
    
    # Handle simple values
    if not text.startswith('{'):
        return text.strip('"')
    
    # For complex parsing, we need to handle nested tables
    # This is a simplified parser for the structures we expect
    result = {}
    
    # Check if it's an array-like table {{...},{...}}
    if text.startswith('{{'):
        # Parse as array of arrays
        items = []
        current = ""
        depth = 0
        
        for char in text[1:-1]:  # Skip outer braces
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0 and current:
                    items.append(current + '}')
                    current = ""
                    continue
            if depth > 0:
                current += char
        
        return items
    
    # Parse key-value pairs for quest data
    if '["' in text:
        # pfQuest format with ["key"] = value
        matches = re.findall(r'\["([^"]+)"\]\s*=\s*([^,}]+)', text)
        for key, value in matches:
            # Clean up the value
            value = value.strip()
            if value.startswith('{') and value.endswith('}'):
                result[key] = parse_lua_table(value)
            elif value.startswith('"') and value.endswith('"'):
                result[key] = value[1:-1]
            elif value == 'true':
                result[key] = True
            elif value == 'false':
                result[key] = False
            elif value == 'nil':
                result[key] = None
            else:
                try:
                    result[key] = int(value)
                except:
                    result[key] = value
    
    return result if result else text

def extract_objectives_from_pfquest(quest_data: Dict) -> str:
    """
    Extract and convert pfQuest objective data to Questie format
    Questie format: {{{mobId,count,"name"},...},{{objectId,count}},{{itemId,count}}}
    """
    creatures = []
    objects = []
    items = []
    
    # Check if quest_data has 'obj' field (pfQuest objective data)
    if 'obj' in quest_data:
        obj = quest_data['obj']
        
        # U = Units/NPCs to kill
        if 'U' in obj and obj['U']:
            for npc_id, count in obj['U'].items():
                # Try to get NPC name from the quest text if available
                npc_name = f"Mob {npc_id}"  # Default name
                creatures.append(f"{{{npc_id},{count},\"{npc_name}\"}}")
        
        # O = Objects to interact with
        if 'O' in obj and obj['O']:
            for obj_id, count in obj['O'].items():
                objects.append(f"{{{obj_id},{count}}}")
        
        # I = Items to collect
        if 'I' in obj and obj['I']:
            for item_id, count in obj['I'].items():
                items.append(f"{{{item_id},{count}}}")
    
    # Also try to parse from objectives text
    if 'O' in quest_data and quest_data['O']:
        obj_text = quest_data['O']
        
        # Common patterns in objective text
        kill_patterns = [
            r'Kill (\d+) (.+?)(?:\.|,|$)',
            r'Slay (\d+) (.+?)(?:\.|,|$)',
            r'Defeat (\d+) (.+?)(?:\.|,|$)',
            r'Destroy (\d+) (.+?)(?:\.|,|$)'
        ]
        
        collect_patterns = [
            r'Collect (\d+) (.+?)(?:\.|,|$)',
            r'Gather (\d+) (.+?)(?:\.|,|$)',
            r'Obtain (\d+) (.+?)(?:\.|,|$)',
            r'Bring .* (\d+) (.+?)(?:\.|,|$)'
        ]
        
        # Try to extract from text if we don't have structured data
        if not creatures and not items:
            for pattern in kill_patterns:
                matches = re.findall(pattern, obj_text, re.IGNORECASE)
                for count, mob_name in matches:
                    # This is a guess - we don't have the actual mob ID
                    # But it's better than nothing for display purposes
                    creatures.append(f"{{nil,{count},\"{mob_name}\"}}")
            
            for pattern in collect_patterns:
                matches = re.findall(pattern, obj_text, re.IGNORECASE)
                for count, item_name in matches:
                    items.append(f"{{nil,{count},\"{item_name}\"}}")
    
    # Build the final objectives structure
    if creatures or objects or items:
        creature_str = "{{" + ",".join(creatures) + "}}" if creatures else "nil"
        object_str = "{{" + ",".join(objects) + "}}" if objects else "nil"
        item_str = "{{" + ",".join(items) + "}}" if items else "nil"
        return f"{{{creature_str},{object_str},{item_str}}}"
    
    return "nil"

def find_pfquest_databases():
    """Find pfQuest database files"""
    import os
    import glob
    
    # Common locations for pfQuest data
    search_paths = [
        "/Users/*/Library/CloudStorage/Dropbox/**/pfquest*/**/*.lua",
        "/Users/*/Documents/**/pfquest*/**/*.lua",
        "/Users/*/Downloads/**/pfquest*/**/*.lua",
        "/Users/*/Desktop/**/pfquest*/**/*.lua"
    ]
    
    quest_files = []
    for pattern in search_paths:
        found = glob.glob(pattern, recursive=True)
        for f in found:
            if 'quest' in f.lower() and 'epoch' in f.lower():
                quest_files.append(f)
    
    return quest_files

def load_pfquest_data(filepath: str) -> Dict[int, Dict]:
    """Load pfQuest database file"""
    quests = {}
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
        # Find quest entries in pfQuest format
        # Format: [questId] = { ["T"] = "Title", ["O"] = "Objectives", ... }
        pattern = r'\[(\d+)\]\s*=\s*(\{[^}]+(?:\{[^}]+\}[^}]+)*\})'
        matches = re.findall(pattern, content)
        
        for quest_id, quest_data in matches:
            try:
                parsed = parse_lua_table(quest_data)
                if parsed:
                    quests[int(quest_id)] = parsed
            except:
                continue
    
    return quests

def convert_to_questie_format(quest_id: int, pfquest_data: Dict) -> str:
    """Convert pfQuest entry to Questie format with proper objectives"""
    
    # Initialize 30 fields with nil
    fields = ['nil'] * 30
    
    # Field 1: Quest name
    if 'T' in pfquest_data:
        fields[0] = f'"{pfquest_data["T"]}"'
    
    # Field 2: startedBy - NPCs that give the quest
    if 'start' in pfquest_data:
        start = pfquest_data['start']
        if isinstance(start, list):
            fields[1] = "{{" + ",".join(str(s) for s in start) + "}}"
        elif start:
            fields[1] = f"{{{{{start}}}}}"
    
    # Field 3: finishedBy - NPCs for turn-in
    if 'end' in pfquest_data:
        end = pfquest_data['end']
        if isinstance(end, list):
            fields[2] = "{{" + ",".join(str(e) for e in end) + "}}"
        elif end:
            fields[2] = f"{{{{{end}}}}}"
    
    # Field 4: requiredLevel
    if 'min' in pfquest_data:
        fields[3] = str(pfquest_data['min'])
    
    # Field 5: questLevel
    if 'lvl' in pfquest_data:
        fields[4] = str(pfquest_data['lvl'])
    
    # Field 6: requiredRaces
    if 'race' in pfquest_data:
        race = pfquest_data['race']
        # Convert pfQuest race to Questie format
        if race == 77:  # Alliance
            fields[5] = '77'
        elif race == 178:  # Horde
            fields[5] = '178'
    
    # Field 8: objectivesText
    if 'O' in pfquest_data:
        fields[7] = f'{{"{pfquest_data["O"]}"}}'
    
    # Field 10: OBJECTIVES - The critical field!
    objectives = extract_objectives_from_pfquest(pfquest_data)
    fields[9] = objectives
    
    # Field 12: preQuestGroup (prerequisites)
    if 'pre' in pfquest_data:
        pre = pfquest_data['pre']
        if isinstance(pre, list):
            fields[11] = "{" + ",".join(str(p) for p in pre) + "}"
        elif pre:
            fields[11] = f"{{{pre}}}"
    
    # Field 17: zoneOrSort
    if 'zone' in pfquest_data:
        fields[16] = str(pfquest_data['zone'])
    
    # Field 22: nextQuestInChain
    if 'next' in pfquest_data:
        fields[21] = str(pfquest_data['next'])
    
    # Build the final entry
    return f"[{quest_id}] = {{{','.join(fields)}}}"

def main():
    """Main conversion process"""
    print("=== Enhanced pfQuest to Questie Converter ===")
    print("Now with proper objective extraction!\n")
    
    # Try to find pfQuest databases
    print("Searching for pfQuest database files...")
    pfquest_files = find_pfquest_databases()
    
    if not pfquest_files:
        print("No pfQuest database files found.")
        print("\nTrying to parse from existing converted file...")
        
        # Parse the already converted file to extract what we can
        converted_file = "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/Questie/pfquest_safe_conversion/pfquest_properly_converted.lua"
        
        if os.path.exists(converted_file):
            with open(converted_file, 'r') as f:
                content = f.read()
                
            # Extract quests and try to identify objective patterns
            print(f"Analyzing {converted_file}...")
            
            # For now, let's focus on fixing the existing quests with known objectives
            # from the quest text
            fixes = []
            
            # Known gnome quests that need objectives
            gnome_fixes = {
                28901: {
                    'objectives': '{{{46837,10,"Underfed Trogg"}},nil,nil}',
                    'comment': 'Kill 10 Underfed Troggs'
                },
                28902: {
                    'objectives': '{{{46839,8,"Irradiated Ooze"},{46838,4,"Infected Gnome"}},nil,nil}',
                    'comment': 'Kill 8 Irradiated Oozes and 4 Infected Gnomes'
                }
            }
            
            for quest_id, fix_data in gnome_fixes.items():
                fixes.append(f"-- Quest {quest_id}: {fix_data['comment']}")
                fixes.append(f"-- UPDATE: Set field 10 (objectives) to: {fix_data['objectives']}")
            
            print(f"\nGenerated {len(gnome_fixes)} quest fixes")
            
            # Save the fixes
            with open("objective_fixes.lua", 'w') as f:
                f.write("-- Objective fixes for quests with missing mob data\n")
                f.write("-- Apply these to epochQuestDB.lua\n\n")
                for fix in fixes:
                    f.write(fix + "\n")
            
            print("Fixes saved to objective_fixes.lua")
    
    else:
        print(f"Found {len(pfquest_files)} pfQuest database files:")
        for f in pfquest_files[:5]:
            print(f"  - {f}")
        
        # Load and convert
        all_quests = {}
        for filepath in pfquest_files:
            quests = load_pfquest_data(filepath)
            all_quests.update(quests)
        
        print(f"\nLoaded {len(all_quests)} quests from pfQuest")
        
        # Convert with objectives
        converted = []
        quests_with_objectives = 0
        
        for quest_id, quest_data in sorted(all_quests.items()):
            converted_entry = convert_to_questie_format(quest_id, quest_data)
            converted.append(converted_entry)
            
            if 'obj' in quest_data:
                quests_with_objectives += 1
        
        print(f"Converted {len(converted)} quests")
        print(f"Quests with objective data: {quests_with_objectives}")
        
        # Save the converted data
        with open("pfquest_converted_with_objectives.lua", 'w') as f:
            f.write("-- pfQuest to Questie conversion WITH objective data\n")
            f.write("local epochQuestDB = {}\n\n")
            for entry in converted:
                f.write(entry + "\n")
            f.write("\nreturn epochQuestDB\n")
        
        print("\nConversion complete! Saved to pfquest_converted_with_objectives.lua")

if __name__ == "__main__":
    import os
    main()