import os
from typing import Callable
from PySide6.QtCore import QThread, Signal
from core.converter import ImageConverter


class BatchTask:
    def __init__(self, input_path: str, output_format: str, output_dir: str | None = None, options: dict | None = None):
        self.input_path = input_path
        self.output_format = output_format
        self.output_dir = output_dir
        self.options = options or {}


class BatchEngine(QThread):
    progress = Signal(int, int, str)  # current, total, filename
    file_done = Signal(str, str)      # input_path, output_path
    file_error = Signal(str, str)     # input_path, error_message
    finished_all = Signal(int, int)   # succeeded, failed

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks: list[BatchTask] = []
        self._paused = False
        self._cancelled = False
        self._converter = ImageConverter()

    def set_tasks(self, tasks: list[BatchTask]):
        self._tasks = tasks

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        succeeded = 0
        failed = 0
        total = len(self._tasks)

        for i, task in enumerate(self._tasks):
            if self._cancelled:
                break

            while self._paused and not self._cancelled:
                self.msleep(100)

            if self._cancelled:
                break

            filename = os.path.basename(task.input_path)
            self.progress.emit(i + 1, total, filename)

            try:
                output_dir = task.output_dir or ImageConverter.get_output_dir(task.input_path)
                output_path = ImageConverter.get_output_path(
                    task.input_path, task.output_format, output_dir
                )
                self._converter.convert(task.input_path, output_path, task.options)
                self.file_done.emit(task.input_path, output_path)
                succeeded += 1
            except Exception as e:
                self.file_error.emit(task.input_path, str(e))
                failed += 1

        self.finished_all.emit(succeeded, failed)
