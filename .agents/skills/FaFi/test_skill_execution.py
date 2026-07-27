#!/usr/bin/env python3
"""Test script for skill execution."""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from registry.registry import SkillAgentRegistry
from orchestrator.orchestrator import Orchestrator

def test_skill_execution():
    """Test executing various skills."""
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    registry = SkillAgentRegistry(
        db_path=os.path.join(base_path, 'registry', 'registry.db'),
        base_path=base_path
    )
    orchestrator = Orchestrator(registry, base_path)
    
    # Scan registry first
    registry.scan_and_register()
    
    results = {
        "tested": [],
        "passed": [],
        "failed": [],
        "skipped": []
    }
    
    # Test 1: text_summarizer (native skill)
    print("\n1. Testing text_summarizer skill...")
    try:
        result = orchestrator.execute_skill('text_summarizer', {
            'text': 'Dies ist ein sehr langer Text, der zusammengefasst werden soll. Er enthält viele wichtige Informationen über verschiedene Themen. Die Zusammenfassung sollte die Kernpunkte erfassen.',
            'max_length': 50
        })
        results["tested"].append("text_summarizer")
        if 'summary' in result:
            results["passed"].append("text_summarizer: Execution successful")
            print(f"   ✓ Summary generated: {result.get('summary', '')[:100]}...")
        else:
            results["failed"].append(f"text_summarizer: Unexpected result {result}")
    except Exception as e:
        results["tested"].append("text_summarizer")
        results["failed"].append(f"text_summarizer: {str(e)}")
        print(f"   ✗ Error: {e}")
    
    # Test 2: data_analyzer (native skill)
    print("\n2. Testing data_analyzer skill...")
    try:
        test_data = [
            {"name": "A", "value": 10},
            {"name": "B", "value": 20},
            {"name": "C", "value": 30}
        ]
        result = orchestrator.execute_skill('data_analyzer', {
            'data': test_data,
            'analysis_type': 'summary'
        })
        results["tested"].append("data_analyzer")
        if 'analysis' in result or 'statistics' in result:
            results["passed"].append("data_analyzer: Execution successful")
            print(f"   ✓ Analysis result: {json.dumps(result, indent=2)[:200]}...")
        else:
            results["failed"].append(f"data_analyzer: Unexpected result {result}")
    except Exception as e:
        results["tested"].append("data_analyzer")
        results["failed"].append(f"data_analyzer: {str(e)}")
        print(f"   ✗ Error: {e}")
    
    # Test 3: file_reader (native skill)
    print("\n3. Testing file_reader skill...")
    try:
        # Create a test file
        test_file_path = os.path.join(base_path, 'test_file.txt')
        with open(test_file_path, 'w') as f:
            f.write("This is a test file content.\nLine 2.\nLine 3.")
        
        result = orchestrator.execute_skill('file_reader', {
            'file_path': test_file_path
        })
        results["tested"].append("file_reader")
        if 'content' in result:
            results["passed"].append("file_reader: Execution successful")
            print(f"   ✓ File content read: {result.get('content', '')[:100]}...")
        else:
            results["failed"].append(f"file_reader: Unexpected result {result}")
        
        # Cleanup
        os.remove(test_file_path)
    except Exception as e:
        results["tested"].append("file_reader")
        results["failed"].append(f"file_reader: {str(e)}")
        print(f"   ✗ Error: {e}")
    
    # Test 4: web_scraper (native skill)
    print("\n4. Testing web_scraper skill...")
    try:
        result = orchestrator.execute_skill('web_scraper', {
            'url': 'https://example.com'
        })
        results["tested"].append("web_scraper")
        if 'content' in result or 'html' in result or 'text' in result:
            results["passed"].append("web_scraper: Execution successful")
            print(f"   ✓ Web content scraped successfully")
        else:
            results["failed"].append(f"web_scraper: Unexpected result {result}")
    except Exception as e:
        results["tested"].append("web_scraper")
        results["failed"].append(f"web_scraper: {str(e)}")
        print(f"   ✗ Error: {e}")
    
    # Test 5: Check imported skills (they require API keys)
    print("\n5. Checking imported skills (API-dependent)...")
    imported_skills = [
        'openai_chat_completion',
        'openai_dalle_generate',
        'perplexity_web_search',
        'hubspot_crm_operations'
    ]
    
    for skill_name in imported_skills:
        skill = registry.get_by_name(skill_name)
        if skill:
            results["skipped"].append(f"{skill_name}: Requires API key")
            print(f"   ⚠ {skill_name}: Skipped (requires API key)")
        else:
            results["skipped"].append(f"{skill_name}: Not found")
            print(f"   ⚠ {skill_name}: Not found in registry")
    
    # Summary
    print("\n" + "="*60)
    print("SKILL EXECUTION TEST SUMMARY")
    print("="*60)
    
    print(f"\nTested: {len(results['tested'])} skills")
    print(f"✓ Passed: {len(results['passed'])}")
    for p in results['passed']:
        print(f"   {p}")
    
    if results['failed']:
        print(f"\n✗ Failed: {len(results['failed'])}")
        for f in results['failed']:
            print(f"   {f}")
    
    print(f"\n⚠ Skipped: {len(results['skipped'])}")
    for s in results['skipped']:
        print(f"   {s}")
    
    return results

if __name__ == "__main__":
    print("="*60)
    print("Skill & Agent Hub - Skill Execution Tests")
    print("="*60)
    
    results = test_skill_execution()
