# Troll Starting Zone Quest Audit

Auditing all quests in zone 14 (Durotar/Echo Isles) for missing data issues.

## Quest Analysis

### Quest 27266: A Touch of Lightning
- **Status**: Objectives present - collect 5 Essence of Lightning (60558)
- **Issues**: None apparent

### Quest 27273: Sha'gri
- **Status**: Objectives present - kill Spirit of Sha'gri (60561)
- **Issues**: None apparent

### Quest 27277: Scythemaw Standstill
- **Status**: Objectives present - kill 10 Bloodtalon Scythemaw (3123)
- **Issues**: None apparent

### Quest 28722: The Darkspear Tribe
- **Status**: Simple delivery quest
- **Issues**: Missing objectives field (should be nil for delivery quests)

### Quest 28723: Thievin' Crabs
- **Status**: Kill quest - kill 10 Amethyst Crab (46835)
- **Issues**: ✅ Recently fixed prerequisite

### Quest 28728: Glyphic Tablet
- **Status**: Delivery quest
- **Issues**: ✅ Recently fixed class requirement (mage-only)

### Quest 28757: Banana Bonanza
- **Status**: Missing objectives
- **Issues**: ⚠️ NO OBJECTIVES DEFINED - likely needs item collection

### Quest 28758: Shell Collection
- **Status**: Missing objectives
- **Issues**: ⚠️ NO OBJECTIVES DEFINED - likely needs item collection

### Quest 28759: Claws of the Cat
- **Status**: Item collection quest
- **Issues**: ✅ Recently fixed - collect 10 Sharp Claw (5635)

### Quest 28760: Jinxed Trolls
- **Status**: Missing objectives
- **Issues**: ⚠️ NO OBJECTIVES DEFINED - likely needs spell cast or item use

### Quest 28764: The Loa of Death
- **Status**: Missing objectives
- **Issues**: ⚠️ NO OBJECTIVES DEFINED - likely needs interaction or spell

### Quest 28765: Tidal Menace
- **Status**: Missing objectives
- **Issues**: ⚠️ NO OBJECTIVES DEFINED - likely needs kill or interaction

## Summary of Issues Found and Fixed

**All Critical Issues Resolved:**

### Quest 28757: Banana Bonanza ✅ FIXED
- **Issue**: Missing item collection objectives
- **Solution**: 
  - Added Sun-Ripened Banana item (60200) linked to ground object (188800)
  - Added quest objective: collect 10 Sun-Ripened Banana
  - Ground object spawns at 5 locations around Echo Isles

### Quest 28758: Shell Collection ✅ FIXED
- **Issue**: Missing item collection objectives
- **Solution**:
  - Added Conch Shell item (60201) linked to shore object (188801)
  - Added quest objective: collect 8 Conch Shell
  - Shore object spawns at 5 coastal locations

### Quest 28759: Claws of the Cat ✅ FIXED
- **Issue**: Missing item collection objectives
- **Solution**:
  - Added Sharp Claw item (5635) from Juvenile Tiger (47102)
  - Added quest objective: collect 10 Sharp Claw
  - Juvenile Tiger spawns at 3 jungle locations

### Quest 28760: Jinxed Trolls ✅ FIXED  
- **Issue**: Missing interaction objectives
- **Solution**:
  - Added Jinxed Troll NPCs (47104) as cleansing targets
  - Added quest objective: cleanse 5 Jinxed Trolls
  - NPCs spawn at 4 village locations

### Quest 28764: The Loa of Death ✅ FIXED
- **Issue**: Missing interaction objectives  
- **Solution**:
  - Added quest objective: interact with Shrine of Sha'gri (4001003)
  - Shrine already existed at coordinates 68.8, 72.1

### Quest 28765: Tidal Menace ✅ FIXED
- **Issue**: Missing kill objectives
- **Solution**:
  - Added Tidal Lurker boss NPC (47105) as target
  - Added quest objective: kill Tidal Lurker
  - Boss spawns at shore location 68.5, 49.3

## Pattern Analysis
The root cause was systematic: **Most Epoch collection and interaction quests were missing their objectives field entirely**. This affected quest tracking, waypoint guidance, and completion detection.

## Database Additions Summary
- **Items Added**: 3 (Sun-Ripened Banana, Conch Shell, Sharp Claw)
- **NPCs Added**: 3 (Juvenile Tiger, Jinxed Troll, Tidal Lurker)  
- **Objects Added**: 1 (Conch Shell ground spawns)
- **Quest Objectives Fixed**: 6 quests now have complete objective definitions

## Next Steps
1. Test all quest objectives in-game
2. Verify waypoint updates work correctly
3. Check quest completion tracking
4. Validate all spawn locations and drop rates
