#!/usr/bin/env python3
"""
Test script to verify arXiv 2026 ID handling
Run: uv run python test_arxiv_2026.py
"""

import sys
sys.path.insert(0, 'src')

from paper2saas.utils import validate_arxiv_id

def test_validation():
    """Test that validation accepts 2026 IDs"""
    test_cases = [
        ("2602.04503", True, "February 2026 - CURRENT paper"),
        ("2601.12345", True, "January 2026 - CURRENT paper"),
        ("2612.99999", True, "December 2026 - CURRENT paper"),
        ("2301.12345", True, "January 2023 - past paper"),
        ("0704.0001", True, "April 2007 - old format"),
        ("123.456", False, "Invalid format"),
    ]
    
    print("=" * 70)
    print("arXiv ID Validation Test")
    print("=" * 70)
    
    all_passed = True
    for arxiv_id, expected, description in test_cases:
        result = validate_arxiv_id(arxiv_id)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        if result != expected:
            all_passed = False
        
        print(f"{status} | {arxiv_id:15} | {description}")
    
    print("=" * 70)
    if all_passed:
        print("✓ All validation tests passed!")
    else:
        print("✗ Some tests failed!")
        sys.exit(1)

def check_instructions():
    """Verify that agent instructions include 2026 context"""
    from paper2saas.prompts.research import PAPER_ANALYZER_INSTRUCTIONS
    from paper2saas.prompts.reporting import PAPER2SAAS_TEAM_INSTRUCTIONS
    
    print("\n" + "=" * 70)
    print("Agent Instructions Check")
    print("=" * 70)
    
    checks = [
        ("Current Year: 2026" in PAPER_ANALYZER_INSTRUCTIONS, 
         "PAPER_ANALYZER has 2026 context"),
        ("2602.04503" in PAPER_ANALYZER_INSTRUCTIONS,
         "PAPER_ANALYZER has 2026 example"),
        ("MANDATORY TOOL USAGE" in PAPER_ANALYZER_INSTRUCTIONS,
         "PAPER_ANALYZER enforces tool usage"),
        ("simulate" in PAPER_ANALYZER_INSTRUCTIONS.lower(),
         "PAPER_ANALYZER warns against simulation"),
        ("Current Year: 2026" in PAPER2SAAS_TEAM_INSTRUCTIONS,
         "Team supervisor has 2026 context"),
    ]
    
    all_passed = True
    for check, description in checks:
        status = "✓ PASS" if check else "✗ FAIL"
        if not check:
            all_passed = False
        print(f"{status} | {description}")
    
    print("=" * 70)
    if all_passed:
        print("✓ All instruction checks passed!")
    else:
        print("✗ Some instruction checks failed!")
        sys.exit(1)

if __name__ == "__main__":
    test_validation()
    check_instructions()
    print("\n✓ All tests passed! The fix is properly implemented.")
