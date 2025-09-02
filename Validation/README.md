# Questie Validation & Conversion Tools

This folder contains all scripts for validating, converting, and merging quest data from pfQuest into Questie format.

## Table of Contents
1. [Main Pipeline Scripts](#main-pipeline-scripts)
2. [Conversion Tools](#conversion-tools)
3. [Validation Tools](#validation-tools)
4. [Modular Validators](#modular-validators)
5. [Fix Tools](#fix-tools)
6. [Merge & Comparison Tools](#merge--comparison-tools)
7. [Usage Workflow](#usage-workflow)

## Main Pipeline Scripts

### `correct_converter.py` ⭐ **RECOMMENDED**
The correct pfQuest to Questie converter that avoids nesting issues.
```bash
python3 correct_converter.py pfquest_data.lua pfquest_text.lua output.lua
```
- Creates properly formatted 30-field quest structures
- Handles objectives correctly (6-element structure)
- Avoids all nesting issues from the start

### `test_framework.py` ⭐ **ESSENTIAL**
Validates quest database structure and reports issues.
```bash
python3 test_framework.py database.lua
# Compare two databases:
python3 test_framework.py original.lua fixed.lua
```
- Reports pass rate percentage
- Identifies specific structural issues
- Lists problematic quest IDs

### `smart_merge_pfquest.py` ⭐ **KEY TOOL**
Smart merge tool that compares pfQuest data with existing Questie database.
```bash
python3 smart_merge_pfquest.py
```
- Trusts Questie data over pfQuest for conflicts
- Only adds genuinely new quests
- Enhances existing quests with missing objective data
- Generates detailed merge report

## Conversion Tools

### `enhanced_pfquest_converter.py`
Enhanced converter with better objective handling.

### `convert_pfquest_to_questie.py`
Original converter (has nesting issues - use `correct_converter.py` instead).

### `extract_pfquest_objectives.py` / `extract_pfquest_objectives_v2.py`
Extracts objective data from pfQuest format.

## Validation Tools

### `check_pfquest_duplicates.py`
Identifies duplicate quests between pfQuest and Questie databases.
```bash
python3 check_pfquest_duplicates.py
```

### `compare_quest_versions.py`
Compares different versions of the same quest.
```bash
python3 compare_quest_versions.py
```

### `find_duplicate_quests.py`
Finds duplicate quest entries within a single database.
```bash
python3 find_duplicate_quests.py
```

### `analyze_pfquest_data.py`
Analyzes pfQuest data structure and statistics.

## Modular Validators

### `run_validators.py` ⭐ **NEW**
Runs all modular validators to check for common issues.
```bash
python3 run_validators.py
# With auto-fix (when implemented):
python3 run_validators.py --fix
```

### validators_module/
Contains specialized validators for specific issues:
- **double_dash.py** - Detects double dashes that break Lua comments
- **duplicate_entries.py** - Finds duplicate quest/NPC IDs
- **duplicate_zones.py** - Detects duplicate zone spawns in NPCs
- **nil_objectives.py** - Finds quests with nil objective IDs
- **npc_structure.py** - Validates NPC database structure
- **quest_structure.py** - Validates quest database structure
- **wrong_types.py** - Detects wrong data types in fields

## Fix Tools

### `comprehensive_fixer.py`
Fixes all nesting issues in existing damaged databases.
```bash
python3 comprehensive_fixer.py input.lua output.lua
```

### `fix_edge_cases_v2.py`
Fixes specific quests with unwrapped creature objectives.
- Targets 34 known problematic quests
- Wraps creatures in proper 6-element structure

### `fix_final_edge_cases.py`
Handles remaining edge cases with item objectives.
- Fixes items in position 3 of objectives
- Handles corrupted quests

### Other Fix Scripts
- `careful_nesting_fix.py` - Careful approach to nesting issues
- `final_nesting_fix.py` - Final pass nesting fixes
- `comprehensive_string_fix.py` - String formatting fixes
- `find_and_fix_all_objectives.py` - Comprehensive objective fixes

## Merge & Comparison Tools

### `fixed_merge_pfquest.py`
Fixed version of merge script with better handling.

### `simple_merge_fix.py`
Simple merge approach for basic cases.

### `nuke_duplicate_quests.py`
Removes duplicate quest entries (use with caution).

## Usage Workflow

### For NEW pfQuest Data Conversion:

1. **Convert the data correctly:**
```bash
python3 correct_converter.py pfquest_data.lua pfquest_enUS.lua converted.lua
```

2. **Validate the conversion:**
```bash
python3 test_framework.py converted.lua
```

3. **Compare with existing database:**
```bash
python3 smart_merge_pfquest.py
# This will generate:
# - smart_merge_report.txt (what will be merged)
# - epochQuestDB_MERGED_SMART.lua (merged result)
```

4. **Test the merged result:**
```bash
python3 test_framework.py epochQuestDB_MERGED_SMART.lua
```

5. **If tests pass (>99% validity), apply:**
```bash
cp epochQuestDB_MERGED_SMART.lua ../Database/Epoch/epochQuestDB.lua
```

### For FIXING Existing Database:

1. **Test current state:**
```bash
python3 test_framework.py ../Database/Epoch/epochQuestDB.lua
```

2. **If issues found, run comprehensive fixer:**
```bash
python3 comprehensive_fixer.py ../Database/Epoch/epochQuestDB.lua fixed.lua
```

3. **Run edge case fixers if needed:**
```bash
python3 fix_edge_cases_v2.py
python3 fix_final_edge_cases.py
```

4. **Validate final result:**
```bash
python3 test_framework.py fixed.lua
```

## Important Notes

### Quest Structure (30 fields)
```lua
[questId] = {
    [1] "name",                  -- string
    [2] {{NPCs},{Objects},{Items}}, -- startedBy
    [3] {{NPCs},{Objects}},      -- finishedBy
    [4] requiredLevel,           -- int or nil
    [5] questLevel,              -- int
    -- ... (30 fields total)
    [10] objectives,             -- CRITICAL FIELD
    -- ...
}
```

### Objectives Structure (field 10)
```lua
{
    [1] creatures,    -- {{npcId, count, "name"},...}
    [2] objects,      -- {{objectId, count},...}
    [3] items,        -- {{itemId, count},...}
    [4] reputation,   -- {factionId, value}
    [5] killCredit,   -- {{npcIds...}, baseNpcId, "text"}
    [6] spells        -- {{spellId, "text"},...}
}
```

### Common Issues & Solutions

**Quadruple braces:** `{{{{45103,1}}}}` → `{{{45103,1}}}`

**Unwrapped creatures:** `{{{46374,nil}}}` → `{{{46374,nil}},nil,nil,nil,nil,nil}`

**Items in wrong position:** `{{{item}}}` → `{nil,nil,{{item}},nil,nil,nil}`

## Testing Checklist

- [ ] Run test_framework.py - should show >99% pass rate
- [ ] Check brace balance - open and close counts must match
- [ ] No quadruple braces (search for `{{{{`)
- [ ] Restart WoW completely after changes
- [ ] Test quest compilation in-game

## Current Status

As of last run:
- **99.3% validity rate** achieved
- 855 of 861 quests properly structured
- Pipeline tested and proven on 800+ quests
- Ready for large-scale conversions