function transcribeVideo() {
    const url = document.getElementById('youtube-url').value;
    const resultDiv = document.getElementById('result');
    const statusDiv = document.getElementById('status');

    statusDiv.innerHTML = 'Iniciando transcripción...';
    resultDiv.innerHTML = '';

    fetch('/transcribe', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({url: url}),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            statusDiv.innerHTML = 'Transcripción completada.';
            resultDiv.innerHTML = `<h2>Transcripción:</h2><p>${data.transcription}</p>`;
        } else {
            statusDiv.innerHTML = 'Error en la transcripción.';
            resultDiv.innerHTML = `<p>Error: ${data.error || data.message}</p>`;
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        statusDiv.innerHTML = 'Error en la transcripción.';
        resultDiv.innerHTML = `<p>Ocurrió un error durante la transcripción: ${error.message}</p>`;
    });
}