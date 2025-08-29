# Changelog

## [Unreleased]

### Fixed
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
- **Data Collection**: Enhanced ground object and container tracking
  - Now detects quest progress from system messages (e.g., "Bananas looted: 1/10")
  - Captures container/object data when quest progress is detected
  - Links ground objects to quest objectives for proper map placement

### Added
- **Quest Data**: Added new troll starting zone quests
  - Quest 28722 "The Darkspear Tribe" with quest giver and turn-in NPC
  - Quest 28723 "Thievin' Crabs" level 2 quest
  - Quest 28757 "Banana Bonanza" with ground object collection
  - NPC 46834 "Joz'jarz" in Durotar
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