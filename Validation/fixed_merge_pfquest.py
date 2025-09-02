#!/usr/bin/env python3

"""
Fixed smart merge - simplified approach that preserves exact Lua syntax
"""

import re
from datetime import datetime
from collections import defaultdict

def load_questie_quests():
    """Load Questie quests by parsing line by line"""
    with open("Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    quests = {}
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        # Match quest entries: [id] = {data},
        match = re.match(r'^\[(\d+)\]\s*=\s*\{(.+)\},?\s*(?:--.*)?$', line)
        if match:
            quest_id = int(match.group(1))
            content = match.group(2)
            # Extract quest name (first field)
            name_match = re.match(r'^"([^"]*)"', content)
            name = name_match.group(1) if name_match else "Unknown"
            
            quests[quest_id] = {
                'name': name,
                'line': line,
                'line_num': line_num
            }
    
    print(f"Loaded {len(quests)} Questie quests")
    return quests

def load_pfquest_quests():
    """Load pfQuest quests by parsing line by line"""
    with open("pfquest_objectives_v2.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    quests = {}
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        # Match quest entries: [id] = {data},
        match = re.match(r'^\[(\d+)\]\s*=\s*\{(.+)\},?\s*$', line)
        if match:
            quest_id = int(match.group(1))
            content = match.group(2)
            # Extract quest name (first field)
            name_match = re.match(r'^"([^"]*)"', content)
            name = name_match.group(1) if name_match else "Unknown"
            
            quests[quest_id] = {
                'name': name,
                'line': line,
                'line_num': line_num
            }
    
    print(f"Loaded {len(quests)} pfQuest quests")
    return quests

def smart_merge():
    """Smart merge pfQuest into Questie"""
    print("Loading databases...")
    questie_db = load_questie_quests()
    pfquest_db = load_pfquest_quests()
    
    # Analysis
    new_quests = {}
    conflicts = []
    placeholder_updates = {}
    
    for quest_id, pfquest_data in pfquest_db.items():
        pfquest_name = pfquest_data['name']
        
        if quest_id in questie_db:
            questie_name = questie_db[quest_id]['name']
            
            # Placeholder update
            if questie_name.startswith("[Epoch] Quest"):
                placeholder_updates[quest_id] = pfquest_data
                print(f"  Placeholder update: {quest_id} -> {pfquest_name}")
            
            # Conflict - trust Questie
            elif questie_name != pfquest_name:
                conflicts.append({
                    'id': quest_id,
                    'questie': questie_name,
                    'pfquest': pfquest_name
                })
        else:
            # Check for name duplicates
            questie_has_name = any(q['name'] == pfquest_name 
                                 for q in questie_db.values() 
                                 if not q['name'].startswith("[Epoch]"))
            
            if not questie_has_name:
                new_quests[quest_id] = pfquest_data
                print(f"  New quest: {quest_id} -> {pfquest_name}")
    
    print(f"\nAnalysis complete:")
    print(f"  New quests: {len(new_quests)}")
    print(f"  Placeholder updates: {len(placeholder_updates)}")
    print(f"  Conflicts (skipped): {len(conflicts)}")
    
    # Create merged database
    print(f"\nCreating merged database...")
    
    # Read the original file and rebuild it
    with open("Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        original_lines = f.readlines()
    
    output_lines = []
    
    # Copy everything until the closing }
    for i, line in enumerate(original_lines):
        # Update placeholders
        line_stripped = line.strip()
        if line_stripped.startswith('[') and '=' in line_stripped:
            match = re.match(r'^\[(\d+)\]', line_stripped)
            if match:
                quest_id = int(match.group(1))
                if quest_id in placeholder_updates:
                    # Replace with pfQuest version
                    indent = len(line) - len(line.lstrip())
                    new_line = ' ' * indent + placeholder_updates[quest_id]['line']
                    if not new_line.endswith('\n'):
                        new_line += '\n'
                    output_lines.append(new_line)
                    continue
        
        # Check for closing brace
        if line.strip() == '}':
            # Add new quests before the closing brace
            if new_quests:
                output_lines.append('\n-- NEW QUESTS FROM PFQUEST\n')
                for quest_id in sorted(new_quests.keys()):
                    new_line = new_quests[quest_id]['line']
                    if not new_line.endswith(','):
                        new_line = new_line.rstrip() + ','
                    output_lines.append(new_line + ' -- From pfQuest\n')
                output_lines.append('\n')
            
            # Add the closing brace
            output_lines.append(line)
        else:
            output_lines.append(line)
    
    # Write merged database
    with open("epochQuestDB_FIXED_MERGE.lua", 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    print(f"✅ Merged database saved: epochQuestDB_FIXED_MERGE.lua")
    print(f"   Original Questie: {len(questie_db)}")
    print(f"   New from pfQuest: {len(new_quests)}")
    print(f"   Placeholders updated: {len(placeholder_updates)}")
    print(f"   Total: {len(questie_db) + len(new_quests)}")
    
    # Test Lua syntax
    print(f"\nTesting Lua syntax...")
    try:
        with open("epochQuestDB_FIXED_MERGE.lua", 'r') as f:
            content = f.read()
        
        # Basic syntax check - count braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        print(f"  Open braces: {open_braces}")
        print(f"  Close braces: {close_braces}")
        
        if open_braces == close_braces:
            print("  ✅ Brace count matches")
        else:
            print(f"  ❌ Brace mismatch: {open_braces - close_braces}")
        
        # Check for common syntax errors
        lines = content.split('\n')
        errors = 0
        for i, line in enumerate(lines, 1):
            if '[' in line and '=' in line and not line.strip().startswith('--'):
                if not (line.rstrip().endswith(',') or line.rstrip().endswith('},')):
                    if not line.rstrip().endswith('}'):  # Allow final entry without comma
                        print(f"  Warning line {i}: Missing comma - {line.strip()[:50]}...")
                        errors += 1
        
        if errors == 0:
            print("  ✅ No obvious syntax errors found")
        else:
            print(f"  ⚠️  {errors} potential syntax issues found")
            
    except Exception as e:
        print(f"  ❌ Error reading merged file: {e}")
    
    return len(new_quests)

if __name__ == "__main__":
    added_count = smart_merge()
    print(f"\n🎉 Successfully merged {added_count} new quests from pfQuest!")