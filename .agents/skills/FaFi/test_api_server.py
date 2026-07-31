#!/usr/bin/env python3
"""Test script for the Skill & Agent Hub API Server."""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from adapters.api_server import app, registry, discovery, orchestrator, adapters

def test_endpoints():
    """Test all major API endpoints."""
    
    results = {
        "passed": [],
        "failed": [],
        "warnings": []
    }
    
    with app.test_client() as client:
        
        # Test 1: Health Check
        print("\n1. Testing Health Check...")
        response = client.get('/api/v1/health')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('status') == 'healthy':
                results["passed"].append("Health Check: OK")
                print(f"   ✓ Status: {data}")
            else:
                results["failed"].append(f"Health Check: Unexpected status {data}")
        else:
            results["failed"].append(f"Health Check: HTTP {response.status_code}")
        
        # Test 2: Info Endpoint
        print("\n2. Testing Info Endpoint...")
        response = client.get('/api/v1/info')
        if response.status_code == 200:
            data = response.get_json()
            results["passed"].append("Info Endpoint: OK")
            print(f"   ✓ Version: {data.get('version')}")
            print(f"   ✓ Total Skills: {data.get('statistics', {}).get('total_skills')}")
            print(f"   ✓ Total Agents: {data.get('statistics', {}).get('total_agents')}")
        else:
            results["failed"].append(f"Info Endpoint: HTTP {response.status_code}")
        
        # Test 3: Registry Scan
        print("\n3. Testing Registry Scan...")
        response = client.post('/api/v1/registry/scan')
        if response.status_code == 200:
            data = response.get_json()
            results["passed"].append(f"Registry Scan: {data.get('registered_count')} entities")
            print(f"   ✓ Registered: {data.get('registered_count')} entities")
        else:
            results["failed"].append(f"Registry Scan: HTTP {response.status_code}")
        
        # Test 4: List All Entities
        print("\n4. Testing Registry List...")
        response = client.get('/api/v1/registry/list')
        if response.status_code == 200:
            data = response.get_json()
            results["passed"].append(f"Registry List: {data.get('count')} entities")
            print(f"   ✓ Count: {data.get('count')}")
        else:
            results["failed"].append(f"Registry List: HTTP {response.status_code}")
        
        # Test 5: List Skills Only
        print("\n5. Testing Skills List...")
        response = client.get('/api/v1/registry/list?type=skill')
        if response.status_code == 200:
            data = response.get_json()
            skills = data.get('entities', [])
            results["passed"].append(f"Skills List: {len(skills)} skills")
            print(f"   ✓ Skills: {len(skills)}")
            for s in skills[:5]:
                print(f"      - {s.get('name')}")
        else:
            results["failed"].append(f"Skills List: HTTP {response.status_code}")
        
        # Test 6: List Imported Skills
        print("\n6. Testing Imported Skills...")
        response = client.get('/api/v1/registry/imported')
        if response.status_code == 200:
            data = response.get_json()
            results["passed"].append(f"Imported Skills: {data.get('total_count')} skills")
            print(f"   ✓ Total imported: {data.get('total_count')}")
            print(f"   ✓ By platform: {list(data.get('by_platform', {}).keys())}")
        else:
            results["failed"].append(f"Imported Skills: HTTP {response.status_code}")
        
        # Test 7: Discovery
        print("\n7. Testing Discovery...")
        response = client.post('/api/v1/discover', 
            json={"query": "text zusammenfassen", "limit": 3})
        if response.status_code == 200:
            data = response.get_json()
            results["passed"].append(f"Discovery: {data.get('count')} results")
            print(f"   ✓ Found: {data.get('count')} matching skills")
            for r in data.get('results', [])[:3]:
                print(f"      - {r['entity']['name']} (score: {r['relevance_score']:.2f})")
        else:
            results["failed"].append(f"Discovery: HTTP {response.status_code}")
        
        # Test 8: Platform Catalogs
        print("\n8. Testing Platform Catalogs...")
        platforms = ['claude', 'manus', 'chatgpt_codex', 'antigravity']
        for platform in platforms:
            response = client.get(f'/api/v1/catalog/{platform}')
            if response.status_code == 200:
                results["passed"].append(f"Catalog {platform}: OK")
                print(f"   ✓ {platform}: OK")
            else:
                results["failed"].append(f"Catalog {platform}: HTTP {response.status_code}")
                print(f"   ✗ {platform}: FAILED")
        
        # Test 9: Get Specific Entity
        print("\n9. Testing Get Entity...")
        response = client.get('/api/v1/registry/get/text_summarizer')
        if response.status_code == 200:
            data = response.get_json()
            results["passed"].append("Get Entity: OK")
            print(f"   ✓ Found: {data.get('entity', {}).get('name')}")
        elif response.status_code == 404:
            results["warnings"].append("Get Entity: text_summarizer not found (may be expected)")
            print("   ⚠ text_summarizer not found")
        else:
            results["failed"].append(f"Get Entity: HTTP {response.status_code}")
        
        # Test 10: Suggest Composition
        print("\n10. Testing Suggest Composition...")
        response = client.post('/api/v1/suggest-composition',
            json={"task": "Lade eine Webseite und fasse den Inhalt zusammen"})
        if response.status_code == 200:
            data = response.get_json()
            composition = data.get('composition', {})
            steps = composition.get('steps', [])
            results["passed"].append(f"Suggest Composition: {len(steps)} steps")
            print(f"   ✓ Suggested {len(steps)} steps")
            for step in steps:
                print(f"      Step {step.get('step_number')}: {step.get('suggested_skill')}")
        else:
            results["failed"].append(f"Suggest Composition: HTTP {response.status_code}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"\n✓ PASSED: {len(results['passed'])}")
    for p in results['passed']:
        print(f"   {p}")
    
    if results['warnings']:
        print(f"\n⚠ WARNINGS: {len(results['warnings'])}")
        for w in results['warnings']:
            print(f"   {w}")
    
    if results['failed']:
        print(f"\n✗ FAILED: {len(results['failed'])}")
        for f in results['failed']:
            print(f"   {f}")
    
    return results

if __name__ == "__main__":
    print("="*60)
    print("Skill & Agent Hub - API Server Test Suite")
    print("="*60)
    
    # First scan the registry
    print("\nInitializing registry...")
    count = registry.scan_and_register()
    print(f"Registered {count} entities")
    
    # Run tests
    results = test_endpoints()
    
    # Exit code
    if results['failed']:
        sys.exit(1)
    else:
        sys.exit(0)
