let startTime;
let timerInterval;
let currentTaskId;

console.log("Script de transcripción cargado");

function transcribeVideo(event) {
    event.preventDefault();
    console.log("Función transcribeVideo llamada");
    
    const url = document.getElementById('youtube-url').value;
    const modelType = document.getElementById('model-type').value;
    const englishOnly = document.getElementById('english-only').checked;
    const statusDiv = document.getElementById('status');
    const elapsedTimeDiv = document.getElementById('elapsed-time');

    console.log(`URL: ${url}, Model: ${modelType}, English Only: ${englishOnly}`);

    statusDiv.innerHTML = 'Enviando solicitud de transcripción...';
    elapsedTimeDiv.innerHTML = '';

    startTime = new Date();
    updateElapsedTime();
    timerInterval = setInterval(updateElapsedTime, 1000);

    console.log("Enviando solicitud fetch");
    fetch('/transcription/transcribe', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            url: url,
            model_type: modelType,
            english_only: englishOnly
        }),
    })
    .then(response => {
        console.log("Respuesta recibida", response);
        if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.json();
    })
    .then(data => {
        console.log("Datos recibidos", data);
        if (data.status === 'queued') {
            currentTaskId = data.task_id;
            statusDiv.innerHTML = `Tarea en cola. ID: ${currentTaskId}`;
            checkTaskStatus();
        } else {
            throw new Error(data.error || 'Error desconocido al encolar la tarea');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        clearInterval(timerInterval);
        statusDiv.innerHTML = 'Error al enviar la solicitud de transcripción.';
        elapsedTimeDiv.innerHTML = '';
    });
}

function checkTaskStatus() {
    if (!currentTaskId) return;

    fetch(`/transcription/status/${currentTaskId}`)
        .then(response => response.json())
        .then(data => {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `Estado: ${data.status}`;

            if (data.status === 'Completed') {
                clearInterval(timerInterval);
                const endTime = new Date();
                const totalTime = (endTime - startTime) / 1000;
                document.getElementById('elapsed-time').innerHTML = `Tiempo total: ${formatTime(totalTime)}`;
                showResult(data.result);
            } else if (data.status === 'Failed') {
                clearInterval(timerInterval);
                throw new Error(data.error || 'La transcripción falló');
            } else {
                // Si aún está en proceso, seguir verificando
                setTimeout(checkTaskStatus, 5000);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            clearInterval(timerInterval);
            document.getElementById('status').innerHTML = 'Error al verificar el estado de la tarea.';
        });
}

function showResult(result) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `
        <h2>Transcripción:</h2>
        <pre>${result.transcription}</pre>
        <p><strong>Archivo guardado como:</strong><br>${result.file}</p>
    `;
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
        .then(response => response.json())
        .then(data => {
            document.getElementById('video-title').textContent = data.video_info.title;
            document.getElementById('video-channel').textContent = data.video_info.channel;
            document.getElementById('video-url').href = data.video_info.url;
            document.getElementById('video-url').textContent = data.video_info.url;
            document.getElementById('video-description').textContent = data.video_info.description;
            document.getElementById('transcription-content').textContent = data.content;

            // Crear el embed del video de YouTube
            const videoId = getYouTubeVideoId(data.video_info.url);
            const embedHtml = `<iframe width="560" height="315" src="https://www.youtube.com/embed/${videoId}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>`;
            document.getElementById('video-embed').innerHTML = embedHtml;

            // Mostrar los detalles del video
            document.getElementById('video-details').style.display = 'block';
        })
        .catch(error => console.error('Error:', error));
}

function getYouTubeVideoId(url) {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length === 11) ? match[2] : null;
}

function showQueue() {
    fetch('/transcription/queue')
        .then(response => response.json())
        .then(data => {
            const queueDiv = document.getElementById('queue');
            let queueHtml = '<h2>Cola de Transcripciones</h2><ul>';
            for (const [taskId, task] of Object.entries(data)) {
                queueHtml += `<li>Tarea ${taskId}: ${task.status} - ${task.url}</li>`;
            }
            queueHtml += '</ul>';
            queueDiv.innerHTML = queueHtml;
        })
        .catch(error => console.error('Error al obtener la cola:', error));
}

