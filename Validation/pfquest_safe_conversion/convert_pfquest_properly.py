#!/usr/bin/env python3
"""
Proper conversion of pfQuest data to Questie format
Handles field requirements correctly and preserves valuable data
"""

import re
from typing import Dict, List, Tuple, Optional, Any

def parse_quest_line(line: str) -> Tuple[Optional[int], Optional[List[str]]]:
    """Parse a quest line and extract fields"""
    match = re.match(r'\s*\[(\d+)\]\s*=\s*\{(.*?)\},?\s*(?:--.*)?$', line)
    if not match:
        return None, None
    
    quest_id = int(match.group(1))
    data = match.group(2)
    
    # Parse fields carefully handling nested structures
    fields = []
    current = ""
    depth = 0
    in_string = False
    
    for char in data:
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
    
    return quest_id, fields

def convert_quest_entry(quest_id: int, pfquest_fields: List[str]) -> str:
    """Convert a pfQuest entry to proper Questie format"""
    
    # Ensure we have 30 fields
    while len(pfquest_fields) < 30:
        pfquest_fields.append('nil')
    
    # Build the converted fields
    converted = []
    
    # Field 1: Quest name - keep from pfQuest
    converted.append(pfquest_fields[0])
    
    # Field 2: startedBy - keep from pfQuest
    converted.append(pfquest_fields[1] if pfquest_fields[1] != 'nil' else 'nil')
    
    # Field 3: finishedBy - keep from pfQuest
    converted.append(pfquest_fields[2] if pfquest_fields[2] != 'nil' else 'nil')
    
    # Field 4: requiredLevel - keep from pfQuest
    converted.append(pfquest_fields[3])
    
    # Field 5: questLevel - keep from pfQuest
    converted.append(pfquest_fields[4] if pfquest_fields[4] != 'nil' else '1')  # Default to 1 if nil
    
    # Field 6: requiredRaces - keep from pfQuest
    converted.append(pfquest_fields[5])
    
    # Field 7: requiredClasses - keep from pfQuest (but convert faction)
    # pfQuest uses 1=Horde, 2=Alliance, 3=Both
    # Questie uses nil for no restriction
    faction = pfquest_fields[6]
    if faction == '1':
        converted.append('nil')  # Horde - will use faction-specific NPCs instead
    elif faction == '2':
        converted.append('nil')  # Alliance - will use faction-specific NPCs instead
    elif faction == '3':
        converted.append('nil')  # Both factions
    else:
        converted.append(faction)
    
    # Field 8: objectivesText - keep from pfQuest
    converted.append(pfquest_fields[7])
    
    # Field 9: triggerEnd - usually nil
    converted.append('nil')
    
    # Field 10: objectives - This needs special handling
    # For now, keep nil - we'll need to parse quest text to generate this
    converted.append('nil')
    
    # Field 11: sourceItemId - keep from pfQuest
    converted.append(pfquest_fields[10])
    
    # Field 12: preQuestGroup - keep from pfQuest
    converted.append(pfquest_fields[11])
    
    # Field 13: preQuestSingle - handle single values
    prereq = pfquest_fields[12]
    if prereq != 'nil' and not prereq.startswith('{'):
        # Single quest ID, needs to be in table format
        prereq = '{' + prereq + '}'
    converted.append(prereq)
    
    # Field 14: childQuests - keep from pfQuest
    converted.append(pfquest_fields[13])
    
    # Field 15: inGroupWith - keep from pfQuest
    converted.append(pfquest_fields[14])
    
    # Field 16: exclusiveTo - keep from pfQuest
    converted.append(pfquest_fields[15])
    
    # Field 17: zoneOrSort - keep from pfQuest (but default to 0 if nil)
    zone = pfquest_fields[16]
    converted.append(zone if zone != 'nil' else '0')
    
    # Field 18: requiredSkill - keep from pfQuest
    converted.append(pfquest_fields[17])
    
    # Field 19: requiredMinRep - keep from pfQuest
    converted.append(pfquest_fields[18])
    
    # Field 20: requiredMaxRep - keep from pfQuest
    converted.append(pfquest_fields[19])
    
    # Field 21: requiredSourceItems - keep from pfQuest
    converted.append(pfquest_fields[20])
    
    # Field 22: nextQuestInChain - handle single values
    next_quest = pfquest_fields[21]
    converted.append(next_quest)
    
    # Field 23: questFlags - keep from pfQuest
    converted.append(pfquest_fields[22])
    
    # Field 24: specialFlags - IMPORTANT: Should be 0 not nil
    special = pfquest_fields[23]
    converted.append(special if special != 'nil' else '0')
    
    # Field 25: parentQuest - handle single values
    parent = pfquest_fields[24]
    if parent != 'nil' and parent != '0' and not parent.startswith('{'):
        # Make sure it's just a number
        try:
            int(parent)
        except:
            parent = 'nil'
    converted.append(parent)
    
    # Field 26: reputationReward - keep from pfQuest
    converted.append(pfquest_fields[25])
    
    # Field 27: extraObjectives - keep from pfQuest
    converted.append(pfquest_fields[26])
    
    # Field 28: requiredSpell - keep from pfQuest
    converted.append(pfquest_fields[27])
    
    # Field 29: requiredSpecialization - keep from pfQuest
    converted.append(pfquest_fields[28])
    
    # Field 30: requiredMaxLevel - keep from pfQuest
    converted.append(pfquest_fields[29])
    
    # Build the final quest entry
    return f'[{quest_id}] = {{{",".join(converted)}}}, -- Converted from pfQuest'

