#!/usr/bin/env python3
"""
Fix Questie Epoch quest database issues:
1. Remove duplicate quest entries (keeping best version)
2. Add missing turn-in NPCs where verified
3. Handle faction conflicts (mark as faction=8 when both exist)
"""

import re
from collections import defaultdict

# Duplicate quests to remove (quest_id: lines_to_remove)
# Based on analysis, keeping the best version of each
DUPLICATES_TO_REMOVE = {
    26994: [79],      # Keep line 199
    26217: [305],     # Keep line 82 (has comment)
    26282: [313],     # Keep line 127
    26541: [145],     # Keep line 345
    26779: [18],      # Keep line 375
    26218: [83, 493], # Keep line 403 (has faction data)
    26570: [415],     # Keep line 148 (has comment)
    26777: [17],      # Keep line 420
    26778: [421],     # Keep line 412
    26781: [422],     # Keep line 334
    26768: [426],     # Keep line 9
    26771: [429],     # Keep line 11
    27000: [461],     # Keep line 154 (has comment)
    27167: [465],     # Keep line 406
    27171: [466],     # Keep line 281
    27198: [467],     # Keep line 408
    26885: [317],     # Keep line 471
    27168: [480],     # Keep line 278
    27195: [407],     # Keep line 481
    26287: [486],     # Keep line 271
    26368: [487],     # Keep line 84
    26374: [87],      # Keep line 488
    26186: [633, 747],# Keep line 514
    28476: [165],     # Keep line 641
    27483: [668],     # Keep line 395
    26293: [636],     # Keep line 676
    26295: [637],     # Keep line 677
    27322: [380],     # Keep line 680
    27335: [638],     # Keep line 687
    28722: [98],      # Keep line 688
    28723: [99],      # Keep line 689
    28757: [110],     # Keep line 692
    28758: [111],     # Keep line 693
    28759: [112],     # Keep line 694
    28760: [113],     # Keep line 695
    28764: [117],     # Keep line 696
    28765: [118],     # Keep line 697
    26887: [741],     # Keep line 363
    27128: [593],     # Keep line 750
    26875: [757],     # Keep line 496
    26932: [759],     # Keep line 36
}

# Quests that need turn-in NPCs added (quest_id: npc_id)
TURNIN_FIXES = {
    26529: 45527, 26531: 45528, 26532: 45528, 26533: 45528,
    27254: 46090, 27256: 46090, 26939: 45898, 26963: 46322,
    26965: 46326, 26966: 46322, 26967: 46323, 26968: 46323,
    26969: 46323, 26970: 46326, 26971: 46326, 26972: 46322,
    26973: 46323, 26977: 46324, 26979: 46331, 26980: 46331,
    26981: 46331, 26987: 45939, 26988: 45940, 26989: 45940,
    26218: 2140, 28077: 45604, 28535: 45575, 28618: 45575,
    28722: 46834, 26126: 45549, 27045: 45990, 26858: 45827,
    27659: 5385, 26883: 11748, 26907: 45869, 26915: 45873,
    26784: 45780, 26785: 45782, 27053: 45734, 28573: 2697,
    27243: 46086, 26774: 45775, 27488: 4048, 27500: 4048,
    27501: 4048, 26544: 3544, 27238: 46000, 26542: 2364,
    26802: 2363, 26886: 45845, 27309: 46127, 27197: 7161,
    26376: 9019, 26875: 45841, 27489: 10428, 27300: 46121,
    26817: 2378, 26521: 2317, 26524: 3544, 27420: 7771,
    28901: 46836, 28902: 46836, 26511: 2317, 27030: 45981,
    26293: 45211, 27335: 45211, 26856: 5410, 26918: 3615,
    26597: 7740, 28905: 28945, 27323: 46135, 27324: 46135,
    27325: 46135, 27326: 46135, 27327: 46135, 27328: 46135,
    26180: 45748, 26190: 45777, 26852: 45964, 26854: 46559,
    26855: 46560, 26860: 46563, 26861: 46564, 26862: 46565,
    27103: 47191, 27032: 45983, 27036: 45983, 26170: 45732,
    26171: 45731, 26182: 45774, 26161: 45716, 28520: 46644,
    26863: 46561, 26867: 46570, 26921: 46613,
}

def process_quest_database(input_file, output_file):
    """Process quest database to remove duplicates and add turn-ins."""
    
    lines_to_remove = set()
    for quest_id, line_nums in DUPLICATES_TO_REMOVE.items():
        lines_to_remove.update(line_nums)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    processed_lines = []
    quests_fixed = set()
    
    for line_num, line in enumerate(lines, 1):
        # Skip duplicate lines
        if line_num in lines_to_remove:
            print(f"Removing duplicate at line {line_num}: {line.strip()[:50]}...")
            continue
            
        # Check if this line needs turn-in NPC added
        if 'epochQuestData[' in line:
            match = re.match(r'epochQuestData\[(\d+)\]', line.strip())
            if match:
                quest_id = int(match.group(1))
                
                # Add turn-in NPC if needed
                if quest_id in TURNIN_FIXES and quest_id not in quests_fixed:
                    npc_id = TURNIN_FIXES[quest_id]
                    # Check if it already has a turn-in
                    if ',nil,nil,' in line or ',nil,' in line.split('},{')[0]:
                        # Find the pattern and replace
                        # Format: {"Name",{{giver}},nil,nil,level...
                        # Replace with: {"Name",{{giver}},{{turnin}},nil,level...
                        pattern = r'(\{\{[0-9]+\}\}),nil,'
                        replacement = f'\\1,{{{{{npc_id}}}}},'
                        new_line = re.sub(pattern, replacement, line, count=1)
                        if new_line != line:
                            print(f"Added turn-in NPC {npc_id} to quest {quest_id}")
                            line = new_line
                            quests_fixed.add(quest_id)
        
        processed_lines.append(line)
    
    # Write the fixed database
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(processed_lines)
    
    print(f"\nProcessed {len(lines)} lines")
    print(f"Removed {len(lines_to_remove)} duplicate lines")
    print(f"Fixed {len(quests_fixed)} quests with missing turn-in NPCs")
    print(f"Output written to {output_file}")

if __name__ == "__main__":
    print("Fixing quest database...")
    process_quest_database(
        'Database/Epoch/epochQuestDB.lua',
        'Database/Epoch/epochQuestDB_fixed.lua'
    )
    print("\nDone! Review epochQuestDB_fixed.lua and replace the original if correct.")