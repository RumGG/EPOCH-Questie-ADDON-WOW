#!/usr/bin/env python3
"""
Comprehensive analysis and validation of pfQuest to Questie conversion
Ensures data is properly translated between the two database formats
"""

import re
import json
from typing import Dict, List, Any, Tuple

# Questie database field structure (30 fields)
QUESTIE_FIELDS = [
    (1, "name", "string", "Quest name"),
    (2, "startedBy", "table", "{{NPCs},{Objects},{Items}} that start quest"),
    (3, "finishedBy", "table", "{{NPCs},{Objects}} where quest is turned in"),
    (4, "requiredLevel", "number/nil", "Minimum level to get quest"),
    (5, "questLevel", "number", "Quest's level"),
    (6, "requiredRaces", "bitmask/nil", "Race restrictions (nil = all races)"),
    (7, "requiredClasses", "bitmask/nil", "Class restrictions (nil = all classes)"),
    (8, "objectivesText", "table/string", "Quest objectives description"),
    (9, "triggerEnd", "table", "Exploration trigger: {text, {[zoneID]={{x,y}}}}"),
    (10, "objectives", "table", "Complex objectives structure - see below"),
    (11, "sourceItemId", "number/nil", "Item provided by quest giver"),
    (12, "preQuestGroup", "table", "{questId,...} ALL must be done"),
    (13, "preQuestSingle", "table", "{questId,...} ANY must be done"),
    (14, "childQuests", "table", "{questId,...} Unlocked by this quest"),
    (15, "inGroupWith", "table", "{questId,...} Part of same chain"),
    (16, "exclusiveTo", "table", "{questId,...} Can't have both"),
    (17, "zoneOrSort", "number", ">0 is zoneID, <0 is QuestSort"),
    (18, "requiredSkill", "table", "{skillId, value} Profession requirement"),
    (19, "requiredMinRep", "table", "{factionId, value} Min reputation"),
    (20, "requiredMaxRep", "table", "{factionId, value} Max reputation"),
    (21, "requiredSourceItems", "table", "{itemId,...} Items needed to start"),
    (22, "nextQuestInChain", "number", "Direct follow-up quest"),
    (23, "questFlags", "number", "Special flags"),
    (24, "specialFlags", "number", "More flags (0 common)"),
    (25, "parentQuest", "number", "Parent quest ID"),
    (26, "reputationReward", "table", "{{factionId, value},...}"),
    (27, "extraObjectives", "table", "{{spellId, text},...}"),
    (28, "requiredSpell", "number", "Spell requirement"),
    (29, "requiredSpecialization", "number", "Spec requirement"),
    (30, "requiredMaxLevel", "number", "Maximum level")
]

# Objectives structure (field 10)
OBJECTIVES_STRUCTURE = """
{
    [1] creatures,    -- {{npcId, count, "optional text"},...}
    [2] objects,      -- {{objectId, count, "text"},...}
    [3] items,        -- {{itemId, count},...}
    [4] reputation,   -- {factionId, value}
    [5] killCredit,   -- {{npcIds...}, baseNpcId, "text"}
    [6] spells        -- {{spellId, "text"},...}
}
"""

def parse_quest_line(line: str) -> Tuple[int, List[Any]]:
    """Parse a quest line and extract quest ID and all fields"""
    # Match quest ID
    id_match = re.match(r'\s*\[(\d+)\]\s*=\s*\{(.*)\},?\s*(?:--.*)?$', line)
    if not id_match:
        return None, None
    
    quest_id = int(id_match.group(1))
    data_str = id_match.group(2)
    
    # Parse the fields - this is complex due to nested structures
    fields = []
    current_field = ""
    depth = 0
    in_string = False
    escape_next = False
    
    for char in data_str:
        if escape_next:
            current_field += char
            escape_next = False
            continue
            
        if char == '\\':
            escape_next = True
            current_field += char
            continue
            
        if char == '"' and not escape_next:
            in_string = not in_string
            current_field += char
            continue
            
        if not in_string:
            if char == '{':
                depth += 1
                current_field += char
            elif char == '}':
                depth -= 1
                current_field += char
            elif char == ',' and depth == 0:
                # End of field
                fields.append(current_field.strip())
                current_field = ""
            else:
                current_field += char
        else:
            current_field += char
    
    # Don't forget the last field
    if current_field.strip():
        fields.append(current_field.strip())
    
    return quest_id, fields

