from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsRectItem, QGraphicsPathItem, QGraphicsTextItem
)
from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtGui import (
    QPixmap, QImage, QPainter, QPen, QBrush, QColor,
    QPainterPath, QWheelEvent, QMouseEvent, QFont
)
from enum import Enum, auto


class Tool(Enum):
    SELECT = auto()
    PAN = auto()
    CROP = auto()
    ANNOTATE_RECT = auto()
    ANNOTATE_ARROW = auto()
    ANNOTATE_TEXT = auto()
    BRUSH = auto()


class CanvasWidget(QGraphicsView):
    image_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setBackgroundBrush(QBrush(QColor(45, 45, 48)))

        self._pixmap_item: QGraphicsPixmapItem | None = None
        self._current_tool = Tool.SELECT
        self._panning = False
        self._pan_start = QPointF()
        self._drawing = False
        self._draw_start = QPointF()
        self._temp_item = None
        self._brush_color = QColor(255, 0, 0)
        self._brush_width = 3
        self._pen_color = QColor(255, 0, 0)
        self._pen_width = 2
        self._current_image: QImage | None = None
        self._zoom_level = 1.0

    def set_tool(self, tool: Tool):
        self.current_tool = tool

    @property
    def current_tool(self):
        return self._current_tool

    @current_tool.setter
    def current_tool(self, tool: Tool):
        self._current_tool = tool
        cursors = {
            Tool.SELECT: Qt.ArrowCursor,
            Tool.PAN: Qt.OpenHandCursor,
            Tool.CROP: Qt.CrossCursor,
            Tool.ANNOTATE_RECT: Qt.CrossCursor,
            Tool.ANNOTATE_ARROW: Qt.CrossCursor,
            Tool.ANNOTATE_TEXT: Qt.IBeamCursor,
            Tool.BRUSH: Qt.CrossCursor,
        }
        self.setCursor(cursors.get(tool, Qt.ArrowCursor))

    def load_image(self, image: QImage):
        self._current_image = image
        self._scene.clear()
        self._pixmap_item = QGraphicsPixmapItem(QPixmap.fromImage(image))
        self._scene.addItem(self._pixmap_item)
        self._scene.setSceneRect(QRectF(image.rect()))
        self.fit_in_view()
        self._zoom_level = 1.0
        self.image_changed.emit()

    def load_pil_image(self, pil_image):
        if pil_image.mode == "RGBA":
            qimage = QImage(
                pil_image.tobytes(), pil_image.width, pil_image.height,
                pil_image.width * 4, QImage.Format_RGBA8888
            )
        else:
            pil_image = pil_image.convert("RGB")
            qimage = QImage(
                pil_image.tobytes(), pil_image.width, pil_image.height,
                pil_image.width * 3, QImage.Format_RGB888
            )
        self.load_image(qimage.copy())

    def get_current_image(self) -> QImage | None:
        return self._current_image

    def render_to_image(self) -> QImage | None:
        """Render scene (base image + all overlays) into a single QImage."""
        if self._current_image is None:
            return None
        has_overlays = any(
            item is not self._pixmap_item
            for item in self._scene.items()
        )
        if not has_overlays:
            return self._current_image
        rect = self._scene.sceneRect().toRect()
        if rect.isEmpty():
            return self._current_image
        rendered = QImage(rect.size(), QImage.Format_RGBA8888)
        rendered.fill(Qt.transparent)
        painter = QPainter(rendered)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self._scene.render(painter, QRectF(rendered.rect()), rect)
        painter.end()
        return rendered

    def fit_in_view(self):
        if self._pixmap_item:
            self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
            self._zoom_level = 1.0

    def zoom_in(self):
        self.scale(1.25, 1.25)
        self._zoom_level *= 1.25

    def zoom_out(self):
        self.scale(0.8, 0.8)
        self._zoom_level *= 0.8

    def wheelEvent(self, event: QWheelEvent):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)
        self._zoom_level *= factor

    def _scene_pos_from_event(self, event: QMouseEvent) -> QPointF:
        return self.mapToScene(event.position().toPoint())

    def mousePressEvent(self, event: QMouseEvent):
        pos = self._scene_pos_from_event(event)

        if event.button() == Qt.MiddleButton or (
            event.button() == Qt.LeftButton and self._current_tool == Tool.PAN
        ):
            self._panning = True
            self._pan_start = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            return

        if event.button() == Qt.LeftButton:
            self._drawing = True
            self._draw_start = pos
            self._start_drawing(pos)
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._panning:
            delta = event.position() - self._pan_start
            self._pan_start = event.position()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - int(delta.x())
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - int(delta.y())
            )
            return

        if self._drawing:
            pos = self._scene_pos_from_event(event)
            self._update_drawing(pos)
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._panning:
            self._panning = False
            cursors = {
                Tool.PAN: Qt.OpenHandCursor,
            }
            self.setCursor(cursors.get(self._current_tool, Qt.ArrowCursor))
            return

        if self._drawing:
            pos = self._scene_pos_from_event(event)
            self._finish_drawing(pos)
            self._drawing = False
            return

        super().mouseReleaseEvent(event)

    def _start_drawing(self, pos: QPointF):
        if self._current_tool == Tool.CROP:
            pen = QPen(QColor(0, 150, 255), 2, Qt.DashLine)
            rect = QGraphicsRectItem(QRectF(pos, pos))
            rect.setPen(pen)
            rect.setBrush(QBrush(QColor(0, 150, 255, 30)))
            rect.setData(0, "crop")
            self._scene.addItem(rect)
            self._temp_item = rect

        elif self._current_tool == Tool.ANNOTATE_RECT:
            pen = QPen(self._pen_color, self._pen_width)
            rect = QGraphicsRectItem(QRectF(pos, pos))
            rect.setPen(pen)
            self._scene.addItem(rect)
            self._temp_item = rect

        elif self._current_tool == Tool.ANNOTATE_ARROW:
            pen = QPen(self._pen_color, self._pen_width)
            path = QPainterPath()
            path.moveTo(pos)
            item = QGraphicsPathItem(path)
            item.setPen(pen)
            self._scene.addItem(item)
            self._temp_item = item

        elif self._current_tool == Tool.BRUSH:
            pen = QPen(self._brush_color, self._brush_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            path = QPainterPath()
            path.moveTo(pos)
            item = QGraphicsPathItem(path)
            item.setPen(pen)
            self._scene.addItem(item)
            self._temp_item = item

        elif self._current_tool == Tool.ANNOTATE_TEXT:
            text_item = QGraphicsTextItem("Text")
            text_item.setFont(QFont("Arial", 14))
            text_item.setDefaultTextColor(self._pen_color)
            text_item.setPos(pos)
            text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
            self._scene.addItem(text_item)
            self._temp_item = text_item
            self._drawing = False

    def _update_drawing(self, pos: QPointF):
        if not self._temp_item:
            return

        if self._current_tool in (Tool.CROP, Tool.ANNOTATE_RECT):
            rect = QRectF(self._draw_start, pos).normalized()
            self._temp_item.setRect(rect)

        elif self._current_tool == Tool.ANNOTATE_ARROW:
            start = self._draw_start
            path = QPainterPath()
            path.moveTo(start)
            path.lineTo(pos)
            dx = pos.x() - start.x()
            dy = pos.y() - start.y()
            length = (dx ** 2 + dy ** 2) ** 0.5
            if length > 0:
                arrow_size = min(20, length * 0.3)
                ux, uy = dx / length, dy / length
                px, py = -uy, ux
                tip = pos
                left = QPointF(
                    tip.x() - ux * arrow_size + px * arrow_size * 0.5,
                    tip.y() - uy * arrow_size + py * arrow_size * 0.5,
                )
                right = QPointF(
                    tip.x() - ux * arrow_size - px * arrow_size * 0.5,
                    tip.y() - uy * arrow_size - py * arrow_size * 0.5,
                )
                path.moveTo(tip)
                path.lineTo(left)
                path.moveTo(tip)
                path.lineTo(right)
            self._temp_item.setPath(path)

        elif self._current_tool == Tool.BRUSH:
            path = self._temp_item.path()
            path.lineTo(pos)
            self._temp_item.setPath(path)

    def _finish_drawing(self, pos: QPointF):
        self._update_drawing(pos)
        self._temp_item = None

    def apply_crop(self, rect: QRectF):
        if not self._current_image:
            return
        cropped = self._current_image.copy(rect.toRect())
        if not cropped.isNull():
            self.load_image(cropped)

    def clear_annotations(self):
        for item in self._scene.items():
            if item is not self._pixmap_item and item is not self._temp_item:
                self._scene.removeItem(item)
