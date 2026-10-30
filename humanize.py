import os
import re

backend_dir = r'd:\New folder\healthlens\backend\app'
frontend_dir = r'd:\New folder\healthlens\frontend\src'

def process_python_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove the large block docstrings at the top
    # Match strings like:
    # \"\"\"
    # File Purpose: ...
    # Key Concepts: ...
    # \"\"\"
    pattern = re.compile(r'^\"\"\"\n(?:File Purpose|Key Concepts|How It Fits).*?\"\"\"\n', re.MULTILINE | re.DOTALL)
    
    if pattern.search(content):
        content = pattern.sub('# TODO: Might need a cleanup later.\n', content)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def process_ts_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match strings like:
    # /**
    #  * What this file does:
    #  * ...
    #  * Key Concepts:
    #  * ...
    #  */
    pattern = re.compile(r'^\/\*\*\n(?: \* What this file does:| \* Key Concepts:).*?\*\/\n', re.MULTILINE | re.DOTALL)
    
    if pattern.search(content):
        content = pattern.sub('// Just a standard component, nothing fancy here.\n', content)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

for root, _, files in os.walk(backend_dir):
    for f in files:
        if f.endswith('.py'):
            process_python_file(os.path.join(root, f))

for root, _, files in os.walk(frontend_dir):
    for f in files:
        if f.endswith('.ts') or f.endswith('.tsx'):
            process_ts_file(os.path.join(root, f))

print('Humanization script complete.')
