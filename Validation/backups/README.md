# Backup Organization

This directory contains all backups from the quest database conversion and fixing process.

## Directory Structure

```
backups/
├── quest_db/        # Quest database backups
├── npc_db/          # NPC database backups  
├── item_db/         # Item database backups
├── object_db/       # Object database backups
├── iterative_fixes/ # Step-by-step fix iterations
├── final_versions/  # Final fixed versions
└── sessions/        # Session-specific backups
```

## Backup Naming Convention

- `epochQuestDB_backup_YYYYMMDD_HHMMSS.lua` - Timestamped backups
- `epochQuestDB_FIXED.lua` - Fixed versions
- `epochQuestDB_FINAL.lua` - Final production versions
- `backup_###_description.lua` - Iterative fix backups

## Important Backups

### Quest Database Evolution
1. `epochQuestDB_backup_before_pfquest.lua` - Before pfQuest integration
2. `epochQuestDB_backup_before_nesting_fix.lua` - Before nesting fixes
3. `epochQuestDB_FINAL.lua` - Current production version (99.3% valid)

### Iterative Fixes
The `iterative_fixes/` folder contains numbered backups showing the progression of fixes:
- `backup_001_start.lua` - Initial state
- `backup_002_fixed_26205.lua` - First quest fix
- ... continuing through all iterations

## Recovery Instructions

To restore a backup:
```bash
# From the Validation folder
cp backups/quest_db/[backup_file] ../Database/Epoch/epochQuestDB.lua
```

## Current Status
- Quest database: 99.3% validity (855 of 861 quests valid)
- All critical rshift errors fixed
- Pipeline proven on 800+ quests