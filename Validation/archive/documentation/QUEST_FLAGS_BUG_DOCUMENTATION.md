# Quest Objectives Not Showing on Map - Root Cause Documentation

## The Bug
Quest objectives (mob markers, item locations, etc.) were not appearing on the world map for certain quests, even though the quest data was complete and correct in the database.

## Affected Quests
This issue has been confirmed in two separate starting zones:
1. **Troll Starting Zone** - Quest 28723 "Thievin' Crabs" and related quests
2. **Gnome Starting Zone** - Quest 28725/28901 "Shift into G.E.A.R." and related quests

## Root Cause: questFlags Field

The issue is caused by the `questFlags` field (position 23 in the quest array) being set to `8` instead of `2`.

### Quest Database Structure Reference
```lua
[questId] = {
    [1] name,
    [2] startedBy,
    [3] finishedBy,
    ...
    [23] questFlags,  -- THIS IS THE CRITICAL FIELD
    [24] specialFlags,
    ...
}
```

### The Problem
- **questFlags = 8**: Special quest behavior that PREVENTS objective markers from displaying on the map
- **questFlags = 2**: Normal quest behavior that ALLOWS objective markers to display properly

## Symptoms
When questFlags = 8:
- Quest appears in quest log normally
- Quest tracker shows objectives correctly
- Quest progress updates work
- **BUT: No mob/item/object markers appear on the world map**
- NPCs may show completed quests as available

## The Fix
Change questFlags from 8 to 2 for affected quests:

```lua
-- WRONG (no map markers):
[28901] = {"Quest Name", ..., nil, nil, nil, 8, 0, ...}
                                            ^
                                            Problem!

-- CORRECT (markers show):
[28901] = {"Quest Name", ..., nil, nil, nil, 2, 0, ...}
                                            ^
                                            Fixed!
```

## How to Identify This Issue
1. Player reports quest objectives not showing on map
2. Check quest in database - if questFlags (field 23) = 8, this is likely the cause
3. Compare with a working quest (should have questFlags = 2)

## Additional Complications Found

### Quest ID Mismatches
In the gnome case, there was an additional issue:
- The actual quest ID players receive: 28725
- The quest ID in our database: 28901
- Both were the same quest ("Shift into G.E.A.R.") but with different IDs
- Solution: Add the correct quest ID (28725) to the database

### NPC Quest Lists
NPCs need their questStarts and questEnds lists updated when quest IDs change:
```lua
-- NPC offering duplicate quests:
[46836] = {..., {28725, 28901, 28902}, ...}  -- Shows duplicate

-- Fixed:
[46836] = {..., {28725, 28902, 28903}, ...}  -- No duplicates
```

## Testing Procedure
After making changes:
1. Save all modified files
2. **COMPLETELY EXIT WoW** (not just /reload - this is critical!)
3. Start WoW
4. Check if mob markers appear on map
5. Verify NPC doesn't show duplicate quests

## Common Patterns
This issue often affects:
- Newly added custom quests (Project Epoch specific)
- Quests converted from other databases (pfQuest imports)
- Starting zone quests (where it's most noticeable)

## Prevention
When adding new quests:
1. Always use questFlags = 2 for normal quests
2. Only use questFlags = 8 if there's a specific reason for special behavior
3. Test that objectives appear on the map before considering the quest complete
4. Check that NPCs don't offer duplicate quests

## Historical Fixes
- **Troll Quests**: Fixed questFlags for 28723 and related quests
- **Gnome Quests**: Fixed questFlags for 28725, 28901-28903, 28726-28731
- Pattern: All had questFlags = 8, changed to 2, problem solved

## Keywords for Future Searches
- "objectives not showing on map"
- "mob markers missing"
- "quest markers not appearing"
- "questFlags"
- "field 23"
- "no map icons"
- "tracker works but no map markers"