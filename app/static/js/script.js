let startTime;
let timerInterval;

function transcribeVideo() {
    const url = document.getElementById('youtube-url').value;
    const resultDiv = document.getElementById('result');
    const statusDiv = document.getElementById('status');
    const elapsedTimeDiv = document.getElementById('elapsed-time');

    statusDiv.innerHTML = 'Iniciando transcripción...';
    resultDiv.innerHTML = '';
    elapsedTimeDiv.innerHTML = '';

    startTime = new Date();
    updateElapsedTime();
    timerInterval = setInterval(updateElapsedTime, 1000);

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
        clearInterval(timerInterval);
        if (data.status === 'success') {
            const endTime = new Date();
            const totalTime = (endTime - startTime) / 1000; // in seconds
            statusDiv.innerHTML = 'Transcripción completada.';
            elapsedTimeDiv.innerHTML = `Tiempo total: ${formatTime(totalTime)}`;
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
        clearInterval(timerInterval);
        console.error('Error:', error);
        statusDiv.innerHTML = 'Error en la transcripción.';
        elapsedTimeDiv.innerHTML = '';
        resultDiv.innerHTML = `<p>Ocurrió un error durante la transcripción: ${error.message}</p>`;
    });
}

function updateElapsedTime() {
    const currentTime = new Date();
    const elapsedSeconds = (currentTime - startTime) / 1000;
    document.getElementById('elapsed-time').innerHTML = `Tiempo transcurrido: ${formatTime(elapsedSeconds)}`;
}

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${padZero(hours)}:${padZero(minutes)}:${padZero(remainingSeconds)}`;
}

function padZero(num) {
    return num.toString().padStart(2, '0');
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