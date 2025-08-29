# Release Notes - v1.0.55

## 🎯 Major Fixes

### Data Collection Now Works for ALL Custom Quests! 
- **Fixed Issue #21**: Runtime stubbed quests (like the new troll starting zone) are now properly detected
- **Fixed Issue #27**: No more [DATA] message spam - debug messages only show when explicitly enabled
- Quest ID tracking expanded to ALL Epoch quests (26000+) with no upper limit
- Export window now correctly shows all tracked quests

## 🚀 Key Improvements

### Better User Experience
- Clear "Ready!" message when data collector is initialized
- Export window shows [COMPLETE] or [INCOMPLETE] status for each quest
- Partial quest data can now be exported (even incomplete quests are valuable!)
- Debug messages properly hidden unless `/qdc debug` is used

### What This Means for Players
- **New Troll Starting Zone**: Quest 28722 "The Darkspear Tribe" and all other new quests are now tracked
- **Less Spam**: You won't see constant [DATA] messages unless you want them
- **All Data Matters**: Even if you don't complete a quest, the partial data helps improve the database

## 📝 How to Use

1. Enable data collection: `/qdc enable`
2. Wait for "Ready!" message after reload
3. Accept any custom Epoch quest
4. See "Missing Epoch quest detected!" alert
5. Export data anytime with `/qdc export`

## 🐛 Issues Fixed
- #21: Data collection not starting for stubbed Epoch quests
- #27: [DATA] messages spamming all users

## 🙏 Thanks
Thanks to the community for reporting these issues and helping test the fixes!