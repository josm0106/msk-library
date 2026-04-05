import base64, sys
# Read base64 from file and decode to output file
with open(sys.argv[1], 'r') as f:
    b64 = f.read().strip()
with open(sys.argv[2], 'wb') as f:
    f.write(base64.b64decode(b64))
print(f"Decoded {len(b64)} base64 chars to {sys.argv[2]}")
