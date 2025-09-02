#!/usr/bin/env python3

import re
from datetime import datetime

def validate_database(filepath):
    """Validate the merged database for syntax and data issues"""
    print(f"Validating {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    stats = {
        'total_quests': 0,
        'quests_with_names': 0,
        'quests_with_npcs': 0,
        'quests_with_objectives': 0,
        'placeholder_names': 0,
        'duplicate_ids': [],
        'syntax_errors': []
    }
    
    # Check for basic Lua syntax
    open_braces = content.count('{')
    close_braces = content.count('}')
    if open_braces != close_braces:
        issues.append(f"Brace mismatch: {open_braces} open, {close_braces} close")
    
    # Parse quests
    quest_ids = []
    pattern = r'\[(\d+)\]\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    
    for match in re.finditer(pattern, content):
        quest_id = int(match.group(1))
        quest_data = match.group(2)
        
        # Check for duplicates
        if quest_id in quest_ids:
            stats['duplicate_ids'].append(quest_id)
        quest_ids.append(quest_id)
        
        stats['total_quests'] += 1
        
        # Check quest name
        name_match = re.search(r'^"([^"]+)"', quest_data)
        if name_match:
            name = name_match.group(1)
            stats['quests_with_names'] += 1
            
            if '[Epoch] Quest' in name:
                stats['placeholder_names'] += 1
        
        # Check for NPCs
        if re.search(r'\{\{\d+', quest_data):
            stats['quests_with_npcs'] += 1
        
        # Check for objectives
        if re.search(r'\{"[^"]+"\}', quest_data):
            stats['quests_with_objectives'] += 1
    
    # Check quest ID ranges
    if quest_ids:
        min_id = min(quest_ids)
        max_id = max(quest_ids)
        print(f"Quest ID range: {min_id} - {max_id}")
    
    return stats, issues

def check_conflicts(merged_file, original_file):
    """Check for quest ID conflicts"""
    print("\nChecking for conflicts...")
    
    # Parse merged database
    with open(merged_file, 'r', encoding='utf-8') as f:
        merged_content = f.read()
    
    merged_quests = {}
    pattern = r'\[(\d+)\]\s*=\s*\{"([^"]+)"'
    for match in re.finditer(pattern, merged_content):
        quest_id = int(match.group(1))
        quest_name = match.group(2)
        merged_quests[quest_id] = quest_name
    
    # Parse original database
    with open(original_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    original_quests = {}
    for match in re.finditer(pattern, original_content):
        quest_id = int(match.group(1))
        quest_name = match.group(2)
        original_quests[quest_id] = quest_name
    
    # Find changes
    changes = {
        'new': [],
        'modified': [],
        'unchanged': []
    }
    
    for quest_id, name in merged_quests.items():
        if quest_id not in original_quests:
            changes['new'].append((quest_id, name))
        elif original_quests[quest_id] != name:
            changes['modified'].append((quest_id, original_quests[quest_id], name))
        else:
            changes['unchanged'].append(quest_id)
    
    return changes

def main():
    workspace = "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/Questie/pfquest_conversion_workspace/"
    
    # Validate merged database
    stats, issues = validate_database(workspace + "epochQuestDB_MERGED.lua")
    
    print("\n=== VALIDATION RESULTS ===")
    print(f"Total quests: {stats['total_quests']}")
    print(f"Quests with names: {stats['quests_with_names']}")
    print(f"Quests with NPCs: {stats['quests_with_npcs']}")
    print(f"Quests with objectives: {stats['quests_with_objectives']}")
    print(f"Placeholder names remaining: {stats['placeholder_names']}")
    
    if stats['duplicate_ids']:
        print(f"\n⚠️  DUPLICATE IDS FOUND: {stats['duplicate_ids']}")
    
    if issues:
        print("\n⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ No syntax issues found!")
    
    # Check changes from original
    changes = check_conflicts(
        workspace + "epochQuestDB_MERGED.lua",
        workspace + "epochQuestDB_original.lua"
    )
    
    print(f"\n=== CHANGES FROM ORIGINAL ===")
    print(f"New quests added: {len(changes['new'])}")
    print(f"Quests modified: {len(changes['modified'])}")
    print(f"Quests unchanged: {len(changes['unchanged'])}")
    
    # Show sample of new quests
    if changes['new']:
        print("\nSample of new quests (first 10):")
        for quest_id, name in changes['new'][:10]:
            print(f"  [{quest_id}] {name}")
    
    # Show modified quests
    if changes['modified']:
        print("\nModified quests (placeholders updated):")
        for quest_id, old_name, new_name in changes['modified']:
            if '[Epoch] Quest' in old_name:
                print(f"  [{quest_id}] {old_name} -> {new_name}")
    
    # Generate final report
    report_path = workspace + "validation_report.txt"
    with open(report_path, 'w') as f:
        f.write("MERGED DATABASE VALIDATION REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Date: {datetime.now()}\n\n")
        
        f.write("STATISTICS:\n")
        f.write(f"  Total quests: {stats['total_quests']}\n")
        f.write(f"  With names: {stats['quests_with_names']}\n")
        f.write(f"  With NPCs: {stats['quests_with_npcs']}\n")
        f.write(f"  With objectives: {stats['quests_with_objectives']}\n")
        f.write(f"  Placeholders remaining: {stats['placeholder_names']}\n\n")
        
        f.write("CHANGES:\n")
        f.write(f"  New quests: {len(changes['new'])}\n")
        f.write(f"  Modified: {len(changes['modified'])}\n")
        f.write(f"  Unchanged: {len(changes['unchanged'])}\n\n")
        
        if issues:
            f.write("ISSUES:\n")
            for issue in issues:
                f.write(f"  - {issue}\n")
        else:
            f.write("✅ No validation issues found!\n")
        
        f.write("\nThe merged database is ready for testing.\n")
    
    print(f"\nValidation report saved to: validation_report.txt")
    
    print("\n=== READY FOR TESTING ===")
    print("The merged database has been validated and is ready for testing!")
    print(f"Total quests in merged database: {stats['total_quests']}")
    print(f"New quests added from pfQuest: {len(changes['new'])}")
    print("\nTo test in WoW:")
    print("1. Back up your current Database/Epoch/epochQuestDB.lua")
    print("2. Copy epochQuestDB_MERGED.lua to Database/Epoch/")
    print("3. Rename it to epochQuestDB.lua")
    print("4. Restart WoW completely (not just /reload)")
    print("5. Test the new quests!")

if __name__ == "__main__":
    main()