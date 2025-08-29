-- Debug mailbox locations
local function DebugMailboxes()
    print("=== Debugging Mailbox Locations ===")
    
    local QuestieDB = QuestieLoader:ImportModule("QuestieDB")
    if not QuestieDB then
        print("QuestieDB not found")
        return
    end
    
    -- Check all mailbox objects
    local mailboxObjects = {
        [142075] = "Mailbox (142075)",
        [144128] = "Mailbox (144128)",
        [144129] = "Mailbox (144129)",
        [144130] = "Mailbox (144130)",
        [144131] = "Mailbox (144131)",
    }
    
    for objectId, name in pairs(mailboxObjects) do
        local objectData = QuestieDB:GetObject(objectId)
        if objectData then
            print(name .. ":")
            if objectData.spawns then
                for zoneId, coords in pairs(objectData.spawns) do
                    if zoneId == 1519 then -- Stormwind
                        print("  Stormwind spawns:")
                        for _, coord in pairs(coords) do
                            print(string.format("    %.2f, %.2f", coord[1], coord[2]))
                        end
                    end
                end
            else
                print("  No spawns data")
            end
        else
            print(name .. ": Not in database")
        end
    end
    
    -- Check what's actually on the map
    print("\n=== Checking Map Icons ===")
    local HBDPins = QuestieCompat and QuestieCompat.HBDPins
    if HBDPins and HBDPins.worldmapPins then
        local mailboxCount = 0
        for icon, data in pairs(HBDPins.worldmapPins) do
            if icon.data and icon.data.ObjectData and icon.data.ObjectData.name then
                local name = icon.data.ObjectData.name
                if string.find(name, "Mailbox") then
                    mailboxCount = mailboxCount + 1
                    local x = icon.x or data.x or 0
                    local y = icon.y or data.y or 0
                    print(string.format("Mailbox icon at %.2f, %.2f", x, y))
                end
            end
        end
        print("Total mailbox icons on map: " .. mailboxCount)
    end
    
    print("=== End Debug ===")
end

SLASH_DEBUGMAILBOX1 = "/debugmail"
SlashCmdList["DEBUGMAILBOX"] = DebugMailboxes

print("|cFFFFFF00Mailbox debug loaded. Type /debugmail to check mailbox locations|r")