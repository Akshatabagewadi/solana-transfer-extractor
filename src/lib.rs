mod pb {
    include!(concat!(env!("OUT_DIR"), "/solana.transfers.v1.rs"));
}

mod solana_pb {
    include!(concat!(env!("OUT_DIR"), "/sf.solana.r#type.v1.rs"));
}

use pb::{Transfer, Transfers};
use solana_pb::{Block, CompiledInstruction};
use std::collections::HashMap;

const SYSTEM_PROGRAM: &str = "11111111111111111111111111111111";
const SPL_TOKEN_PROGRAM: &str = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA";
const SPL_TOKEN_2022_PROGRAM: &str = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb";

#[substreams::handlers::map]
fn map_transfers(block: Block) -> Result<Transfers, substreams::errors::Error> {
    let mut output = Transfers {
        transfers: Vec::new(),
    };

    for confirmed in &block.transactions {
        let tx = match confirmed.transaction.as_ref() {
            Some(value) => value,
            None => continue,
        };

        let message = match tx.message.as_ref() {
            Some(value) => value,
            None => continue,
        };

        let meta = match confirmed.meta.as_ref() {
            Some(value) => value,
            None => continue,
        };

        if meta.err.is_some() {
            continue;
        }

        let mut account_keys = message.account_keys.clone();
        account_keys.extend(meta.loaded_writable_addresses.iter().cloned());
        account_keys.extend(meta.loaded_readonly_addresses.iter().cloned());

        let mut token_owners = HashMap::new();

        for balance in meta
            .pre_token_balances
            .iter()
            .chain(meta.post_token_balances.iter())
        {
            if !balance.owner.is_empty() {
                token_owners.insert(balance.account_index as usize, balance.owner.clone());
            }
        }

        for instruction in &message.instructions {
            extract_instruction(
                instruction,
                &account_keys,
                &token_owners,
                &mut output,
            );
        }

        for group in &meta.inner_instructions {
            for instruction in &group.instructions {
                extract_instruction(
                    instruction,
                    &account_keys,
                    &token_owners,
                    &mut output,
                );
            }
        }
    }

    Ok(output)
}

fn extract_instruction(
    instruction: &CompiledInstruction,
    account_keys: &[Vec<u8>],
    token_owners: &HashMap<usize, String>,
    output: &mut Transfers,
) {
    let program_id = match account_keys.get(instruction.program_id_index as usize) {
        Some(bytes) => bs58::encode(bytes).into_string(),
        None => return,
    };

    let indexes = &instruction.accounts;
    let data = &instruction.data;

    if program_id == SYSTEM_PROGRAM && data.len() >= 12 {
        let discriminator = u32::from_le_bytes(data[0..4].try_into().unwrap());

        if discriminator == 2 && indexes.len() >= 2 {
            let amount = u64::from_le_bytes(data[4..12].try_into().unwrap());

            if let (Some(from), Some(to)) = (
                key_string(account_keys, indexes[0]),
                key_string(account_keys, indexes[1]),
            ) {
                output.transfers.push(Transfer { from, to, amount });
            }
        }

        return;
    }

    if program_id == SPL_TOKEN_PROGRAM || program_id == SPL_TOKEN_2022_PROGRAM {
        if data.len() < 9 {
            return;
        }

        let amount = u64::from_le_bytes(data[1..9].try_into().unwrap());

        let (source_pos, destination_pos) = match data[0] {
            3 if indexes.len() >= 3 => (0, 1),
            12 if indexes.len() >= 4 => (0, 2),
            _ => return,
        };

        let source_index = indexes[source_pos] as usize;
        let destination_index = indexes[destination_pos] as usize;

        let from = token_owners
            .get(&source_index)
            .cloned()
            .or_else(|| key_string(account_keys, indexes[source_pos]));

        let to = token_owners
            .get(&destination_index)
            .cloned()
            .or_else(|| key_string(account_keys, indexes[destination_pos]));

        if let (Some(from), Some(to)) = (from, to) {
            output.transfers.push(Transfer { from, to, amount });
        }
    }
}

fn key_string(account_keys: &[Vec<u8>], index: u8) -> Option<String> {
    account_keys
        .get(index as usize)
        .map(|bytes| bs58::encode(bytes).into_string())
}