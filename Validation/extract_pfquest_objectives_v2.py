#!/usr/bin/env python3

"""
Extract objective data from pfQuest-epoch database - Version 2
More robust parsing of nested Lua tables
"""

import re
from datetime import datetime

def parse_pfquest_quests():
    """Parse pfQuest quest database with better objective extraction"""
    
    quest_file = "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/pfQuest-epoch/db/quests-epoch.lua"
    text_file = "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/pfQuest-epoch/db/enUS/quests-epoch.lua"
    
    # Read files
    with open(quest_file, 'r', encoding='utf-8') as f:
        quest_content = f.read()
    
    with open(text_file, 'r', encoding='utf-8') as f:
        text_content = f.read()
    
    quests = {}
    
    # Split by quest entries - look for [questId] = {
    entries = re.split(r'(?=\[\d+\]\s*=\s*\{)', quest_content)
    
    for entry in entries:
        if not entry.strip():
            continue
            
        # Extract quest ID
        id_match = re.match(r'\[(\d+)\]\s*=\s*\{', entry)
        if not id_match:
            continue
            
        quest_id = int(id_match.group(1))
        
        quest = {
            'id': quest_id,
            'start_npcs': [],
            'end_npcs': [],
            'objectives': {
                'mobs': [],
                'items': [],
                'objects': []
            },
            'level': 1,
            'race': None,
            'prerequisite': None,
            'next_quest': None
        }
        
        # Extract start NPCs
        if '["start"]' in entry:
            start_section = entry[entry.find('["start"]'):entry.find('},', entry.find('["start"]'))+1]
            if '["U"]' in start_section:
                npcs = re.findall(r'\d+', start_section[start_section.find('["U"]'):])
                quest['start_npcs'] = [int(n) for n in npcs[:5]]  # Limit to first 5
        
        # Extract end NPCs  
        if '["end"]' in entry:
            end_section = entry[entry.find('["end"]'):entry.find('},', entry.find('["end"]'))+1]
            if '["U"]' in end_section:
                npcs = re.findall(r'\d+', end_section[end_section.find('["U"]'):])
                quest['end_npcs'] = [int(n) for n in npcs[:5]]  # Limit to first 5
        
        # Extract objectives - this is the key part
        if '["obj"]' in entry:
            # Find the obj section
            obj_start = entry.find('["obj"]')
            obj_section = entry[obj_start:]
            
            # Find the matching closing brace for obj
            brace_count = 0
            obj_end = 0
            in_obj = False
            for i, char in enumerate(obj_section):
                if char == '{':
                    brace_count += 1
                    if brace_count == 1:
                        in_obj = True
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0 and in_obj:
                        obj_end = i
                        break
            
            obj_content = obj_section[:obj_end+1]
            
            # Extract mobs (U = Units)
            if '["U"]' in obj_content:
                u_start = obj_content.find('["U"]')
                u_section = obj_content[u_start:]
                # Find the { } for this U section
                if '{' in u_section:
                    bracket_start = u_section.find('{')
                    bracket_end = u_section.find('}', bracket_start)
                    mob_str = u_section[bracket_start+1:bracket_end]
                    mob_ids = re.findall(r'\d+', mob_str)
                    for mob_id in mob_ids:
                        quest['objectives']['mobs'].append({'id': int(mob_id), 'count': 1})
            
            # Extract items (I = Items)
            if '["I"]' in obj_content:
                i_start = obj_content.find('["I"]')
                i_section = obj_content[i_start:]
                if '{' in i_section:
                    bracket_start = i_section.find('{')
                    bracket_end = i_section.find('}', bracket_start)
                    item_str = i_section[bracket_start+1:bracket_end]
                    item_ids = re.findall(r'\d+', item_str)
                    for item_id in item_ids:
                        quest['objectives']['items'].append({'id': int(item_id), 'count': 1})
            
            # Extract objects (O = Objects)
            if '["O"]' in obj_content:
                o_start = obj_content.find('["O"]')
                o_section = obj_content[o_start:]
                if '{' in o_section:
                    bracket_start = o_section.find('{')
                    bracket_end = o_section.find('}', bracket_start)
                    obj_str = o_section[bracket_start+1:bracket_end]
                    obj_ids = re.findall(r'\d+', obj_str)
                    for obj_id in obj_ids:
                        quest['objectives']['objects'].append({'id': int(obj_id), 'count': 1})
        
        # Extract level
        level_match = re.search(r'\["lvl"\]\s*=\s*(\d+)', entry)
        if level_match:
            quest['level'] = int(level_match.group(1))
        
        # Extract race (faction)
        race_match = re.search(r'\["race"\]\s*=\s*(\d+)', entry)
        if race_match:
            quest['race'] = int(race_match.group(1))
        
        # Extract prerequisite
        pre_match = re.search(r'\["pre"\]\s*=\s*(\d+)', entry)
        if pre_match:
            quest['prerequisite'] = int(pre_match.group(1))
        
        # Extract next quest
        next_match = re.search(r'\["next"\]\s*=\s*(\d+)', entry)
        if next_match:
            quest['next_quest'] = int(next_match.group(1))
        
        quests[quest_id] = quest
    
    # Parse quest text
    texts = {}
    text_entries = re.split(r'(?=\[\d+\]\s*=\s*\{)', text_content)
    
    for entry in text_entries:
        if not entry.strip():
            continue
            
        id_match = re.match(r'\[(\d+)\]\s*=\s*\{', entry)
        if not id_match:
            continue
            
        quest_id = int(id_match.group(1))
        texts[quest_id] = {}
        
        # Extract title
        title_match = re.search(r'\["T"\]\s*=\s*"([^"]*)"', entry)
        if title_match:
            texts[quest_id]['title'] = title_match.group(1)
        
        # Extract objectives
        obj_match = re.search(r'\["O"\]\s*=\s*"([^"]*)"', entry)
        if obj_match:
            texts[quest_id]['objectives'] = obj_match.group(1)
    
    return quests, texts

