# Solana Transfer Extractor (Substreams)

A Rust Substreams map module intended to extract executed native SOL and SPL
Token / Token-2022 transfer instructions from Solana mainnet blocks
**385870151 through 385870156**.

## Important interpretation notes

- `SystemProgram::Transfer` is emitted as `asset = "SOL"` and `amount` is in
  lamports (the raw on-chain integer).
- SPL `Transfer` and `TransferChecked` are emitted as `asset = "SPL"` and
  `amount` is the raw token base-unit integer (not decimal-adjusted).
- The SPL wallet address is taken from token-balance `owner` metadata when
  available. If unavailable, the token-account address is used as a fallback.
- Failed transactions are excluded.
- Both top-level and inner/CPI instructions are inspected.
- This first implementation intentionally focuses on the canonical System
  Program transfer opcode and SPL Token transfer opcodes. It does not yet decode
  System Program `TransferWithSeed`, token multisig semantics, or non-standard
  token programs. Review these limitations against the employer's expected
  definition of "transfer".

## Requirements

- Rust toolchain (the project pins Rust 1.75.0)
- `wasm32-unknown-unknown` target
- Substreams CLI
- Substreams provider credentials (run `substreams auth`)

## Build

```bash
rustup target add wasm32-unknown-unknown
substreams build
substreams pack ./substreams.yaml
```

The build script uses `protoc-bin-vendored` to compile `proto/transfers.proto`
into Rust code during Cargo build.

## Run the requested slots

Substreams stop blocks are exclusive. To include slots 385870151 through
385870156, use stop block 385870157:

```bash
substreams run ./solana-transfer-extractor-v0.1.0.spkg map_transfers \
  -e mainnet.sol.streamingfast.io:443 \
  --start-block 385870151 \
  --stop-block 385870157
```

The exact generated SPKG filename may differ; use the filename printed by
`substreams pack`.

## JSON output

Substreams protobuf JSON represents 64-bit integers as strings in standard
protobuf JSON mapping. The assignment asks for JSON numbers. Save the module
output as JSON and normalize it with:

```bash
python3 scripts/format_output.py < substreams-output.json > transfers.jsonl
```

Each line of `transfers.jsonl` will have the requested shape:

```json
{"from":"...","to":"...","amount":123}
```

## Verification checklist

- [ ] `substreams build` succeeds
- [ ] `substreams pack` creates an SPKG
- [ ] `substreams run` completes slots 385870151–385870156
- [ ] Inspect all transfer records and check sender/recipient ownership
- [ ] Keep the SPKG, source code, and `transfers.jsonl` together for submission

## References

- Solana Substreams quickstart: https://github.com/streamingfast/substreams-solana-quickstart
- Substreams Solana crate: https://docs.rs/substreams-solana
- Solana Substreams docs: https://docs.substreams.dev/how-to-guides/develop-your-own-substreams/solana/explore-solana