def convert_database(input_file: str, output_file: str, existing_quest_ids: set):
    """Convert the pfQuest database to Questie format"""
    print(f"Converting {input_file}...")
    
    converted_quests = []
    skipped_contaminated = []
    skipped_existing = []
    total_processed = 0
    
    # Contaminated quest ranges (TBC/Wrath)
    contaminated_ranges = [
        (8000, 11999),   # TBC
        (12000, 14999),  # Wrath
    ]
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if re.match(r'\s*\[\d+\]', line):
                quest_id, fields = parse_quest_line(line)
                if quest_id and fields:
                    total_processed += 1
                    
                    # Skip if already in Questie database
                    if quest_id in existing_quest_ids:
                        skipped_existing.append(quest_id)
                        continue
                    
                    # Check for contamination
                    is_contaminated = False
                    for min_id, max_id in contaminated_ranges:
                        if min_id <= quest_id <= max_id:
                            is_contaminated = True
                            skipped_contaminated.append(quest_id)
                            break
                    
                    if is_contaminated:
                        continue
                    
                    # Convert the quest
                    converted = convert_quest_entry(quest_id, fields)
                    converted_quests.append((quest_id, converted))
    
    # Write the converted database
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('-- Converted pfQuest database for Questie\n')
        f.write('-- This file contains quests from pfQuest that are NOT in the current Questie database\n')
        f.write('-- Contaminated quests (TBC/Wrath) have been filtered out\n\n')
        
        f.write('local QuestieLoader = {}\n')
        f.write('QuestieLoader.ImportModule = function() return {} end\n')
        f.write('local QuestieDB = QuestieLoader:ImportModule("QuestieDB")\n\n')
        
        f.write('pfQuestConverted = {\n')
        
        for quest_id, entry in sorted(converted_quests):
            f.write(f'  {entry}\n')
        
        f.write('}\n\n')
        f.write('-- Summary:\n')
        f.write(f'-- Total processed: {total_processed}\n')
        f.write(f'-- Converted: {len(converted_quests)}\n')
        f.write(f'-- Skipped (already exists): {len(skipped_existing)}\n')
        f.write(f'-- Skipped (contaminated): {len(skipped_contaminated)}\n')
    
    return {
        'total_processed': total_processed,
        'converted': len(converted_quests),
        'skipped_existing': skipped_existing,
        'skipped_contaminated': skipped_contaminated,
        'converted_quests': [q[0] for q in converted_quests]
    }

def load_existing_quest_ids(questie_file: str) -> set:
    """Load quest IDs from existing Questie database"""
    quest_ids = set()
    
    with open(questie_file, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'\s*\[(\d+)\]', line)
            if match:
                quest_ids.add(int(match.group(1)))
    
    return quest_ids

def compare_databases(converted_file: str, original_file: str):
    """Compare converted database with original Questie database"""
    print("\n" + "="*60)
    print("DATABASE COMPARISON")
    print("="*60)
    
    # Load both databases
    converted_ids = set()
    with open(converted_file, 'r') as f:
        for line in f:
            match = re.match(r'\s*\[(\d+)\]', line)
            if match:
                converted_ids.add(int(match.group(1)))
    
    original_ids = load_existing_quest_ids(original_file)
    
    # Compare
    new_quests = converted_ids - original_ids
    print(f"\nNew quests added: {len(new_quests)}")
    if len(new_quests) <= 20:
        print(f"  Quest IDs: {sorted(new_quests)}")
    else:
        print(f"  First 20: {sorted(new_quests)[:20]}")
    
    # Sample some conversions to verify quality
    print("\nSample Converted Quests:")
    with open(converted_file, 'r') as f:
        count = 0
        for line in f:
            if re.match(r'\s*\[\d+\]', line) and count < 3:
                print(f"  {line[:100]}...")
                count += 1

def main():
    # Load existing Questie quest IDs
    print("Loading existing Questie database...")
    existing_ids = load_existing_quest_ids('epochQuestDB.lua')
    print(f"Found {len(existing_ids)} existing quests in Questie")
    
    # Convert pfQuest database
    results = convert_database(
        'pfquest_converted_quests.lua',
        'pfquest_properly_converted.lua',
        existing_ids
    )
    
    print("\n" + "="*60)
    print("CONVERSION RESULTS")
    print("="*60)
    print(f"Total quests processed: {results['total_processed']}")
    print(f"Successfully converted: {results['converted']}")
    print(f"Skipped (already in Questie): {len(results['skipped_existing'])}")
    print(f"Skipped (TBC/Wrath contamination): {len(results['skipped_contaminated'])}")
    
    if results['skipped_contaminated']:
        print(f"\nContaminated quest IDs removed: {results['skipped_contaminated']}")
    
    # Compare with original
    compare_databases('pfquest_properly_converted.lua', 'epochQuestDB.lua')
    
    print("\n✅ Conversion complete! Check pfquest_properly_converted.lua")

if __name__ == "__main__":
    main()