#!/usr/bin/env python3

"""
Find the specific quest with bracket issues
"""

import re

def find_bracket_issue():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    in_main_table = False
    current_quest = None
    quest_line = 0
    
    for i, line in enumerate(lines, 1):
        # Skip comments
        if line.strip().startswith('--'):
            continue
            
        # Check if we're starting the main table
        if 'epochQuestDB = {' in line:
            in_main_table = True
            continue
            
        # Check if we're ending the main table
        if line.strip() == '}' and in_main_table:
            print(f"✅ Main table closes at line {i}")
            in_main_table = False
            continue
            
        # Look for quest entries
        if in_main_table and re.match(r'^\s*\[\d+\]\s*=\s*\{', line):
            quest_match = re.search(r'\[(\d+)\]', line)
            if quest_match:
                # Check if previous quest was properly closed
                if current_quest:
                    # Count brackets in the quest definition
                    quest_text = ''.join(lines[quest_line-1:i-1])
                    open_count = quest_text.count('{')
                    close_count = quest_text.count('}')
                    if open_count != close_count:
                        print(f"⚠️ Quest {current_quest} (line {quest_line}) has mismatched brackets:")
                        print(f"   Opens: {open_count}, Closes: {close_count}")
                        # Show the quest line
                        print(f"   Line {quest_line}: {lines[quest_line-1].strip()[:100]}")
                        return quest_line
                
                current_quest = quest_match.group(1)
                quest_line = i
    
    # Check the last quest
    if current_quest and in_main_table:
        # Find where main table should close
        for i in range(quest_line, len(lines)):
            if lines[i].strip() == '}':
                quest_text = ''.join(lines[quest_line-1:i])
                open_count = quest_text.count('{')
                close_count = quest_text.count('}')
                if open_count != close_count:
                    print(f"⚠️ Quest {current_quest} (line {quest_line}) has mismatched brackets:")
                    print(f"   Opens: {open_count}, Closes: {close_count}")
                    return quest_line
                break
    
    # Count total brackets in the quest section
    quest_section = ''.join(lines[3:890])  # From epochQuestDB = { to the closing }
    total_opens = quest_section.count('{')
    total_closes = quest_section.count('}')
    print(f"\n📊 Total bracket count in quest section:")
    print(f"   Opening braces: {total_opens}")
    print(f"   Closing braces: {total_closes}")
    print(f"   Difference: {total_opens - total_closes}")
    
    if total_opens > total_closes:
        print(f"\n❌ Missing {total_opens - total_closes} closing brace(s)")
    elif total_closes > total_opens:
        print(f"\n❌ Extra {total_closes - total_opens} closing brace(s)")
    else:
        print(f"\n✅ Brackets are balanced overall")

if __name__ == "__main__":
    find_bracket_issue()