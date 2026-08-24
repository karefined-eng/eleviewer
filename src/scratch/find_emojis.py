import os, re
import sys

emoji_pattern = re.compile(
    r'['
    r'\U00010000-\U0010ffff'
    r'\u2600-\u27BF'
    r'\u2300-\u23FF'
    r']'
)

for root, _, files in os.walk(r'c:\Users\kwadw\Documents\eleviewer'):
    if 'venv' in root or '.git' in root or '__pycache__' in root or 'build' in root or 'dist' in root or 'scratch' in root or 'tests' in root:
        continue
    for file in files:
        if not file.endswith('.py'):
            continue
        filepath = os.path.join(root, file)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                if emoji_pattern.search(line):
                    print(f"{file}:{i+1} {line.strip()}")
        except Exception as e:
            pass
