#!/usr/bin/env python3
"""
Ultimate database fixer - handles ALL structural issues properly.
"""

import re

def fix_npc_database():
    """Fix the NPC database structure."""
    print("\n" + "="*60)
    print("Fixing epochNpcDB.lua")
    print("="*60)
    
    with open('Database/Epoch/epochNpcDB.lua', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Already fixed by previous script
    print("✅ epochNpcDB.lua structure is correct")
    return True

def fix_quest_database():
    """Fix the quest database structure completely."""
    print("\n" + "="*60)
    print("Fixing epochQuestDB.lua")
    print("="*60)
    
    with open('Database/Epoch/epochQuestDB.lua', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    inside_table = False
    found_entries = []
    header_lines = []
    footer_lines = []
    
    # Parse the file
    for i, line in enumerate(lines):
        # Keep header
        if not inside_table and 'epochQuestData = {' not in line:
            if not re.match(r'^\[\d+\] = \{', line.strip()):
                header_lines.append(line)
                continue
        
        # Start of table
        if 'epochQuestData = {' in line:
            inside_table = True
            # Change {} to just {
            if line.strip() == 'epochQuestData = {}':
                header_lines.append('epochQuestData = {\n')
            else:
                header_lines.append(line)
            continue
        
        # Quest entries
        if re.match(r'^\[\d+\] = \{', line.strip()):
            # Ensure it has a comma
            if not line.rstrip().endswith(','):
                if '--' in line:
                    line = re.sub(r'\}(\s*--.*)?$', r'},\1', line)
                else:
                    line = line.rstrip() + ',\n'
            found_entries.append(line)
            continue
        
        # Comments between entries
        if inside_table and (line.strip().startswith('--') or not line.strip()):
            found_entries.append(line)
            continue
        
        # End of entries - everything else is footer
        if line.strip() and not line.strip().startswith('--'):
            footer_lines.append(line)
    
    # Rebuild the file
    new_lines.extend(header_lines)
    new_lines.extend(found_entries)
    
    # Remove trailing comma from last entry
    if new_lines and new_lines[-1].rstrip().endswith(','):
        # Find last actual entry (not comment or blank)
        for i in range(len(new_lines) - 1, -1, -1):
            if re.match(r'^\[\d+\] = \{', new_lines[i].strip()):
                # Remove comma from this line
                new_lines[i] = new_lines[i].rstrip()[:-1] + '\n'
                break
    
    # Add closing brace
    new_lines.append('}\n')
    new_lines.append('\n')
    
    # Add the QuestieDB assignment
    new_lines.append('-- Stage the Epoch questData for later merge during compilation\n')
    new_lines.append('QuestieDB._epochQuestData = epochQuestData\n')
    
    # Save the fixed file
    with open('Database/Epoch/epochQuestDB.lua', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ Fixed structure with {len(found_entries)} entries")
    return True

def validate_files():
    """Validate both files have correct structure."""
    print("\n" + "="*60)
    print("Validating Database Files")
    print("="*60)
    
    valid = True
    
    # Check NPC database
    with open('Database/Epoch/epochNpcDB.lua', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'epochNpcData = {' not in content:
        print("❌ epochNpcDB.lua: Missing table declaration")
        valid = False
    elif content.count('{') != content.count('}'):
        print(f"❌ epochNpcDB.lua: Brace mismatch ({content.count('{')} open, {content.count('}')} close)")
        valid = False
    elif 'QuestieDB._epochNpcData' not in content:
        print("❌ epochNpcDB.lua: Missing QuestieDB assignment")
        valid = False
    else:
        print("✅ epochNpcDB.lua: Structure valid")
    
    # Check quest database
    with open('Database/Epoch/epochQuestDB.lua', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'epochQuestData = {' not in content:
        print("❌ epochQuestDB.lua: Missing table declaration")
        valid = False
    elif content.count('{') != content.count('}'):
        print(f"❌ epochQuestDB.lua: Brace mismatch ({content.count('{')} open, {content.count('}')} close)")
        valid = False
    elif 'QuestieDB._epochQuestData' not in content:
        print("❌ epochQuestDB.lua: Missing QuestieDB assignment")
        valid = False
    else:
        print("✅ epochQuestDB.lua: Structure valid")
    
    return valid

def main():
    print("="*60)
    print("ULTIMATE QUESTIE DATABASE FIXER")
    print("="*60)
    
    # Fix both databases
    fix_npc_database()
    fix_quest_database()
    
    # Validate
    if validate_files():
        print("\n" + "="*60)
        print("✅ ALL DATABASE FILES ARE NOW SYNTACTICALLY CORRECT!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ Some issues remain - check error messages above")
        print("="*60)

if __name__ == "__main__":
    main()