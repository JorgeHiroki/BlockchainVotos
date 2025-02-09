import hashlib
import json
import os
from time import time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Classe que representa um bloco
class Block:
    def __init__(self, index, timestamp, voter_id, candidate_number, previous_hash, hash=None):
        self.index = index
        self.timestamp = timestamp
        self.voter_id = voter_id
        self.candidate_number = candidate_number
        self.previous_hash = previous_hash
        self.hash = hash

    def compute_hash(self):
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "voter_id": self.voter_id,
            "candidate_number": self.candidate_number,
            "previous_hash": self.previous_hash
        }
        block_string = json.dumps(block_data, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "voter_id": self.voter_id,
            "candidate_number": self.candidate_number,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

# Classe da Blockchain local do peer
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        GENESIS_BLOCK = Block(
            index=0,
            timestamp=0,
            voter_id="0",
            candidate_number="0",
            previous_hash="0",
            hash="GENESIS_HASH"
        )

        self.chain.append(GENESIS_BLOCK)

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, block_data):
        """
        Recebe dados de um novo bloco (dict), valida e adiciona à cadeia.
        Retorna True se o bloco for adicionado; caso contrário, False.
        """
        last_block = self.get_last_block()
        if block_data["index"] != last_block.index + 1:
            return False

        if block_data["previous_hash"] != last_block.hash:
            return False

        new_block = Block(
            index=block_data["index"],
            timestamp=block_data["timestamp"],
            voter_id=block_data["voter_id"],
            candidate_number=block_data["candidate_number"],
            previous_hash=block_data["previous_hash"],
            hash=block_data["hash"]
        )

        if new_block.hash != block_data["hash"]:
            return False

        self.chain.append(new_block)
        return True

    def validate_chain(self):
        """
        Valida a blockchain localmente.
        Retorna uma tupla (booleano, mensagem).
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.index != previous.index + 1:
                return False, f"Índice incorreto no bloco {current.index}"
            if current.previous_hash != previous.hash:
                return False, f"Previous_hash incorreto no bloco {current.index}"
            recalculated_hash = Block(
                current.index, current.timestamp, current.voter_id, current.candidate_number, current.previous_hash
            ).compute_hash()
            if recalculated_hash != current.hash:
                return False, f"Hash inválido no bloco {current.index}"
        return True, "Blockchain válida"

# Instância da blockchain do peer
blockchain = Blockchain()

# Endpoint para receber um novo bloco
@app.route('/new_block', methods=['POST'])
def new_block():
    try:
        block_data = request.get_json()
        print(f"Recebendo bloco: {block_data}")

        if not block_data:
            return jsonify({"message": "Erro: JSON inválido ou ausente."}), 400
        
        if blockchain.add_block(block_data):
            return jsonify({"message": "Bloco adicionado com sucesso."}), 201
        else:
            return jsonify({"message": "Bloco inválido ou rejeitado."}), 400

    except Exception as e:
        return jsonify({"message": f"Erro inesperado: {str(e)}"}), 500

# Endpoint para consultar a blockchain local
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = [block.to_dict() for block in blockchain.chain]
    return jsonify(chain_data), 200

# Endpoint para validar a blockchain local
@app.route('/validate', methods=['GET'])
def validate_blockchain():
    is_valid, message = blockchain.validate_chain()
    return jsonify({"valid": is_valid, "message": message}), 200

@app.route("/")
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        methods = ",".join(rule.methods)
        line = urllib.parse.unquote(f"{rule.endpoint}: {rule.rule} [{methods}]")
        output.append(line)
    return "<br>".join(output)

if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT)