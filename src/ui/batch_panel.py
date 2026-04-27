import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QSlider, QCheckBox, QSpinBox, QProgressBar,
    QFileDialog, QListWidget, QListWidgetItem, QGroupBox,
    QFormLayout, QMessageBox, QStatusBar, QWidget
)
from PySide6.QtCore import Qt
from core.batch_engine import BatchEngine, BatchTask
from core.converter import ImageConverter, SUPPORTED_INPUT


class BatchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("批量转换")
        self.setMinimumSize(600, 500)
        self.resize(700, 550)

        self._engine: BatchEngine | None = None
        self._output_dir: str | None = None
        self._errors: list[tuple[str, str]] = []

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        files_group = QGroupBox("文件列表")
        files_layout = QVBoxLayout(files_group)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("添加文件...")
        add_btn.clicked.connect(self._add_files)
        add_folder_btn = QPushButton("添加文件夹...")
        add_folder_btn.clicked.connect(self._add_folder)
        remove_btn = QPushButton("移除选中")
        remove_btn.clicked.connect(self._remove_selected)
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self._clear_files)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(add_folder_btn)
        btn_row.addWidget(remove_btn)
        btn_row.addWidget(clear_btn)
        files_layout.addLayout(btn_row)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
        files_layout.addWidget(self.file_list)

        self.file_count_label = QLabel("共 0 个文件")
        files_layout.addWidget(self.file_count_label)
        layout.addWidget(files_group)

        settings_group = QGroupBox("转换设置")
        settings_layout = QFormLayout(settings_group)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG", "WebP", "BMP", "TIFF", "ICO"])
        settings_layout.addRow("目标格式:", self.format_combo)

        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(95)
        self.quality_label = QLabel("95")
        self.quality_slider.valueChanged.connect(lambda v: self.quality_label.setText(str(v)))
        settings_layout.addRow("质量:", self.quality_slider)
        settings_layout.addRow("", self.quality_label)

        self.lossless_check = QCheckBox("无损压缩 (WebP)")
        settings_layout.addRow(self.lossless_check)

        self.output_dir_label = QLabel("与源文件同目录/converted")
        output_browse = QPushButton("选择输出目录...")
        output_browse.clicked.connect(self._browse_output_dir)
        settings_layout.addRow("输出目录:", self.output_dir_label)
        settings_layout.addRow("", output_browse)

        layout.addWidget(settings_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        action_row = QHBoxLayout()
        self.start_btn = QPushButton("开始转换")
        self.start_btn.setStyleSheet(
            "QPushButton { background-color: #0078d4; color: white; "
            "padding: 8px 20px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #106ebe; }"
        )
        self.start_btn.clicked.connect(self._start_batch)

        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self._toggle_pause)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel_batch)

        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)

        action_row.addWidget(self.start_btn)
        action_row.addWidget(self.pause_btn)
        action_row.addWidget(self.cancel_btn)
        action_row.addStretch()
        action_row.addWidget(self.close_btn)
        layout.addLayout(action_row)

    def _add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "选择图片文件", "",
            "图片文件 (*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.tif *.gif *.ico *.psd);;"
            "所有文件 (*)"
        )
        for p in paths:
            self.file_list.addItem(p)
        self._update_count()

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if not folder:
            return
        for root, dirs, files in os.walk(folder):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in SUPPORTED_INPUT:
                    self.file_list.addItem(os.path.join(root, f))
        self._update_count()

    def _remove_selected(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))
        self._update_count()

    def _clear_files(self):
        self.file_list.clear()
        self._update_count()

    def _update_count(self):
        count = self.file_list.count()
        self.file_count_label.setText(f"共 {count} 个文件")

    def _browse_output_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if folder:
            self._output_dir = folder
            self.output_dir_label.setText(folder)

    def _start_batch(self):
        if self.file_list.count() == 0:
            QMessageBox.information(self, "提示", "请先添加文件")
            return

        fmt = self.format_combo.currentText()
        options = {}
        if fmt in ("JPEG", "WebP"):
            options["quality"] = self.quality_slider.value()
        if fmt == "WebP" and self.lossless_check.isChecked():
            options["lossless"] = True

        tasks = []
        for i in range(self.file_list.count()):
            path = self.file_list.item(i).text()
            tasks.append(BatchTask(path, fmt, self._output_dir, options.copy()))

        self._engine = BatchEngine(self)
        self._engine.set_tasks(tasks)
        self._engine.progress.connect(self._on_progress)
        self._engine.file_done.connect(self._on_file_done)
        self._engine.file_error.connect(self._on_file_error)
        self._engine.finished_all.connect(self._on_finished)

        self._errors.clear()

        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(tasks))
        self.progress_bar.setValue(0)
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.status_label.setText("转换中...")

        self._engine.start()

    def _toggle_pause(self):
        if self._engine is None:
            return
        if self.pause_btn.text() == "暂停":
            self._engine.pause()
            self.pause_btn.setText("继续")
            self.status_label.setText("已暂停")
        else:
            self._engine.resume()
            self.pause_btn.setText("暂停")
            self.status_label.setText("转换中...")

    def _cancel_batch(self):
        if self._engine:
            self._engine.cancel()

    def _on_progress(self, current: int, total: int, filename: str):
        self.progress_bar.setValue(current)
        self.status_label.setText(f"({current}/{total}) {filename}")

    def _on_file_done(self, input_path: str, output_path: str):
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item.text() == input_path:
                item.setText(f"✓ {os.path.basename(input_path)}")
                item.setForeground(Qt.darkGreen)
                break

    def _on_file_error(self, input_path: str, error: str):
        self._errors.append((input_path, error))
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if os.path.basename(item.text()).replace("✗ ", "") == os.path.basename(input_path) or item.text() == input_path:
                item.setText(f"✗ {os.path.basename(input_path)}: {error}")
                item.setForeground(Qt.red)
                break

    def _on_finished(self, succeeded: int, failed: int):
        self.progress_bar.setVisible(False)
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.pause_btn.setText("暂停")
        self.status_label.setText(f"完成: 成功 {succeeded}, 失败 {failed}")
        if failed == 0:
            QMessageBox.information(self, "完成", f"全部 {succeeded} 个文件转换成功！")
        else:
            error_details = "\n".join(f"• {os.path.basename(p)}: {e}" for p, e in self._errors[:20])
            QMessageBox.warning(self, "完成", f"成功 {succeeded}, 失败 {failed}\n\n失败明细:\n{error_details}")

    def add_folder(self, folder: str):
        for root, dirs, files in os.walk(folder):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in SUPPORTED_INPUT:
                    self.file_list.addItem(os.path.join(root, f))
        self._update_count()
