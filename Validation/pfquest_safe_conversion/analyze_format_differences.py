#!/usr/bin/env python3
"""
Analyze the actual format differences between pfQuest converted data and Questie database
"""

import re
from typing import Dict, List, Tuple, Any

def parse_quest_line(line: str) -> Tuple[int, List[str]]:
    """Parse a quest line and extract fields"""
    # Match quest entry
    match = re.match(r'\s*\[(\d+)\]\s*=\s*\{(.*?)\},?\s*(?:--.*)?$', line)
    if not match:
        return None, None
    
    quest_id = int(match.group(1))
    data = match.group(2)
    
    # Parse fields more carefully
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

def analyze_questie_format():
    """Analyze actual Questie database format"""
    print("Analyzing Questie Database Format...")
    print("="*60)
    
    questie_examples = {}
    with open('epochQuestDB.lua', 'r', encoding='utf-8') as f:
        for line in f:
            if re.match(r'\s*\[\d+\]', line):
                quest_id, fields = parse_quest_line(line)
                if quest_id and fields and len(questie_examples) < 5:
                    questie_examples[quest_id] = fields
    
    # Analyze field patterns
    print("\nQuestie Field Analysis:")
    for quest_id, fields in questie_examples.items():
        print(f"\nQuest {quest_id}: {len(fields)} fields")
        for i, field in enumerate(fields[:10]):  # Show first 10 fields
            field_preview = field[:50] + "..." if len(field) > 50 else field
            print(f"  Field {i+1}: {field_preview}")
    
    return questie_examples

def analyze_pfquest_format():
    """Analyze pfQuest converted format"""
    print("\n" + "="*60)
    print("Analyzing pfQuest Converted Format...")
    print("="*60)
    
    pfquest_examples = {}
    with open('pfquest_converted_quests.lua', 'r', encoding='utf-8') as f:
        for line in f:
            if re.match(r'\s*\[\d+\]', line):
                quest_id, fields = parse_quest_line(line)
                if quest_id and fields and len(pfquest_examples) < 5:
                    pfquest_examples[quest_id] = fields
    
    print("\npfQuest Field Analysis:")
    for quest_id, fields in pfquest_examples.items():
        print(f"\nQuest {quest_id}: {len(fields)} fields")
        for i, field in enumerate(fields[:10]):
            field_preview = field[:50] + "..." if len(field) > 50 else field
            print(f"  Field {i+1}: {field_preview}")
    
    return pfquest_examples

def compare_formats(questie_examples: Dict, pfquest_examples: Dict):
    """Compare the two formats"""
    print("\n" + "="*60)
    print("FORMAT COMPARISON")
    print("="*60)
    
    # Check field counts
    questie_counts = [len(fields) for fields in questie_examples.values()]
    pfquest_counts = [len(fields) for fields in pfquest_examples.values()]
    
    print(f"\nField Counts:")
    print(f"  Questie: {min(questie_counts)} - {max(questie_counts)} fields")
    print(f"  pfQuest: {min(pfquest_counts)} - {max(pfquest_counts)} fields")
    
    # Identify field patterns
    print("\nField Pattern Analysis:")
    
    # Check a specific quest if it exists in both
    common_ids = set(questie_examples.keys()) & set(pfquest_examples.keys())
    if common_ids:
        test_id = list(common_ids)[0]
        print(f"\nComparing Quest {test_id}:")
        
        q_fields = questie_examples[test_id]
        p_fields = pfquest_examples[test_id]
        
        for i in range(min(10, min(len(q_fields), len(p_fields)))):
            print(f"\n  Field {i+1}:")
            print(f"    Questie: {q_fields[i][:40]}...")
            print(f"    pfQuest: {p_fields[i][:40]}...")
    
    # Identify nil handling
    print("\n\nNil Value Patterns:")
    
    questie_nil_positions = set()
    for fields in questie_examples.values():
        for i, field in enumerate(fields):
            if field == "nil":
                questie_nil_positions.add(i+1)
    
    pfquest_nil_positions = set()
    for fields in pfquest_examples.values():
        for i, field in enumerate(fields):
            if field == "nil":
                pfquest_nil_positions.add(i+1)
    
    print(f"  Questie commonly has nil at positions: {sorted(questie_nil_positions)[:10]}")
    print(f"  pfQuest commonly has nil at positions: {sorted(pfquest_nil_positions)[:10]}")
    
    return questie_nil_positions, pfquest_nil_positions

