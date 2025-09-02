#!/usr/bin/env python3

import re
import os
from datetime import datetime

def extract_lua_table(content, table_name):
    """Extract a Lua table from content"""
    pattern = rf'{table_name}\s*=\s*\{{'
    start = re.search(pattern, content)
    if not start:
        return {}
    
    # Simple extraction - find matching braces
    brace_count = 0
    start_idx = start.end() - 1
    end_idx = start_idx
    
    for i in range(start_idx, len(content)):
        if content[i] == '{':
            brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
    
    table_str = content[start_idx:end_idx]
    return parse_lua_table(table_str)

def parse_lua_table(table_str):
    """Parse a Lua table string into a Python dict (simplified)"""
    result = {}
    
    # Extract quest entries [ID] = { ... }
    pattern = r'\[(\d+)\]\s*=\s*(\{[^}]*\}|"[^"]*")'
    matches = re.finditer(pattern, table_str)
    
    for match in matches:
        quest_id = int(match.group(1))
        value = match.group(2)
        
        if value.startswith('"'):
            # String value (placeholder quest)
            result[quest_id] = value.strip('"')
        else:
            # Table value (actual quest data)
            result[quest_id] = value
    
    return result

def load_pfquest_data():
    """Load pfQuest-epoch database files"""
    base_path = "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/pfQuest-epoch/db/"
    
    # Load quest data
    with open(base_path + "quests-epoch.lua", 'r', encoding='utf-8') as f:
        quest_content = f.read()
    
    # Load quest text (English)
    with open(base_path + "enUS/quests-epoch.lua", 'r', encoding='utf-8') as f:
        text_content = f.read()
    
    # Parse quest IDs and basic info
    quests = {}
    quest_pattern = r'\[(\d+)\]\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    
    for match in re.finditer(quest_pattern, quest_content):
        quest_id = int(match.group(1))
        quest_data = match.group(2)
        
        # Skip removed quests
        if '"_"' in quest_data or '= "_"' in quest_content[match.start():match.end()]:
            continue
            
        quests[quest_id] = {
            'raw': quest_data,
            'level': None,
            'start_npcs': [],
            'end_npcs': []
        }
        
        # Extract level
        level_match = re.search(r'\["lvl"\]\s*=\s*(\d+)', quest_data)
        if level_match:
            quests[quest_id]['level'] = int(level_match.group(1))
        
        # Extract start NPCs
        start_match = re.search(r'\["start"\]\s*=\s*\{[^}]*\["U"\]\s*=\s*\{([^}]+)\}', quest_data)
        if start_match:
            npc_ids = re.findall(r'\d+', start_match.group(1))
            quests[quest_id]['start_npcs'] = [int(npc) for npc in npc_ids]
        
        # Extract end NPCs
        end_match = re.search(r'\["end"\]\s*=\s*\{[^}]*\["U"\]\s*=\s*\{([^}]+)\}', quest_data)
        if end_match:
            npc_ids = re.findall(r'\d+', end_match.group(1))
            quests[quest_id]['end_npcs'] = [int(npc) for npc in npc_ids]
    
    # Parse quest text
    texts = {}
    text_pattern = r'\[(\d+)\]\s*=\s*\{([^}]+(?:\[[^\]]*\][^}]*)*)\}'
    
    for match in re.finditer(text_pattern, text_content):
        quest_id = int(match.group(1))
        text_data = match.group(2)
        
        texts[quest_id] = {}
        
        # Extract title
        title_match = re.search(r'\["T"\]\s*=\s*"([^"]+)"', text_data)
        if title_match:
            texts[quest_id]['title'] = title_match.group(1)
        
        # Extract objectives
        obj_match = re.search(r'\["O"\]\s*=\s*"([^"]+)"', text_data)
        if obj_match:
            texts[quest_id]['objectives'] = obj_match.group(1)
    
    return quests, texts