console.log("Script de transcripción cargado");

document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM cargado");
    
    const form = document.getElementById('transcription-form');
    const transcribeButton = document.getElementById('transcribe-button');
    const queueButton = document.getElementById('show-queue-button');

    console.log("Formulario:", form);
    console.log("Botón de transcripción:", transcribeButton);
    console.log("Botón de cola:", queueButton);

    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            console.log("Formulario enviado");
            transcribeVideo();
        });
    } else {
        console.error("Formulario no encontrado");
    }

    if (transcribeButton) {
        transcribeButton.addEventListener('click', function(event) {
            event.preventDefault();
            console.log("Botón de transcripción clickeado");
            transcribeVideo();
        });
    } else {
        console.error("Botón de transcripción no encontrado");
    }

    if (queueButton) {
        queueButton.addEventListener('click', function() {
            console.log("Botón de mostrar cola clickeado");
            showQueue();
        });
    } else {
        console.error("Botón de mostrar cola no encontrado");
    }
});

function transcribeVideo() {
    console.log("Función transcribeVideo llamada");
    
    const url = document.getElementById('youtube-url').value;
    const modelType = document.getElementById('model-type').value;
    const englishOnly = document.getElementById('english-only').checked;

    console.log(`URL: ${url}, Model: ${modelType}, English Only: ${englishOnly}`);

    fetch('/transcription/transcribe', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            url: url,
            model_type: modelType,
            english_only: englishOnly
        }),
    })
    .then(response => {
        console.log("Respuesta recibida", response);
        if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.json();
    })
    .then(data => {
        console.log("Datos recibidos", data);
        if (data.status === 'queued') {
            document.getElementById('status').innerHTML = `Tarea en cola. ID: ${data.task_id}`;
            checkTaskStatus(data.task_id);
        } else {
            throw new Error(data.error || 'Error desconocido al encolar la tarea');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        document.getElementById('status').innerHTML = 'Error al enviar la solicitud de transcripción.';
    });
}

function showQueue() {
    console.log("Función showQueue llamada");
    fetch('/transcription/queue')
        .then(response => response.json())
        .then(data => {
            console.log("Datos de la cola recibidos", data);
            const queueDiv = document.getElementById('queue');
            let queueHtml = '<h2>Cola de Transcripciones</h2><ul>';
            for (const [taskId, task] of Object.entries(data)) {
                queueHtml += `<li>Tarea ${taskId}: ${task.status} - ${task.url}</li>`;
            }
            queueHtml += '</ul>';
            queueDiv.innerHTML = queueHtml;
        })
        .catch(error => console.error('Error al obtener la cola:', error));
}

function checkTaskStatus(taskId) {
    console.log(`Verificando estado de la tarea: ${taskId}`);
    fetch(`/transcription/status/${taskId}`)
        .then(response => response.json())
        .then(data => {
            console.log("Estado de la tarea recibido", data);
            document.getElementById('status').innerHTML = `Estado: ${data.status}`;
            if (data.status === 'Completed') {
                showResult(data.result);
            } else if (data.status === 'Failed') {
                throw new Error(data.error || 'La transcripción falló');
            } else {
                setTimeout(() => checkTaskStatus(taskId), 5000);
            }
        })
        .catch(error => {
            console.error('Error al verificar el estado de la tarea:', error);
            document.getElementById('status').innerHTML = 'Error al verificar el estado de la tarea.';
        });
}

function showResult(result) {
    console.log("Mostrando resultado", result);
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `
        <h2>Transcripción:</h2>
        <pre>${result.transcription}</pre>
        <p><strong>Archivo guardado como:</strong><br>${result.file}</p>
    `;
}