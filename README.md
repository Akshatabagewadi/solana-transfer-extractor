# Solana Transfer Extractor

A blockchain data extraction project that identifies native SOL and SPL Token transfer instructions from Solana mainnet blocks using Rust, Substreams, and Python.

## Overview

The Solana Transfer Extractor processes Solana blockchain transactions and extracts transfer information into structured JSON records.

The project focuses on extracting transfer details, including sender address, recipient address, and transfer amount.

## Tech Stack

- **Rust** – Substreams module development
- **Substreams** – Blockchain data processing framework
- **Python** – Solana RPC data extraction and JSON processing
- **Protocol Buffers** – Structured data definitions
- **Solana JSON-RPC** – Blockchain data retrieval
- **JSON** – Output format

## Features

- Extracts native SOL transfer instructions.
- Supports SPL Token and Token-2022 transfer instructions.
- Processes top-level and inner transaction instructions.
- Skips failed transactions.
- Supports versioned transactions and loaded addresses in the RPC extraction script.
- Generates structured JSON Lines output.
- Validates extracted records.

## Project Scope

The implementation retrieves data from the following Solana mainnet blocks:

| Block Number | Transfers Extracted |
|---|---:|
| 385870151 | 542 |
| 385870152 | 581 |
| 385870153 | 961 |
| 385870154 | 596 |
| 385870155 | 474 |
| 385870156 | 820 |
| **Total** | **3,974** |

## Output Format

Each transfer is represented as a JSON object containing exactly three fields:

```json
{
  "from": "sender_wallet_address",
  "to": "recipient_wallet_address",
  "amount": 123456
}
```

The output is stored in `transfers.jsonl`, with one JSON object per line.

Amounts are represented as raw integer units (lamports for SOL and base units for SPL tokens).

## Project Structure

```text
solana-transfer-extractor/
│
├── proto/
│   ├── solana.proto
│   └── transfers.proto
│
├── scripts/
│   ├── extract_rpc_transfers.py
│   └── format_output.py
│
├── src/
│   ├── lib.rs
│   └── pb/
│
├── Cargo.toml
├── Cargo.lock
├── build.rs
├── substreams.yaml
├── solana-transfer-extractor-v0.1.0.spkg
├── transfers.jsonl
└── README.md
```

## Prerequisites

- Rust stable toolchain
- Python 3
- Substreams CLI
- Protocol Buffers / Buf CLI

## Run the RPC Extraction Script

Download the six required Solana block JSON files using the Solana mainnet RPC endpoint, placing them in the project root with these filenames:

```text
block-385870151.json
block-385870152.json
block-385870153.json
block-385870154.json
block-385870155.json
block-385870156.json
```

Run:

```bash
python3 scripts/extract_rpc_transfers.py
```

The script generates:

```text
transfers.jsonl
```

## Build the Substreams Package

Build the Rust WebAssembly package using:

```bash
cargo build --release --target wasm32-unknown-unknown
```

Then package it using:

```bash
substreams build
```

The generated package is:

```text
solana-transfer-extractor-v0.1.0.spkg
```

Executing the package against a Substreams provider requires valid provider authentication.

## Validation

Validate the JSON output:

```bash
python3 -m json.tool transfers.jsonl
```

For JSON Lines validation, parse each line individually and verify the required fields.

## Implementation Notes and Limitations

- The Rust Substreams package was successfully built.
- The 3,974 transfer records were generated using the Python-based Solana RPC extraction script.
- An authenticated Substreams provider was not available during testing, so the package was not independently executed against the requested block range.
- SPL token amounts are raw base units, not decimal-adjusted values.
- The extraction script handles standard System Program transfers and SPL Token `Transfer` and `TransferChecked` instructions. Other transfer instruction variants may not be covered.

## Learning Outcomes

- Understanding Solana blockchain transaction structures.
- Working with Rust and Substreams.
- Retrieving blockchain data using JSON-RPC.
- Processing native SOL and SPL Token instructions.
- Handling transaction instructions and inner instructions.
- Generating and validating structured JSON data.

## Author

**Akshata Bagewadi**

GitHub: [Akshatabagewadi](https://github.com/Akshatabagewadi)
