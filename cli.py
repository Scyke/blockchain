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
        json.dump({'node_id': node_id, "chain": chain}, f, indent=2)
        
def verify_pow(last_proof: int, proof: int, zeros: int) -> bool:
    guess = f'{last_proof}{proof}'.encode()
    #will have to update to change to binary for FPGA mining
    digest = hashlib.sha256(guess).hexdigest();
    return digest.startswith("0" * zeros);

def proof_of_work_offload(last_proof: int, zeros: int = 4, port: str = None, start_nonce: int = 0, batch_size: int = 500_000) -> int:
    #Should have UART protocol, want to test with CPU mining for now
    proof = start_nonce;
    
    while True:
        if verify_pow(last_proof, proof, zeros):
            return proof
        proof += 1;
        
def cmd_mine(args):
    node_id, persisted_chain = load_state();
    blk = Blockchain()
    if persisted_chain:
        blk.chain = persisted_chain; #load previous chain
        
    last_block = blk.last_block;
    last_proof = blk.last_block["proof"];
    
    if args.use_uart: #if im using UART, else use CPU mining
        proof = proof_of_work_offload(last_proof, zeros=args.zeros, port=args.port, start_nonce=args.start_nonce, batch_size=args.batch)
    else:
        proof = blk.proof_of_work(last_proof);
        
    blk.new_transaction(sender='0', recipient=node_id, amount=1); #one proof is cracked, prepare a reward
    
    previous_hash = blk.hash(last_block);
    
    block = blk.new_block(proof, previous_hash=previous_hash);
    
    save_state(node_id, blk.chain);
    
    out = {
        "message": 'New Block mined',
        "index": block['index'],
        "transactions": block['transactions'],
        'proof': block['proof'],
        "previous_hash": block["previous_hash"],
    }
    print(json.dumps(out, indent=2))
    
def cmd_tx(args):
    node_id, persisted_chain = load_state();
    
    blk = Blockchain()
    
    if persisted_chain:
        blk.chain = persisted_chain;
        
    #validating inputs
    for k in ('sender', 'recipient', 'amount'):
        if getattr(args, k) is None:
            print(f"Missing --{k}", file=sys.stderr)
            sys.exit(1);
    index = blk.new_transaction(args.sender, args.recipient, args.amount)
    save_state(node_id, blk.chain)
    print(json.dumps({"message": f'Transaction will be added to Block {index}'}))
    
    
    
    