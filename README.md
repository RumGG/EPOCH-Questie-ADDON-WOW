### ☕ Support Development
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support%20Development-orange?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/trav346)

If you find Questie helpful, consider [buying me a coffee](https://buymeacoffee.com/trav346) to support continued development!

---

### 📝 Want to Help? Easy Data Collection!

**Quick Start:**
1. Type `/qdc enable` to turn on collection - this should persist through log in/out
2. Quest normally - Questie automatically detect if a quest is not in the database and begin collecting at a for it!
3. Type `/qdc export` when done questing
4. Share on [GitHub](https://github.com/trav346/Questie/issues/new)

**Not feeling up to it?** No problem! Just use Questie normally. /qdc disable

## v1.0.60-hotfix2 - Latest Release

### Massive Update: 300+ Quests Added, and Critical Errors Fixed!

**Hotfix2 Updates:**
- Fixed quest 26768 "Barrel Down" compilation error
- Fixed load order error causing crashes on startup
- Added toggle for [DATA] messages - collect silently without chat spam! (`/qdc messages`)

#### All Runtime Errors Fixed
- **No More Crashes**: Fixed AvailableQuests and QuestieTracker nil errors
- **Chat Filter Working**: QuestieShutUp now properly blocks party spam
- **Map Errors Gone**: Custom Project Epoch zones no longer cause errors
- **Data Collector Silent**: No more chat spam - silently tracks quest data

####  All Service NPCs Now Working!
- **WotLK Database Imported**: Fixed version detection for 3.3.5 client
- **All Cities Fixed**: Innkeepers, bankers, auctioneers, trainers show everywhere
- **Stormwind Fully Functional**: All service NPCs at correct Project Epoch locations. Let me know if I missed any.
- **No More Placeholders**: Removed 274 "[Epoch] NPC XXXXX" entries

####  300+ New Quests Added (GitHub Issues #32-87)
This release combines all quest additions from versions 1.0.56 through 1.0.60:

**Starting Zones Complete:**
- **Gnome**: 18 quests with complete NPC data
- **Troll/Orc**: 21 quests including "The Darkspear Tribe", "Banana Bonanza"
- **Human**: Hunter training, Tattered Letter, Soaked Barrel chains

**Major Quest Chains:**
- **Duskwood**: Riders In The Night, Life In Death, Until Death Do Us Part chains
- **Westfall**: Barroom Blitz chain, Hand of Azora chain, The Killing Fields
- **Ironforge Airfield**: Complete 10-quest chain with proper NPCs
- **The Hinterlands**: 11 Alliance quests including "A Sticky Situation" series
- **Desolace**: "The Argus Wake" 5-quest chain (42-44)

**PvP Content:**
- **Ashenvale**: "Fight for Warsong Gulch" battleground introduction
- **Multiple Zones**: 8 "Call to Skirmish" quests for world PvP

**Level 1-60 Coverage:**
- Elwynn Forest, Darkshore, Stranglethorn Vale, Hillsbrad Foothills
- The Barrens, Stonetalon Mountains, Thousand Needles, Mulgore
- Arathi Highlands, Badlands, Swamp of Sorrows, Tanaris
- Winterspring, Eastern Plaguelands, Searing Gorge

#### 🛠️ Major Fixes Since v1.0.56

**Container Collection Fixed:**
- Sun-Ripened Banana containers now properly identified
- Ground object quests show accurate map pins
- Auto-rescan after reload - no manual commands needed

**Quest Tracking Improvements:**
- TomTom no longer changes your tracker sort preference
- Completed quests properly removed from tracker
- Quest items don't cause tracking to break

**Database Cleanup:**
- Fixed duplicate quest entries
- Removed conflicting stub entries
- Updated 100+ quests with complete data

#### 📝 Children's Week Removed
- Seasonal quest no longer shows year-round
- NPCs properly blacklisted

---

## 💡 Known Issues

- Some Epoch quests still have placeholder data - please use /qdc enable to help collect data
- Map icons may not appear for quests with incomplete NPC/object data
- Project Epoch has modified numerous vanilla quests to be cross-faction, causing conflicts with the original database
- Modified vanilla quests may trigger "missing quest" alerts even though they exist (due to significant changes from original)

---

## Previous Releases

### v1.0.53
New feature!

 -Auto Waypoint has been added thanks to @fing3rguns. To enable, /questie -> Tracker -> tick box for Auto Waypoint in Tom Tom section. (must have Tom Tom installed and enabled)

  🎉 Major Improvements

  Quest Tracker Reliability

  - Fixed critical tracker crashes when encountering missing Epoch quest data
  - Implemented runtime quest stubbing - tracker now works even for quests not in the database
  - Fixed "attempt to compare number with table" errors that prevented tracker from loading
  - Resolved tracker showing only 5 of 25 quests - fixed AutoUntrackedQuests filtering logic
  - Added /questie tracker clear command to reset untracked quest list

  Database Improvements

  - Added 200+ missing Project Epoch quests with proper data
  - Fixed quest stubbing mechanism to include all 30 required fields (was only 18)
  - Added automatic database corruption detection and recovery
  - Fixed nil comparison errors when quests have missing sourceItemId values

  Community Data Collection System

  - Added exploration objective tracking for area/event type quests
  - Fixed mob data not appearing in quest exports
  - Fixed data purge button to properly clear SavedVariables
  - Added quest giver capture for incomplete data detection
  - Improved coordinate tracking for all objective types

  📊 Quest Data Updates

  New Quests Added

  - Call to Skirmish: Ashenvale (26364)
  - Call to Skirmish: Hillsbrad Foothills (26366)
  - A Lost Warrior quest chain (26795, 26796)
  - WANTED: Archmage Zygor (26824)
  - Scarlet Intelligence (26941)
  - Northshore Mine (26937) - corrected with Dark Ooze mobs
  - Plus 195+ other Epoch quests

  Fixed Quests

  - Northshore Mine (26937): Now correctly shows Dark Ooze (45895) as target instead of wrong mob
  - A Box of Relics (26926): Properly configured as exploration + item collection quest
  - Removed placeholder "[Epoch]" prefixes from properly implemented quests

  NPC Corrections

  - Fixed Jasper Greene NPC ID (45885, not 45886)
  - Added Tog'thar in Hillsbrad Foothills
  - Added Dark Ooze with proper spawn locations
  - Corrected 50+ other NPC entries

  🛠️ Technical Fixes

  Memory and Performance

  - Fixed memory leaks in quest tracking
  - Improved database validation performance
  - Reduced tracker update frequency for better FPS

  Error Handling

  - Added defensive nil checks throughout codebase
  - Improved error messages for debugging
  - Added diagnostic commands for troubleshooting

  📝 Documentation

  - Added installation instructions with clear steps
  - Updated README with current features
  - Removed outdated version information

  🔧 Developer Tools

  New Commands

  - /questie tracker clear - Reset auto-untracked quests
  - /epochvalidate - Validate database integrity
  - /qdc export <questId> - Export specific quest data
  - /qdc show - View all tracked quest data

  Data Collection Improvements

  - Exploration objectives now tracked with exact trigger coordinates
  - Mob kill locations properly exported
  - Item drop sources linked to specific mobs
  - Object interactions captured with coordinates

  🐛 Bug Fixes

  - Fixed tracker not showing when no quests in log
  - Fixed map pin displacement when using zoom addons (Magnify compatibility)
  - Fixed quest stubbing failures for runtime-generated quests
  - Fixed SavedVariables corruption on reload
  - Fixed quest prefixes showing incorrectly ([Epoch] vs [Missing])
  - Fixed tracker initialization errors with corrupted saved data


  🙏 Contributors

  Special thanks to:
  - @Bennylavaa for testing and bug reports
  - @desizt and @esurm for the original data collection system
  - All players submitting quest data through GitHub

  ---
  To Update: Download from GitHub, extract to your AddOns folder, and rename from Questie-Epoch-master to Questie
