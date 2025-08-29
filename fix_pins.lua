-- Fix to enable Questie and show all pins
local function FixPins()
    print("=== Fixing Questie Pins ===")
    
    -- Enable Questie
    if Questie and Questie.db then
        print("Enabling Questie...")
        Questie.db.profile.enabled = true
        Questie.db.profile.enableMapIcons = true
        Questie.db.profile.enableMiniMapIcons = true
        print("  Questie enabled: " .. tostring(Questie.db.profile.enabled))
    end
    
    -- Get HBDPins
    local HBDPins = QuestieCompat and QuestieCompat.HBDPins
    if not HBDPins then
        print("ERROR: HBDPins not found!")
        return
    end
    
    -- Fix worldmap pins
    local worldmapPins = HBDPins.worldmapPins
    if worldmapPins then
        local fixedCount = 0
        local shownCount = 0
        
        for icon, data in pairs(worldmapPins) do
            -- If the icon is FakeHidden, restore it
            if icon.hidden then
                -- Restore the original Show/Hide functions
                if icon._show then
                    icon.Show = icon._show
                    icon._show = nil
                end
                if icon._hide then
                    icon.Hide = icon._hide
                    icon._hide = nil
                end
                icon.hidden = false
                icon.shouldBeShowing = true
                fixedCount = fixedCount + 1
            end
            
            -- Force the icon to show
            if icon.Show then
                icon:Show()
                if icon:IsShown() then
                    shownCount = shownCount + 1
                end
            end
        end
        
        print(string.format("Fixed %d FakeHidden pins", fixedCount))
        print(string.format("Now showing %d pins", shownCount))
    end
    
    -- Fix minimap pins too
    local minimapPins = HBDPins.minimapPins
    if minimapPins then
        local fixedCount = 0
        
        for icon, data in pairs(minimapPins) do
            if icon.hidden then
                if icon._show then
                    icon.Show = icon._show
                    icon._show = nil
                end
                if icon._hide then
                    icon.Hide = icon._hide
                    icon._hide = nil
                end
                icon.hidden = false
                icon.shouldBeShowing = true
                fixedCount = fixedCount + 1
                icon:Show()
            end
        end
        
        print(string.format("Fixed %d minimap pins", fixedCount))
    end
    
    -- Refresh the map
    if HBDPins.UpdateWorldMap then
        HBDPins:UpdateWorldMap()
        print("Updated world map")
    end
    
    -- Also try to redraw quest icons
    if QuestieQuest and QuestieQuest.ToggleShowIcons then
        QuestieQuest:ToggleShowIcons(true)
        print("Toggled quest icons on")
    end
    
    print("=== Fix Complete ===")
    print("Try opening and closing the map to refresh")
end

SLASH_FIXPINS1 = "/fixpins"
SlashCmdList["FIXPINS"] = FixPins

print("|cFFFFFF00Pin fix loaded. Type /fixpins to enable Questie and show all pins|r")