def identify_field_meanings():
    """Try to identify what each field means based on patterns"""
    print("\n" + "="*60)
    print("FIELD IDENTIFICATION")
    print("="*60)
    
    # Known Questie field structure
    field_meanings = [
        (1, "name", "Quest name string"),
        (2, "startedBy", "{{NPCs},{Objects},{Items}}"),
        (3, "finishedBy", "{{NPCs},{Objects}}"),
        (4, "requiredLevel", "Min level or nil"),
        (5, "questLevel", "Quest level"),
        (6, "requiredRaces", "Race bitmask or nil"),
        (7, "requiredClasses", "Class bitmask or nil"),
        (8, "objectivesText", "Quest text or nil"),
        (9, "triggerEnd", "Exploration trigger or nil"),
        (10, "objectives", "Complex objectives structure or nil"),
        (11, "sourceItemId", "Item ID or nil"),
        (12, "preQuestGroup", "All prereqs or nil"),
        (13, "preQuestSingle", "Any prereq or nil"),
        (14, "childQuests", "Unlocked quests or nil"),
        (15, "inGroupWith", "Quest group or nil"),
        (16, "exclusiveTo", "Exclusive quests or nil"),
        (17, "zoneOrSort", "Zone ID or sort"),
        (18, "requiredSkill", "Skill requirement or nil"),
        (19, "requiredMinRep", "Min rep or nil"),
        (20, "requiredMaxRep", "Max rep or nil"),
        (21, "requiredSourceItems", "Required items or nil"),
        (22, "nextQuestInChain", "Next quest ID or nil"),
        (23, "questFlags", "Flags or nil"),
        (24, "specialFlags", "Special flags (often 0 or 8)"),
        (25, "parentQuest", "Parent quest or nil"),
        (26, "reputationReward", "Rep rewards or nil"),
        (27, "extraObjectives", "Extra objectives or nil"),
        (28, "requiredSpell", "Spell requirement or nil"),
        (29, "requiredSpecialization", "Spec requirement or nil"),
        (30, "requiredMaxLevel", "Max level or nil")
    ]
    
    print("\nExpected Questie Field Structure:")
    for pos, name, desc in field_meanings:
        print(f"  {pos:2d}. {name:25s} - {desc}")
    
    return field_meanings

def main():
    # Analyze both formats
    questie_examples = analyze_questie_format()
    pfquest_examples = analyze_pfquest_format()
    
    # Compare them
    questie_nils, pfquest_nils = compare_formats(questie_examples, pfquest_examples)
    
    # Identify field meanings
    field_meanings = identify_field_meanings()
    
    # Recommendations
    print("\n" + "="*60)
    print("CONVERSION RECOMMENDATIONS")
    print("="*60)
    
    print("""
1. Both databases use 30 fields - structure is similar
2. pfQuest has good data for:
   - Quest names (field 1)
   - NPCs (fields 2-3)
   - Quest level (field 5)
   - Objectives text (field 8)
   
3. Key differences to handle:
   - pfQuest uses 'nil' extensively which is VALID in Questie
   - Some fields like field 24 should be 0 not nil
   - Objectives structure (field 10) needs special handling
   
4. Conversion strategy:
   - Keep pfQuest's valuable data (names, NPCs, text)
   - Use Questie's defaults for other fields
   - Special handling for objectives structure
   - Ensure field 24 is 0 not nil
""")

if __name__ == "__main__":
    main()