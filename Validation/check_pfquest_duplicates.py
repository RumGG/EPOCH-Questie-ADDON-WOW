#!/usr/bin/env python3

"""
Check for duplicates in pfQuest extracted data
Also compare with existing Questie database to find conflicts
"""

import re
from collections import defaultdict

def load_quest_database(filepath):
    """Load quest database and extract quest names"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    quests = {}
    pattern = r'\[(\d+)\]\s*=\s*\{"([^"]*)"'
    
    for match in re.finditer(pattern, content):
        quest_id = int(match.group(1))
        quest_name = match.group(2)
        quests[quest_id] = quest_name
    
    return quests

def find_duplicates_within(quests, source_name):
    """Find duplicate quest names within a single database"""
    name_to_ids = defaultdict(list)
    
    for quest_id, name in quests.items():
        if not name.startswith("[Epoch] Quest"):
            name_to_ids[name].append(quest_id)
    
    duplicates = []
    for name, ids in name_to_ids.items():
        if len(ids) > 1:
            duplicates.append((name, ids))
    
    if duplicates:
        print(f"\n{'='*80}")
        print(f"DUPLICATES WITHIN {source_name}:")
        print('='*80)
        for name, ids in sorted(duplicates):
            print(f'  "{name}": {len(ids)} instances')
            for quest_id in ids:
                print(f'    - Quest {quest_id}')
    else:
        print(f"\n✅ No duplicates found within {source_name}")
    
    return duplicates

def compare_databases(questie_db, pfquest_db):
    """Compare two databases for conflicts"""
    conflicts = {
        'same_id_diff_name': [],
        'same_name_diff_id': [],
        'would_overwrite': []
    }
    
    # Check for same ID, different name
    for quest_id in pfquest_db:
        if quest_id in questie_db:
            if questie_db[quest_id] != pfquest_db[quest_id]:
                # Don't count placeholder updates as conflicts
                if not questie_db[quest_id].startswith("[Epoch] Quest"):
                    conflicts['same_id_diff_name'].append({
                        'id': quest_id,
                        'questie_name': questie_db[quest_id],
                        'pfquest_name': pfquest_db[quest_id]
                    })
                else:
                    # This would update a placeholder
                    conflicts['would_overwrite'].append({
                        'id': quest_id,
                        'old': questie_db[quest_id],
                        'new': pfquest_db[quest_id]
                    })
    
    # Check for same name, different ID
    questie_names = {name: qid for qid, name in questie_db.items() 
                     if not name.startswith("[Epoch] Quest")}
    
    for pfquest_id, pfquest_name in pfquest_db.items():
        if pfquest_name in questie_names:
            questie_id = questie_names[pfquest_name]
            if questie_id != pfquest_id:
                conflicts['same_name_diff_id'].append({
                    'name': pfquest_name,
                    'questie_id': questie_id,
                    'pfquest_id': pfquest_id
                })
    
    return conflicts

def main():
    print("="*80)
    print("PFQUEST DUPLICATE & CONFLICT CHECKER")
    print("="*80)
    
    # Load databases
    print("\nLoading databases...")
    
    questie_db = load_quest_database("Database/Epoch/epochQuestDB.lua")
    print(f"Questie database: {len(questie_db)} quests")
    
    pfquest_db = load_quest_database("pfquest_objectives_v2.lua")
    print(f"pfQuest extracted: {len(pfquest_db)} quests")
    
    # Check for duplicates within each database
    print("\n" + "="*80)
    print("CHECKING FOR INTERNAL DUPLICATES")
    print("="*80)
    
    questie_dupes = find_duplicates_within(questie_db, "Questie Database")
    pfquest_dupes = find_duplicates_within(pfquest_db, "pfQuest Data")
    
    # Compare databases
    print("\n" + "="*80)
    print("COMPARING DATABASES FOR CONFLICTS")
    print("="*80)
    
    conflicts = compare_databases(questie_db, pfquest_db)
    
    # Report conflicts
    if conflicts['same_id_diff_name']:
        print(f"\n⚠️  CONFLICTING QUEST IDS (same ID, different names): {len(conflicts['same_id_diff_name'])}")
        print("-"*80)
        for conflict in conflicts['same_id_diff_name'][:10]:  # Show first 10
            print(f"  Quest {conflict['id']}:")
            print(f"    Questie: {conflict['questie_name']}")
            print(f"    pfQuest: {conflict['pfquest_name']}")
        if len(conflicts['same_id_diff_name']) > 10:
            print(f"  ... and {len(conflicts['same_id_diff_name']) - 10} more")
    
    if conflicts['same_name_diff_id']:
        print(f"\n⚠️  DUPLICATE NAMES (different IDs): {len(conflicts['same_name_diff_id'])}")
        print("-"*80)
        for conflict in conflicts['same_name_diff_id'][:10]:
            print(f'  "{conflict["name"]}":')
            print(f'    Questie ID: {conflict["questie_id"]}')
            print(f'    pfQuest ID: {conflict["pfquest_id"]}')
        if len(conflicts['same_name_diff_id']) > 10:
            print(f"  ... and {len(conflicts['same_name_diff_id']) - 10} more")
    
    if conflicts['would_overwrite']:
        print(f"\n✅ PLACEHOLDER UPDATES: {len(conflicts['would_overwrite'])}")
        print("-"*80)
        print("These pfQuest entries would replace placeholder names:")
        for update in conflicts['would_overwrite'][:5]:
            print(f"  Quest {update['id']}: {update['old']} → {update['new']}")
        if len(conflicts['would_overwrite']) > 5:
            print(f"  ... and {len(conflicts['would_overwrite']) - 5} more")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    # Count new quests
    new_quests = [qid for qid in pfquest_db if qid not in questie_db]
    print(f"\n📊 Statistics:")
    print(f"  - New quests to add: {len(new_quests)}")
    print(f"  - Placeholder updates: {len(conflicts['would_overwrite'])}")
    print(f"  - Name conflicts: {len(conflicts['same_id_diff_name'])}")
    print(f"  - Duplicate names: {len(conflicts['same_name_diff_id'])}")
    print(f"  - Internal duplicates (pfQuest): {len(pfquest_dupes)}")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if conflicts['same_id_diff_name']:
        print("  ⚠️  Review name conflicts - keep Questie version or update?")
    if conflicts['same_name_diff_id']:
        print("  ⚠️  Duplicate quest names with different IDs - investigate which is correct")
    if pfquest_dupes:
        print("  ⚠️  pfQuest has internal duplicates - dedupe before merging")
    
    if not conflicts['same_id_diff_name'] and not pfquest_dupes:
        print("  ✅ Safe to merge! No major conflicts detected.")
    
    # Save detailed report
    with open("pfquest_conflict_report.txt", 'w') as f:
        f.write("PFQUEST CONFLICT REPORT\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Total quests in Questie: {len(questie_db)}\n")
        f.write(f"Total quests in pfQuest: {len(pfquest_db)}\n")
        f.write(f"New quests to add: {len(new_quests)}\n\n")
        
        if conflicts['same_id_diff_name']:
            f.write("NAME CONFLICTS (same ID, different name):\n")
            for conflict in conflicts['same_id_diff_name']:
                f.write(f"  {conflict['id']}: '{conflict['questie_name']}' vs '{conflict['pfquest_name']}'\n")
        
        if conflicts['same_name_diff_id']:
            f.write("\nDUPLICATE NAMES (different IDs):\n")
            for conflict in conflicts['same_name_diff_id']:
                f.write(f"  '{conflict['name']}': {conflict['questie_id']} vs {conflict['pfquest_id']}\n")
    
    print("\n📄 Detailed report saved to: pfquest_conflict_report.txt")

if __name__ == "__main__":
    main()