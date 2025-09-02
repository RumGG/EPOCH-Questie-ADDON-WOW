-- EMERGENCY FIX FOR GNOME STARTING QUESTS
-- Apply these directly to the database files if quests aren't working

-- =====================================
-- CRITICAL FIXES NEEDED
-- =====================================

-- 1. FIX ALREADY APPLIED TO epochNpcDB.lua line 909:
-- [46836] = {"Tinker Captain Whistlescrew",nil,nil,5,5,0,{[1]={{24.7,59.1}}},nil,1,{28901,28902,28903},{28901,28902},nil,"A",nil,2}

-- 2. CHECK/FIX NPC 46882 (Windle Fusespring) - quest 28903 turn-in:
epochNpcDB[46882] = {"Windle Fusespring",nil,nil,5,5,0,{[1]={{24.5,59.0}}},nil,1,nil,{28903},nil,"A",nil,2} -- Quest turn-in NPC

-- 3. VERIFY MOB NPCS EXIST:
-- These should already be in epochNpcDB.lua around line 900-920:
epochNpcDB[46837] = {"Underfed Trogg",nil,nil,1,2,0,{[1]={{24.5,60.2},{25.1,61.5},{23.8,62.1},{24.9,58.9},{23.2,59.8}}},nil,1,nil,nil,nil,"AH",nil,0} -- Changed to AH (both factions)
epochNpcDB[46838] = {"Infected Gnome",nil,nil,2,3,0,{[1]={{25.8,59.1},{24.2,60.8},{23.9,61.2},{25.5,58.7}}},nil,1,nil,nil,nil,"AH",nil,0} -- Changed to AH
epochNpcDB[46839] = {"Irradiated Ooze",nil,nil,2,3,0,{[1]={{26.1,58.9},{23.7,60.1},{24.8,61.8},{25.2,57.8},{23.5,59.2}}},nil,1,nil,nil,nil,"AH",nil,0} -- Changed to AH

-- =====================================
-- TEST QUEST REPLACEMENTS
-- =====================================
-- If quests still don't work, try these simplified versions:

-- Test version with simplified objectives (no mob names):
epochQuestDB[28901] = {"Shift into G.E.A.R.",{{46836}},{{46836}},nil,1,nil,nil,{"Kill 10 Underfed Troggs."},nil,{{{46837,10}},nil,nil},nil,nil,nil,nil,nil,nil,1,nil,nil,nil,nil,nil,nil,0,nil,nil,nil,nil,nil,nil}

epochQuestDB[28902] = {"No Room for Sympathy",{{46836}},{{46836}},nil,2,nil,nil,{"Kill 8 Irradiated Oozes and 4 Infected Gnomes."},nil,{{{46839,8},{46838,4}},nil,nil},nil,nil,nil,nil,nil,nil,1,nil,nil,nil,nil,nil,nil,0,nil,nil,nil,nil,nil,nil}

epochQuestDB[28903] = {"Encrypted Memorandum",{{46836}},{{46882}},nil,1,nil,nil,{"Read the Encrypted Memorandum then speak to Windle Fusespring at G.E.A.R. in Dun Morogh."},nil,nil,nil,nil,nil,nil,nil,nil,1,nil,nil,nil,nil,nil,nil,0,nil,nil,nil,nil,nil,nil}

-- =====================================
-- HOW TO APPLY THESE FIXES
-- =====================================

-- METHOD 1: Direct Database Edit
-- 1. Open Database/Epoch/epochQuestDB.lua
-- 2. Find line 365 (quest 28901)
-- 3. Replace the three quest entries with the test versions above
-- 4. Open Database/Epoch/epochNpcDB.lua  
-- 5. Verify/fix NPCs as shown above
-- 6. Save files
-- 7. COMPLETELY RESTART WOW (not /reload)

-- METHOD 2: Runtime Override (temporary test)
-- 1. Create a new file: FixGnomeQuests.lua in Questie folder
-- 2. Add to Questie.toc file list
-- 3. Paste this code:
--[[
local function FixGnomeQuests()
    -- Override quest data at runtime
    if QuestieDB and QuestieDB.questData then
        -- Force override the quest data
        QuestieDB.questData[28901] = {28901,1,1,nil,1,nil,nil,nil,nil,{{{46837,10}},nil,nil}}
        QuestieDB.questData[28902] = {28902,2,2,nil,2,nil,nil,nil,nil,{{{46839,8},{46838,4}},nil,nil}}
    end
    
    -- Force spawn data
    if QuestieDB and QuestieDB.npcData then
        QuestieDB.npcData[46837] = {46837,"Underfed Trogg",{[1]={{24.5,60.2},{25.1,61.5}}}}
        QuestieDB.npcData[46838] = {46838,"Infected Gnome",{[1]={{25.8,59.1},{24.2,60.8}}}}
        QuestieDB.npcData[46839] = {46839,"Irradiated Ooze",{[1]={{26.1,58.9},{23.7,60.1}}}}
    end
end

-- Hook into Questie initialization
if QuestieLoader then
    local frame = CreateFrame("Frame")
    frame:RegisterEvent("PLAYER_LOGIN")
    frame:SetScript("OnEvent", function()
        C_Timer.After(5, FixGnomeQuests)
    end)
end
]]

-- =====================================
-- DEBUGGING COMMANDS
-- =====================================

-- Check if quest exists in Questie:
-- /script print(QuestieDB:GetQuest(28901) and "Quest 28901 found" or "Quest 28901 NOT FOUND")

-- Check if NPC exists:
-- /script print(QuestieDB:GetNPC(46837) and "NPC 46837 found" or "NPC 46837 NOT FOUND")

-- Force show quest on map:
-- /script QuestieQuest:DrawAllAvailableQuests()

-- Check quest objectives:
-- /script local q = QuestieDB:GetQuest(28901); if q and q.Objectives then for i,o in pairs(q.Objectives[1]) do print(i,o) end end

-- =====================================
-- MOST IMPORTANT
-- =====================================
-- After ANY changes to database files:
-- 1. SAVE the files
-- 2. COMPLETELY EXIT WOW
-- 3. RESTART WOW
-- 4. Run: /qdc recompile
-- 5. Let it reload
-- 6. Test quests