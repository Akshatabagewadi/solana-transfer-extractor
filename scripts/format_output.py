#!/usr/bin/env python3
\"\"\"Convert Substreams protobuf-JSON output into one transfer JSON object per line.

Usage:
  python3 scripts/format_output.py < substreams-output.json > transfers.jsonl

The script accepts a single protobuf JSON object, an array of such objects,
or newline-delimited JSON. It normalizes protobuf uint64 strings to JSON integers.
\"\"\"
import json
import sys

def walk(obj):
    if isinstance(obj, list):
        for item in obj:
            yield from walk(item)
    elif isinstance(obj, dict):
        if "transfers" in obj and isinstance(obj["transfers"], list):
            for transfer in obj["transfers"]:
                yield transfer
        elif {"from", "to", "amount"}.issubset(obj.keys()):
            yield obj
        else:
            for value in obj.values():
                if isinstance(value, (dict, list)):
                    yield from walk(value)

raw = sys.stdin.read().strip()
if not raw:
    raise SystemExit("No JSON input received")

# Accept either one JSON document or newline-delimited JSON records.
try:
    payload = json.loads(raw)
    records = list(walk(payload))
except json.JSONDecodeError:
    records = []
    for line in raw.splitlines():
        if line.strip():
            records.extend(walk(json.loads(line)))

for item in records:
    print(json.dumps({
        "from": item["from"],
        "to": item["to"],
        "amount": int(item["amount"]),
    }, separators=(",", ":")))
