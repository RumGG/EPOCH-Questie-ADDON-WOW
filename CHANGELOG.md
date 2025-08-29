# Changelog

## [Unreleased]

### Fixed
- **Stormwind NPCs**: Restored Innkeeper Allison and Dungar Longdrink (flight master) on map tracker
  - Removed placeholder entries in epochNpcDB.lua that were overriding Classic database
  - NPCs now show with proper names and service flags when tracked

### Added
- **Quest Data**: Added 10 new Epoch quests from GitHub issues (#68, #70)
  - The Hinterlands: 5 Alliance quests including "A Sticky Situation", "Can't Make An Omelette Without...", "Falling Up To Grace", "Parts From Afar", "Stalking the Stalkers"
  - Westfall: 5 Alliance quests including "Hand of Azora" chain, "Homecoming", "The Killing Fields"
- **NPCs**: Added 9 new NPCs with proper locations
  - The Hinterlands: Truk Wildbeard, Kerr Ironsight, Tizzie Sparkcraft, Chief Engineer Urul, Gryphon Master Stonemace, Gryphon Master Talonaxe
  - Westfall: Karlain, Revil Kost, Quartermaster Lewis
- **Objects**: Added ground objects for quest item collection
  - Sack of Oats in Westfall (3 spawn points)
  - Fishing Bobber in Stormwind City

### Fixed
- **POI Markers**: Fixed service NPCs not appearing on Stormwind map (Fixes #42)
  - Added proper npcFlags to flight master, innkeeper, auctioneers, bankers, trainers, and repair vendors
  - Updated epochStormwindFixes.lua with service flags for 30+ NPCs
- **Mailbox Locations**: Fixed misplaced mailboxes throughout Stormwind (Fixes #42)
  - Updated 10 mailbox coordinates based on actual WotLK positions
  - Added mailboxes in Trade District, Cathedral Square, Park District, Mage Quarter, Old Town, and Dwarven District

## [1.0.57] - 2025-08-29

### Added
- **Quest Data**: Added 100+ Epoch quests from GitHub issues (#40-67)
  - Elwynn Forest: Hunter training quests, Tattered Letter, Soaked Barrel chain
  - Darkshore: Twilight's Hammer, Welcome to Auberdine, Commission for Archaeologist Everit
  - Duskwood: Riders In The Night chain, Life In Death chain, Until Death Do Us Part chain, Wanted: Plagued Shambler
  - Stranglethorn Vale: Kaldorei Lune, Looting the Looters, Call to Skirmish
  - Hillsbrad Foothills: Threats from Abroad
  - The Barrens: Burning Blade Signets, WANTED: Deepskin
  - Ashenvale: Heart of the Ancient
  - Stonetalon Mountains: Attack on the Mine, Ore for Sun Rock, Twilight Fangs
  - Thousand Needles: Fresh Water Delivery, Podium Finish, racing quests
  - Westfall: Barroom Blitz chain, The Venture to Sentinel Hill
  - Mulgore: In Favor of the Sun, Grimtotem Encroachment, Finding Mone
  - Arathi Highlands: Commission for Indon Cliffreach
  - Badlands: Primitive Relic, Trapped Miners chain, The Strange Ore
  - Swamp of Sorrows: Deathstrike Remedy, Horrors of the Swamp
  - Multiple zones: Various level 1-60 quests with NPCs and objectives
- **NPCs**: Added 30+ Epoch NPCs with proper locations and quest associations
  - Quest givers and turn-in NPCs for all new quest chains
  - Mob spawns for quest objectives
  - Proper coordinates for all NPC locations

### Fixed
- **Debug Spam Cleanup**: Removed excessive debug messages shown to users
  - Fixed "GetQuest failed" errors appearing on startup by waiting for full initialization
  - Moved all [DATA] container tracking messages to debug mode only
  - Container detection tips now only show when debug mode is enabled
  - Quest progress tracking messages moved to debug output
- **Map Scaling**: Simplified world map dimension calculations (Fixes #39)
  - Removed unnecessary conditional scaling logic that was never triggered
  - WorldMapButton width consistently returns 1002 in both fullscreen and windowed modes
  - Map icons should now position correctly regardless of map mode
- **Available Quests**: Fixed nil NPC/GameObject errors when drawing quest starters (Fixes #43, #46, #52)
  - Added defensive nil checks when NPCs or GameObjects are missing from database
  - Quest markers now gracefully handle incomplete quest data
  - Debug messages logged when starter data is missing instead of crashing
- **Quest Level Filtering**: Fixed quest level filtering and improved usability (Fixes #41)
  - Quests with "[Epoch] Quest XXXXX" placeholder names are now hidden from the map
  - Epoch quests with missing/zero requiredLevel now properly respect level filters
  - Changed "Show only quests granting experience" to hide red quests (5+ levels above player)
  - Now shows green, yellow, and orange quests but hides red quests that clutter the map
  - Properly handles Epoch quests like 26332 (level 60), 27470 (level 44) that had requiredLevel = 0

## [1.0.56] - 2025-08-29

### Fixed
- **Data Collection - Container Names**: Major fixes to ground object/container tracking (Fixes #32)
  - Fixed container names being lost when they match item names (e.g., "Sun-Ripened Banana") 
  - Fixed container names being overwritten with placeholders like "Unidentified Container"
  - Container names now properly captured from GameTooltip during mouseover
  - Removed 5-second timestamp restriction that prevented using cached container names
  - Container names preserved even when loot window doesn't show the name
  - Export now includes proper container data for ground object quests
  - Confirmed working: "Sun-Ripened Banana" containers now properly captured for quest 28757
- **Data Collection - Quest Progress Detection**: Enhanced automatic tracking
  - Now detects quest progress from system messages (e.g., "Sun-Ripened Banana: 7/10")
  - Automatically captures container/object data when quest progress is detected
  - Links ground objects to quest objectives for proper map icon placement
  - Added automatic rescan 1 second after initialization (no more manual `/qdc rescan` needed)
- **Data Collection - Debug Commands**: Added new debugging tools
  - Added `/qdc check <questId>` command to inspect specific quest data
  - Added `/qdc save` command to force save data to SavedVariables
- **Party Tooltips**: Fixed party member quest progress not showing in tooltips
  - Properly access remoteQuestLogs structure for fallback mechanism
  - Shows party progress even when no per-mob tooltip cache exists
- **Tracker Issues**: Fixed multiple tracker update issues
  - Fixed tracker showing completed quests after accepting new ones
  - Fixed tracker not refreshing properly when completing and accepting quests
  - Completed quests are now properly cleaned from QuestiePlayer.currentQuestlog
- **TomTom Integration**: Fixed TomTom auto-waypoint permanently changing tracker sort
  - TomTom now finds closest quest independently without modifying tracker sort preference
  - User's chosen sort order (proximity, level, etc.) is no longer overridden
- **Quest Item Tracking**: Fixed tracker hiding quests when looting quest items
  - Preserves quest tracking state when items are looted from ground objects
  - Prevents quests from being inadvertently untracked during objective updates

### Added
- **Quest Data**: Added 90+ new Epoch quests from GitHub submissions (#32-#38)
  - Issue #35: Quest 26892 "Beastial Allies" with NPCs (Stranglethorn Vale)
  - Issue #34: 18 quests including Ironforge Airfield chain (26202, 26205, 26208, 26663-26696, 26987, 26998, 28087, 28375)
  - Issue #33: 6 Hinterlands quests (26209-26212, 27322, 28536)
  - Issue #32: 18 Gnome starting area quests with complete NPC data
  - Issue #37: Complete - All 21 remaining Troll/Orc starting area quests added (27201, 28550, 28628, 28750-28755, 28757-28767, 28769)
  - Issue #38: 3 additional quests (26289 "Renegade Naga", 26594 "WANTED: Scorchmaw", 26863 "The Shadowforge Librarian")
  - Added corresponding NPCs for all quests with location data
- **Quest Data**: Troll starting zone improvements
  - Quest 28722 "The Darkspear Tribe" with quest giver and turn-in NPC  
  - Quest 28723 "Thievin' Crabs" level 2 quest
  - Quest 28757 "Banana Bonanza" with working ground object collection
  - NPC 46834 "Joz'jarz" in Durotar
- **Quest Data**: Added multiple new Epoch quests from GitHub submissions
  - Quest 26277 "Shaman of the Flame" in Azshara (kill 12 Flamescale Naga)
  - Quest 27484 "Purifying the Essence" in The Barrens (defeat Undead Champion)
  - Quest 27400 "Mirkfallon Bracers" in Stonetalon Mountains (partial data)
  - Quest placeholders for 26285, 26884, 26906, 27499 (incomplete submissions)
  - Added NPCs: Lord Aithalis (45143), Kolkar Waylayer (3610), Tammra Windfield (11864), Undead Champion (62026)
  - Added item: Tainted Essence (63509)
- **Ready Message**: Added "Questie Ready!" message after full initialization
  - Shows when quest tracking and map icons are fully active
  - Appears after all initialization stages complete

## [1.0.55] - 2025-08-29

### Fixed
- **Data Collection**: Fixed missing quest detection for runtime stubbed quests (Fixes #21)
  - Now properly detects quests created as runtime stubs (e.g., new troll starting zone quests)
  - Removed upper limit on Epoch quest IDs (now tracks all quests 26000+)
  - Fixed detection of [Epoch] prefix in questData.name for placeholder quests
  - Now correctly identifies and tracks quest 28722 "The Darkspear Tribe" and similar new quests
- **Data Collection Spam**: Fixed [DATA] messages being shown to all users (Fixes #27)
  - All [DATA] tracking messages now only show when debug mode is enabled
  - Important alerts (missing quest detection, completion notices) still show to users
  - Added helper function to properly handle debug-only messages
  - Removed excessive initialization and event logging

### Changed
- **Data Export**: All quest data can now be exported, even incomplete quests
  - Partial data is valuable - shows quest givers, objectives, NPCs even without turn-in
  - Export window now shows [COMPLETE] or [INCOMPLETE] status for each quest
  - Export format clearly indicates if quest data is incomplete

### Added
- **Initialization Message**: Added clear message when data collector is ready to accept quests

## [1.0.54] - 2025-08-29

### Fixed
- **World Map Tooltips**: Fixed tooltips not showing on vanilla fullscreen world map (merged PR #25 from @virtiz)
  - Tooltips now properly check full parent chain to detect WorldMapFrame ancestry
  - Added SetClampedToScreen to keep tooltips visible at screen edges
- **Object Data Errors**: Fixed "Missing objective data" errors showing table references instead of meaningful descriptions
  - Now silently skips missing data or logs at debug level only
  - Prevents spam for missing object ID 6445625 and similar

### Added
- **Release Automation**: GitHub Actions workflow for automated releases
- **Documentation**: Added CHANGELOG.md and RELEASE_PROCESS.md
- **Map Scaling Fix**: Improved coordinate calculation for different map modes

### Changed
- Improved error handling for missing quest objective data
- Updated .gitignore to properly track important documentation files

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