import json
import os

SERVICE_ACCOUNT_FILE = 'service_account.json'

try:
    with open(SERVICE_ACCOUNT_FILE, 'r', encoding='utf-8') as f:
        data = f.read()
        print(f"File content length: {len(data)}")
        print(f"File content snippet: {repr(data[:100])}")
        
    with open(SERVICE_ACCOUNT_FILE, 'r', encoding='utf-8') as f:
        info = json.load(f)
        
    key = info.get('private_key', '')
    print(f"Original key length: {len(key)}")
    print(f"Original key repr snippet: {repr(key[:100])}")
    
    # Simulate the fix
    fixed_key = key.replace('\\n', '\n')
    print(f"Fixed key length: {len(fixed_key)}")
    print(f"Fixed key repr snippet: {repr(fixed_key[:100])}")
    
    # Check for backslashes
    if '\\' in fixed_key:
        print(f"WARNING: Backslash validation failed! Found {fixed_key.count('\\')} backslashes.")
        print(f"First backslash index: {fixed_key.find('\\')}")
        print(f"Context around first backslash: {repr(fixed_key[fixed_key.find('\\')-10:fixed_key.find('\\')+10])}")
    else:
        print("SUCCESS: No backslashes found in fixed key.")

except Exception as e:
    print(f"ERROR: {e}")
