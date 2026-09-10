import os
import sys

print('Python:', sys.version)
print('Working dir:', os.getcwd())

# Test network with a simple request
import urllib.request
try:
    print('Testing urllib.request to httpbin.org...')
    req = urllib.request.urlopen('http://httpbin.org/ip', timeout=5)
    print('Success:', req.read().decode()[:100])
except Exception as e:
    print('urllib error:', type(e).__name__, str(e)[:200])

# Test HTTPS
try:
    print('Testing urllib.request to https://httpbin.org...')
    req = urllib.request.urlopen('https://httpbin.org/ip', timeout=5)
    print('Success:', req.read().decode()[:100])
except Exception as e:
    print('urllib HTTPS error:', type(e).__name__, str(e)[:200])

print('Done')
