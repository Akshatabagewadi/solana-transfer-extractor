import json
import struct
from pathlib import Path

SYSTEM_PROGRAM = "11111111111111111111111111111111"
TOKEN_PROGRAMS = {
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb",
}

def b58decode(value):
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    number = 0
    for char in value:
        number = number * 58 + alphabet.index(char)

    decoded = number.to_bytes((number.bit_length() + 7) // 8, "big")
    return b"\0" * (len(value) - len(value.lstrip("1"))) + decoded

def extract_block(block_number):
    path = Path(f"block-385870{block_number}.json")
    data = json.loads(path.read_text())
    result = data.get("result")

    if result is None:
        raise ValueError(f"No block result in {path}")

    transfers = []

    for tx in result.get("transactions", []):
        meta = tx.get("meta") or {}
        if meta.get("err") is not None:
            continue

        message = tx["transaction"]["message"]
        keys = [
            item["pubkey"] if isinstance(item, dict) else item
            for item in message.get("accountKeys", [])
        ]

        loaded = meta.get("loadedAddresses") or {}
        keys += loaded.get("writable", [])
        keys += loaded.get("readonly", [])

        owners = {}
        for balance in meta.get("preTokenBalances", []) + meta.get("postTokenBalances", []):
            if balance.get("owner"):
                owners[balance["accountIndex"]] = balance["owner"]

        def process(ix):
            try:
                program_index = ix["programIdIndex"]
                program = keys[program_index]
                accounts = ix.get("accounts", [])
                raw = b58decode(ix["data"])

                if program == SYSTEM_PROGRAM and len(raw) >= 12:
                    instruction_type = struct.unpack("<I", raw[:4])[0]
                    if instruction_type == 2 and len(accounts) >= 2:
                        amount = struct.unpack("<Q", raw[4:12])[0]
                        transfers.append({
                            "from": keys[accounts[0]],
                            "to": keys[accounts[1]],
                            "amount": amount
                        })

                elif program in TOKEN_PROGRAMS and len(accounts) >= 3:
                    opcode = raw[0] if raw else -1
                    if opcode == 3 and len(raw) >= 9:
                        source, destination = accounts[0], accounts[1]
                        amount = struct.unpack("<Q", raw[1:9])[0]
                    elif opcode == 12 and len(raw) >= 10 and len(accounts) >= 4:
                        source, destination = accounts[0], accounts[2]
                        amount = struct.unpack("<Q", raw[1:9])[0]
                    else:
                        return

                    transfers.append({
                        "from": owners.get(source, keys[source]),
                        "to": owners.get(destination, keys[destination]),
                        "amount": amount
                    })
            except (IndexError, KeyError, ValueError, struct.error):
                return

        for ix in message.get("instructions", []):
            process(ix)

        for group in meta.get("innerInstructions", []):
            for ix in group.get("instructions", []):
                process(ix)

    return transfers

all_transfers = []
for number in range(151, 157):
    block_transfers = extract_block(number)
    print(f"Block 385870{number}: {len(block_transfers)} transfers")
    all_transfers.extend(block_transfers)

with open("transfers.jsonl", "w") as output:
    for transfer in all_transfers:
        output.write(json.dumps(transfer) + "\n")

print(f"\nTotal transfers extracted: {len(all_transfers)}")
print("Output saved to transfers.jsonl")
