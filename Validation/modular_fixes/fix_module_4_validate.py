#!/usr/bin/env python3

"""
Module 4: Validate and check for remaining issues
"""

import re

def validate_database(input_file):
    """Validate the database for remaining issues"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check brace balance
    open_braces = content.count('{')
    close_braces = content.count('}')
    
    # Check for problematic patterns
    quadruple_count = content.count('{{{{')
    triple_count = len(re.findall(r'\{\{\{(?![^}]+\}\},nil,nil,nil,nil,nil\})', content))
    
    # Find lines with potential issues
    problem_quests = []
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        if not (line.strip().startswith('[') and '=' in line):
            continue
            
        # Check for quadruple braces
        if '{{{{' in line:
            quest_match = re.search(r'\[(\d+)\]', line)
            quest_id = quest_match.group(1) if quest_match else f"line {line_num}"
            problem_quests.append(f"{quest_id} (quadruple)")
        
        # Check for problematic triple braces
        elif '{{{' in line and not re.search(r'\{\{\{[^}]+\}\},nil,nil,nil,nil,nil\}', line):
            quest_match = re.search(r'\[(\d+)\]', line)
            quest_id = quest_match.group(1) if quest_match else f"line {line_num}"
            problem_quests.append(f"{quest_id} (triple)")
    
    print("=" * 60)
    print("DATABASE VALIDATION REPORT")
    print("=" * 60)
    print(f"Brace Balance: {open_braces} open, {close_braces} close", end='')
    if open_braces == close_braces:
        print(" ✅")
    else:
        print(f" ❌ (diff: {open_braces - close_braces})")
    
    print(f"Quadruple braces remaining: {quadruple_count}", end='')
    if quadruple_count == 0:
        print(" ✅")
    else:
        print(" ❌")
    
    print(f"Problematic triple braces: {triple_count}", end='')
    if triple_count == 0:
        print(" ✅")
    else:
        print(" ⚠️")
    
    if problem_quests:
        print(f"\nQuests with issues ({len(problem_quests)}):")
        for quest in problem_quests[:20]:
            print(f"  - Quest {quest}")
        if len(problem_quests) > 20:
            print(f"  ... and {len(problem_quests)-20} more")
    else:
        print("\n✅ No problematic quests found!")
    
    print("=" * 60)
    
    return open_braces == close_braces and quadruple_count == 0

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "../Database/Epoch/epochQuestDB_temp3.lua"
    
    is_valid = validate_database(input_file)
    
    if is_valid:
        print("\n✅ Database is valid and ready to use!")
    else:
        print("\n⚠️  Database still has issues that need manual fixing")