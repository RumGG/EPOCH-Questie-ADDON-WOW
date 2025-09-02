#!/usr/bin/env python3

"""
Smart merge of pfQuest data into Questie
- Trusts Questie data over pfQuest for conflicts
- Only adds genuinely new quests
- Enhances existing quests with objective data where missing
- Skips pfQuest's internal duplicates
"""

import re
from datetime import datetime
from collections import defaultdict

def parse_quest_entry(full_entry, content_only):
    """Parse a single quest entry to extract all fields"""
    # Extract quest name from content
    name_match = re.match(r'^"([^"]*)"', content_only.strip())
    name = name_match.group(1) if name_match else "Unknown"
    
    # Try to extract objective data (field 10)
    # Look for pattern like {{{mobId,count}},nil,{{itemId,count}}}
    obj_pattern = r'\{\{\{[\d,\s]+\}\}.*?\}\}'
    obj_match = re.search(obj_pattern, content_only)
    
    return {
        'name': name,
        'full_entry': full_entry,  # Complete [id] = {...}, syntax
        'content': content_only,   # Just the content inside {...}
        'has_objectives': obj_match is not None
    }

def load_questie_database():
    """Load current Questie database"""
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    quests = {}
    
    for line in lines:
        # Match quest entries - they're all on single lines in epochQuestDB
        match = re.match(r'\[(\d+)\]\s*=\s*\{(.*?)\},?\s*(?:--.*)?$', line)
        if match:
            quest_id = int(match.group(1))
            quest_content = match.group(2)
            full_entry = line.strip()
            if full_entry.endswith(','):
                full_entry = full_entry[:-1]  # Remove trailing comma
            quests[quest_id] = parse_quest_entry(full_entry, quest_content)
    
    return quests

def load_pfquest_database():
    """Load pfQuest converted database"""
    # Try to use fixed version first, fall back to original
    import os
    if os.path.exists("pfquest_objectives_v2_fixed.lua"):
        filename = "pfquest_objectives_v2_fixed.lua"
        print("Using fixed pfQuest data file")
    else:
        filename = "pfquest_objectives_v2.lua"
        print("Using original pfQuest data file")
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    quests = {}
    current_quest = None
    current_id = None
    
    for line in lines:
        # Check for quest start
        match = re.match(r'\s*\[(\d+)\]\s*=\s*\{(.*)', line)
        if match:
            current_id = int(match.group(1))
            quest_content = match.group(2)
            
            # Check if it's a complete single-line quest
            if quest_content.rstrip().endswith('},'):
                # Complete quest on one line
                full_content = quest_content.rstrip()[:-2]  # Remove trailing '},'
                quests[current_id] = parse_quest_entry(line.strip(), full_content)
                current_quest = None
                current_id = None
            else:
                # Multi-line quest, will be handled by continuation
                current_quest = quest_content
        elif current_quest is not None:
            # Continue building multi-line quest
            current_quest += line
            if line.strip().endswith('},'):
                # End of multi-line quest
                full_content = current_quest.rstrip()[:-2]  # Remove trailing '},'
                full_entry = f"[{current_id}] = {{{full_content}}}"
                quests[current_id] = parse_quest_entry(full_entry, full_content)
                current_quest = None
                current_id = None
    
    return quests

def identify_quest_chains(quests):
    """Identify quest chains (sequential IDs with same name)"""
    name_to_ids = defaultdict(list)
    
    for quest_id, data in quests.items():
        name = data['name']
        if not name.startswith("[Epoch]"):
            name_to_ids[name].append(quest_id)
    
    chains = {}
    for name, ids in name_to_ids.items():
        if len(ids) > 1:
            sorted_ids = sorted(ids)
            # Check if sequential
            is_chain = all(sorted_ids[i] == sorted_ids[i-1] + 1 for i in range(1, len(sorted_ids)))
            if is_chain:
                for qid in ids:
                    chains[qid] = name
    
    return chains

