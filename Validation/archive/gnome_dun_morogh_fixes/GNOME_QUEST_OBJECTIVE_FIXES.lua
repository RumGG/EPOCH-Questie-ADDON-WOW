-- GNOME QUEST OBJECTIVE FIXES
-- These quests already exist but may have missing objective data (field 10)
-- Apply these fixes to epochQuestDB.lua

-- The issue: pfQuest conversion didn't map the 'obj' field to Questie's objectives field
-- This file contains manual fixes for known quests that need objective data

-- Format for objectives field (field 10):
-- {{{mobId,count,"name"},...},{{objectId,count,"name"},...},{{itemId,count,"name"},...}}

-- =====================================
-- GNOME STARTING AREA FIXES
-- =====================================

-- Quest 28901: Shift into G.E.A.R. (already has objectives in current DB)
-- Current data shows it already has: {{{46837,10,"Underfed Trogg"}}}
-- This is CORRECT - no fix needed

-- Quest 28902: No Room for Sympathy (already has objectives in current DB)
-- Current data shows it already has: {{{46839,8,"Irradiated Ooze"},{46838,4,"Infected Gnome"}}}
-- This is CORRECT - no fix needed

-- Quest 28903: Encrypted Memorandum
-- This is a delivery quest - no mobs to kill, so nil objectives is correct

-- =====================================
-- MISSING QUEST TO ADD
-- =====================================

-- Quest 28725: The first gnome quest (mentioned by user, not in database)
-- This quest needs to be captured in-game using data collector
epochQuestDB[28725] = {"[NEEDS DATA COLLECTION]",nil,nil,nil,1,nil,nil,{"[Quest text needs to be captured]"},nil,nil,nil,nil,nil,nil,nil,nil,1,nil,nil,nil,nil,nil,8,0,nil,nil,nil,nil,nil,nil} -- Placeholder for gnome starter quest

-- =====================================
-- QUESTS THAT NEED OBJECTIVE DATA
-- =====================================

-- These quests from pfQuest conversion have nil objectives but should have mob/item data
-- We need to identify which ones actually need fixes

-- Example format for adding objectives:
-- Find quest with nil objectives: [questId] = {"Name",start,end,minLvl,lvl,race,class,text,trigger,nil,...}
-- Replace the nil in field 10 with: {{{mobId,count,"name"}},nil,nil}

-- Sample quests that might need objectives (from pfQuest data):
-- These are Epoch custom quests that pfQuest had but without objective data in conversion

-- Quest 26169: Can't Make An Omelette Without...
-- Needs egg collection objectives - data collector needed

-- Quest 26776: Swiftpaw
-- Already in DB with objectives: {nil,nil,{{60388,nil}}} - item collection

-- Quest 27230: A Gnome in Need
-- Already in DB with objectives: {nil,nil,{{63106,1,"Undelivered Letter"}}}

-- =====================================
-- HOW TO APPLY THESE FIXES
-- =====================================

-- 1. For quests that already have correct objectives: NO ACTION NEEDED
-- 2. For missing quest 28725: Use data collector in-game
--    /qdc enable
--    Accept quest 28725
--    /qdc export 28725
-- 3. For quests with nil objectives that should have data:
--    - Check if quest actually needs mob/item objectives
--    - Use data collector to capture the real data
--    - Update this file with the correct objectives

-- =====================================
-- DATA COLLECTION BUGS TO FIX
-- =====================================

-- Issues identified:
-- 1. Container names not always captured correctly
-- 2. Some objectives not linking to mobs properly
-- 3. Quest 28725 missing entirely

-- Next steps:
-- 1. Test gnome starting area with data collector enabled
-- 2. Capture quest 28725 if it exists
-- 3. Verify all objectives are tracked correctly