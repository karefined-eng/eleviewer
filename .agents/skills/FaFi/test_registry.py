#!/usr/bin/env python3
"""Test script for the Skill & Agent Hub registry."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from registry.registry import SkillAgentRegistry

def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_path, 'registry', 'registry.db')
    
    print(f"Base path: {base_path}")
    print(f"DB path: {db_path}")
    
    # Initialize registry
    registry = SkillAgentRegistry(db_path=db_path, base_path=base_path)
    print("Registry initialized")
    
    # Scan and register
    count = registry.scan_and_register()
    print(f"Registered: {count} entities")
    
    # List skills
    skills = registry.list_all('skill')
    print(f"\nSkills found: {len(skills)}")
    for s in skills[:10]:
        print(f"  - {s['name']}")
    
    # List agents
    agents = registry.list_all('agent')
    print(f"\nAgents found: {len(agents)}")
    for a in agents:
        print(f"  - {a['name']}")
    
    print("\nRegistry test completed successfully!")

if __name__ == "__main__":
    main()
