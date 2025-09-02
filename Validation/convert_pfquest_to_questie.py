#!/usr/bin/env python3

import re
import os
from datetime import datetime

def parse_pfquest_quests(filepath):
    """Parse pfQuest quest data with proper level extraction"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    quests = {}
    
    # Split by quest entries
    quest_blocks = re.split(r'\n\s*\[(\d+)\]\s*=\s*', content)
    
    for i in range(1, len(quest_blocks), 2):
        quest_id = int(quest_blocks[i])
        quest_data = quest_blocks[i+1]
        
        # Skip removed quests
        if quest_data.strip() == '"_",' or quest_data.strip().startswith('"_"'):
            continue
        
        # Extract the full quest block up to the next quest or end
        block_end = quest_data.find('\n  [')
        if block_end == -1:
            block = quest_data
        else:
            block = quest_data[:block_end]
        
        quest_info = {
            'id': quest_id,
            'level': None,
            'min_level': None,
            'start_npcs': [],
            'end_npcs': [],
            'race': None,
            'pre': None
        }
        
        # Extract level
        level_match = re.search(r'\["lvl"\]\s*=\s*(\d+)', block)
        if level_match:
            quest_info['level'] = int(level_match.group(1))
        
        # Extract min level
        min_match = re.search(r'\["min"\]\s*=\s*(\d+)', block)
        if min_match:
            quest_info['min_level'] = int(min_match.group(1))
        
        # Extract race/faction
        race_match = re.search(r'\["race"\]\s*=\s*(\d+)', block)
        if race_match:
            quest_info['race'] = int(race_match.group(1))
        
        # Extract prerequisite
        pre_match = re.search(r'\["pre"\]\s*=\s*\{\s*(\d+)', block)
        if pre_match:
            quest_info['pre'] = int(pre_match.group(1))
        
        # Extract start NPCs
        start_match = re.search(r'\["start"\]\s*=\s*\{[^}]*\["U"\]\s*=\s*\{([^}]+)\}', block)
        if start_match:
            npc_ids = re.findall(r'\d+', start_match.group(1))
            quest_info['start_npcs'] = [int(npc) for npc in npc_ids]
        
        # Extract end NPCs  
        end_match = re.search(r'\["end"\]\s*=\s*\{[^}]*\["U"\]\s*=\s*\{([^}]+)\}', block)
        if end_match:
            npc_ids = re.findall(r'\d+', end_match.group(1))
            quest_info['end_npcs'] = [int(npc) for npc in npc_ids]
        
        quests[quest_id] = quest_info
    
    return quests

def parse_pfquest_texts(filepath):
    """Parse pfQuest quest text data"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    texts = {}
    
    # Split by quest entries
    quest_blocks = re.split(r'\n\s*\[(\d+)\]\s*=\s*', content)
    
    for i in range(1, len(quest_blocks), 2):
        quest_id = int(quest_blocks[i])
        quest_data = quest_blocks[i+1]
        
        # Extract the full quest block
        block_end = quest_data.find('\n  [')
        if block_end == -1:
            block = quest_data
        else:
            block = quest_data[:block_end]
        
        text_info = {}
        
        # Extract title
        title_match = re.search(r'\["T"\]\s*=\s*"([^"]+(?:\\"[^"]*)*)"', block)
        if title_match:
            text_info['title'] = title_match.group(1).replace('\\"', '"')
        
        # Extract objectives
        obj_match = re.search(r'\["O"\]\s*=\s*"([^"]+(?:\\"[^"]*)*)"', block)
        if obj_match:
            text_info['objectives'] = obj_match.group(1).replace('\\"', '"').replace('\\n', ' ')
        
        # Extract description
        desc_match = re.search(r'\["D"\]\s*=\s*"([^"]+(?:\\"[^"]*)*)"', block)
        if desc_match:
            text_info['description'] = desc_match.group(1).replace('\\"', '"').replace('\\n', ' ')
        
        if text_info:
            texts[quest_id] = text_info
    
    return texts

def convert_faction(race_flag):
    """Convert pfQuest race flag to Questie faction"""
    if not race_flag:
        return 3  # Both factions
    
    # Alliance races: 1 (Human), 4 (Night Elf), 8 (Gnome), 64 (Draenei) = 77
    # 3 (Dwarf) = 3
    # Combined Alliance = 77, 3, etc.
    alliance_flags = [1, 3, 4, 5, 7, 8, 64, 65, 68, 69, 71, 72, 73, 76, 77]
    
    # Horde races: 2 (Orc), 16 (Tauren), 32 (Troll), 128 (Blood Elf) = 178
    # 10 (Undead) = 10
    # Combined Horde = 178, 10, etc.
    horde_flags = [2, 10, 16, 18, 32, 128, 130, 138, 146, 154, 162, 170, 178]
    
    if race_flag in alliance_flags:
        return 2  # Alliance
    elif race_flag in horde_flags:
        return 1  # Horde
    else:
        return 3  # Both factions

