import os
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QDockWidget,
    QStatusBar, QLabel, QMenuBar, QWidget, QVBoxLayout,
    QProgressBar, QHBoxLayout, QComboBox, QSlider, QCheckBox,
    QSpinBox, QPushButton, QGroupBox, QFormLayout, QTabWidget,
    QSplitter
)
from PySide6.QtCore import Qt, QThreadPool, QRunnable, Signal
from PySide6.QtGui import QImage, QAction, QKeySequence, QColor
from PySide6.QtWidgets import QGraphicsRectItem
from PySide6.QtWidgets import QGraphicsRectItem

from ui.canvas_widget import CanvasWidget, Tool
from ui.toolbar import ToolBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ConvertTools - 图片格式转换工具")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        self._current_file_path = None
        self._image_history: list[QImage] = []
        self._history_index = -1
        self._max_history = 20
        self._setup_ui()
        self._setup_menu()
        self._setup_connections()
        self._update_status("就绪")

    def _setup_ui(self):
        self.toolbar = ToolBar("工具栏")
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        self.canvas = CanvasWidget(self)
        self.setCentralWidget(self.canvas)

        self._setup_layer_panel()
        self._setup_right_panel()

        self.status_label = QLabel()
        self.zoom_label = QLabel("100%")
        self.progressBar = QProgressBar()
        self.progressBar.setMaximumWidth(200)
        self.progressBar.setVisible(False)
        self.statusBar().addWidget(self.status_label, 1)
        self.statusBar().addPermanentWidget(self.zoom_label)
        self.statusBar().addPermanentWidget(self.progressBar)

    def _setup_layer_panel(self):
        dock = QDockWidget("图层", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)

        self.layer_list = QWidget()
        self.layer_layout = QVBoxLayout(self.layer_list)
        self.layer_layout.setAlignment(Qt.AlignTop)
        self.layer_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.layer_list)

        self.layer_info = QLabel("打开 PSD 文件以查看图层")
        self.layer_info.setAlignment(Qt.AlignCenter)
        self.layer_info.setStyleSheet("color: #888; padding: 20px;")
        layout.addWidget(self.layer_info)

        dock.setWidget(container)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        self.layer_dock = dock

    def _setup_right_panel(self):
        dock = QDockWidget("属性", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        dock.setMinimumWidth(260)

        tabs = QTabWidget()

        self._setup_export_tab(tabs)
        self._setup_filter_tab(tabs)

        dock.setWidget(tabs)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.right_dock = dock

    def _setup_export_tab(self, tabs: QTabWidget):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        format_group = QGroupBox("输出格式")
        format_layout = QFormLayout(format_group)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG", "WebP", "BMP", "TIFF", "ICO"])
        format_layout.addRow("格式:", self.format_combo)

        self.quality_group = QGroupBox("质量设置")
        quality_layout = QFormLayout(self.quality_group)

        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(95)
        self.quality_label = QLabel("95")
        quality_layout.addRow("质量:", self.quality_slider)
        quality_layout.addRow("", self.quality_label)

        self.lossless_check = QCheckBox("无损压缩")
        quality_layout.addRow(self.lossless_check)

        self.png_compression = QSpinBox()
        self.png_compression.setRange(0, 9)
        self.png_compression.setValue(6)
        quality_layout.addRow("PNG压缩:", self.png_compression)

        layout.addWidget(format_group)
        layout.addWidget(self.quality_group)

        path_group = QGroupBox("输出路径")
        path_layout = QVBoxLayout(path_group)
        self.output_path_label = QLabel("与源文件同目录")
        self.output_browse_btn = QPushButton("选择输出目录...")
        path_layout.addWidget(self.output_path_label)
        path_layout.addWidget(self.output_browse_btn)

        layout.addWidget(path_group)

        self.export_btn = QPushButton("导出")
        self.export_btn.setStyleSheet(
            "QPushButton { background-color: #0078d4; color: white; "
            "padding: 8px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #106ebe; }"
        )
        layout.addWidget(self.export_btn)

        self.batch_btn = QPushButton("批量转换...")
        layout.addWidget(self.batch_btn)

        layout.addStretch()
        tabs.addTab(tab, "导出")

    def _setup_filter_tab(self, tabs: QTabWidget):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        filter_group = QGroupBox("调整")
        filter_layout = QFormLayout(filter_group)

        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_label = QLabel("0")
        filter_layout.addRow("亮度:", self.brightness_slider)
        filter_layout.addRow("", self.brightness_label)

        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(0)
        self.contrast_label = QLabel("0")
        filter_layout.addRow("对比度:", self.contrast_slider)
        filter_layout.addRow("", self.contrast_label)

        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setRange(-100, 100)
        self.saturation_slider.setValue(0)
        self.saturation_label = QLabel("0")
        filter_layout.addRow("饱和度:", self.saturation_slider)
        filter_layout.addRow("", self.saturation_label)

        layout.addWidget(filter_group)

        preset_group = QGroupBox("滤镜预设")
        preset_layout = QVBoxLayout(preset_group)
        for name in ["灰度", "怀旧", "反色", "模糊", "锐化"]:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, n=name: self._apply_filter_preset(n))
            preset_layout.addWidget(btn)
        layout.addWidget(preset_group)

        btn_layout = QHBoxLayout()
        self.filter_apply_btn = QPushButton("应用")
        self.filter_reset_btn = QPushButton("重置")
        btn_layout.addWidget(self.filter_apply_btn)
        btn_layout.addWidget(self.filter_reset_btn)
        layout.addLayout(btn_layout)

        layout.addStretch()
        tabs.addTab(tab, "滤镜")

    def _setup_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("文件(&F)")
        self._add_action(file_menu, "打开(&O)...", self._open_file, "Ctrl+O")
        self._add_action(file_menu, "打开文件夹(&D)...", self._open_folder, "Ctrl+D")
        file_menu.addSeparator()
        self._add_action(file_menu, "导出(&E)...", self._export_file, "Ctrl+S")
        self._add_action(file_menu, "批量转换(&B)...", self._open_batch, "Ctrl+B")
        file_menu.addSeparator()
        self._add_action(file_menu, "退出(&Q)", self.close, "Ctrl+Q")

        edit_menu = menu_bar.addMenu("编辑(&E)")
        self._add_action(edit_menu, "撤销(&U)", self._undo, "Ctrl+Z")
        self._add_action(edit_menu, "清除标注", self.canvas.clear_annotations)
        edit_menu.addSeparator()
        self._add_action(edit_menu, "应用裁剪", self._apply_crop, "Enter")

        view_menu = menu_bar.addMenu("视图(&V)")
        self._add_action(view_menu, "放大", self.canvas.zoom_in, "=")
        self._add_action(view_menu, "缩小", self.canvas.zoom_out, "-")
        self._add_action(view_menu, "适应窗口", self.canvas.fit_in_view, "Ctrl+0")
        view_menu.addSeparator()
        self._add_action(view_menu, "图层面板", lambda: self.layer_dock.setVisible(not self.layer_dock.isVisible()))
        self._add_action(view_menu, "属性面板", lambda: self.right_dock.setVisible(not self.right_dock.isVisible()))

    def _add_action(self, menu, text, callback, shortcut=None):
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(callback)
        menu.addAction(action)
        return action

    def _setup_connections(self):
        self.toolbar.tool_selected.connect(self.canvas.set_tool)
        self.toolbar.zoom_in_clicked.connect(self.canvas.zoom_in)
        self.toolbar.zoom_out_clicked.connect(self.canvas.zoom_out)
        self.toolbar.zoom_fit_clicked.connect(self.canvas.fit_in_view)

        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        self.quality_slider.valueChanged.connect(
            lambda v: self.quality_label.setText(str(v))
        )
        self.export_btn.clicked.connect(self._export_file)
        self.batch_btn.clicked.connect(self._open_batch)
        self.output_browse_btn.clicked.connect(self._browse_output_dir)

        self.brightness_slider.valueChanged.connect(
            lambda v: self.brightness_label.setText(str(v))
        )
        self.contrast_slider.valueChanged.connect(
            lambda v: self.contrast_label.setText(str(v))
        )
        self.saturation_slider.valueChanged.connect(
            lambda v: self.saturation_label.setText(str(v))
        )

        self.canvas.image_changed.connect(self._on_image_changed)

        self.filter_apply_btn.clicked.connect(self._apply_filter_adjustments)
        self.filter_reset_btn.clicked.connect(self._reset_filter_adjustments)

    def _on_format_changed(self, fmt: str):
        has_quality = fmt in ("JPEG", "WebP")
        self.quality_group.setVisible(has_quality)
        self.png_compression.setVisible(fmt == "PNG")
        self.lossless_check.setVisible(fmt == "WebP")

    def _on_image_changed(self):
        img = self.canvas.get_current_image()
        if img:
            self._update_status(f"图片: {img.width()} x {img.height()}")

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "打开图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.tif *.gif *.ico *.psd);;"
            "所有文件 (*)"
        )
        if path:
            self._load_file(path)

    def _open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self._open_batch_with_folder(folder)

    def _load_file(self, path: str):
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".psd":
                self._load_psd(path)
            else:
                from PIL import Image
                img = Image.open(path)
                self.canvas.load_pil_image(img)
                self._current_file_path = path
                self._update_status(f"已打开: {os.path.basename(path)}")
                self.setWindowTitle(f"ConvertTools - {os.path.basename(path)}")
                self._push_history()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件:\n{e}")

    def _load_psd(self, path: str):
        try:
            from core.psd_handler import PSDHandler
            handler = PSDHandler(path)
            composite = handler.get_composite()
            if composite:
                self.canvas.load_pil_image(composite)
            self._current_file_path = path
            self._update_status(f"已打开 PSD: {os.path.basename(path)}")
            self.setWindowTitle(f"ConvertTools - {os.path.basename(path)}")
            self._push_history()
            self._populate_layers(handler)
        except ImportError:
            QMessageBox.warning(self, "提示", "PSD 支持需要安装 psd-tools:\npip install psd-tools")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开 PSD 文件:\n{e}")

    def _populate_layers(self, handler):
        while self.layer_layout.count():
            item = self.layer_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.layer_info.setVisible(False)

        layers = handler.get_layer_list()
        for layer_info in layers:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(2, 2, 2, 2)

            check = QCheckBox()
            check.setChecked(layer_info.get("visible", True))
            check.setProperty("layer_idx", layer_info["index"])
            row_layout.addWidget(check)

            name = QLabel(layer_info["name"])
            name.setStyleSheet("font-size: 12px;")
            row_layout.addWidget(name, 1)

            preview_btn = QPushButton("预览")
            preview_btn.setFixedWidth(50)
            preview_btn.clicked.connect(
                lambda checked, h=handler, idx=layer_info["index"]: self._preview_layer(h, idx)
            )
            row_layout.addWidget(preview_btn)

            self.layer_layout.addWidget(row)

    def _preview_layer(self, handler, layer_idx):
        img = handler.get_layer_image(layer_idx)
        if img:
            self.canvas.load_pil_image(img)
            self._update_status(f"预览图层 #{layer_idx}")

    def _export_file(self):
        if not self._current_file_path:
            QMessageBox.information(self, "提示", "请先打开一个图片文件")
            return

        img = self.canvas.get_current_image()
        if not img:
            return

        fmt = self.format_combo.currentText()
        ext_map = {"PNG": ".png", "JPEG": ".jpg", "WebP": ".webp", "BMP": ".bmp", "TIFF": ".tiff", "ICO": ".ico"}
        default_name = os.path.splitext(os.path.basename(self._current_file_path))[0] + ext_map.get(fmt, ".png")

        save_path, _ = QFileDialog.getSaveFileName(
            self, "导出图片", default_name,
            f"{fmt} 文件 (*{ext_map.get(fmt, '')})"
        )
        if not save_path:
            return

        try:
            from core.converter import ImageConverter
            converter = ImageConverter()
            options = self._get_export_options(fmt)
            converter.convert_qimage(img, save_path, fmt, options)
            self._update_status(f"已导出: {os.path.basename(save_path)}")
            QMessageBox.information(self, "成功", f"图片已导出到:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败:\n{e}")

    def _get_export_options(self, fmt: str) -> dict:
        options = {}
        if fmt in ("JPEG", "WebP"):
            options["quality"] = self.quality_slider.value()
        if fmt == "WebP" and self.lossless_check.isChecked():
            options["lossless"] = True
        if fmt == "PNG":
            options["compress_level"] = self.png_compression.value()
        return options

    def _browse_output_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if folder:
            self.output_path_label.setText(folder)

    def _open_batch(self):
        try:
            from ui.batch_panel import BatchDialog
            dialog = BatchDialog(self)
            dialog.exec()
        except ImportError:
            QMessageBox.information(self, "提示", "批量转换功能正在开发中")

    def _open_batch_with_folder(self, folder):
        self._open_batch()

    def _apply_crop(self):
        for item in self.canvas._scene.items():
            if isinstance(item, QGraphicsRectItem) and item is not self.canvas._pixmap_item:
                rect = item.sceneBoundingRect()
                self.canvas.apply_crop(rect)
                self._push_history()
                break

    def _undo(self):
        if self._history_index > 0:
            self._history_index -= 1
            self.canvas.load_image(self._image_history[self._history_index].copy())
            self._update_status(f"撤销 ({self._history_index + 1}/{len(self._image_history)})")

    def _push_history(self):
        img = self.canvas.get_current_image()
        if img is None:
            return
        self._image_history = self._image_history[:self._history_index + 1]
        self._image_history.append(img.copy())
        if len(self._image_history) > self._max_history:
            self._image_history.pop(0)
        self._history_index = len(self._image_history) - 1

    def _apply_filter_preset(self, name: str):
        img = self.canvas.get_current_image()
        if img is None:
            return
        from core.converter import ImageConverter
        converter = ImageConverter()
        pil_img = converter._qimage_to_pil(img)
        from core.filters import PRESETS
        if name not in PRESETS:
            return
        result = PRESETS[name](pil_img)
        self.canvas.load_pil_image(result)
        self._push_history()
        self._update_status(f"已应用滤镜: {name}")

    def _apply_filter_adjustments(self):
        img = self.canvas.get_current_image()
        if img is None:
            return
        brightness = self.brightness_slider.value()
        contrast = self.contrast_slider.value()
        saturation = self.saturation_slider.value()
        if brightness == 0 and contrast == 0 and saturation == 0:
            return
        from core.converter import ImageConverter
        converter = ImageConverter()
        pil_img = converter._qimage_to_pil(img)
        from core.filters import apply_adjustments
        result = apply_adjustments(pil_img, brightness, contrast, saturation)
        self.canvas.load_pil_image(result)
        self._push_history()
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        self.saturation_slider.setValue(0)
        self._update_status("已应用亮度/对比度/饱和度调整")

    def _reset_filter_adjustments(self):
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        self.saturation_slider.setValue(0)
        self._update_status("已重置滤镜参数")

    def _update_status(self, text: str):
        self.status_label.setText(text)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isfile(path):
                self._load_file(path)
