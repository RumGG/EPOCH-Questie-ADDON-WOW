#!/usr/bin/env python3

"""
Fix objectives field where there's incorrect nesting causing 'rshift' errors.
The objectives field should have this structure:
{
    {creatures},     -- {{npcId, count}, ...}
    {objects},       -- {{objectId, count}, ...}
    {items},         -- {{itemId, count}, ...}
    {reputation},    -- {factionId, value} or nil
    {killCredit},    -- {{npcIds...}, baseNpcId, "text"} or nil
    {spells}         -- {{spellId, "text"}, ...} or nil
}

The error happens when we have triple-nested structures like {{{id,count}}}
"""

import re

def fix_objectives_nesting():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_made = 0
    
    # Pattern to find objectives field with triple-nested structures
    # This matches objectives fields that contain {{{ patterns
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if not line.strip().startswith('[') or '=' not in line:
            continue
            
        if '{{{' in line:
            original = line
            quest_match = re.search(r'\[(\d+)\]', line)
            quest_id = quest_match.group(1) if quest_match else 'unknown'
            
            # Fix triple-nested arrays in objectives
            # Replace {{{x,y},{a,b}}} with {{x,y},{a,b}}
            fixed_line = line
            
            # Pattern to match triple-nested structures
            # Match patterns like {{{num,num},{num,num}}} or {{{num,num}}}
            pattern = r'\{\{\{(\d+,\d+(?:\},\{)?(?:\d+,\d+)?)\}\}\}'
            
            def replace_triple_nesting(match):
                inner = match.group(1)
                # If it contains },{, it's multiple pairs
                if '},{' in inner:
                    return '{{' + inner + '}}'
                else:
                    # Single pair - needs double braces
                    return '{{' + inner + '}}'
            
            # Fix triple nesting
            while '{{{' in fixed_line:
                before = fixed_line
                fixed_line = re.sub(r'\{\{\{([^}]+)\}\}\}', r'{{\1}}', fixed_line)
                if fixed_line == before:
                    # Try a different pattern
                    fixed_line = re.sub(r'\{\{\{([^}]+)\}\}', r'{{\1}', fixed_line)
                    if fixed_line == before:
                        break
            
            if fixed_line != original:
                lines[i] = fixed_line
                fixes_made += 1
                print(f"Fixed quest {quest_id}: removed triple nesting in objectives")
    
    # Write back
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f'\n✅ Fixed {fixes_made} quests with triple-nested objectives')

if __name__ == "__main__":
    fix_objectives_nesting()