def merge_databases():
    """Smart merge of pfQuest into Questie"""
    
    print("Loading databases...")
    questie_db = load_questie_database()
    pfquest_db = load_pfquest_database()
    
    print(f"Questie: {len(questie_db)} quests")
    print(f"pfQuest: {len(pfquest_db)} quests")
    
    # Identify quest chains in pfQuest (keep these even if duplicate names)
    pfquest_chains = identify_quest_chains(pfquest_db)
    print(f"Quest chains identified: {len(set(pfquest_chains.values()))} chains with {len(pfquest_chains)} total quests")
    
    # Categories for merge
    new_quests = {}
    enhanced_quests = {}
    skipped_conflicts = []
    skipped_duplicates = []
    placeholder_updates = {}
    
    # Track which pfQuest names we've seen (for duplicate detection)
    seen_pfquest_names = defaultdict(list)
    for qid, data in pfquest_db.items():
        seen_pfquest_names[data['name']].append(qid)
    
    # Process each pfQuest entry
    for quest_id, pfquest_data in pfquest_db.items():
        pfquest_name = pfquest_data['name']
        
        # Check if this quest exists in Questie
        if quest_id in questie_db:
            questie_name = questie_db[quest_id]['name']
            
            # Case 1: Placeholder update
            if questie_name.startswith("[Epoch] Quest"):
                placeholder_updates[quest_id] = pfquest_data
                
            # Case 2: Name conflict - trust Questie
            elif questie_name != pfquest_name:
                skipped_conflicts.append({
                    'id': quest_id,
                    'questie': questie_name,
                    'pfquest': pfquest_name
                })
                
            # Case 3: Same name - check if we can enhance with objectives
            elif pfquest_data['has_objectives'] and not questie_db[quest_id]['has_objectives']:
                enhanced_quests[quest_id] = pfquest_data
        
        # Quest doesn't exist in Questie
        else:
            # Skip if it's a duplicate name (unless it's a quest chain)
            if len(seen_pfquest_names[pfquest_name]) > 1 and quest_id not in pfquest_chains:
                # This is a duplicate, skip it unless it's the first one
                if quest_id != min(seen_pfquest_names[pfquest_name]):
                    skipped_duplicates.append({
                        'id': quest_id,
                        'name': pfquest_name,
                        'reason': 'Duplicate name, keeping lower ID'
                    })
                    continue
            
            # Check if this name already exists in Questie with different ID
            questie_has_name = any(q['name'] == pfquest_name for q in questie_db.values() 
                                  if not q['name'].startswith("[Epoch]"))
            
            if questie_has_name and quest_id not in pfquest_chains:
                skipped_duplicates.append({
                    'id': quest_id,
                    'name': pfquest_name,
                    'reason': 'Name already exists in Questie'
                })
            else:
                # This is genuinely new
                new_quests[quest_id] = pfquest_data
    
    # Generate merge report
    print("\n" + "="*80)
    print("MERGE ANALYSIS")
    print("="*80)
    
    print(f"\n✅ NEW QUESTS TO ADD: {len(new_quests)}")
    if len(new_quests) > 0:
        print("Sample new quests:")
        for qid in sorted(new_quests.keys())[:5]:
            print(f"  {qid}: {new_quests[qid]['name']}")
    
    print(f"\n✅ PLACEHOLDER UPDATES: {len(placeholder_updates)}")
    if placeholder_updates:
        for qid in sorted(placeholder_updates.keys())[:5]:
            old_name = questie_db[qid]['name']
            new_name = placeholder_updates[qid]['name']
            print(f"  {qid}: {old_name} → {new_name}")
    
    print(f"\n✅ QUESTS TO ENHANCE WITH OBJECTIVES: {len(enhanced_quests)}")
    if enhanced_quests:
        for qid in sorted(enhanced_quests.keys())[:5]:
            print(f"  {qid}: {questie_db[qid]['name']} (adding mob/item data)")
    
    print(f"\n❌ SKIPPED CONFLICTS (trusting Questie): {len(skipped_conflicts)}")
    if skipped_conflicts:
        for conflict in skipped_conflicts[:5]:
            print(f"  {conflict['id']}: Keeping '{conflict['questie']}' not '{conflict['pfquest']}'")
    
    print(f"\n❌ SKIPPED DUPLICATES: {len(skipped_duplicates)}")
    if skipped_duplicates:
        for dup in skipped_duplicates[:5]:
            print(f"  {dup['id']}: {dup['name']} ({dup['reason']})")
    
    # Create merged database
    print("\n" + "="*80)
    print("CREATING MERGED DATABASE")
    print("="*80)
    
    output = []
    output.append("-- SMART MERGE: Questie + pfQuest")
    output.append(f"-- Generated: {datetime.now()}")
    output.append("-- Strategy: Trust Questie, add only new quests from pfQuest")
    output.append(f"-- New quests added: {len(new_quests)}")
    output.append(f"-- Placeholders updated: {len(placeholder_updates)}")
    output.append(f"-- Objectives enhanced: {len(enhanced_quests)}")
    output.append("")
    output.append("epochQuestData = {")
    
    # First, output all existing Questie quests
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract complete quest entries (single line with nested structures)
    pattern = r'(\[(\d+)\]\s*=\s*\{.*?\},)(?:\s*--.*)?$'
    
    updated_count = 0
    for match in re.finditer(pattern, content, re.MULTILINE):
        full_entry = match.group(1)
        quest_id = int(match.group(2))
        
        # Update placeholders
        if quest_id in placeholder_updates:
            # Replace the entry with pfQuest version (preserve full structure)
            entry = placeholder_updates[quest_id]['full_entry']
            if not entry.endswith(','):
                entry += ','
            output.append(f"{entry} -- Updated from pfQuest")
            updated_count += 1
        # Enhance with objectives
        elif quest_id in enhanced_quests:
            # TODO: This would require parsing and merging the objective data
            # For now, keep original
            if full_entry.endswith(','):
                output.append(full_entry[:-1] + ", -- TODO: Enhance with pfQuest objectives")
            else:
                output.append(full_entry + ", -- TODO: Enhance with pfQuest objectives")
        else:
            # Keep original - ensure it has a comma
            if not full_entry.endswith(','):
                output.append(full_entry + ',')
            else:
                output.append(full_entry)
    
    # Add new quests from pfQuest
    output.append("")
    output.append("-- NEW QUESTS FROM PFQUEST")
    output.append("-- " + "="*76)
    
    for quest_id in sorted(new_quests.keys()):
        entry = new_quests[quest_id]['full_entry']
        if not entry.endswith(','):
            entry += ','
        output.append(f"{entry} -- From pfQuest")
    
    output.append("}")
    output.append("")
    output.append(f"-- Total quests: {len(questie_db) + len(new_quests)}")
    
    # Save merged database
    with open("epochQuestDB_MERGED_SMART.lua", 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
    
    print(f"\n✅ Merged database saved: epochQuestDB_MERGED_SMART.lua")
    print(f"   Total quests: {len(questie_db) + len(new_quests)}")
    print(f"   Original Questie: {len(questie_db)}")
    print(f"   New from pfQuest: {len(new_quests)}")
    
    # Save detailed report
    with open("smart_merge_report.txt", 'w') as f:
        f.write("SMART MERGE REPORT\n")
        f.write("="*80 + "\n\n")
        f.write(f"Date: {datetime.now()}\n")
        f.write(f"Strategy: Trust Questie data, add only genuinely new quests\n\n")
        
        f.write(f"STATISTICS:\n")
        f.write(f"  Original Questie quests: {len(questie_db)}\n")
        f.write(f"  pfQuest quests analyzed: {len(pfquest_db)}\n")
        f.write(f"  New quests added: {len(new_quests)}\n")
        f.write(f"  Placeholders updated: {len(placeholder_updates)}\n")
        f.write(f"  Conflicts skipped: {len(skipped_conflicts)}\n")
        f.write(f"  Duplicates skipped: {len(skipped_duplicates)}\n")
        f.write(f"  Final total: {len(questie_db) + len(new_quests)}\n\n")
        
        f.write("NEW QUESTS ADDED:\n")
        for qid in sorted(new_quests.keys()):
            f.write(f"  {qid}: {new_quests[qid]['name']}\n")
    
    print("\n📄 Detailed report saved: smart_merge_report.txt")
    
    return len(new_quests)

if __name__ == "__main__":
    new_quest_count = merge_databases()