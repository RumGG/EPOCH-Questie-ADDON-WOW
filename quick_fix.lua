-- Quick fix to enable Questie map pins
local function QuickFix()
    if Questie and Questie.db and Questie.db.profile then
        local oldValue = Questie.db.profile.enabled
        Questie.db.profile.enabled = true
        
        print(string.format("|cFFFFFF00Questie pins enabled (was %s, now %s)|r", 
            tostring(oldValue), tostring(Questie.db.profile.enabled)))
        
        -- Toggle the notes to refresh all pins
        if QuestieQuest and QuestieQuest.ToggleNotes then
            QuestieQuest:ToggleNotes(true)
            print("|cFF00FF00Refreshing all quest pins...|r")
        end
        
        print("|cFF00FF00Done! Open and close the map to see pins.|r")
    else
        print("|cFFFF0000Error: Questie profile not found|r")
    end
end

-- Run the fix automatically when this file loads
local C_Timer = QuestieCompat and QuestieCompat.C_Timer or C_Timer
if C_Timer then
    C_Timer.After(1, QuickFix)
else
    -- Fallback if C_Timer not available
    QuickFix()
end

SLASH_QUICKFIX1 = "/qfix"
SlashCmdList["QUICKFIX"] = QuickFix

print("|cFFFFFF00Questie pin fix loaded. Type /qfix if pins don't appear automatically.|r")