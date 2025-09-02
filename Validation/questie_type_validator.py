#!/usr/bin/env python3

"""
Questie-specific type validator that mimics the in-game compilation checks.
Validates that all fields match the expected datatypes.
"""

import re

# Define Questie's expected field types (based on error messages)
FIELD_TYPES = {
    # Position -> (Field Name, Expected Type, Description)
    1: ("name", "string", "Quest name"),
    2: ("startedBy", "table", "{{NPCs},{Objects},{Items}}"),
    3: ("finishedBy", "table", "{{NPCs},{Objects}}"),
    4: ("requiredLevel", "number_or_nil", "Min level or nil"),
    5: ("questLevel", "number", "Quest level"),
    6: ("requiredRaces", "number_or_nil", "Race bitmask or nil"),
    7: ("requiredClasses", "number_or_nil", "Class bitmask or nil"),
    8: ("objectivesText", "table_or_nil", "{text,...} or nil"),
    9: ("triggerEnd", "table_or_nil", "Exploration trigger or nil"),
    10: ("objectives", "table_or_nil", "6-element objectives array or nil"),
    11: ("sourceItemId", "number_or_nil", "Item ID or nil"),
    12: ("preQuestGroup", "u8u24array", "{questId,...} or nil"),
    13: ("preQuestSingle", "u8u24array", "{questId,...} or nil"),
    14: ("childQuests", "u8u24array", "{questId,...} or nil"),
    15: ("inGroupWith", "u8u24array", "{questId,...} or nil"),
    16: ("exclusiveTo", "u8u24array", "{questId,...} or nil"),
    17: ("zoneOrSort", "number_or_nil", "Zone ID or quest sort"),
    18: ("requiredSkill", "u12pair", "{skillId, value} or nil"),
    19: ("requiredMinRep", "s24pair", "{factionId, value} or nil"),
    20: ("requiredMaxRep", "s24pair", "{factionId, value} or nil"),
    21: ("requiredSourceItems", "u8u24array", "{itemId,...} or nil"),
    22: ("nextQuestInChain", "number_or_nil", "Quest ID or nil"),
    23: ("questFlags", "number_or_nil", "Flags or nil"),
    24: ("specialFlags", "number_or_nil", "Special flags or nil"),
    25: ("parentQuest", "number_or_nil", "Parent quest ID or nil"),
    26: ("reputationReward", "table_or_nil", "{{factionId, value},...} or nil"),
    27: ("extraObjectives", "table_or_nil", "{{spellId, text},...} or nil"),
    28: ("requiredSpell", "number_or_nil", "Spell ID or nil"),
    29: ("requiredSpecialization", "number_or_nil", "Spec ID or nil"),
    30: ("requiredMaxLevel", "number_or_nil", "Max level or nil")
}

def analyze_quest_structure(line):
    """Parse quest line and return list of fields"""
    match = re.search(r'\[(\d+)\] = \{(.*)\},', line)
    if not match:
        return None, None
    
    quest_id = match.group(1)
    data = '{' + match.group(2) + '}'
    
    # Split by commas at depth 1
    parts = []
    current = ""
    depth = 0
    in_string = False
    escape = False
    
    for char in data[1:-1]:  # Skip outer braces
        if escape:
            current += char
            escape = False
            continue
            
        if char == '\\':
            escape = True
            current += char
            continue
            
        if char == '"' and not escape:
            in_string = not in_string
            current += char
        elif not in_string:
            if char == '{':
                depth += 1
                current += char
            elif char == '}':
                depth -= 1
                current += char
            elif char == ',' and depth == 0:
                parts.append(current.strip())
                current = ""
            else:
                current += char
        else:
            current += char
            
    if current:
        parts.append(current.strip())
    
    return quest_id, parts