def convert_to_questie(quests, texts):
    """Convert to Questie format"""
    
    output = []
    output.append("-- pfQuest-epoch conversion with objective data")
    output.append(f"-- Generated on {datetime.now()}")
    output.append("")
    output.append("pfQuestObjectiveData = {")
    
    converted = 0
    with_objectives = 0
    
    for quest_id in sorted(quests.keys()):
        quest = quests[quest_id]
        text = texts.get(quest_id, {})
        
        if not text.get('title'):
            continue
        
        title = text['title'].replace('"', '\\"')
        level = quest['level']
        
        # Determine faction
        race = quest.get('race', 0)
        if race == 77:
            faction = 2  # Alliance
        elif race == 178:
            faction = 1  # Horde
        else:
            faction = 3  # Both
        
        # Build quest entry
        line = f'  [{quest_id}] = {{"{title}",'
        
        # Start/End NPCs
        if quest['start_npcs']:
            line += '{{' + ','.join(map(str, quest['start_npcs'])) + '}},'
        else:
            line += 'nil,'
            
        if quest['end_npcs']:
            line += '{{' + ','.join(map(str, quest['end_npcs'])) + '}},'
        else:
            line += 'nil,'
        
        # Levels
        line += f'nil,{level},nil,nil,'
        
        # Objectives text
        if text.get('objectives'):
            obj_text = text['objectives'].replace('"', '\\"')
            line += f'{{"{obj_text}"}},nil,'
        else:
            line += 'nil,nil,'
        
        # Objective data (field 10)
        if quest['objectives']['mobs'] or quest['objectives']['items'] or quest['objectives']['objects']:
            with_objectives += 1
            
            # Mobs
            if quest['objectives']['mobs']:
                mob_list = ','.join([f'{{{m["id"]},{m["count"]}}}' for m in quest['objectives']['mobs']])
                mobs = '{{' + mob_list + '}}'
            else:
                mobs = 'nil'
            
            # Objects
            if quest['objectives']['objects']:
                obj_list = ','.join([f'{{{o["id"]},{o["count"]}}}' for o in quest['objectives']['objects']])
                objs = '{{' + obj_list + '}}'
            else:
                objs = 'nil'
            
            # Items
            if quest['objectives']['items']:
                item_list = ','.join([f'{{{i["id"]},{i["count"]}}}' for i in quest['objectives']['items']])
                items = '{{' + item_list + '}}'
            else:
                items = 'nil'
            
            line += f'{{{mobs},{objs},{items}}},'
        else:
            line += 'nil,'
        
        # Prerequisites
        line += 'nil,nil,'
        if quest.get('prerequisite'):
            line += f'{{{quest["prerequisite"]}}},'
        else:
            line += 'nil,'
        
        # Chain fields
        line += 'nil,nil,nil,nil,nil,nil,nil,nil,'
        
        # Next quest
        if quest.get('next_quest'):
            line += f'{quest["next_quest"]},'
        else:
            line += 'nil,'
        
        # Flags
        line += '2,0,'
        
        # Parent quest
        if quest.get('prerequisite'):
            line += f'{quest["prerequisite"]},'
        else:
            line += 'nil,'
        
        # End
        line += 'nil,nil,nil,nil,nil,nil},'
        
        output.append(line)
        converted += 1
    
    output.append('}')
    output.append('')
    output.append(f'-- Total: {converted} quests')
    output.append(f'-- With objectives: {with_objectives}')
    
    return '\n'.join(output), converted, with_objectives

def main():
    print("Extracting pfQuest objective data (v2)...")
    print("=" * 50)
    
    quests, texts = parse_pfquest_quests()
    print(f"Parsed {len(quests)} quests")
    
    # Count objectives
    with_obj = sum(1 for q in quests.values() 
                   if q['objectives']['mobs'] or 
                      q['objectives']['items'] or 
                      q['objectives']['objects'])
    print(f"Quests with objectives: {with_obj}")
    
    # Show samples
    if with_obj > 0:
        print("\nSample quests with objectives:")
        count = 0
        for qid, quest in sorted(quests.items()):
            if quest['objectives']['mobs']:
                title = texts.get(qid, {}).get('title', 'Unknown')
                print(f"  Quest {qid}: {title}")
                print(f"    Mobs: {quest['objectives']['mobs']}")
                count += 1
                if count >= 3:
                    break
    
    # Convert
    output, converted, with_objectives = convert_to_questie(quests, texts)
    
    # Save
    output_file = "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/Questie/pfquest_objectives_v2.lua"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"\nSaved: pfquest_objectives_v2.lua")
    print(f"Converted: {converted}")
    print(f"With objectives: {with_objectives}")

if __name__ == "__main__":
    main()