#!/usr/bin/env python3
"""
Remove duplicate quest entries from epochQuestDB.lua
Keeps the first occurrence of each quest ID
"""

import re
from collections import OrderedDict

def remove_duplicate_quests():
    """Remove duplicate quest entries."""
    
    print("="*60)
    print("Removing Duplicate Quest Entries")
    print("="*60)
    
    with open('Database/Epoch/epochQuestDB.lua', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Track quest entries
    quest_entries = OrderedDict()
    quest_lines = {}
    other_lines = []
    inside_table = False
    
    for i, line in enumerate(lines):
        # Check for table start
        if 'epochQuestData = {' in line:
            inside_table = True
            other_lines.append((i, line))
            continue
            
        # Check for table end
        if line.strip() == '}' and inside_table:
            inside_table = False
            other_lines.append((i, line))
            continue
            
        # Check for quest entries
        match = re.match(r'^\[(\d+)\] = \{', line.strip())
        if match and inside_table:
            quest_id = int(match.group(1))
            
            if quest_id not in quest_entries:
                # First occurrence - keep it
                quest_entries[quest_id] = line
                quest_lines[quest_id] = i + 1
            else:
                # Duplicate - will be removed
                print(f"  Removing duplicate quest {quest_id} from line {i+1}")
        else:
            # Non-quest lines (comments, QuestieDB assignment, etc)
            other_lines.append((i, line))
    
    print(f"\nFound {len(quest_entries)} unique quests")
    
    # Rebuild the file
    new_lines = []
    
    # Add header lines
    for idx, line in other_lines:
        if 'epochQuestData = {' in line:
            new_lines.append(line)
            break
        if idx < 10:  # Keep initial header/imports
            new_lines.append(line)
    
    # Add unique quest entries
    for quest_id, line in quest_entries.items():
        new_lines.append(line)
    
    # Add footer lines (closing brace and QuestieDB assignment)
    found_closing = False
    for idx, line in other_lines:
        if line.strip() == '}' and not found_closing:
            new_lines.append(line)
            found_closing = True
        elif 'QuestieDB._epochQuestData' in line:
            new_lines.append('\n')
            new_lines.append(line)
    
    # Save the cleaned file
    with open('Database/Epoch/epochQuestDB.lua', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ Removed duplicates, kept {len(quest_entries)} unique quests")
    
    return len(quest_entries)

def main():
    count = remove_duplicate_quests()
    
    print("\n" + "="*60)
    print(f"Database cleaned: {count} unique quests")
    print("IMPORTANT: Restart WoW completely to load changes")
    print("="*60)

if __name__ == "__main__":
    main()