def check_field_type(value, expected_type):
    """Check if a field value matches the expected type"""
    if value == 'nil':
        # nil is acceptable for types ending with _or_nil or for array types
        return expected_type.endswith('_or_nil') or 'array' in expected_type or 'pair' in expected_type or 'table' in expected_type
    
    if expected_type == "string":
        return value.startswith('"') and value.endswith('"')
    
    elif expected_type == "number":
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    elif expected_type == "number_or_nil":
        if value == 'nil':
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    elif expected_type == "table":
        return value.startswith('{') and value.endswith('}')
    
    elif expected_type == "table_or_nil":
        return value == 'nil' or (value.startswith('{') and value.endswith('}'))
    
    elif expected_type == "u8u24array":  # Array of quest/item IDs
        if value == 'nil':
            return True
        if not (value.startswith('{') and value.endswith('}')):
            return False
        return True
    
    elif expected_type == "u12pair":  # {skillId, value} pair
        if value == 'nil':
            return True
        if not (value.startswith('{') and value.endswith('}')):
            return False
        # Should be a pair like {182, 300}
        return True
    
    elif expected_type == "s24pair":  # {factionId, value} pair for reputation
        if value == 'nil':
            return True
        if not (value.startswith('{') and value.endswith('}')):
            return False
        # Should be a pair like {68, 3000}
        return True
    
    return False

def validate_questie_types():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    errors = []
    quest_count = 0
    
    for i, line in enumerate(lines, 1):
        if not line.strip().startswith('[') or '=' not in line:
            continue
            
        if line.strip().startswith('--'):
            continue
        
        quest_id, fields = analyze_quest_structure(line)
        if not fields:
            continue
        
        quest_count += 1
        
        # Check each field against expected type
        for pos in range(1, min(len(fields) + 1, 31)):
            if pos not in FIELD_TYPES:
                continue
                
            field_name, expected_type, description = FIELD_TYPES[pos]
            
            if pos > len(fields):
                # Field is missing - this is OK if it can be nil
                if not expected_type.endswith('_or_nil') and expected_type not in ['u8u24array', 'u12pair', 's24pair', 'table_or_nil']:
                    errors.append({
                        'quest_id': quest_id,
                        'line': i,
                        'field': field_name,
                        'position': pos,
                        'error': f"Missing required field (expected {expected_type})",
                        'value': 'MISSING'
                    })
                continue
            
            field_value = fields[pos - 1]
            
            # Special check for plain numbers in array/pair fields
            if expected_type in ['u8u24array', 'u12pair', 's24pair'] and field_value != 'nil':
                if not field_value.startswith('{'):
                    try:
                        int(field_value)
                        errors.append({
                            'quest_id': quest_id,
                            'line': i,
                            'field': field_name,
                            'position': pos,
                            'error': f"Invalid datatype! Quests[{quest_id}].{field_name}: 'number' is not compatible with type '{expected_type}'",
                            'value': field_value
                        })
                    except ValueError:
                        pass
            elif not check_field_type(field_value, expected_type):
                errors.append({
                    'quest_id': quest_id,
                    'line': i,
                    'field': field_name,
                    'position': pos,
                    'error': f"Type mismatch (expected {expected_type})",
                    'value': field_value[:50] + '...' if len(field_value) > 50 else field_value
                })
    
    # Print results
    print(f"=== Questie Type Validation Report ===")
    print(f"Quests analyzed: {quest_count}")
    print(f"Type errors found: {len(errors)}\n")
    
    if errors:
        print("Errors matching in-game compilation checks:\n")
        
        # Group by field
        field_errors = {}
        for error in errors:
            field = error['field']
            if field not in field_errors:
                field_errors[field] = []
            field_errors[field].append(error)
        
        for field, field_error_list in sorted(field_errors.items()):
            print(f"\n{field} (position {field_error_list[0]['position']}): {len(field_error_list)} errors")
            for err in field_error_list[:3]:
                print(f"  Quest {err['quest_id']} (line {err['line']}): {err['error']}")
                print(f"    Value: {err['value']}")
            if len(field_error_list) > 3:
                print(f"  ... and {len(field_error_list) - 3} more")
    else:
        print("✅ No type errors found! Database should compile successfully in-game.")
    
    return errors

if __name__ == "__main__":
    errors = validate_questie_types()
    
    if errors:
        print("\n" + "="*60)
        print("To fix these errors, values need to be:")
        print("- Moved to the correct field position")
        print("- Wrapped in array syntax {} for array fields")
        print("- Set to nil if invalid")
        print("\nRun fix_all_field_types.py to fix these automatically.")