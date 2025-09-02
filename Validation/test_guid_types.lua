#!/usr/bin/env lua

-- Test script to verify GUID type detection for NPCs vs Objects
-- Run this to ensure the fix correctly distinguishes between them

local function TestGUIDType(guid, expected_type, description)
    -- In WoW 3.3.5 GUIDs like 0xF130000B5D00019E:
    -- 0xF1 = prefix
    -- 30 = object type (positions 5-6 in the string)
    -- Extract GUID type (positions 5-6 after the 0x prefix)
    local guidType = tonumber(guid:sub(5, 6), 16)
    
    -- Check if it's an NPC type (0x30 for creature, 0x10 for pet, 0x40 for vehicle)
    local isNPC = guidType and (guidType == 0x30 or guidType == 0x10 or guidType == 0x40)
    
    print(string.format("Testing: %s", description))
    print(string.format("  GUID: %s", guid))
    print(string.format("  Type byte: 0x%02X", guidType or 0))
    print(string.format("  Is NPC: %s", tostring(isNPC)))
    print(string.format("  Expected: %s", expected_type))
    
    if (expected_type == "NPC" and isNPC) or (expected_type == "Object" and not isNPC) then
        print("  ✓ PASS")
    else
        print("  ✗ FAIL")
    end
    print("")
end

print("=== WoW 3.3.5 GUID Type Testing ===")
print("Testing GUID type detection for NPCs vs Objects")
print("")

-- Test NPCs (should be detected as NPCs)
TestGUIDType("0xF130000B5D00019E", "NPC", "Standard NPC (0xF1 30)")
TestGUIDType("0xF130000B5D00019E", "NPC", "Quest Giver NPC")
TestGUIDType("0xF1300016A4001234", "NPC", "Another NPC")
TestGUIDType("0xF110000B5D00019E", "NPC", "Different NPC type (0xF1 10)")

-- Test Objects (should NOT be detected as NPCs)
TestGUIDType("0xF150000B5D00019E", "Object", "Game Object (0xF1 50)")
TestGUIDType("0xF170000B5D00019E", "Object", "Dynamic Object (0xF1 70)")
TestGUIDType("0xF160000B5D00019E", "Object", "Item (0xF1 60)")
TestGUIDType("0xF1500001F4001234", "Object", "Pirate's Treasure (object)")

-- Test Player GUIDs (should NOT be detected as NPCs)
TestGUIDType("0x0000000000000001", "Object", "Player GUID")
TestGUIDType("0x0100000000000001", "Object", "Another Player format")

print("=== Test Complete ===")
print("The fix should correctly identify NPCs (0x30, 0x10, 0x40) and reject objects/players")