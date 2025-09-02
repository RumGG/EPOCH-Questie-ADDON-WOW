#!/usr/bin/env python3

"""
Fix incomplete quest objective strings that end with backslash
"""

import re

def fix_incomplete_strings():
    """Fix quest objectives that end with backslash"""
    
    with open("pfquest_objectives_v2_fixed.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes = {
        '26182': 'Collect 8 Turtle Shells.',
        '26817': 'Bring Paul\'s remains to the quest giver.',
        '27138': 'Complete the quest objectives.',
        '27463': 'Collect Marai\'s possessions.',
        '27465': 'Place 4 Explosives around Slightly Opened Oil Barrels.'
    }
    
    fixed_count = 0
    
    for i, line in enumerate(lines):
        quest_match = re.search(r'\[(\d+)\]', line)
        if quest_match:
            quest_id = quest_match.group(1)
            if quest_id in fixes:
                # Find and replace the bad objective text
                old_pattern = r'\{"[^"]*\\"\}'
                new_text = '{"' + fixes[quest_id] + '"}'
                if re.search(old_pattern, line):
                    lines[i] = re.sub(old_pattern, new_text, line)
                    fixed_count += 1
                    print(f"Fixed quest {quest_id}: {fixes[quest_id]}")
    
    # Save the fixed file
    with open("pfquest_objectives_v2_fixed.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"\n✅ Fixed {fixed_count} incomplete quest objectives")
    
    return fixed_count

if __name__ == "__main__":
    fix_incomplete_strings()