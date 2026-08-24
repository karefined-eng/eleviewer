import os

with open('ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("font-weight: 800;", "font-weight: bold;")
content = content.replace("letter-spacing: -1px;", "")
content = content.replace("letter-spacing: 1px;", "")

with open('ui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("CSS Fixed")
