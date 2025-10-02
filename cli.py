import argparse, json, os, sys, struct, hashlib
from uuid import uuid4
from pathlib import Path

from blockchain import Blockchain

STATE_FILE = Path(".chain_state.json"); #create path inside blockchain folder to create chain_state,json

def load_state():
    if STATE_FILE.exists(): #if it exists load previous data
        with STATE_FILE.open("r") as f:
            data = json.load(f);
        return data["node_id"], data["chain"];
    # run for first time
    node_id = str(uuid4()).replace('-', " ");
    return node_id, None

def save_state(node_id, chain):
    with STATE_FILE.open('w') as f:
        json.dump({'node_id': node_id, "chain": chain}, f)
        
def verify_pow(last_proof: int, proof: int, zeros: int) -> bool:
    guess = f'{last_proof}{proof}'.encode()
    #will have to update to change to binary for FPGA mining
    digest = hashlib.sha256(guess).hexdigest();
    return digest.startswith("0" * zeros);

def proof_of_work_offload(last_proof: int, zeros: int = 4, port: str = None, start_nonce: int = 0, batch_size: int = 500_000) -> int:
    #Should have UART protocol, want to test with CPU mining for now
    proof = 0;
    
    while True:
        if verify_pow(last_proof, proof, zeros):
            return proof
        proof += 1;
    