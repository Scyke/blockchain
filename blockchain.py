import hashlib
import json
from time import time
from uuid import uuid4

class Blockchain (object):
    def __init__(self):
        self.chain = [];
        self.current_transactions = [];
        
        #creating new genesis (first) block
    
        self.new_block(previous_hash=1, proof=100); #every time blockchain is called, it creates a genesis
    
    def new_block(self, proof, previous_hash=None): #will create a new Block and add to chain
        #could add error that enforces minimum one transaction per block
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            
        }
        
        self.current_transactions = [] #has to wipe all pending transactions
        
        self.chain.append(block); #adds itself to the blockchain
        
        return block;
    
    def new_transaction(self, sender, recipient, amount): #specifies a new transaction
        
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
                
        return self.last_block['index'] + 1;
    
    def proof_of_work(self,last_proof):
        #find p such that hash(p * p_past) contains 4 leading zeros, p is current proof
        
        proof = 0;
        
        while self.valid_proof(last_proof, proof) is False:
            proof += 1;
            
        return proof
    
    @staticmethod
    def valid_proof(last_proof, proof):
        #validates the proof does hash(p * p_past) have 4 leading zeros
        
        guess = f'{last_proof}{proof}'.encode()
        hashed_guess = hashlib.sha256(guess).hexdigest();
        return hashed_guess[:4] == "0000"
    
    @staticmethod
    def hash(block):
        
        block_string = json.dumps(block, sort_keys=True).encode() #converts the block info to a JSON string, and then bytes
        return hashlib.sha256(block_string).hexdigest() #hashes using sha256 and formats it in hexadecimal
        
    
    @property
    def last_block(self):
        pass