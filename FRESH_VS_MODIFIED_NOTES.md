# Fresh Questie 3.3.5 vs Modified Questie - Comparison Notes

## Overview
This document tracks key differences between the fresh 3.3.5 Questie and our heavily modified Project Epoch version. Use this as a reference when debugging issues.

## Critical Structural Differences

### 1. Database Organization
**Fresh Version:**
```
Database/
├── Classic/     # Vanilla WoW data
├── TBC/         # Burning Crusade data  
├── Wotlk/       # WotLK data (WE'RE MISSING THIS!)
│   ├── wotlkNpcDB.lua    # Has correct WotLK npcFlags
│   ├── wotlkQuestDB.lua
│   ├── wotlkItemDB.lua
│   └── wotlkObjectDB.lua
└── Corrections/
```

**Our Version:**
```
Database/
├── Classic/     # Using Classic data for WotLK (WRONG FLAGS!)
├── Epoch/       # Project Epoch overrides
│   ├── epochNpcDB.lua    # 274 placeholder NPCs breaking Stormwind
│   ├── epochQuestDB.lua
│   ├── epochItemDB.lua
│   └── epochObjectDB.lua
└── Corrections/
```

### 2. NPC Flag Values (Critical Issue)

**WotLK (3.3.5) Service Flags:**
- INNKEEPER: 65536 (bit 16)
- BANKER: 256 (bit 8)
- AUCTIONEER: 4096 (bit 12)
- TRAINER: 16 (bit 4)
- Combined example: Innkeeper = 66179 (65536 + other flags)

**Classic Era Flags (What we're using):**
- INNKEEPER: 128 (bit 7) 
- BANKER: Different bit position
- Combined example: Innkeeper = 135 (128 + vendor flags)

**This mismatch is why service NPCs don't show on maps!**

### 3. Database Loading Strategy

**Fresh Version (QuestieInit.lua):**
```lua
-- Loads appropriate expansion data based on game version
if Questie.IsWotlk then
    LoadWotlkDatabase()
elseif Questie.IsTBC then
    LoadTBCDatabase()
else
    LoadClassicDatabase()
end
```

**Our Version (Lines 444-457):**
```lua
-- Aggressively overwrites everything with Epoch data
for id, data in pairs(QuestieDB._epochNpcData) do
    QuestieDB.npcData[id] = data  -- Unconditional override!
    overwritten = overwritten + 1
end
```

### 4. Epoch Override Problems

**Issue:** epochNpcDB.lua has 274 Stormwind NPCs with:
- Placeholder names: "[Epoch] NPC XXXXX"
- Zero service flags: npcFlags = 0
- These override good WotLK data

**Example:**
```lua
-- epochNpcDB.lua
[2455] = {"[Epoch] NPC 2455",1200,1350,30,30,0,{[1519]={{57.7,72.8}}},nil,1519,nil,nil,0,"A",nil,0},
-- Should be:
[2455] = {"Olivia Burnside",3006,3006,45,45,0,{[1519]={{57.66,72.78}}},nil,1519,nil,nil,257,"A","Banker",3},
```

## Key Files to Check When Debugging

### Pin Display Issues
1. `Modules/Map/QuestieMap.lua` - How pins are created
2. `Modules/FramePool/QuestieFramePool.lua` - Pin pooling/recycling
3. `Compat/HBD.lua` - Coordinate translation (PR #39 broke this once)

### Database Issues
1. `Modules/QuestieInit.lua` - Database loading/merging
2. `Database/QuestieDB.lua` - Database access functions
3. `Database/Corrections/QuestieCorrections.lua` - Correction loading

### Service NPC Detection
1. Check npcFlags field (position 15 in NPC array)
2. Verify bit flags match WotLK values, not Classic

## Common Pitfalls

### 1. Wrong Expansion Data
- **Problem:** Using Classic database for WotLK client
- **Symptom:** Service NPCs don't show on map
- **Fix:** Import Wotlk database files

### 2. Aggressive Epoch Overrides
- **Problem:** Placeholder data overwrites good data
- **Symptom:** NPCs show as "[Epoch] NPC XXXXX"
- **Fix:** Conditional override - only if Epoch data is complete

### 3. Disabled Correction Files
- **Problem:** epochStormwindFixes.lua disabled
- **Symptom:** Wrong NPC positions
- **Fix:** Selectively enable or fix in database directly

### 4. Database Reload Issues
- **Problem:** `/reload` doesn't reload database files
- **Symptom:** Changes don't appear
- **Fix:** Must completely restart WoW

## Quick Diagnosis Checklist

When pins aren't showing:
- [ ] Check npcFlags value (should be WotLK flags)
- [ ] Check if epochNpcDB has placeholder override
- [ ] Verify Questie.db.profile.enabled = true
- [ ] Check HBD.lua isn't broken
- [ ] Ensure database was recompiled after changes

## Recommended Fixes

### Immediate Fix
1. Copy `Wotlk/` folder from fresh Questie
2. Update QuestieInit to load WotLK data
3. Fix epoch override logic to be conditional

### Long-term Fix
1. Audit all 274 Stormwind placeholder NPCs
2. Replace with proper data from WotLK database
3. Remove or fix epochStormwindFixes.lua

## Testing Notes

**Fresh Questie Test Results:**
- All service NPCs show correctly
- Proper coordinates for WotLK Stormwind
- No placeholder names
- All service flags working

**Our Version Issues:**
- Missing WotLK database entirely
- 274 broken Stormwind NPCs
- Wrong flag values throughout
- Aggressive override logic

## File Versions

- Fresh Questie: Version from standard 3.3.5 repository
- Our Version: Heavily modified for Project Epoch
- Key Breaking Change: Removal of Wotlk database folder

## Notes for Future Debugging

1. **Always check flag values first** - Classic vs WotLK flags are different
2. **Epoch overrides are aggressive** - They replace everything unconditionally
3. **Database structure matters** - Missing Wotlk folder breaks service detection
4. **Test with fresh Questie** - If it works there, compare the code
5. **Placeholder NPCs are everywhere** - 274 in Stormwind alone

## Commands for Quick Testing

```lua
/dump QuestieDB.npcData[6740]  -- Check NPC data
/console scriptErrors 1          -- Enable error display
/run print(bit.band(66179, 65536) > 0)  -- Test INNKEEPER flag
```

## Status Summary

**Working:**
- Quest tracking (mostly)
- Basic NPC display
- Dungar Longdrink (manually fixed)
- Innkeeper Allison (manually fixed)

**Broken:**
- Most service NPCs in Stormwind
- 274 NPCs with placeholder data
- Missing WotLK database
- Flag detection for services

**Next Steps:**
1. Import WotLK database
2. Fix epoch override logic
3. Audit and fix placeholder NPCs