#!/usr/bin/env python3
"""
Questie Database Validator - Simple and Robust
Focuses on CRITICAL issues that will break WoW
"""

import re
import sys
from collections import defaultdict

def validate_database(filepath, table_name):
    """Validate a Questie database file for critical issues."""
    
    print(f"\nValidating {filepath}")
    print("-" * 60)
    
    errors = []
    warnings = []
    ids_seen = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return False
        
    # Check 1: Basic structure
    if f'{table_name} = {{' not in content:
        errors.append(f"Missing table declaration: {table_name} = {{")
        
    # Check 2: Brace matching
    open_braces = content.count('{')
    close_braces = content.count('}')
    if open_braces != close_braces:
        errors.append(f"Brace mismatch: {open_braces} open, {close_braces} close")
        
    # Check 3: QuestieDB assignment exists and is outside table
    if f'QuestieDB._{table_name}' not in content:
        warnings.append(f"Missing QuestieDB._{table_name} assignment")
        
    # Check 4: Missing commas (simple check)
    missing_commas = 0
    for i, line in enumerate(lines, 1):
        if re.match(r'^\[\d+\] = \{.*\}$', line.strip()):
            if not line.rstrip().endswith(','):
                # Check if next line is another entry or closing brace
                if i < len(lines):
                    next_line = lines[i].strip()
                    if next_line and (next_line.startswith('[') or next_line == '}'):
                        missing_commas += 1
                        errors.append(f"Line {i}: Missing comma")
                        
    # Check 5: Wrong prefixes
    wrong_prefix = re.findall(f'^{table_name}\[\d+\]', content, re.MULTILINE)
    if wrong_prefix:
        errors.append(f"Found {len(wrong_prefix)} entries with wrong prefix '{table_name}['")
        
    # Check 6: Triple nested coordinates (NPC database only)
    if 'Npc' in filepath:
        triple_nested = content.count('{{{')
        if triple_nested > 0:
            errors.append(f"Found {triple_nested} triple-nested coordinates")
            
    # Check 7: Duplicate IDs and problematic quest fields
    for i, line in enumerate(lines, 1):
        # Look for entries
        match = re.match(r'^\[(\d+)\] = \{', line.strip())
        if match:
            entry_id = int(match.group(1))
            
            # Check for duplicates
            if entry_id in ids_seen:
                errors.append(f"Duplicate ID {entry_id} on lines {ids_seen[entry_id]} and {i}")
            else:
                ids_seen[entry_id] = i
                
            # For quests, check field 4 (requiredSkill)
            if 'Quest' in filepath:
                # Simple check - if we see },{{ after the third comma, field 4 is likely wrong
                parts = line.split(',', 5)
                if len(parts) > 4:
                    field4 = parts[3].strip()
                    if field4.startswith('{{') and not field4.startswith('{['):
                        errors.append(f"Line {i}: Quest {entry_id} has NPC data in field 4 (should be nil or skill)")
                        
    # Report
    print(f"Entries found: {len(ids_seen)}")
    
    if errors:
        print(f"\n❌ CRITICAL ERRORS ({len(errors)}):")
        for error in errors[:20]:
            print(f"  • {error}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more")
    else:
        print("✅ No critical errors")
        
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  • {warning}")
            
    return len(errors) == 0

def main():
    print("=" * 60)
    print("QUESTIE DATABASE VALIDATOR")
    print("=" * 60)
    
    # Validate both databases
    quest_ok = validate_database('Database/Epoch/epochQuestDB.lua', 'epochQuestData')
    npc_ok = validate_database('Database/Epoch/epochNpcDB.lua', 'epochNpcData')
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    if quest_ok and npc_ok:
        print("✅ DATABASES ARE CLEAN - Safe to start WoW!")
        sys.exit(0)
    else:
        print("❌ CRITICAL ERRORS FOUND - Fix before starting WoW!")
        print("\nCommon fixes:")
        print("  • Missing commas: python3 fix_all_commas.py")
        print("  • Wrong prefixes: perl -i -pe 's/^epochQuestData(\\[\\d+\\])/\\1/' Database/Epoch/epochQuestDB.lua")
        print("  • Triple coordinates: python3 fix_npc_issues.py")
        print("  • Duplicate IDs: python3 fix_duplicate_npcs.py")
        sys.exit(1)

if __name__ == "__main__":
    main()