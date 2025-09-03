# Questie for Project Epoch

[![Version](https://img.shields.io/badge/version-1.1.1-blue?style=for-the-badge)](https://github.com/trav346/Questie/releases)
[![WoW Version](https://img.shields.io/badge/WoW-3.3.5a-green?style=for-the-badge)](https://github.com/trav346/Questie)
[![Project Epoch](https://img.shields.io/badge/Project-Epoch-purple?style=for-the-badge)](https://project-epoch.net)

**An actively maintained version of Questie for Project Epoch with enhanced data collection capabilities.**

Questie is the ultimate quest helper addon for World of Warcraft 3.3.5a, specifically optimized for Project Epoch server. It shows quest objectives on your map and minimap, tracks quest progress, and helps you navigate the world efficiently.

## ✨ Features

### 🗺️ **Quest Map Integration**
- **Map Markers**: Quest objectives, NPCs, and turn-in locations displayed on world map and minimap
- **Dynamic Updates**: Real-time quest progress tracking with automatic marker updates
- **Zone Coverage**: Support for all Project Epoch zones and custom content
- **Smart Filtering**: Toggle quest types, levels, and completion status

### 📋 **Quest Tracking**
- **Auto-Tracker**: Automatically tracks new quests and updates progress
- **Progress Display**: Shows current objective status (e.g., "Bloodtalon Scythemaw slain: 10/10")
- **Multiple Quests**: Track multiple quests simultaneously with organized display
- **Completion Detection**: Automatic detection of quest completion and turn-in opportunities

### 🎯 **Data Collection System** *(Unique Feature)*
- **Missing Quest Detection**: Automatically detects quests not in database
- **Real-time Data Capture**: Records quest objectives, NPCs, items, and locations as you play
- **Progress Tracking**: Captures detailed progress locations with mob kill information
- **Community Contributions**: Easy export system for submitting data to improve the database

### ⚙️ **Customization Options**
- **Minimap Button**: Quick access to settings and data export
- **Slash Commands**: `/questie` for settings, `/qdc` for data collection
- **Visual Options**: Customize marker icons, colors, and display preferences
- **Performance Tuning**: Adjustable update frequencies and memory optimization

## 📦 Installation

### **Automatic Installation (Recommended)**
1. **Download**: Get the latest release from [GitHub Releases](https://github.com/trav346/Questie/releases)
2. **Extract**: Unzip the downloaded file
3. **Install**: Copy the `Questie` folder to your WoW AddOns directory:
   ```
   World of Warcraft 3.3.5/Interface/AddOns/Questie
   ```
4. **Restart**: Restart WoW completely (not just reload UI)

### **Manual Installation**
1. **Clone Repository**:
   ```bash
   git clone https://github.com/trav346/Questie.git
   cd Questie
   ```
2. **Copy to AddOns**: Move the entire folder to your WoW AddOns directory
3. **Enable Addon**: Make sure it's enabled in the addon list at character select

### **Verify Installation**
- Look for the Questie minimap button (green compass icon)
- Type `/questie` to open settings
- Check that version shows as **v1.1.1** in addon list

## 🚀 Getting Started

### **Basic Usage**
1. **Log In**: Start the game and load your character
2. **Enable Data Collection**: Type `/qdc enable` to help improve quest database
3. **Accept Quests**: Quest objectives will automatically appear on map and minimap
4. **Track Progress**: Watch your progress update in real-time as you complete objectives
5. **Turn In**: Quest completion markers guide you to turn-in NPCs

### **Essential Commands**
```
/questie                    - Open main settings
/questie refreshcomplete    - Refresh completed quests from server
/qdc enable                 - Enable data collection 
/qdc show                   - View collected quest data
/qdc export                 - Export data for GitHub submission
```

### **First-Time Setup**
1. **Enable Data Collection**: `/qdc enable` - This helps expand the quest database
2. **Configure Display**: Click minimap button → Settings to customize appearance
3. **Test Functionality**: Accept a quest and verify markers appear on map

## 🔧 Data Collection System

**Help improve Questie for everyone by enabling data collection!**

### **What It Does**
- **Automatic Detection**: Identifies quests missing from the database
- **Real-time Tracking**: Records quest objectives, NPCs, and locations as you play
- **Progress Logging**: Captures where objectives are completed with detailed information
- **No Performance Impact**: Lightweight system that doesn't affect gameplay

### **How to Contribute**
1. **Enable Collection**: `/qdc enable`
2. **Play Normally**: Accept and complete quests as usual
3. **Export Data**: Use `/qdc export <questId>` when quest is complete
4. **Submit to GitHub**: Create issue at [GitHub Issues](https://github.com/trav346/Questie/issues)
5. **Help the Community**: Your data helps everyone get better quest information

### **Data Collection Commands**
```
/qdc enable                 - Start collecting data
/qdc disable               - Stop collecting data  
/qdc status                - Check collection status
/qdc show                  - Display all tracked quests
/qdc export <questId>      - Export quest data for submission
/qdc clear                 - Clear all collected data
/qdc validate <questId>    - Validate quest data quality
```

## ⚡ Performance & Compatibility

### **System Requirements**
- **WoW Version**: 3.3.5a (Wrath of the Lich King client)
- **Server**: Optimized for Project Epoch
- **Memory**: ~10MB RAM usage
- **Dependencies**: None required (works standalone)

### **Known Compatibility**
- ✅ **ElvUI**: Full compatibility with custom themes
- ✅ **Bartender**: Works with custom action bars
- ✅ **Auctionator**: No conflicts with auction house features
- ✅ **Details**: Compatible with damage meters
- ⚠️ **Other Quest Addons**: May conflict - disable other quest helpers

### **Performance Tips**
- Use `/reload` after making major setting changes
- Clear data collection periodically with `/qdc clear` if memory usage grows
- Disable unused features in settings to improve performance

## 🐛 Known Issues & Troubleshooting

### **Common Issues**
- **Quest Markers Missing**: Some Project Epoch quests have incomplete data - enable data collection to help fix this
- **Map Icons Not Appearing**: Quest may need complete NPC/object data - submit data via `/qdc export`
- **"Missing Quest" Alerts**: Modified vanilla quests may trigger false alerts due to Project Epoch changes

### **Database Status**
- **~4,800 Quests**: Current database size for Project Epoch content
- **600+ Missing**: Estimated quests still needing data collection
- **Active Development**: Regular updates with community-submitted data

### **Getting Help**
1. **Check Issues**: Browse [GitHub Issues](https://github.com/trav346/Questie/issues) for known problems
2. **Enable Debug**: Use `/console scriptErrors 1` to see detailed error information  
3. **Report Bugs**: Create detailed issue reports with steps to reproduce
4. **Discord Support**: Join Project Epoch Discord for community help

## 📈 Version History

### **Latest: v1.1.1** *(Current)*
- 🐛 Fixed coordinate formatting crashes
- 🐛 Fixed QuestieSlash command errors  
- 🚀 Enhanced objective tracking with mob kill correlation
- 📍 Improved progress location display matching v1.0.68 quality

### **Previous Releases**
- **v1.1.0**: Data collection overhaul, completed quest sync
- **v1.0.68**: Enhanced objective tracking, turn-in NPC fixes
- **v1.0.63**: Initial Project Epoch compatibility

[View Full Changelog](CHANGELOG.md)

## 🤝 Contributing

### **Ways to Help**
1. **Submit Quest Data**: Use `/qdc enable` and submit exports via GitHub
2. **Report Bugs**: Create detailed issue reports with reproduction steps  
3. **Test Features**: Try new releases and provide feedback
4. **Documentation**: Help improve guides and documentation
5. **Spread the Word**: Tell other Project Epoch players about Questie

### **Development**
- **Repository**: https://github.com/trav346/Questie
- **Issues**: https://github.com/trav346/Questie/issues
- **Pull Requests**: Welcome for bug fixes and improvements
- **Coding Style**: Follow existing Lua patterns and include tests

### **Data Submission Process**
1. Enable data collection: `/qdc enable`
2. Complete quests normally (accept → complete → turn in)
3. Export quest data: `/qdc export <questId>`
4. Create GitHub issue with exported data
5. Use title format: "Missing Quest: [Quest Name] (ID: #####)"

## 🙏 Credits & Support

### **Special Thanks**
- **@esurm**: Original Questie author and data collection system
- **@desizt**: Data collection enhancements and testing
- **@Bennylavaa**: Extensive testing and bug reporting
- **Project Epoch Community**: Quest data submissions and feedback
- **All Contributors**: Everyone who has submitted quest data via GitHub

### **Support Development**
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support%20Development-orange?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/trav346)

If you find this enhanced version of Questie helpful, consider [buying me a coffee](https://buymeacoffee.com/trav346) to support continued development and maintenance!

---

## 📋 Quick Reference

### **Essential Commands**
| Command | Description |
|---------|-------------|
| `/questie` | Open main settings |
| `/questie refreshcomplete` | Refresh completed quests |
| `/qdc enable` | Enable data collection |
| `/qdc export <questId>` | Export quest data |
| `/qdc show` | View collected data |

### **Installation Checklist**
- [ ] Downloaded latest release (v1.1.1)
- [ ] Extracted to correct AddOns folder
- [ ] Restarted WoW completely
- [ ] Enabled addon at character select
- [ ] Minimap button appears
- [ ] Ran `/qdc enable` to help community

### **Support Links**
- **Download**: [GitHub Releases](https://github.com/trav346/Questie/releases)
- **Bug Reports**: [GitHub Issues](https://github.com/trav346/Questie/issues)  
- **Server Info**: [Project Epoch](https://project-epoch.net)
- **Support Development**: [Buy Me A Coffee](https://buymeacoffee.com/trav346)

---

*Questie for Project Epoch - Making quest navigation effortless while building the most comprehensive quest database through community collaboration.*