def validate_field(field_num: int, value: str, field_def: Tuple) -> List[str]:
    """Validate a single field against its definition"""
    issues = []
    field_name = field_def[1]
    field_type = field_def[2]
    
    # Handle nil values
    if value == "nil":
        if "nil" not in field_type:
            issues.append(f"Field {field_num} ({field_name}): nil not allowed, expected {field_type}")
        return issues
    
    # Check field types
    if field_type == "string":
        if not value.startswith('"'):
            issues.append(f"Field {field_num} ({field_name}): Expected string, got {value[:20]}")
    
    elif field_type == "number":
        try:
            int(value)
        except:
            issues.append(f"Field {field_num} ({field_name}): Expected number, got {value}")
    
    elif field_type == "table":
        if not value.startswith('{'):
            issues.append(f"Field {field_num} ({field_name}): Expected table, got {value[:20]}")
    
    elif "bitmask" in field_type:
        if value != "nil":
            try:
                int(value)
            except:
                issues.append(f"Field {field_num} ({field_name}): Expected bitmask (number), got {value}")
    
    return issues

def analyze_quest(quest_id: int, fields: List[str]) -> Dict:
    """Analyze a quest entry for issues"""
    analysis = {
        "quest_id": quest_id,
        "field_count": len(fields),
        "issues": [],
        "warnings": [],
        "data_quality": {}
    }
    
    # Check field count
    if len(fields) != 30:
        analysis["issues"].append(f"Wrong field count: {len(fields)} (expected 30)")
        return analysis
    
    # Validate each field
    for i, field_value in enumerate(fields):
        field_num = i + 1
        if field_num <= len(QUESTIE_FIELDS):
            field_def = QUESTIE_FIELDS[i]
            issues = validate_field(field_num, field_value, field_def)
            if issues:
                analysis["issues"].extend(issues)
    
    # Check for data quality
    # Field 1: Quest name
    if fields[0] != "nil":
        name = fields[0].strip('"')
        if "[Epoch]" in name:
            analysis["warnings"].append("Placeholder quest name")
            analysis["data_quality"]["has_real_name"] = False
        else:
            analysis["data_quality"]["has_real_name"] = True
    
    # Field 2: Quest givers
    if fields[1] != "nil":
        analysis["data_quality"]["has_quest_giver"] = True
    
    # Field 3: Turn-in NPCs
    if fields[2] != "nil":
        analysis["data_quality"]["has_turn_in"] = True
    
    # Field 8: Objectives text
    if fields[7] != "nil":
        analysis["data_quality"]["has_objectives_text"] = True
    
    # Field 10: Objectives structure
    if fields[9] != "nil":
        analysis["data_quality"]["has_objectives"] = True
    
    # Check for potential contamination
    if quest_id >= 8000 and quest_id < 12000:
        analysis["warnings"].append(f"Quest ID {quest_id} in TBC range (8000-11999)")
    elif quest_id >= 12000 and quest_id < 15000:
        analysis["warnings"].append(f"Quest ID {quest_id} in Wrath range (12000-14999)")
    
    return analysis

def analyze_file(filepath: str) -> Dict:
    """Analyze entire quest database file"""
    print(f"Analyzing {filepath}...")
    
    results = {
        "total_quests": 0,
        "valid_quests": 0,
        "invalid_quests": 0,
        "contaminated_quests": [],
        "field_issues": {},
        "data_quality_summary": {
            "with_real_names": 0,
            "with_quest_givers": 0,
            "with_turn_ins": 0,
            "with_objectives_text": 0,
            "with_objectives": 0
        }
    }
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if re.match(r'\s*\[\d+\]', line):
                quest_id, fields = parse_quest_line(line)
                if quest_id and fields:
                    results["total_quests"] += 1
                    
                    analysis = analyze_quest(quest_id, fields)
                    
                    if analysis["issues"]:
                        results["invalid_quests"] += 1
                        results["field_issues"][quest_id] = analysis["issues"]
                    else:
                        results["valid_quests"] += 1
                    
                    if analysis["warnings"]:
                        for warning in analysis["warnings"]:
                            if "TBC range" in warning or "Wrath range" in warning:
                                results["contaminated_quests"].append(quest_id)
                    
                    # Update quality summary
                    for key, value in analysis["data_quality"].items():
                        if value:
                            metric = key.replace("has_", "with_")
                            if metric in results["data_quality_summary"]:
                                results["data_quality_summary"][metric] += 1
    
    return results

