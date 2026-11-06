#!/usr/bin/env bash
set -euo pipefail
PACKAGE="${1:-./solana-transfer-extractor-v0.1.0.spkg}"
substreams run "$PACKAGE" map_transfers \
  -e mainnet.sol.streamingfast.io:443 \
  --start-block 385870151 \
  --stop-block 385870157
