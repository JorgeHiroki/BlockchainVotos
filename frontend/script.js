document.getElementById('voteForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const voterId = document.getElementById('voterId').value;
    const candidateNumber = document.getElementById('candidateNumber').value;

    try {
        const response = await fetch('http://localhost:5000/vote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                voter_id: voterId,
                candidate_number: candidateNumber,
            }),
        });

        const data = await response.json();
        document.getElementById('message').textContent = data.message || "Voto registrado com sucesso!";
    } catch (error) {
        document.getElementById('message').textContent = "Erro ao enviar voto. Tente novamente.";
    }
});

if (window.location.pathname.includes("index.html")) {
    document.getElementById("voterId").addEventListener("input", () => {
        document.getElementById("message").textContent = "";
    });

    document.getElementById("candidateNumber").addEventListener("input", () => {
        document.getElementById("message").textContent = "";
    });
}
