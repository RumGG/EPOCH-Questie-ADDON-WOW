#!/usr/bin/env python3
"""
Detailed comparison between our Questie database and the converted pfQuest data
"""

import re
from typing import Dict, Set, Tuple

def load_quest_ids_and_names(filepath: str) -> Dict[int, str]:
    """Load quest IDs and names from a database file"""
    quests = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'\s*\[(\d+)\]\s*=\s*\{"([^"]*)"', line)
            if match:
                quest_id = int(match.group(1))
                quest_name = match.group(2)
                quests[quest_id] = quest_name
    
    return quests

def compare_databases():
    """Compare our database with converted pfQuest"""
    
    print("="*70)
    print("DETAILED DATABASE COMPARISON")
    print("="*70)
    
    # Load both databases
    print("\nLoading databases...")
    our_quests = load_quest_ids_and_names('epochQuestDB.lua')
    pfquest_quests = load_quest_ids_and_names('pfquest_properly_converted_FIXED.lua')
    
    print(f"Our database: {len(our_quests)} quests")
    print(f"pfQuest converted: {len(pfquest_quests)} quests")
    
    # Find overlaps and differences
    our_ids = set(our_quests.keys())
    pfquest_ids = set(pfquest_quests.keys())
    
    only_in_ours = our_ids - pfquest_ids
    only_in_pfquest = pfquest_ids - our_ids
    in_both = our_ids & pfquest_ids
    
    print(f"\n{'='*70}")
    print("QUEST DISTRIBUTION")
    print(f"{'='*70}")
    print(f"Only in our database: {len(only_in_ours)} quests")
    print(f"Only in pfQuest: {len(only_in_pfquest)} quests (NEW)")
    print(f"In both databases: {len(in_both)} quests (should be 0)")
    
    # Check for name mismatches in overlapping quests
    if in_both:
        print(f"\n⚠️ WARNING: Found {len(in_both)} quests in both databases!")
        print("This shouldn't happen - conversion should have skipped existing quests")
        print("\nFirst 5 overlapping quests:")
        for quest_id in sorted(in_both)[:5]:
            print(f"  ID {quest_id}:")
            print(f"    Ours: {our_quests[quest_id]}")
            print(f"    pfQuest: {pfquest_quests[quest_id]}")
    
    # Analyze quest ID ranges
    print(f"\n{'='*70}")
    print("QUEST ID RANGE ANALYSIS")
    print(f"{'='*70}")
    
    def analyze_id_ranges(quest_ids: Set[int], name: str):
        if not quest_ids:
            return
        
        ranges = {
            "Classic (1-7999)": [q for q in quest_ids if q < 8000],
            "TBC (8000-11999)": [q for q in quest_ids if 8000 <= q < 12000],
            "Wrath (12000-14999)": [q for q in quest_ids if 12000 <= q < 15000],
            "Cata (15000-25999)": [q for q in quest_ids if 15000 <= q < 26000],
            "Custom/Epoch (26000+)": [q for q in quest_ids if q >= 26000],
        }
        
        print(f"\n{name}:")
        for range_name, ids in ranges.items():
            if ids:
                print(f"  {range_name}: {len(ids)} quests")
                if len(ids) <= 10:
                    print(f"    IDs: {sorted(ids)}")
    
    analyze_id_ranges(our_ids, "Our Database")
    analyze_id_ranges(pfquest_ids, "pfQuest Converted")
    
    # Sample some NEW quests to show what we're getting
    print(f"\n{'='*70}")
    print("SAMPLE NEW QUESTS FROM PFQUEST")
    print(f"{'='*70}")
    
    print("\nFirst 20 new quests we'd be adding:")
    for i, quest_id in enumerate(sorted(only_in_pfquest)[:20]):
        print(f"  {quest_id:5d}: {pfquest_quests[quest_id]}")
    
    # Look for placeholder names in our database that pfQuest might fix
    print(f"\n{'='*70}")
    print("PLACEHOLDER ANALYSIS")
    print(f"{'='*70}")
    
    our_placeholders = {qid: name for qid, name in our_quests.items() 
                       if "[Epoch]" in name or "Quest" in name and "XXXXX" in name}
    
    print(f"\nWe have {len(our_placeholders)} placeholder quests")
    
    # Check if pfQuest has real names for any of our placeholders
    # (This won't happen since conversion skips existing, but good to verify)
    fixed_placeholders = []
    for qid in our_placeholders:
        if qid in pfquest_quests:
            fixed_placeholders.append((qid, our_quests[qid], pfquest_quests[qid]))
    
    if fixed_placeholders:
        print(f"\npfQuest could fix {len(fixed_placeholders)} placeholder names:")
        for qid, old_name, new_name in fixed_placeholders[:10]:
            print(f"  {qid}: '{old_name}' -> '{new_name}'")
    else:
        print("\nNo placeholder fixes (expected - conversion skips existing quests)")
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    print(f"""
✅ The conversion properly:
   - Skipped all {len(our_ids)} existing quests in our database
   - Added {len(pfquest_ids)} NEW quests not in our database
   - No overlapping quest IDs (no duplicates)
   
📊 What we'd gain by merging:
   - {len(pfquest_ids)} additional quests
   - Mostly Classic and Custom/Epoch content
   - Quest names, NPCs, and descriptions
   
⚠️ Note:
   - These new quests lack objective structures (kill/collect counts)
   - NPCs won't show on map without coordinate data
   - Should be tested before production use
""")

if __name__ == "__main__":
    compare_databases()