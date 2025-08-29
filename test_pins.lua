-- Test if pins are now showing properly
local function TestPins()
    print("=== Testing Pin Visibility ===")
    
    -- Check HBDPins
    local HBDPins = QuestieCompat and QuestieCompat.HBDPins
    if not HBDPins then
        print("ERROR: HBDPins not found!")
        return
    end
    
    -- Check worldmap pins
    local worldmapPins = HBDPins.worldmapPins
    if not worldmapPins then
        print("No worldmap pins table")
        return
    end
    
    local totalCount = 0
    local shownCount = 0
    local hiddenCount = 0
    
    for icon, data in pairs(worldmapPins) do
        totalCount = totalCount + 1
        if icon:IsShown() then
            shownCount = shownCount + 1
        else
            hiddenCount = hiddenCount + 1
        end
    end
    
    print(string.format("Worldmap Pins: %d total, %d shown, %d hidden", 
        totalCount, shownCount, hiddenCount))
    
    -- Check if WorldMapButton is visible
    if WorldMapButton then
        print("WorldMapButton:")
        print("  IsShown: " .. tostring(WorldMapButton:IsShown()))
        print("  Width: " .. WorldMapButton:GetWidth())
        print("  Height: " .. WorldMapButton:GetHeight())
        print("  Scale: " .. WorldMapButton:GetScale())
    end
    
    -- Check a sample of frames
    local sampleCount = 0
    for icon, data in pairs(worldmapPins) do
        if sampleCount < 3 then
            local parent = icon:GetParent()
            print(string.format("Sample pin %d:", sampleCount + 1))
            print("  Parent: " .. (parent and parent:GetName() or "nil"))
            print("  IsShown: " .. tostring(icon:IsShown()))
            print("  FrameStrata: " .. (icon:GetFrameStrata() or "nil"))
            print("  FrameLevel: " .. (icon:GetFrameLevel() or 0))
            sampleCount = sampleCount + 1
        else
            break
        end
    end
    
    print("=== End Test ===")
end

SLASH_TESTPINS1 = "/testpins"
SlashCmdList["TESTPINS"] = TestPins

print("|cFFFFFF00Pin test loaded. Open map and type /testpins to check pin visibility|r")