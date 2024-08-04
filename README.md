# YouTube Transcriber

## Description
This project is a web application that allows users to transcribe YouTube videos. It uses Flask as the backend framework and JavaScript for frontend interactions.

## Features
- Transcription of YouTube videos from the video URL
- Storage of transcriptions for later access
- Simple and easy-to-use user interface

## Prerequisites
- Python 3.7+
- Flask
- Other dependencies as listed in `requirements.txt`

## Installation
1. Clone this repository:
   ```
   git clone https://github.com/ezequielsobrino/whisper-transcriber.git
   ```
2. Navigate to the project directory:
   ```
   cd whisper-transcriber
   ```
3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Start the application:
   ```
   python run.py
   ```
2. Open a browser and go to `http://localhost:5000`
3. Enter the URL of a YouTube video in the text field
4. Click "Transcribe" to get the transcription

## Project Structure
```
whisper-transcriber/
│
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/
│   │       └── script.js
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   └── transcriptions.html
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   └── routes/
│       ├── main_routes.py
│       └── transcription_routes.py
│
├── transcriptions/
├── requirements.txt
├── run.py
└── README.md
```

## Dependencies
The project relies on the following main dependencies:
```
numpy==1.24.3
torch==2.2.0
torchaudio==2.2.0
torchvision==0.17.0
openai-whisper
flask
yt-dlp
werkzeug
```
For a complete list of dependencies, please refer to the `requirements.txt` file.

## Contributing
Contributions to this project are welcome. Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License.