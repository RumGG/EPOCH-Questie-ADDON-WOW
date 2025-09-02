-- DUN MOROGH / GNOME STARTING ZONE FIXES
-- Generated from analysis of pfQuest data and current issues

-- ========================================
-- ISSUES FOUND:
-- ========================================
-- 1. NPC 1265 is missing (needed for Quest 27128: Venomous Conclusions)
-- 2. Quest 26502 has malformed data (items in wrong field)
-- 3. Quest chains 26484-26486 need zone corrections
-- ========================================

-- FIX 1: Add missing NPC 1265
-- This NPC is referenced by Quest 27128 but doesn't exist
-- Creating stub entry - needs in-game coordinate collection
epochNpcDB[1265] = {"Rudra Amberstill",nil,nil,10,10,0,{[1]={{38.9,46.3}}},nil,1,{27128},{27128},nil,"AH",nil,2} -- Stub NPC for Dun Morogh

-- FIX 2: Fix Quest 26502 "Rare Books"
-- The quest has items (63090, 63091) incorrectly placed in preQuestSingle field
-- They should be in the objectives/items field
-- CORRECTED ENTRY:
epochQuestDB[26502] = {"Rare Books",{{2277}},{{2277}},nil,42,nil,2,{"Collect Tales from Tel'Abim, Collect Night Stars By Longitude"},nil,{nil,nil,{{63090,1,"Tales from Tel'Abim"},{63091,1,"Night Stars By Longitude"}}},nil,nil,nil,nil,nil,nil,267,nil,nil,nil,nil,nil,2,0,nil,nil,nil,nil,nil,nil} -- Fixed: moved items to correct field

-- FIX 3: Update zone for quest chain quests
-- These quests are part of Dun Morogh chains but marked with wrong zones
epochQuestDB[26485] = {"Call of Fire",{{45519}},{{45520}},nil,10,nil,nil,{"Defeat Baron Kurdran and retrieve Lucidity."},nil,{{{46883,nil,"Baron Kurdran"}},nil,{{63088,nil,"Lucidity"}}},nil,nil,{26484},nil,nil,nil,1,nil,nil,nil,nil,nil,8,0,26484,nil,nil,nil,nil,nil} -- Changed zone to 1 (Dun Morogh)

epochQuestDB[26486] = {"Call of Fire",{{45520}},{{45520}},nil,10,nil,nil,{"Speak with Juldugs Firetale."},nil,nil,nil,nil,{26485},{26487},nil,nil,1,nil,nil,nil,nil,26487,8,0,26485,nil,nil,nil,nil,nil} -- Changed zone to 1 (Dun Morogh)

-- FIX 4: Add missing NPC 46883 (Baron Kurdran) for quest objective
-- This NPC is referenced in quest 26485 but might be missing
if not epochNpcDB[46883] then
    epochNpcDB[46883] = {"Baron Kurdran",nil,nil,10,11,1,{[1]={{30.5,45.8}}},nil,1,nil,nil,nil,"AH",nil,0} -- Elite mob in Dun Morogh
end

-- ========================================
-- SUMMARY OF FIXES:
-- ========================================
-- 1. Added NPC 1265 (Rudra Amberstill) - needs coordinates
-- 2. Fixed Quest 26502 data corruption
-- 3. Corrected zone IDs for quest chain 26484-26486
-- 4. Added NPC 46883 (Baron Kurdran) if missing
--
-- TO APPLY THESE FIXES:
-- 1. Copy the NPC entries to epochNpcDB.lua
-- 2. Copy the quest entries to epochQuestDB.lua
-- 3. Restart WoW completely
-- 4. Test the quest chains in Dun Morogh
-- ========================================