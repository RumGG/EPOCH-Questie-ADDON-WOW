#!/usr/bin/env python3
"""
Base validator class for Questie database validation.
Each specific validator inherits from this base class.
"""

import re
import os
from pathlib import Path
from abc import ABC, abstractmethod

class ValidatorBase(ABC):
    """Base class for all validators."""
    
    def __init__(self, auto_fix=False):
        self.auto_fix = auto_fix
        self.issues = []
        self.fixes_applied = []
        
    @abstractmethod
    def name(self):
        """Return the name of this validator."""
        pass
    
    @abstractmethod
    def description(self):
        """Return a description of what this validator checks."""
        pass
    
    @abstractmethod
    def validate_line(self, line, line_num, entry_type='quest'):
        """
        Validate a single line.
        Returns: (has_issue, issue_description, fixed_line)
        """
        pass
    
    def validate_file(self, filepath, entry_type='quest'):
        """Validate an entire file."""
        self.issues = []
        self.fixes_applied = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Skip non-entry lines
            if not line.strip().startswith('['):
                fixed_lines.append(line)
                continue
            
            # Skip commented lines
            if line.strip().startswith('--'):
                fixed_lines.append(line)
                continue
            
            has_issue, issue_desc, fixed_line = self.validate_line(line, line_num, entry_type)
            
            if has_issue:
                self.issues.append(f"Line {line_num}: {issue_desc}")
                if self.auto_fix and fixed_line:
                    fixed_lines.append(fixed_line)
                    self.fixes_applied.append(f"Line {line_num}: {issue_desc} - FIXED")
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return self.issues, fixed_lines
    
    def run(self, filepath, entry_type='quest'):
        """Run the validator on a file."""
        print(f"\n[{self.name()}] {self.description()}")
        print("-" * 60)
        
        issues, fixed_lines = self.validate_file(filepath, entry_type)
        
        if issues:
            print(f"Found {len(issues)} issue(s):")
            for issue in issues[:5]:  # Show first 5
                print(f"  • {issue}")
            if len(issues) > 5:
                print(f"  ... and {len(issues) - 5} more")
            
            if self.auto_fix and self.fixes_applied:
                # Save fixed file
                output_path = filepath.replace('.lua', f'_{self.name()}_FIXED.lua')
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.writelines(fixed_lines)
                print(f"\n✅ Fixed {len(self.fixes_applied)} issue(s)")
                print(f"Output saved to: {output_path}")
            else:
                print("\n💡 Run with --fix to auto-fix these issues")
        else:
            print("✅ No issues found")
        
        return len(issues) == 0