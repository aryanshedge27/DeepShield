"""
Blockchain layer — two modes:
  1. LOCAL  (default): stores hashes in a local JSON ledger (great for dev)
  2. ETHEREUM: registers on-chain via Web3 + your deployed contract
Set BLOCKCHAIN_MODE=ethereum in .env to enable on-chain mode.
"""

import json, os, time, hashlib
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MODE           = os.getenv("BLOCKCHAIN_MODE", "local")
LEDGER_FILE    = Path("ledger.json")
ETH_RPC        = os.getenv("ETH_RPC_URL", "")          # e.g. Infura/Alchemy URL
CONTRACT_ADDR  = os.getenv("CONTRACT_ADDRESS", "")
PRIVATE_KEY    = os.getenv("PRIVATE_KEY", "")


# ── Local ledger (JSON file) ─────────────────────────────────────────────────
def _load_ledger() -> dict:
    if LEDGER_FILE.exists():
        return json.loads(LEDGER_FILE.read_text())
    return {}


def _save_ledger(data: dict):
    LEDGER_FILE.write_text(json.dumps(data, indent=2))


def local_register(sha256: str, metadata: dict) -> dict:
    ledger = _load_ledger()
    if sha256 in ledger:
        return {"status": "already_registered", "record": ledger[sha256]}
    record = {
        "sha256":     sha256,
        "timestamp":  int(time.time()),
        "metadata":   metadata,
        "block":      f"LOCAL-{len(ledger)+1:05d}",
    }
    ledger[sha256] = record
    _save_ledger(ledger)
    return {"status": "registered", "record": record}


def local_verify(sha256: str) -> dict:
    ledger = _load_ledger()
    if sha256 in ledger:
        return {"found": True, "record": ledger[sha256]}
    return {"found": False}


# ── Ethereum (on-chain) ──────────────────────────────────────────────────────
ABI = [
    {
        "inputs": [{"internalType": "bytes32", "name": "hash", "type": "bytes32"},
                   {"internalType": "string",  "name": "meta", "type": "string"}],
        "name":    "register",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type":    "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "hash", "type": "bytes32"}],
        "name":    "verify",
        "outputs": [
            {"internalType": "bool",    "name": "exists",    "type": "bool"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "address", "name": "registrar", "type": "address"},
            {"internalType": "string",  "name": "meta",      "type": "string"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]


def _get_contract():
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider(ETH_RPC))
    if not w3.is_connected():
        raise RuntimeError("Cannot connect to Ethereum node")
    return w3, w3.eth.contract(address=CONTRACT_ADDR, abi=ABI)


def eth_register(sha256_hex: str, metadata: dict) -> dict:
    w3, contract = _get_contract()
    h32   = bytes.fromhex(sha256_hex)
    meta  = json.dumps(metadata)
    acct  = w3.eth.account.from_key(PRIVATE_KEY)
    nonce = w3.eth.get_transaction_count(acct.address)
    tx    = contract.functions.register(h32, meta).build_transaction({
        "from":     acct.address,
        "nonce":    nonce,
        "gas":      200_000,
        "gasPrice": w3.eth.gas_price,
    })
    signed   = acct.sign_transaction(tx)
    tx_hash  = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt  = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    return {
        "status":   "registered",
        "tx_hash":  tx_hash.hex(),
        "block":    receipt.blockNumber,
    }


def eth_verify(sha256_hex: str) -> dict:
    w3, contract = _get_contract()
    h32  = bytes.fromhex(sha256_hex)
    exists, ts, registrar, meta = contract.functions.verify(h32).call()
    return {
        "found":      exists,
        "timestamp":  ts,
        "registrar":  registrar,
        "metadata":   json.loads(meta) if meta else {},
    }


# ── Public API ────────────────────────────────────────────────────────────────
def register_hash(sha256: str, metadata: dict) -> dict:
    if MODE == "ethereum":
        return eth_register(sha256, metadata)
    return local_register(sha256, metadata)


def verify_hash(sha256: str) -> dict:
    if MODE == "ethereum":
        return eth_verify(sha256)
    return local_verify(sha256)