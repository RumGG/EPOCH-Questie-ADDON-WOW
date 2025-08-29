-- Debug script to check HBD mapData
local function CheckMapData()
    print("=== Checking HBD Map Data ===")
    
    local HBD = QuestieCompat and QuestieCompat.HBD
    if not HBD or not HBD.mapData then
        print("ERROR: HBD or mapData not found!")
        return
    end
    
    -- Check Eastern Kingdoms (1453)
    local data = HBD.mapData[1453]
    if data then
        print("Eastern Kingdoms (1453) data:")
        print(string.format("  Width: %s, Height: %s", tostring(data[1]), tostring(data[2])))
        print(string.format("  Left: %s, Top: %s", tostring(data[3]), tostring(data[4])))
        print(string.format("  Instance: %s", tostring(data.instance)))
    else
        print("Eastern Kingdoms (1453) data: MISSING!")
    end
    
    -- Check Elwynn Forest (1429)
    data = HBD.mapData[1429]
    if data then
        print("Elwynn Forest (1429) data:")
        print(string.format("  Width: %s, Height: %s", tostring(data[1]), tostring(data[2])))
        print(string.format("  Left: %s, Top: %s", tostring(data[3]), tostring(data[4])))
    else
        print("Elwynn Forest (1429) data: MISSING!")
    end
    
    -- Check Stormwind (1453)
    data = HBD.mapData[1519]
    if data then
        print("Stormwind City (1519) data:")
        print(string.format("  Width: %s, Height: %s", tostring(data[1]), tostring(data[2])))
        print(string.format("  Left: %s, Top: %s", tostring(data[3]), tostring(data[4])))
    else
        print("Stormwind City (1519) data: MISSING!")
    end
    
    -- Count total maps
    local count = 0
    local emptyCount = 0
    for mapId, mapInfo in pairs(HBD.mapData) do
        count = count + 1
        if mapInfo[1] == 0 or mapInfo[2] == 0 then
            emptyCount = emptyCount + 1
        end
    end
    
    print(string.format("Total maps: %d, Empty (0 width/height): %d", count, emptyCount))
    
    print("=== End Check ===")
end

SLASH_MAPDATA1 = "/mapdata"
SlashCmdList["MAPDATA"] = CheckMapData

print("|cFFFFFF00Map Data check loaded. Type /mapdata to check.|r")