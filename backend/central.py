import hashlib
import json
import os
from time import time
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Dados pré-cadastrados
VOTERS = {"voter1", "voter2", "voter3", "voter4", "voter5", "voter6", "voter7", "voter8", "voter9", "voter10"}
CANDIDATES = {"111", "222", "333"}
# Dicionário para mapear números de candidatos aos seus nomes
CANDIDATE_NAMES = {
    "111": "Candidato A",
    "222": "Candidato B",
    "333": "Candidato C"
}
# Dicionário para controle se um votante já votou
voted = {}

# Lista de peers cadastrados (endereços na forma "http://ip:porta")
peers = []  # Inicialmente vazia; peers poderão ser adicionados via endpoint
if os.getenv("AUTO_REGISTER_PEERS", "false").lower() == "true":
    peers.append("http://peer1:5001")
    peers.append("http://peer2:5002")
    print("Peers registrados automaticamente:", peers)

# Classe que representa um bloco
class Block:
    def __init__(self, index, timestamp, voter_id, candidate_number, previous_hash, hash=None):
        self.index = index
        self.timestamp = timestamp
        self.voter_id = voter_id
        self.candidate_number = candidate_number
        self.previous_hash = previous_hash
        self.hash = hash if hash else self.compute_hash()

    def compute_hash(self):
        # Cria um dicionário sem o campo "hash" para evitar recursividade
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

# Classe da Blockchain
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

    def add_block(self, voter_id, candidate_number):
        last_block = self.get_last_block()
        new_block = Block(
            index=last_block.index + 1,
            timestamp=time(),
            voter_id=voter_id,
            candidate_number=candidate_number,
            previous_hash=last_block.hash
        )
        self.chain.append(new_block)
        return new_block

    def validate_chain(self):
        """
        Valida toda a blockchain localmente.
        Retorna uma tupla (booleano, mensagem).
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            # Verifica se o índice está correto
            if current.index != previous.index + 1:
                return False, f"Índice incorreto no bloco {current.index}"
            # Verifica se o previous_hash bate
            if current.previous_hash != previous.hash:
                return False, f"Previous_hash incorreto no bloco {current.index}"
            # Recalcula o hash do bloco e compara com o hash armazenado
            recalculated_hash = Block(
                current.index, current.timestamp, current.voter_id, current.candidate_number, current.previous_hash
            ).compute_hash()
            if recalculated_hash != current.hash:
                return False, f"Hash inválido no bloco {current.index}"
        return True, "Blockchain valida"

# Instância da blockchain do servidor central
blockchain = Blockchain()

# Endpoint para registrar um novo peer
@app.route('/register_peer', methods=['POST'])
def register_peer():
    """
    Registra um novo peer na rede.
    Espera um JSON com:
      - peer_url: URL do peer (ex: "http://192.168.1.5:5001")
    """
    data = request.get_json()
    peer_url = data.get("peer_url")
    if not peer_url:
        return jsonify({"message": "peer_url é obrigatório."}), 400

    if peer_url in peers:
        return jsonify({"message": "Peer já registrado."}), 400

    peers.append(peer_url)
    return jsonify({"message": "Peer registrado com sucesso.", "peers": peers}), 201

@app.route('/register_voter', methods=['POST'])
def register_voter():
    data = request.get_json()
    voter_id = data.get("voter_id")

    if not voter_id:
        return jsonify({"error": "Voter ID is required"}), 400

    if voter_id in VOTERS:
        return jsonify({"error": "Voter already registered"}), 400

    VOTERS.add(voter_id)
    return jsonify({"message": "Voter registered successfully"}), 201

@app.route('/register_candidate', methods=['POST'])
def register_candidate():
    data = request.get_json()
    candidate_number = data.get("candidate_number")
    candidate_name = data.get("candidate_name")

    if not candidate_name:
        return jsonify({"error": "Candidate name ir required"}), 400

    if not candidate_number:
        return jsonify({"error": "Candidate number is required"}), 400

    if candidate_number in CANDIDATES:
        return jsonify({"error": "Candidate already registered"}), 400
    
    CANDIDATES.add(candidate_number)
    CANDIDATE_NAMES[candidate_number] = candidate_name

    return jsonify({"message": "Candidate registered successfully"}), 201


# Endpoint para receber votos
@app.route('/vote', methods=['POST'])
def receive_vote():
    """
    Recebe um voto via POST.
    JSON deve conter:
      - voter_id: ID do votante
      - candidate_number: número do candidato
    """
    data = request.get_json()
    voter_id = data.get("voter_id")
    candidate_number = data.get("candidate_number")

    # Verifica se há pelo menos 2 peers cadastrados
    if len(peers) < 2:
        return jsonify({"message": "Rede com número insuficiente de peers para processar o voto."}), 400

    # Validação do votante e candidato
    if voter_id not in VOTERS:
        return jsonify({"message": "Votante não cadastrado."}), 400

    if candidate_number not in CANDIDATES:
        return jsonify({"message": "Candidato não cadastrado."}), 400

    if voter_id in voted:
        return jsonify({"message": "Este votante já registrou seu voto."}), 400

    # Adiciona o voto à blockchain
    new_block = blockchain.add_block(voter_id, candidate_number)
    voted[voter_id] = True

    # Distribuição do novo bloco para todos os peers
    block_data = new_block.to_dict()
    distribution_results = []

    for peer in peers:
        url = f"{peer}/new_block"
        try:
            response = requests.post(url, json=block_data, timeout=5)
            distribution_results.append({
                "peer": peer,
                "status": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text
            })
        except requests.exceptions.RequestException as e:
            distribution_results.append({
                "peer": peer,
                "status": "failed",
                "error": str(e)
            })

    return jsonify({
        "message": "Voto registrado.",
        "block": block_data,
        "distribution": distribution_results
    }), 201


# Endpoint para consultar a blockchain do servidor central
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = [block.to_dict() for block in blockchain.chain]
    return jsonify(chain_data), 200

# Endpoint para validar a blockchain
@app.route('/validate', methods=['GET'])
def validate_blockchain():
    """
    Valida a blockchain local e dispara a validação nos peers.
    Retorna os resultados locais e de cada peer.
    """
    results = {}
    # Validação local
    is_valid, message = blockchain.validate_chain()
    results["central"] = {"valid": is_valid, "message": message}

    # Dispara a validação em cada peer
    for peer in peers:
        try:
            url = f"{peer}/validate"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                results[peer] = response.json()
            else:
                results[peer] = {"valid": False, "message": f"Erro: status {response.status_code}"}
        except Exception as e:
            results[peer] = {"valid": False, "message": f"Erro ao conectar: {str(e)}"}

    return jsonify(results), 200

@app.route('/results', methods=['GET'])
def get_election_results():
    results = {candidate: 0 for candidate in CANDIDATES}

    for block in blockchain.chain[1:]:
        candidate_number = block.candidate_number
        if candidate_number in results:
            results[candidate_number] += 1

    # Adiciona os nomes dos candidatos ao resultado
    detailed_results = {
        candidate: {
            "name": CANDIDATE_NAMES.get(candidate, "Desconhecido"),
            "votes": votes
        }
        for candidate, votes in results.items()
    }

    return jsonify(detailed_results), 200

if __name__ == '__main__':
    # O servidor central roda na porta 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
