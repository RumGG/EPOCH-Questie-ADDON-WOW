-- Debug script to test map dimensions and pin positioning
local function TestMapPins()
    print("=== Testing Map Pin Positioning ===")
    
    -- Get HBDPins
    local HBDPins = QuestieCompat and QuestieCompat.HBDPins
    if not HBDPins then
        print("ERROR: HBDPins not found!")
        return
    end
    
    -- Open the world map if it's not open
    if not WorldMapFrame:IsVisible() then
        print("Opening world map...")
        ShowUIPanel(WorldMapFrame)
        -- Wait a moment for it to initialize
        C_Timer.After(0.5, function()
            TestMapPinsDelayed()
        end)
    else
        TestMapPinsDelayed()
    end
end

function TestMapPinsDelayed()
    local HBDPins = QuestieCompat and QuestieCompat.HBDPins
    
    print("WorldMapFrame visible: " .. tostring(WorldMapFrame:IsVisible()))
    print("WorldMapButton:")
    print("  Width: " .. WorldMapButton:GetWidth())
    print("  Height: " .. WorldMapButton:GetHeight())
    print("  Scale: " .. WorldMapButton:GetScale())
    
    -- Check worldmapWidth and worldmapHeight from HBDPins
    if HBDPins.worldmapWidth then
        print("HBDPins worldmapWidth: " .. tostring(HBDPins.worldmapWidth))
    else
        print("HBDPins worldmapWidth: NOT SET")
    end
    
    if HBDPins.worldmapHeight then
        print("HBDPins worldmapHeight: " .. tostring(HBDPins.worldmapHeight))
    else
        print("HBDPins worldmapHeight: NOT SET")
    end
    
    -- Force an update
    if HBDPins.UpdateWorldMap then
        print("Forcing UpdateWorldMap...")
        HBDPins.UpdateWorldMap()
        
        -- Check again after update
        if HBDPins.worldmapWidth then
            print("After update - worldmapWidth: " .. tostring(HBDPins.worldmapWidth))
        end
        if HBDPins.worldmapHeight then
            print("After update - worldmapHeight: " .. tostring(HBDPins.worldmapHeight))
        end
    end
    
    -- Check if any pins are visible
    local visibleCount = 0
    local hiddenCount = 0
    local firstFewPins = {}
    
    if HBDPins.worldmapPins then
        for icon, data in pairs(HBDPins.worldmapPins) do
            if icon:IsVisible() then
                visibleCount = visibleCount + 1
                if visibleCount <= 3 then
                    local point, relativeTo, relativePoint, xOfs, yOfs = icon:GetPoint()
                    table.insert(firstFewPins, string.format("  Pin visible at: %s %.1f, %.1f", 
                        point or "?", xOfs or 0, yOfs or 0))
                end
            else
                hiddenCount = hiddenCount + 1
            end
        end
    end
    
    print("Pin visibility:")
    print("  Visible pins: " .. visibleCount)
    print("  Hidden pins: " .. hiddenCount)
    
    if #firstFewPins > 0 then
        print("First few visible pins:")
        for _, pinInfo in ipairs(firstFewPins) do
            print(pinInfo)
        end
    end
    
    print("=== End Test ===")
end

-- Create slash command
SLASH_MAPTEST1 = "/maptest"
SlashCmdList["MAPTEST"] = TestMapPins

print("|cFFFFFF00Map Pin Test loaded. Type /maptest with the map open to test.|r")