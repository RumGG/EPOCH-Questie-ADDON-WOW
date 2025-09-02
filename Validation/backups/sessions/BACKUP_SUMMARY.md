# Questie Database Backup Summary

## Safe Backups Created

### before_pfquest_integration_20250901_205507
**Date**: September 1, 2025 @ 8:55 PM
**Purpose**: Full backup before integrating 342 new quests from pfQuest conversion
**Contents**:
- epochQuestDB.lua (622 quests)
- epochNpcDB.lua (original NPC database)
- epochItemDB.lua (item database)
- epochObjectDB.lua (object database)
- epochQuestDB.backup.lua (older backup)
- epochNpcDB_FIXED.lua (fixed NPC database)

## Available Converted Data

### pfquest_safe_conversion/epochQuestDB_COMPLETE.lua
- **Total Quests**: 966 (342 new from pfQuest)
- **New Content**: Classic quests, Epoch custom chains, high-level content
- **Status**: Ready to integrate, NOT YET APPLIED

### pfquest_safe_conversion/epochNpcDB_COMPLETE.lua
- **Total NPCs**: 1255 (4 new stub NPCs)
- **Status**: Ready to integrate, NOT YET APPLIED

## How to Restore if Needed

To restore the original database before pfQuest integration:
```bash
cd "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/Questie"
cp SAFE_BACKUPS/before_pfquest_integration_20250901_205507/epochQuestDB.lua Database/Epoch/
cp SAFE_BACKUPS/before_pfquest_integration_20250901_205507/epochNpcDB.lua Database/Epoch/
```

## How to Apply the pfQuest Integration

To apply the 342 new quests from pfQuest:
```bash
cd "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/Questie"
cp pfquest_safe_conversion/epochQuestDB_COMPLETE.lua Database/Epoch/epochQuestDB.lua
cp pfquest_safe_conversion/epochNpcDB_COMPLETE.lua Database/Epoch/epochNpcDB.lua
```

Then restart WoW completely (not just /reload).

## Other Available Backups

- Database/Epoch/epochQuestDB.lua.backup_20250901_093245
- Database/Epoch/epochNpcDB.lua.backup_20250901_093303
- pfquest_safe_conversion/BACKUPS/merge_20250901_194228/
- Multiple older backups from August 27-30

## Important Notes

1. The pfQuest conversion adds 342 new quests with names and basic NPCs
2. Quest objectives (what to kill/collect) are not included - need in-game collection
3. NPC coordinates for 4 new NPCs are missing - need in-game collection
4. All backups are in Dropbox so they're cloud-synced and safe