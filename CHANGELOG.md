# Changelog

## [1.0.60-hotfix] - 2025-08-30

### Fixed
- **Load Order Error**: Fixed epochQuestDB.lua causing "attempt to index global QuestieDB (a nil value)" error
  - Added missing QuestieDB import at top of file
  - Other Epoch database files already had proper imports

### Added  
- **Data Collection Message Toggle**: Added setting to control [DATA] message visibility
  - New setting in Advanced tab: "Show Collection Messages" (off by default)
  - `/qdc messages` command to quickly toggle messages on/off
  - Allows silent data collection without chat spam
  - Collection still works even with messages disabled

## [1.0.60] - 2025-08-30

### Fixed

#### Critical Error Fixes
- **AvailableQuests Error**: Fixed "attempt to index local 'npc' (a nil value)" error when quest starters are single IDs instead of tables (Fixes #43, #46, #52)
  - Now properly handles quests with single NPC or GameObject starters
  - Converts single IDs to tables before processing
  - Quest markers now gracefully handle incomplete quest data
- **QuestieTracker Error**: Fixed "IsComplete() nil value" error when tracking malformed quests
  - Added defensive check for quest objects missing the IsComplete method
  - Prevents tracker crash when encountering incomplete quest data
  - Fixed tracker showing completed quests after accepting new ones
  - Fixed tracker not refreshing properly when completing and accepting quests
  - Completed quests are now properly cleaned from QuestiePlayer.currentQuestlog
- **QuestieShutUp Filter**: Fixed chat filter not blocking Questie messages from party members (Fixes #55)
  - Corrected pattern mismatch between filter and actual message format
  - Filter now properly matches locale-specific message formats
- **World Map Tooltips**: Fixed tooltips not showing on vanilla fullscreen world map (merged PR #25 from @virtiz)
  - Tooltips now properly check full parent chain to detect WorldMapFrame ancestry
  - Added SetClampedToScreen to keep tooltips visible at screen edges
- **Object Data Errors**: Fixed "Missing objective data" errors showing table references instead of meaningful descriptions
  - Now silently skips missing data or logs at debug level only
  - Prevents spam for missing object ID 6445625 and similar
- **Critical Map Pin Fix**: Imported WotLK database to fix all service NPC detection
  - Project Epoch was using Classic-era NPC flags (INNKEEPER=128) but needed WotLK flags (INNKEEPER=65536)
  - Fixed version detection to properly identify 3.3.5 client and use correct flag values
  - All service NPCs (innkeepers, bankers, auctioneers, trainers, etc.) now show correctly on maps
- **Stormwind Service NPCs**: Fixed bankers, auctioneers, and weapon master not showing on map
  - Updated 3 bankers (Olivia, Newton, John Burnside) with correct coordinates and flags from WotLK database
  - Updated 3 auctioneers (Chilton, Fitch, Jaxon) with correct coordinates and flags from WotLK database
  - Fixed Woo Ping (weapon master) location from wrong coordinates (57.13,57.71) to correct position (63.88,69.09)
  - All NPCs now use proper service flags (131073 for bankers, 2097152 for auctioneers, 81 for weapon master)
- **Stormwind NPCs**: Restored Innkeeper Allison and Dungar Longdrink (flight master) on map tracker
  - Removed placeholder entries in epochNpcDB.lua that were overriding Classic database
  - NPCs now show with proper names and service flags when tracked
- **Children's Week**: Permanently removed seasonal quest from showing year-round
  - Removed quest 1468 from event system overrides
  - Blacklisted NPCs 14305 (Human Orphan) and 14450 (Orphan Matron Nightingale)
  - Quest will no longer appear even during May 1-7 event dates
- **Quest Database**: Fixed duplicate and incorrect quest entries (Fixes #78, #79, #80, #81)
  - Consolidated duplicate quest entries for quests 26285, 26286, 26287, 26288, 26289, 26292, 26907
  - Removed conflicting epochQuestData stub entries that were overwriting complete quest data
  - Updated quest 26285 "Deeg's Lost Pipe" with proper quest giver and objective data
  - Added missing quest entries 26286-26292 to main database array with proper data structure
  - Added missing NPC 2488 (Deeg) to support "Deeg's Lost Pipe" quest
  - Removed duplicate entry for quest 26987 "Homecoming" with wrong quest giver (NPC 491)
  - Removed incorrect entry for quest 26987 with wrong title "Moving Up"
  - Fixed Innkeeper Allison coordinates in Stormwind (was 60.39,75.28, now 52.62,65.7)
  - Fixed quest 26993 "The Killing Fields" with proper objectives and mob targets (Riverpaw Gnolls and Scouts)
  - Cleaned up quest data integrity in epochQuestDB.lua
#### Data Collection Overhaul
- **Container Names Fixed**: Major fixes to ground object/container tracking (Fixes #32)
  - Fixed container names being lost when they match item names (e.g., "Sun-Ripened Banana") 
  - Fixed container names being overwritten with placeholders like "Unidentified Container"
  - Container names now properly captured from GameTooltip during mouseover
  - Container names preserved even when loot window doesn't show the name
  - Export now includes proper container data for ground object quests
  - Added automatic rescan 1 second after initialization (no more manual `/qdc rescan` needed)
- **Runtime Stub Detection**: Fixed missing quest detection for runtime stubbed quests (Fixes #21)
  - Now properly detects quests created as runtime stubs (e.g., new troll starting zone quests)
  - Removed upper limit on Epoch quest IDs (now tracks all quests 26000+)
  - Fixed detection of [Epoch] prefix in questData.name for placeholder quests
  - Now correctly identifies and tracks quest 28722 "The Darkspear Tribe" and similar new quests
- **Chat Spam Removed**: Fixed [DATA] messages being shown to all users (Fixes #27)
  - All [DATA] tracking messages now only show when debug mode is enabled
  - Removed all alert messages when accepting quests - silently tracks data
  - Important completion notices still show when needed
  - Added helper function to properly handle debug-only messages
- **Export Improvements**: All quest data can now be exported, even incomplete quests
  - Partial data is valuable - shows quest givers, objectives, NPCs even without turn-in
  - Export window now shows [COMPLETE] or [INCOMPLETE] status for each quest
  - Export format clearly indicates if quest data is incomplete
- **Quest Progress Detection**: Enhanced automatic tracking
  - Now detects quest progress from system messages (e.g., "Sun-Ripened Banana: 7/10")
  - Automatically captures container/object data when quest progress is detected
  - Links ground objects to quest objectives for proper map icon placement

#### Map and Tracking Improvements  
- **Map Error Handling**: Fixed error for unknown zones like custom Project Epoch areas
  - Changed hard error to warning for unmapped zones (e.g., areaId 178 "Deeg")
  - Allows addon to continue functioning with custom server zones
- **Map Scaling**: Simplified world map dimension calculations (Fixes #39)
  - Removed unnecessary conditional scaling logic that was never triggered
  - WorldMapButton width consistently returns 1002 in both fullscreen and windowed modes
  - Map icons should now position correctly regardless of map mode
- **Party Tooltips**: Fixed party member quest progress not showing in tooltips
  - Properly access remoteQuestLogs structure for fallback mechanism
  - Shows party progress even when no per-mob tooltip cache exists
- **TomTom Integration**: Fixed TomTom auto-waypoint permanently changing tracker sort
  - TomTom now finds closest quest independently without modifying tracker sort preference
  - User's chosen sort order (proximity, level, etc.) is no longer overridden
- **Quest Item Tracking**: Fixed tracker hiding quests when looting quest items
  - Preserves quest tracking state when items are looted from ground objects
  - Prevents quests from being inadvertently untracked during objective updates
- **Quest Level Filtering**: Fixed quest level filtering and improved usability (Fixes #41)
  - Quests with "[Epoch] Quest XXXXX" placeholder names are now hidden from the map
  - Epoch quests with missing/zero requiredLevel now properly respect level filters
  - Changed "Show only quests granting experience" to hide red quests (5+ levels above player)
  - Now shows green, yellow, and orange quests but hides red quests that clutter the map

### Added
- **Quest Items**: Added 10+ quest items with proper drop sources
  - Raw Springsocket Eel, Pinch of Bone Marrow, Vial of Vulture Blood, Kratok's Horn, Slaver's Records
  - Commission items for various quests
- **WotLK Database**: Imported complete WotLK database files for proper 3.3.5 support
  - Added wotlkQuestDB.lua, wotlkNpcDB.lua, wotlkObjectDB.lua, wotlkItemDB.lua
  - Fixes all service NPC flag detection issues
  - Provides correct NPC data for WotLK expansion content
- **Quest Data**: Added 90+ new Epoch quests from GitHub issues (#71-87)
  - The Hinterlands: 5 Alliance quests including "A Sticky Situation", "Can't Make An Omelette Without...", "Falling Up To Grace", "Parts From Afar", "Stalking the Stalkers"
  - Westfall: 5 Alliance quests including "Hand of Azora" chain, "Homecoming", "The Killing Fields"
  - Silverpine Forest: 2 Horde quests "Lost in the Lake", "Wreck of the Kestrel"
  - Ashenvale: Added quest 27880 "Fight for Warsong Gulch" (level 14 battleground introduction quest)
  - Westfall: Added quest 28495 "Commission for Protector Gariel" (level 5 collection quest)
  - Various zones: 8 Call to Skirmish quests for Thousand Needles, Alterac Mountains, Desolace, Arathi Highlands and other content
  - Hillsbrad Foothills: "Who Likes Apples?", "Fresh Water Delivery", "The Ghost of the Flats", "Threats from Abroad", "To The Hills"
  - Badlands: "Springsocket Eels", "An Old Debt", multiple commission quests
  - Tanaris: "Call to Skirmish" PvP quests
  - Winterspring/EPL: High-level Horde quests including "Nightmare Seeds", "Hero Worship"
  - Desolace: "The Argus Wake" 5-quest chain (42-44)
  - Searing Gorge: Thorium Brotherhood quests
  - Elwynn Forest: "Barroom Blitz" series, commission quests
  - Updated existing quests with complete data: "Arugal Ambush", "The Killing Fields"
- **NPCs**: Added 35+ new NPCs with proper locations
  - The Hinterlands: Truk Wildbeard, Kerr Ironsight, Tizzie Sparkcraft, Chief Engineer Urul, Gryphon Master Stonemace, Gryphon Master Talonaxe
  - Westfall: Karlain, Revil Kost, Quartermaster Lewis
  - Silverpine Forest: Ainslie Yance, Edwin Harly, Dalar Dawnweaver, Kor
  - Ashenvale: Added NPC 44806 "Warsong Gulch Battlemaster" for battleground quest access
  - Hillsbrad/Thousand Needles: Jason Lemieux, Pozzik, Deeg, Commander Strongborn
  - Badlands: Zeemo, Dirk Windrattle, Joakim Sparkroot
  - Searing Gorge: Merida Stoutforge, Bhurind Stoutforge, Grampy Stoutforge, Lookout Captain Lolo Longstriker
  - Desolace: Felicity Perenolde, Zala'thria, Kratok
  - Eastern Plaguelands: Engineer Flikswitch, Harbinger Balthazad
  - Elwynn Forest: Jason Mathers
- **Objects**: Added ground objects for quest item collection
  - Sack of Oats in Westfall (3 spawn points)
  - Fishing Bobber in Stormwind City

### Changed
- **epochStormwindFixes.lua**: Disabled due to causing issues with seasonal NPCs and incorrect positions
  - Was adding 546 NPC entries, many with wrong coordinates or inappropriate seasonal content
  - Service NPCs now properly handled by WotLK database

### Removed
- **POI Markers**: Fixed service NPCs not appearing on Stormwind map (Fixes #42)
  - Added proper npcFlags to flight master, innkeeper, auctioneers, bankers, trainers, and repair vendors
  - Updated epochStormwindFixes.lua with service flags for 30+ NPCs
- **Mailbox Locations**: Fixed misplaced mailboxes throughout Stormwind (Fixes #42)
  - Updated 10 mailbox coordinates based on actual WotLK positions
  - Added mailboxes in Trade District, Cathedral Square, Park District, Mage Quarter, Old Town, and Dwarven District

## [1.0.53] - 2025-08-28

Note: Versions 1.0.54-59 were internal development versions. All changes from those versions are included in v1.0.60 above.

## [1.0.4] - 2025-08-27

### Fixed
- **Party tracking tooltips**: Added fallback mechanism to show party member quest progress when no per-mob tooltip cache exists
- **DataCollector errors**: Fixed questID being passed as table instead of number in multiple locations
  - Added defensive checks in CheckExistingQuests, OnQuestAccepted, and GetQuestIdFromLogIndex
  - Fixed GetQuestsByZoneId iterating over QuestPointers with table keys
  - Added pcall wrapper to gracefully handle errors
  - Note: Requires complete WoW restart to load the fixes (not just /reload)

## [1.0.3] - 2025-08-27

### Fixed
- **Major tracker fix**: Fixed QuestLogCache not populating on initial load causing only 1 quest to show
- Fixed tracker not showing despite having tracked quests
- Fixed tracker UI element not being visible even when functioning correctly
- Fixed manual quest tracking toggle functionality
- Fixed QuestieDB.GetQuest being called with tables instead of quest IDs
- Fixed TrackerUtils handling of non-table quest entries
- Fixed QuestieDataCollector passing invalid questIDs to GetQuest
- Fixed data purge button not actually clearing saved quest data
- Fixed quest 26936 "Northshore Mine" incorrect turn-in NPC (now correctly shows Jasper Greene)

### Added
- Mouse wheel scrolling support for quest tracker
- Debug commands: `/run QuestieTracker:CheckStatus()` and `/run QuestieTracker:ForceScanQuests()`
- Force show tracker command: `/run QuestieTracker:ForceShow()`
- Added 6 Epoch quests with proper data (26926, 26932, 26934, 26936, 26940, 26942)
- Added NPCs: Fergus Kitsapell (45899), Gernal Burch (45902)
- Added items: Case of Ore (62803), Joseph's Journal (62811)

### Changed
- Improved runtime stub creation for Epoch quests
- Enhanced error handling in database queries
- Updated tracker initialization to force update after load

## [1.0.2] - 2025-08-27

### Fixed
- Fixed tracker nil reference bugs with AutoUntrackedQuests
- Added nil checks to prevent "0/0 quests" display issue
- Fixed manual quest tracking not working
- Added safety checks for frame creation failures

### Added
- Map zoom fix module (experimental)

## [1.0.1] - 2025-08-27

### Fixed
- Repository references updated to point to Questie-Epoch
- Version numbering corrected

## [1.0.0] - 2025-08-27

### Initial Release
- Fork of esurm/Questie optimized for Project Epoch
- 600+ Epoch quests in database (IDs 26000-26999)
- Developer mode for community quest data collection
- Real-time capture of NPCs, items, and objective locations
- Batch export functionality for all captured quest data
- Data purge feature after submission
- Read-only export window
- GitHub submission instructions

### Known Issues
- Map zoom causes marker displacement (3.3.5a limitation)
- Many Epoch quests still need validation through gameplay