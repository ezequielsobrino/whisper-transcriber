function transcribeVideo() {
    const url = document.getElementById('youtube-url').value;
    const resultDiv = document.getElementById('result');
    const statusDiv = document.getElementById('status');

    statusDiv.innerHTML = 'Iniciando transcripción...';
    resultDiv.innerHTML = '';

    fetch('/transcription/transcribe', {
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
            resultDiv.innerHTML = `
                <h2>Transcripción:</h2>
                <pre>${data.transcription}</pre>
                <p><strong>Archivo guardado como:</strong><br>${data.file}</p>
            `;
        } else {
            throw new Error(data.error || data.message || 'Error desconocido en la transcripción');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        statusDiv.innerHTML = 'Error en la transcripción.';
        resultDiv.innerHTML = `<p>Ocurrió un error durante la transcripción: ${error.message}</p>`;
    });
}

function showTranscription(filename) {
    fetch(`/transcription/content/${filename}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.content) {
                document.getElementById('transcription-content').innerHTML = `
                    <h2>Transcripción: ${filename}</h2>
                    <pre>${data.content}</pre>
                    <p><strong>Archivo:</strong><br>${filename}</p>
                `;
            } else {
                throw new Error('No content received from server');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('transcription-content').innerHTML = `<p>Error al cargar la transcripción: ${error.message}</p>`;
        });
}