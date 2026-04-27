from PySide6.QtWidgets import QToolBar, QToolButton, QWidget, QSizePolicy
from PySide6.QtGui import QIcon, QFont, QAction
from PySide6.QtCore import Signal, QSize, Qt
from PySide6.QtWidgets import QMenu
from ui.canvas_widget import Tool


class ToolBar(QToolBar):
    tool_selected = Signal(Tool)
    zoom_in_clicked = Signal()
    zoom_out_clicked = Signal()
    zoom_fit_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setIconSize(QSize(24, 24))
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self._actions = {}
        self._setup_tools()
        self.addSeparator()
        self._setup_view()

    def _make_tool_action(self, name: str, text: str, tool: Tool, shortcut: str = None):
        action = QAction(text, self)
        action.setCheckable(True)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(lambda checked: self._on_tool_triggered(tool))
        self.addAction(action)
        self._actions[tool] = action
        return action

    def _setup_tools(self):
        self._make_tool_action("select", "选择 (V)", Tool.SELECT, "V")
        self._make_tool_action("pan", "平移 (H)", Tool.PAN, "H")
        self.addSeparator()
        self._make_tool_action("crop", "裁剪 (C)", Tool.CROP, "C")
        self.addSeparator()
        self._make_tool_action("rect", "矩形标注 (R)", Tool.ANNOTATE_RECT, "R")
        self._make_tool_action("arrow", "箭头标注 (A)", Tool.ANNOTATE_ARROW, "A")
        self._make_tool_action("text", "文字标注 (T)", Tool.ANNOTATE_TEXT, "T")
        self.addSeparator()
        self._make_tool_action("brush", "画笔 (B)", Tool.BRUSH, "B")

        if Tool.SELECT in self._actions:
            self._actions[Tool.SELECT].setChecked(True)

    def _setup_view(self):
        zoom_in = QAction("放大 (+)", self)
        zoom_in.setShortcut("+")
        zoom_in.triggered.connect(self.zoom_in_clicked.emit)
        self.addAction(zoom_in)

        zoom_out = QAction("缩小 (-)", self)
        zoom_out.setShortcut("-")
        zoom_out.triggered.connect(self.zoom_out_clicked.emit)
        self.addAction(zoom_out)

        zoom_fit = QAction("适应窗口 (0)", self)
        zoom_fit.setShortcut("0")
        zoom_fit.triggered.connect(self.zoom_fit_clicked.emit)
        self.addAction(zoom_fit)

    def _on_tool_triggered(self, tool: Tool):
        for t, action in self._actions.items():
            action.setChecked(t == tool)
        self.tool_selected.emit(tool)

    def set_active_tool(self, tool: Tool):
        self._on_tool_triggered(tool)
