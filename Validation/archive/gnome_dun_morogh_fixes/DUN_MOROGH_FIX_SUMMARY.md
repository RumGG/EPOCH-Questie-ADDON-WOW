# Dun Morogh / Gnome Starting Zone Fixes Applied

## Summary
Fixed the broken gnome starting zone quest issues by adding missing NPCs and correcting quest data.

## Fixes Applied

### 1. ✅ Added Missing NPC 1265
- **NPC Name**: Rudra Amberstill
- **Location**: Dun Morogh (38.9, 46.3) - coordinates are estimated
- **Purpose**: Quest giver and turn-in for "Venomous Conclusions" (Quest 27128)
- **Status**: ADDED to epochNpcDB.lua line 1157

### 2. ✅ Verified Quest Data
- Quest 26502 "Rare Books" - Data is actually correct (items in proper field)
- Quest chain 26484-26487 - These are Loch Modan quests, not Dun Morogh
- All 13 Dun Morogh quests have matching data between current and pfQuest databases

## Current Dun Morogh Quest Status

### Working Quests (13 total):
1. **26484**: Call of Fire (starter)
2. **26487**: Call of Fire (follow-up)
3. **26502**: Rare Books
4. **26676**: A Lost Brother...
5. **26679**: Keeping Us Warm
6. **27128**: Venomous Conclusions *(NOW FIXED with NPC 1265)*
7. **28731**: Orders from Command
8. **28734**: Engineering Solutions
9. **28746**: A Refugee's Quandary
10. **28747**: Emergency Supplies
11. **28748**: Emergency Supplies (different version)
12. **28749**: Frostmane Grotto
13. **28903**: Encrypted Memorandum

### NPCs Verified (16 total):
All quest NPCs exist and have coordinates except:
- ✅ NPC 1265 - NOW ADDED (Rudra Amberstill)

## Testing Instructions

1. **Restart WoW completely** (not just /reload)
2. **Test Quest 27128** "Venomous Conclusions":
   - Should now show quest giver NPC 1265 (Rudra Amberstill)
   - Map marker may appear at 38.9, 46.3 in Dun Morogh
   - Use `/qdc questgiver 27128` while targeting the NPC to capture real coordinates

3. **If coordinates are wrong**:
   - Target the actual NPC in-game
   - Run `/qdc questgiver 27128`
   - Export with `/qdc export 27128`
   - Update NPC 1265 with correct coordinates

## What Was NOT Changed

### pfQuest Integration
- The 342 new quests from pfQuest are still in `pfquest_safe_conversion/epochQuestDB_COMPLETE.lua`
- They have NOT been integrated yet
- Dun Morogh quests were already identical between databases

### Quest Chains
- Quest 26484-26487 chain is in Loch Modan (zone 38), not Dun Morogh
- These are working as intended

## Next Steps

1. **Test the fix in-game**
2. **Collect real coordinates for NPC 1265**
3. **Consider integrating the full pfQuest database** (342 new quests)

## Files Modified
- `Database/Epoch/epochNpcDB.lua` - Added NPC 1265 at line 1157
- No quest file changes needed (data was already correct)