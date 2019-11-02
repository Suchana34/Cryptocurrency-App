
#creating  a blockchain
import datetime
import hashlib
import json
#get json function from the request module
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

#building our blockchain
class Blockchain():
    def __init__(self):
        self.chain = []
        # list of transactions added before it gets mined and added to blockchain..jst to store the requests 
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()
        
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain)+1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
    
        return new_proof
    # we r going to hash a block using sha256
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            # now to check if the prev hash of this block is equal to the hash of the prev block
            if block['previous_hash']  != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
    # now we will check proof of the prev and the currrent block starts with 4 leading zeroes
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
    # thus now we have a hashing algorithm vteween the proofs
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender' :sender , 'receiver':receiver, 'amount' :amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] +1 
    
    def add_node(self, address):
        #it adds the created node with this address to the existing nodes
        #first lets parse the address of the node
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        #it replaces the other shorter chains with the longest one
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for nodes in network:
            #we want to find the chain with the longest length
            response = requests.get(f'http://{node}/getchain')
            
            if response.status_code == 200:
                length = response.json()['length']
                #taking the length key of the dict which will get us the length of the chain
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
                if longest_chain:
                    self.chain = longest_chain
                    return True
                else:
                    return False
                
                
                
# creating webapp
app = Flask(__name__)
#creating a blockchain

#creating an address for the node on port 5000
node_address = str(uuid4()).replace('-','')
#our first node address..this will be our address on port 5000

blockchain = Blockchain() #instance of our class


# mining our blockchain
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address,receiver = 'xyz' ,amount = 1)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message' : 'congrats..you just mined a blockchain',
                'index' : block['index'],
                'timestamp': block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash'],
                'transactions': block['transactions']}
    
    return jsonify(response), 200

#getting the full blockchain
@app.route('/get_fullchain', methods = ['GET'])
def get_fullchain():
    response ={'chain' : blockchain.chain,
               'length' : len(blockchain.chain)}
    return jsonify(response), 200 

#adding a new transaction to the blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver','amount']
    if not all (key in json for key in transaction_keys):
        return 'some elements of the transaction are missing', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'] , json['amount'])
    response = {'message':f'this transaction will be added to the block {index}'}
    return jsonify(response), 201
 
#decentralising our blockchain
#connecting new nodes

@app.route('/connect_node',methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get['nodes']
    if nodes is None:
        return 'no node',400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message':'all the nodes are now connected, the suchana blockchain now displays the following nodes',
                'total_nodes':list(blockchain.nodes)}
    return jsonify(response), 201

#replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message':'The nodes had different chains so the chain is replaced by the longest one',
                    'new_chain': blockchain.chain}
    else:
        response = {'message':'all good. the chain was the longest one',
                    'actual_chain':blockchain.chain}
    return jsonify(response), 200
        
    


#running the app
app.run(host = '0.0.0.0' , port = 5003)











