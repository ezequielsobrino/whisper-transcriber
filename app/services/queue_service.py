import threading
from queue import Queue
from enum import Enum
import time

class TaskStatus(Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"

class TranscriptionTask:
    def __init__(self, url, model_type, english_only):
        self.url = url
        self.model_type = model_type
        self.english_only = english_only
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None

class QueueService:
    def __init__(self, transcription_service):
        self.queue = Queue()
        self.tasks = {}
        self.transcription_service = transcription_service
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()

    def add_task(self, url, model_type, english_only):
        task_id = str(time.time())  # Simple unique ID
        task = TranscriptionTask(url, model_type, english_only)
        self.tasks[task_id] = task
        self.queue.put(task_id)
        return task_id

    def get_task_status(self, task_id):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            return {
                "status": task.status.value,
                "result": task.result,
                "error": task.error
            }
        return None

    def get_all_tasks(self):
        return {task_id: {"status": task.status.value, "url": task.url} for task_id, task in self.tasks.items()}

    def _process_queue(self):
        while True:
            task_id = self.queue.get()
            task = self.tasks[task_id]
            task.status = TaskStatus.PROCESSING
            try:
                result = self.transcription_service.transcribe_video(task.url, task.model_type, task.english_only)
                task.result = result
                task.status = TaskStatus.COMPLETED
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.FAILED
            self.queue.task_done()