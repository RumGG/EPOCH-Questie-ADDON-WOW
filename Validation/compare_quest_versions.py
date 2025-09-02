#!/usr/bin/env python3

"""
Compare quest counts across different Questie versions
Shows the progression of quest additions over time
"""

import re
from collections import defaultdict

def count_quests_in_file(filepath, version_name):
    """Count quests in a database file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return None, {}
    
    quests = {}
    # Match quest entries
    pattern = r'\[(\d+)\]\s*=\s*\{"([^"]*)"'
    
    for match in re.finditer(pattern, content):
        quest_id = int(match.group(1))
        quest_name = match.group(2)
        quests[quest_id] = quest_name
    
    # Count categories
    categories = {
        'total': len(quests),
        'placeholders': 0,
        'real_quests': 0,
        'epoch_prefix': 0
    }
    
    for name in quests.values():
        if name.startswith("[Epoch] Quest"):
            categories['placeholders'] += 1
        elif name.startswith("[Epoch]"):
            categories['epoch_prefix'] += 1
        else:
            categories['real_quests'] += 1
    
    return categories, quests

def main():
    print("="*80)
    print("QUESTIE VERSION COMPARISON - QUEST DATABASE GROWTH")
    print("="*80)
    
    versions = [
        ("v1.0.68", "epochQuestDB_v68.lua"),
        ("v1.1 Current", "Database/Epoch/epochQuestDB.lua"),
        ("v1.1 + pfQuest", "epochQuestDB_MERGED_SMART.lua")
    ]
    
    all_data = {}
    all_quests = {}
    
    # Analyze each version
    for version_name, filepath in versions:
        stats, quests = count_quests_in_file(filepath, version_name)
        if stats:
            all_data[version_name] = stats
            all_quests[version_name] = quests
    
    # Display results
    if all_data:
        print("\n📊 QUEST COUNT BY VERSION:")
        print("-"*80)
        
        for version_name, _ in versions:
            if version_name in all_data:
                stats = all_data[version_name]
                print(f"\n{version_name}:")
                print(f"  Total quests:     {stats['total']:,}")
                print(f"  Real quests:      {stats['real_quests']:,}")
                print(f"  Placeholders:     {stats['placeholders']:,}")
                if stats['epoch_prefix']:
                    print(f"  Epoch prefixed:   {stats['epoch_prefix']:,}")
        
        # Calculate growth
        if "v1.0.68" in all_data and "v1.1 Current" in all_data:
            print("\n" + "="*80)
            print("📈 GROWTH ANALYSIS:")
            print("-"*80)
            
            v68 = all_data["v1.0.68"]
            v11 = all_data["v1.1 Current"]
            
            total_growth = v11['total'] - v68['total']
            real_growth = v11['real_quests'] - v68['real_quests']
            
            print(f"\nFrom v1.0.68 to v1.1:")
            print(f"  Total growth:     {total_growth:+,} quests ({total_growth/v68['total']*100:.1f}% increase)")
            print(f"  Real quest growth: {real_growth:+,} quests")
            print(f"  Placeholders reduced: {v68['placeholders'] - v11['placeholders']:+,}")
            
            # Find what was added/removed
            v68_ids = set(all_quests["v1.0.68"].keys())
            v11_ids = set(all_quests["v1.1 Current"].keys())
            
            added = v11_ids - v68_ids
            removed = v68_ids - v11_ids
            
            if added:
                print(f"\n  New quest IDs in v1.1: {len(added)}")
                # Show sample of new quests
                sample_new = sorted(added)[:5]
                for qid in sample_new:
                    print(f"    - {qid}: {all_quests['v1.1 Current'][qid]}")
                if len(added) > 5:
                    print(f"    ... and {len(added)-5} more")
            
            if removed:
                print(f"\n  Removed quest IDs: {len(removed)}")
                # Our duplicate purge removed these
                sample_removed = sorted(removed)[:5]
                for qid in sample_removed:
                    print(f"    - {qid}: {all_quests['v1.0.68'][qid]}")
                if len(removed) > 5:
                    print(f"    ... and {len(removed)-5} more")
        
        # Future projection with pfQuest
        if "v1.1 + pfQuest" in all_data:
            print("\n" + "="*80)
            print("🚀 WITH PFQUEST MERGE:")
            print("-"*80)
            
            merged = all_data["v1.1 + pfQuest"]
            current = all_data["v1.1 Current"]
            
            total_growth = merged['total'] - current['total']
            print(f"\nPotential after pfQuest merge:")
            print(f"  Total quests:     {merged['total']:,}")
            print(f"  Growth:           {total_growth:+,} quests ({total_growth/current['total']*100:.1f}% increase)")
            print(f"  Real quests:      {merged['real_quests']:,}")
            
            # Overall growth from v68
            if "v1.0.68" in all_data:
                v68 = all_data["v1.0.68"]
                overall_growth = merged['total'] - v68['total']
                print(f"\n  Total growth from v1.0.68: {overall_growth:+,} quests ({overall_growth/v68['total']*100:.1f}% increase)")
    
    # Summary timeline
    print("\n" + "="*80)
    print("📅 QUESTIE EPOCH TIMELINE:")
    print("-"*80)
    
    print("""
    v1.0.68 (Original):     619 quests (mostly placeholders)
             ↓
    v1.1 (Current):         581 quests (cleaned duplicates, fixed data)
             ↓
    v1.1 + pfQuest:         915 quests (334 new quests with objectives!)
    
    Net improvement:        +296 quests (48% growth from v68)
                           Better data quality
                           Map markers for objectives
    """)

if __name__ == "__main__":
    main()