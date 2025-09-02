# Gnome Quest Debug Report

## Current Issues
1. ❌ **Underfed Trogg not showing on map** despite quest 28901 being in quest log
2. ❌ **Quest tooltip shows quests as available** when already accepted (28901, 28902, 28903)
3. ❌ **No mob markers** appearing for quest objectives

## Data Verification

### Quest 28901: "Shift into G.E.A.R."
```lua
-- Current in epochQuestDB.lua line 365:
[28901] = {"Shift into G.E.A.R.",{{46836}},{{46836}},nil,1,nil,nil,{"Kill 10 Underfed Troggs."},nil,{{{46837,10,"Underfed Trogg"}}},nil,nil,nil,nil,nil,nil,1,nil,nil,nil,nil,nil,8,0,nil,nil,nil,nil,nil,nil}
```
✅ Quest data looks CORRECT - has objectives pointing to NPC 46837

### NPC 46837: Underfed Trogg
```lua
-- Current in epochNpcDB.lua:
[46837] = {"Underfed Trogg",nil,nil,1,2,0,{[1]={{24.5,60.2},{25.1,61.5},{23.8,62.1},{24.9,58.9},{23.2,59.8}}},nil,1,nil,nil,nil,"A",nil,0}
```
✅ NPC data looks CORRECT - has 5 spawn coordinates in zone 1 (Dun Morogh)

### NPC 46836: Quest Giver
```lua
-- BEFORE FIX:
[46836] = {"Tinker Captain Whistlescrew",nil,nil,5,5,0,{[1]={{24.7,59.1}}},nil,1,{27034,27035,27036,28901,28902,28903},{27034,27035,28901,28902},11,"A",nil,0}

-- AFTER FIX:
[46836] = {"Tinker Captain Whistlescrew",nil,nil,5,5,0,{[1]={{24.7,59.1}}},nil,1,{28901,28902,28903},{28901,28902},nil,"A",nil,2}
```

### Issues Fixed:
1. ✅ Removed non-existent quests (27034, 27035, 27036)
2. ✅ Fixed questEnds - removed 28903 (it ends at NPC 46882)
3. ✅ Fixed factionID field (was 11, now nil)
4. ✅ Set npcFlags to 2 (questgiver)

## Potential Root Causes

### 1. Database Not Recompiled
**Most likely issue!** After making changes:
- Run `/qdc recompile` in-game
- OR completely restart WoW (not just /reload)

### 2. Objective Structure Issue
The objectives field looks correct but double-check format:
- Field 10: `{{{46837,10,"Underfed Trogg"}}}`
- Format: `{creatures,objects,items}`
- Creatures: `{{npcId,count,"name"}}`

### 3. Faction/Race Restrictions
- NPCs are marked as "A" (Alliance)
- Quest has no race restrictions (field 6 is nil)
- Should work for gnomes

### 4. Zone ID Mismatch
- Quest zone: 1 (Dun Morogh) ✅
- NPC zone: 1 (Dun Morogh) ✅
- Mob zone: 1 (Dun Morogh) ✅

## Testing Steps

1. **Force Database Recompilation:**
   ```
   /qdc recompile
   ```
   
2. **Check Quest Status:**
   ```
   /dump QuestieDB:GetQuest(28901)
   ```
   
3. **Check NPC Data:**
   ```
   /dump QuestieDB:GetNPC(46837)
   ```

4. **Manual Verification:**
   - Open quest log
   - Click on quest 28901
   - Check if objectives show "Kill Underfed Trogg (0/10)"
   - Check map for any markers

5. **Data Collection Test:**
   ```
   /qdc enable
   /qdc export 28901
   ```
   Check what the data collector sees

## Similar Troll Data Issues?
You mentioned this is similar to troll data problems. Common issues were:
- Wrong zone IDs
- Missing or incorrect NPC IDs
- Malformed objective structure
- Quest chain prerequisites broken

## Emergency Fix
If nothing else works, try this minimal test entry:
```lua
-- Simplified test version
[28901] = {"Shift into G.E.A.R. TEST",{{46836}},{{46836}},nil,1,nil,nil,{"Kill 10 Underfed Troggs."},nil,{{{46837,10}}},nil,nil,nil,nil,nil,nil,1,nil,nil,nil,nil,nil,8,0,nil,nil,nil,nil,nil,nil}
```

## Next Steps
1. **Recompile database** - Most important!
2. **Check error log** - `/console scriptErrors 1`
3. **Test with fresh character** - Rule out character-specific issues
4. **Capture real data** - Use data collector to see what game sees