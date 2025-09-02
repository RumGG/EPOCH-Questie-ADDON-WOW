# pfQuest-epoch to Questie-Epoch Conversion Summary

## Overview
Successfully analyzed and compared quest data between pfQuest-epoch and Questie-Epoch addons, discovering significant opportunities to expand the Questie database.

## Key Findings

### Database Comparison
- **pfQuest-epoch**: 661 quests
- **Questie-Epoch**: 619 quests
- **Missing in Questie**: 341 quests (may be due to wrath db removal)
- **Placeholder names**: 13 quests that can be updated with proper names

## How pfQuest-epoch Works

### Data Structure
pfQuest uses a modular database structure:

1. **Quest Data** (`db/quests-epoch.lua`):
   - Quest IDs mapped to mechanics (NPCs, objectives, levels, prerequisites)
   - Fields: `start` (quest givers), `end` (turn-in NPCs), `lvl` (level), `race` (faction), `pre` (prerequisites)

2. **Quest Text** (`db/enUS/quests-epoch.lua`):
   - Quest IDs mapped to localized text
   - Fields: `T` (title), `O` (objectives), `D` (description)

3. **NPC Data** (`db/units-epoch.lua`):
   - NPC IDs mapped to spawn locations and metadata
   - Contains coordinates, faction, level information

### Key Differences from Questie
- pfQuest separates data from localization (two-file system)
- Uses compact field notation (`T`, `O`, `D` instead of full names)
- Faction system uses race bitmasks (77 = Alliance, 178 = Horde)

## Conversion Tools Created

### 1. `analyze_pfquest_data.py`
- Basic analysis script
- Counts quests in both databases
- Identifies missing and placeholder quests

### 2. `convert_pfquest_to_questie.py`
- Full conversion script
- Properly extracts all quest data including levels, NPCs, and prerequisites
- Generates ready-to-use Questie format entries
- Converts faction flags correctly

### 3. Generated Files
- `pfquest_conversions.lua`: Contains 50 ready-to-add quests in Questie format
- `pfquest_missing_quests.txt`: List of missing quests
- `pfquest_name_updates.txt`: Quests needing name updates

## Notable Missing Quests Found

Some significant quests missing from Questie but present in pfQuest:

1. **Classic Quests**:
   - [11] Riverpaw Gnoll Bounty (Level 10, Elwynn Forest)
   - [76] The Jasperlode Mine (Level 10, Elwynn Forest)
   - [109] Report to Gryan Stoutmantle (Level 10, Westfall)
   - [487] The Road to Darnassus (Level 8, Teldrassil)

2. **Epoch Custom Chains**:
   - [26297-26301] "Fit For A King" chain (Level 47, 5-quest series)
   - [26546-26557] Elemental Council chain (Level 37-38, Arathi Highlands)
   - [26172-26173] "Falling Up To Grace" chain (Level 48, Hinterlands)

3. **High-Level Content**:
   - [26107] Eau de Parfish (Level 60, Azshara)
   - [26264] Contract #1010: Magical Residue (Level 60)
   - [26477] A Cloak of Shadows (Level 60, Rogue quest)

## How to Use This Data

### Adding Missing Quests to Questie

1. **Review the conversion file**: `pfquest_conversions.lua`
2. **For each quest you want to add**:
   - Copy the quest entry
   - Add it to `Database/Epoch/epochQuestDB.lua`
   - Check if referenced NPCs exist in `epochNpcDB.lua`
   - Add missing NPCs from pfQuest's units database if needed

3. **Update placeholder names**:
   - Find quests starting with "[Epoch] Quest"
   - Replace with proper names from pfQuest data

### Example Quest Addition
```lua
-- From pfquest_conversions.lua
[26297] = {"Fit For A King",{{45865}},{{45865}},nil,47,nil,3,
  {"Collect Swirling Molten Rock and Blistering Flame Essence from earth and fire elementals within the Searing Gorge."},
  nil,nil,nil,nil,26296,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,0,26296,nil,nil,nil,nil,nil}, -- Level 47, pfQuest-epoch
```

### NPC Verification
For quest 26297, check if NPC 45865 exists:
- If missing, find in pfQuest's `units-epoch.lua`
- Add to `epochNpcDB.lua` with proper coordinates

## Recommendations

1. **Prioritize High-Value Additions**:
   - Focus on quest chains (better player experience)
   - Add high-level content first (endgame players need it most)
   - Fix placeholder names (low effort, high impact)

2. **Batch Processing**:
   - Add quests in related groups (same zone, same chain)
   - Test each batch before adding more
   - Document which quests were added from pfQuest

3. **Quality Control**:
   - Verify NPC IDs match between databases
   - Test quest chains for proper prerequisites
   - Ensure coordinates are in correct zone format

## Next Steps

1. **Immediate Actions**:
   - Update the 13 placeholder quest names
   - Add the top 20-30 missing quests
   - Test in-game to verify functionality

2. **Systematic Conversion**:
   - Process remaining 341 missing quests in batches
   - Create automated NPC extraction from pfQuest
   - Build validation script to check data integrity

3. **Long-term Integration**:
   - Consider automated sync between databases
   - Create diff tool to track pfQuest updates
   - Contribute findings back to both projects

## Technical Notes

### Faction Conversion
- pfQuest uses race bitmasks: 77 (Alliance), 178 (Horde), others (Both)
- Questie uses: 1 (Horde), 2 (Alliance), 3 (Both)

### Zone IDs
Both addons use the same zone ID system, making location data compatible.

### Prerequisites
pfQuest tracks quest chains via `pre` field, mapped to Questie fields 12 and 23.

## Files Generated
1. `analyze_pfquest_data.py` - Initial analysis script
2. `convert_pfquest_to_questie.py` - Full conversion script
3. `pfquest_conversions.lua` - Ready-to-use quest data
4. `pfquest_missing_quests.txt` - Missing quest list
5. `pfquest_name_updates.txt` - Name correction list

## Conclusion
This conversion effort could potentially add 341 missing quests to Questie-Epoch, representing a 55% expansion of the quest database. The conversion tools make it straightforward to migrate this data while maintaining data integrity and proper formatting.