def main():
    base_path = "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/"
    
    print("Loading pfQuest-epoch data...")
    pf_quests = parse_pfquest_quests(base_path + "pfQuest-epoch/db/quests-epoch.lua")
    pf_texts = parse_pfquest_texts(base_path + "pfQuest-epoch/db/enUS/quests-epoch.lua")
    
    print("Loading Questie-Epoch data...")
    # Load existing Questie quests to check for duplicates
    questie_quests = {}
    with open(base_path + "Questie/Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        content = f.read()
        for match in re.finditer(r'\[(\d+)\]\s*=\s*\{"([^"]+)"', content):
            questie_quests[int(match.group(1))] = match.group(2)
    
    print(f"\n=== ANALYSIS ===")
    print(f"pfQuest-epoch: {len(pf_quests)} quests")
    print(f"Questie-Epoch: {len(questie_quests)} quests")
    
    # Find quests to add
    missing_quests = []
    update_quests = []
    
    for quest_id, quest_data in pf_quests.items():
        if quest_id in pf_texts:
            if quest_id not in questie_quests:
                missing_quests.append(quest_id)
            elif questie_quests[quest_id].startswith("[Epoch] Quest"):
                update_quests.append(quest_id)
    
    print(f"Missing in Questie: {len(missing_quests)} quests")
    print(f"Placeholder names: {len(update_quests)} quests")
    
    # Generate conversion file
    output_file = base_path + "Questie/pfquest_conversions.lua"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- pfQuest-epoch to Questie-Epoch conversions\n")
        f.write(f"-- Generated on {datetime.now()}\n")
        f.write("-- Review and manually add to epochQuestDB.lua\n\n")
        
        f.write("-- ============================================\n")
        f.write("-- MISSING QUESTS TO ADD (First 50)\n")
        f.write("-- ============================================\n\n")
        
        count = 0
        for quest_id in sorted(missing_quests):
            if count >= 50:
                break
            
            quest = pf_quests[quest_id]
            text = pf_texts.get(quest_id, {})
            
            if not text.get('title'):
                continue
            
            # Build the Questie format entry
            title = text['title'].replace('"', '\\"')
            level = quest['level'] or 1
            min_level = quest['min_level'] or level
            faction = convert_faction(quest['race'])
            
            f.write(f'[{quest_id}] = {{"{title}",')
            
            # Start NPCs
            if quest['start_npcs']:
                f.write('{{' + ','.join(map(str, quest['start_npcs'])) + '}},')
            else:
                f.write('nil,')
            
            # End NPCs
            if quest['end_npcs']:
                f.write('{{' + ','.join(map(str, quest['end_npcs'])) + '}},')
            else:
                f.write('nil,')
            
            # Other fields: requiredSkill, level, questLevel, faction
            f.write(f'nil,{level},nil,{faction},')
            
            # Objectives
            if text.get('objectives'):
                objectives = text['objectives'].replace('"', '\\"')
                f.write(f'{{"{objectives}"}},')
            else:
                f.write('nil,')
            
            # Fill remaining fields
            f.write('nil,nil,nil,nil,')
            
            # Prerequisite quest
            if quest['pre']:
                f.write(f'{quest["pre"]},')
            else:
                f.write('nil,')
            
            # More nil fields
            f.write('nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,0,')
            
            # More nil fields and prerequisite again if exists
            if quest['pre']:
                f.write(f'{quest["pre"]},')
            else:
                f.write('nil,')
            
            f.write('nil,nil,nil,nil,nil},')
            f.write(f' -- Level {level}, pfQuest-epoch\n')
            
            count += 1
            
            print(f"  [{quest_id}] = \"{title}\" (Level {level})")
        
        f.write(f"\n-- Total missing: {len(missing_quests)} quests\n\n")
        
        # Name updates section
        f.write("-- ============================================\n")
        f.write("-- QUESTS WITH PLACEHOLDER NAMES TO UPDATE\n")
        f.write("-- ============================================\n\n")
        
        for quest_id in sorted(update_quests):
            text = pf_texts.get(quest_id, {})
            if text.get('title'):
                current = questie_quests[quest_id]
                new_title = text['title'].replace('"', '\\"')
                f.write(f'-- [{quest_id}] = "{current}" -> "{new_title}"\n')
        
        f.write(f"\n-- Total placeholder names: {len(update_quests)} quests\n")
    
    print(f"\n=== OUTPUT ===")
    print(f"Generated: {output_file}")
    print("\nReview this file and manually add the quests you want to epochQuestDB.lua")
    print("\nNote: NPCs referenced in these quests may also need to be added to epochNpcDB.lua")

if __name__ == "__main__":
    main()