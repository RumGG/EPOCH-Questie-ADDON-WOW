-- Simple test to see if this file loads
print("|cFF00FF00[TEST] test_load.lua is loading!|r")

local function TestQuestieState()
    print("=== Questie State Test ===")
    
    -- Check if Questie exists
    if not Questie then
        print("ERROR: Questie global not found!")
        return
    end
    print("Questie global exists: YES")
    
    -- Check if db exists
    if not Questie.db then
        print("ERROR: Questie.db not found!")
        return
    end
    print("Questie.db exists: YES")
    
    -- Check if profile exists
    if not Questie.db.profile then
        print("ERROR: Questie.db.profile not found!")
        return
    end
    print("Questie.db.profile exists: YES")
    
    -- Try to set the enabled flag directly
    print("Current enabled state: " .. tostring(Questie.db.profile.enabled))
    print("Attempting to set enabled = true...")
    Questie.db.profile.enabled = true
    print("New enabled state: " .. tostring(Questie.db.profile.enabled))
    
    -- Check if QuestieQuest exists
    if QuestieQuest then
        print("QuestieQuest module: FOUND")
        if QuestieQuest.ToggleNotes then
            print("Calling QuestieQuest:ToggleNotes(true)...")
            QuestieQuest:ToggleNotes(true)
            print("ToggleNotes called")
        else
            print("ERROR: ToggleNotes function not found")
        end
    else
        print("ERROR: QuestieQuest module not found")
    end
    
    print("=== End Test ===")
end

-- Register the command
SLASH_TESTLOAD1 = "/testload"
SlashCmdList["TESTLOAD"] = TestQuestieState

-- Try to run after a delay
local frame = CreateFrame("Frame")
frame.elapsed = 0
frame:SetScript("OnUpdate", function(self, elapsed)
    self.elapsed = self.elapsed + elapsed
    if self.elapsed >= 2 then
        print("|cFFFFFF00[TEST] Running delayed test (2 seconds after load)|r")
        TestQuestieState()
        self:SetScript("OnUpdate", nil)
    end
end)

print("|cFF00FF00[TEST] Commands registered. Type /testload to test|r")