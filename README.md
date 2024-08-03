# YouTube Transcription Project

This project is a web application that allows users to transcribe YouTube videos using OpenAI's Whisper model.

## Features

- Transcribes audio from YouTube videos
- Uses OpenAI's Whisper model for transcription
- Simple web interface for entering YouTube URLs
- Displays real-time transcription progress
- Error handling and logging for easy debugging

## Requirements

- Python 3.7+
- Flask
- whisper
- yt-dlp
- FFmpeg

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/ezequielsobrino/whisper-transcriber.git
   cd whisper-transcriber
   ```

2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Ensure you have FFmpeg installed on your system. You can download it from [ffmpeg.org](https://ffmpeg.org/download.html).

## Usage

1. Run the application:
   ```
   python app.py
   ```

2. Open your browser and go to `http://localhost:5000`.

3. Enter the URL of the YouTube video you want to transcribe and click "Transcribe".

4. Wait for the transcription to complete. You'll see a progress bar updating in real-time.

5. Once completed, the transcription will be displayed on the page.

## Project Structure

- `app.py`: Contains the main Flask application logic, including Whisper model configuration, audio download, and transcription process.
- `templates/index.html`: The HTML template for the user interface.
- `static/script.js`: The JavaScript file handling user interaction and AJAX requests for transcription and progress updates.

## Configuration

The project uses Whisper's "base" model by default. If you want to change this, you can modify the following line in `app.py`:

```python
model = whisper.load_model("base")
```

You can change "base" to "medium" or "large" for more accurate transcriptions, but note that this will increase processing time and resource requirements.

## Contributing

If you'd like to contribute to this project, please:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes and commit them (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

Your Name - [@your_twitter](https://twitter.com/your_twitter) - email@example.com

Project Link: [https://github.com/ezequielsobrino/whisper-transcriber](https://github.com/ezequielsobrino/whisper-transcriber)