def generate_report(results: Dict, filename: str):
    """Generate detailed validation report"""
    report = f"""
PFQUEST TO QUESTIE CONVERSION VALIDATION REPORT
{'='*60}

FILE: {filename}

SUMMARY:
--------
Total Quests: {results['total_quests']}
Valid Structure: {results['valid_quests']}
Invalid Structure: {results['invalid_quests']}
Potentially Contaminated: {len(results['contaminated_quests'])}

DATA QUALITY:
-------------
Quests with Real Names: {results['data_quality_summary']['with_real_names']} ({100*results['data_quality_summary']['with_real_names']/max(1,results['total_quests']):.1f}%)
Quests with Quest Givers: {results['data_quality_summary']['with_quest_givers']} ({100*results['data_quality_summary']['with_quest_givers']/max(1,results['total_quests']):.1f}%)
Quests with Turn-in NPCs: {results['data_quality_summary']['with_turn_ins']} ({100*results['data_quality_summary']['with_turn_ins']/max(1,results['total_quests']):.1f}%)
Quests with Objectives Text: {results['data_quality_summary']['with_objectives_text']} ({100*results['data_quality_summary']['with_objectives_text']/max(1,results['total_quests']):.1f}%)
Quests with Objectives Data: {results['data_quality_summary']['with_objectives']} ({100*results['data_quality_summary']['with_objectives']/max(1,results['total_quests']):.1f}%)

CONTAMINATION CHECK:
--------------------
"""
    
    if results['contaminated_quests']:
        report += f"Found {len(results['contaminated_quests'])} potentially contaminated quests:\n"
        for qid in results['contaminated_quests'][:10]:
            report += f"  - Quest {qid}\n"
        if len(results['contaminated_quests']) > 10:
            report += f"  ... and {len(results['contaminated_quests']) - 10} more\n"
    else:
        report += "✅ No contamination detected\n"
    
    report += """
FIELD STRUCTURE ISSUES:
-----------------------
"""
    
    if results['field_issues']:
        report += f"Found issues in {len(results['field_issues'])} quests:\n"
        for qid, issues in list(results['field_issues'].items())[:5]:
            report += f"\nQuest {qid}:\n"
            for issue in issues:
                report += f"  - {issue}\n"
        if len(results['field_issues']) > 5:
            report += f"\n... and {len(results['field_issues']) - 5} more quests with issues\n"
    else:
        report += "✅ All quests have valid structure\n"
    
    report += """
RECOMMENDATIONS:
----------------
"""
    
    if results['invalid_quests'] > 0:
        report += "⚠️ Fix field structure issues before using this database\n"
    
    if len(results['contaminated_quests']) > 0:
        report += "⚠️ Remove contaminated quests from other expansions\n"
    
    if results['data_quality_summary']['with_objectives'] == 0:
        report += "⚠️ No quests have objectives data - tracking won't work properly\n"
    
    if results['valid_quests'] == results['total_quests'] and len(results['contaminated_quests']) == 0:
        report += "✅ Database appears ready for use!\n"
    
    return report

def main():
    # Analyze the converted pfQuest data
    pfquest_file = "pfquest_converted_quests.lua"
    if os.path.exists(pfquest_file):
        results = analyze_file(pfquest_file)
        report = generate_report(results, pfquest_file)
        
        with open("pfquest_conversion_validation.txt", "w") as f:
            f.write(report)
        
        print(report)
        
        # Check if we should proceed
        if results['invalid_quests'] > 0:
            print("\n❌ CRITICAL: Database has structural issues that must be fixed!")
            return False
        elif len(results['contaminated_quests']) > 0:
            print(f"\n⚠️ WARNING: Found {len(results['contaminated_quests'])} contaminated quests")
            print("These should be removed before final use")
            return True
        else:
            print("\n✅ Database structure is valid!")
            return True
    else:
        print(f"File not found: {pfquest_file}")
        return False

if __name__ == "__main__":
    import os
    import sys
    
    success = main()
    sys.exit(0 if success else 1)