def load_questie_data():
    """Load Questie-Epoch database files"""
    base_path = "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/Questie/Database/Epoch/"
    
    # Load quest data
    with open(base_path + "epochQuestDB.lua", 'r', encoding='utf-8') as f:
        content = f.read()
    
    quests = {}
    # Pattern for Questie quest entries
    pattern = r'\[(\d+)\]\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    
    for match in re.finditer(pattern, content):
        quest_id = int(match.group(1))
        quest_data = match.group(2)
        
        # Extract quest name (first field)
        name_match = re.search(r'^"([^"]+)"', quest_data)
        if name_match:
            quests[quest_id] = {
                'name': name_match.group(1),
                'raw': quest_data
            }
    
    return quests

def main():
    print("Loading pfQuest-epoch data...")
    pf_quests, pf_texts = load_pfquest_data()
    
    print("Loading Questie-Epoch data...")
    questie_quests = load_questie_data()
    
    print(f"\n=== ANALYSIS RESULTS ===")
    print(f"pfQuest-epoch has {len(pf_quests)} quests")
    print(f"Questie-Epoch has {len(questie_quests)} quests")
    
    # Find missing quests
    missing_in_questie = []
    placeholder_names = []
    
    for quest_id in pf_quests:
        if quest_id not in questie_quests:
            if quest_id in pf_texts and 'title' in pf_texts[quest_id]:
                missing_in_questie.append(quest_id)
        elif questie_quests[quest_id]['name'].startswith("[Epoch] Quest"):
            if quest_id in pf_texts and 'title' in pf_texts[quest_id]:
                placeholder_names.append(quest_id)
    
    print(f"Missing in Questie: {len(missing_in_questie)} quests")
    print(f"Placeholder names in Questie: {len(placeholder_names)} quests")
    
    # Generate missing quests file
    print("\n=== MISSING QUESTS (First 30) ===")
    output_path = "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/Questie/"
    
    with open(output_path + "pfquest_missing_quests.txt", 'w') as f:
        f.write(f"-- Missing quests from pfQuest-epoch\n")
        f.write(f"-- Generated on {datetime.now()}\n\n")
        
        count = 0
        for quest_id in sorted(missing_in_questie)[:30]:
            if quest_id in pf_texts:
                title = pf_texts[quest_id].get('title', 'Unknown')
                level = pf_quests[quest_id].get('level', '?')
                objectives = pf_texts[quest_id].get('objectives', '')
                
                print(f"  [{quest_id}] = \"{title}\" (Level {level})")
                
                # Generate Questie format
                start_npcs = pf_quests[quest_id]['start_npcs']
                end_npcs = pf_quests[quest_id]['end_npcs']
                
                f.write(f'[{quest_id}] = {{"{title}",')
                
                if start_npcs:
                    f.write('{{' + ','.join(map(str, start_npcs)) + '}},')
                else:
                    f.write('nil,')
                
                if end_npcs:
                    f.write('{{' + ','.join(map(str, end_npcs)) + '}},')
                else:
                    f.write('nil,')
                
                f.write(f'nil,{level or 1},nil,nil,')
                
                if objectives:
                    f.write('{"' + objectives.replace('"', '\\"') + '"},')
                else:
                    f.write('nil,')
                
                f.write('nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,0,nil,nil,nil,nil,nil,nil},')
                f.write(' -- From pfQuest-epoch\n')
                
                count += 1
    
    # Generate name updates file
    print("\n=== PLACEHOLDER NAME UPDATES (First 30) ===")
    
    with open(output_path + "pfquest_name_updates.txt", 'w') as f:
        f.write(f"-- Quest name updates from pfQuest-epoch\n")
        f.write(f"-- Generated on {datetime.now()}\n\n")
        
        count = 0
        for quest_id in sorted(placeholder_names)[:30]:
            if quest_id in pf_texts:
                current_name = questie_quests[quest_id]['name']
                new_name = pf_texts[quest_id].get('title', 'Unknown')
                
                print(f"  [{quest_id}] = \"{current_name}\" -> \"{new_name}\"")
                
                f.write(f"-- [{quest_id}] = \"{current_name}\" -> \"{new_name}\"\n")
                count += 1
    
    print(f"\n=== FILES GENERATED ===")
    print(f"1. pfquest_missing_quests.txt - {len(missing_in_questie)} missing quests (showing first 30)")
    print(f"2. pfquest_name_updates.txt - {len(placeholder_names)} quests with placeholder names (showing first 30)")

if __name__ == "__main__":
    main()