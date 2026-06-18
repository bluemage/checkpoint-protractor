#!/usr/bin/env python3
"""On-screen protractor for Linux (Ubuntu)."""

import math
import sys

from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
)
from PyQt5.QtWidgets import QApplication, QWidget


class ProtractorWindow(QWidget):
    """Always-on-top protractor."""

    RADIUS = 220
    ARM_LENGTH = 280
    HIT_RADIUS = 18
    MARGIN = 50
    TOP_MARGIN = 0

    def __init__(self):
        super().__init__(None)
        self.setMouseTracking(True)
        self.setWindowTitle("On-Screen Protractor")
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.StrongFocus)

        size = (self.RADIUS + self.ARM_LENGTH + self.MARGIN) * 2
        top_extent = self.ARM_LENGTH
        bottom_extent = max(self.RADIUS, self.ARM_LENGTH) + 24
        height = int(self.TOP_MARGIN + top_extent + bottom_extent + self.MARGIN)
        self.setFixedSize(size, height)

        self.center = QPointF(size / 2, self.TOP_MARGIN + top_extent)
        self.base_angle = 0.0
        self.arm1_angle = 30.0
        self.arm2_angle = 150.0

        self._drag_mode = None
        self._last_mouse = QPointF()
        self._window_drag_offset = QPointF()

        primary = QApplication.primaryScreen().availableGeometry()
        self.move(
            primary.x() + (primary.width() - size) // 2,
            primary.y() + (primary.height() - height) // 2,
        )

    def _move_window_to(self, global_pos):
        self.move((global_pos - self._window_drag_offset).toPoint())
        self.raise_()

    def measured_angle(self) -> float:
        diff = abs(self.arm2_angle - self.arm1_angle) % 360
        return diff if diff <= 180 else 360 - diff

    def _world_to_local(self, point: QPointF) -> QPointF:
        return point - self.center

    def _arm_endpoint(self, relative_deg: float) -> QPointF:
        total = math.radians(self.base_angle + relative_deg)
        return self.center + QPointF(
            self.ARM_LENGTH * math.cos(total),
            -self.ARM_LENGTH * math.sin(total),
        )

    def _angle_from_point(self, point: QPointF) -> float:
        local = self._world_to_local(point)
        world_deg = math.degrees(math.atan2(-local.y(), local.x()))
        relative = world_deg - self.base_angle
        while relative < 0:
            relative += 360
        while relative >= 360:
            relative -= 360
        return relative

    def _dist(self, a: QPointF, b: QPointF) -> float:
        return math.hypot(a.x() - b.x(), a.y() - b.y())

    def _hit_test(self, pos: QPointF):
        for mode, angle in (("arm1", self.arm1_angle), ("arm2", self.arm2_angle)):
            if self._dist(pos, self._arm_endpoint(angle)) <= self.HIT_RADIUS:
                return mode

        local = self._world_to_local(pos)
        dist = math.hypot(local.x(), local.y())
        if abs(dist - self.RADIUS) < 24:
            return "rotate"

        return "move"

    def _try_system_move(self) -> bool:
        if QApplication.platformName() != "wayland":
            return False
        handle = self.windowHandle()
        if handle is not None and hasattr(handle, "startSystemMove"):
            handle.startSystemMove()
            return True
        return False

    def mousePressEvent(self, event):
        pos = event.localPos()
        if event.button() == Qt.LeftButton:
            hit = self._hit_test(pos)
            self._drag_mode = hit
            self._last_mouse = pos
            if hit == "move" and not self._try_system_move():
                self._window_drag_offset = event.globalPos() - self.frameGeometry().topLeft()
                self.grabMouse()
            self.setFocus()
            event.accept()
        elif event.button() == Qt.RightButton:
            self.close()
            event.accept()

    def mouseMoveEvent(self, event):
        pos = event.localPos()

        if self._drag_mode == "move" and event.buttons() & Qt.LeftButton:
            if self.mouseGrabber() is self:
                self._move_window_to(event.globalPos())
        elif self._drag_mode in ("arm1", "arm2") and event.buttons() & Qt.LeftButton:
            angle = self._angle_from_point(pos)
            if self._drag_mode == "arm1":
                self.arm1_angle = angle
            else:
                self.arm2_angle = angle
            self.update()
        elif self._drag_mode == "rotate" and event.buttons() & Qt.LeftButton:
            a0 = math.degrees(
                math.atan2(
                    self._last_mouse.y() - self.center.y(),
                    self._last_mouse.x() - self.center.x(),
                )
            )
            a1 = math.degrees(
                math.atan2(pos.y() - self.center.y(), pos.x() - self.center.x())
            )
            self.base_angle += a1 - a0
            self._last_mouse = pos
            self.update()
        else:
            mode = self._hit_test(pos)
            if mode in ("arm1", "arm2"):
                self.setCursor(Qt.CrossCursor)
            elif mode == "rotate":
                self.setCursor(Qt.OpenHandCursor)
            elif mode == "move":
                self.setCursor(Qt.SizeAllCursor)
            else:
                self.unsetCursor()

    def mouseReleaseEvent(self, _event):
        if self.mouseGrabber() is self:
            self.releaseMouse()
        self._drag_mode = None

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        step = 1.0 if delta > 0 else -1.0
        if event.modifiers() & Qt.ShiftModifier:
            self.arm1_angle = (self.arm1_angle + step) % 360
        elif event.modifiers() & Qt.ControlModifier:
            self.arm2_angle = (self.arm2_angle + step) % 360
        else:
            self.base_angle += step
        self.update()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Escape, Qt.Key_Q):
            self.close()
        elif event.key() == Qt.Key_R:
            self.base_angle = 0.0
            self.arm1_angle = 30.0
            self.arm2_angle = 150.0
            self.update()
        elif event.key() == Qt.Key_H:
            self.setVisible(not self.isVisible())
        elif event.key() == Qt.Key_Left:
            self.move(self.x() - 20, self.y())
        elif event.key() == Qt.Key_Right:
            self.move(self.x() + 20, self.y())
        elif event.key() == Qt.Key_Up:
            self.move(self.x(), self.y() - 20)
        elif event.key() == Qt.Key_Down:
            self.move(self.x(), self.y() + 20)
        else:
            super().keyPressEvent(event)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx, cy = self.center.x(), self.center.y()

        shadow = QPainterPath()
        shadow.addEllipse(QPointF(cx + 3, cy + 3), self.RADIUS + 8, self.RADIUS + 8)
        painter.fillPath(shadow, QBrush(QColor(0, 0, 0, 40)))

        self._draw_protractor_body(painter)
        self._draw_arms(painter)
        self._draw_center_handle(painter)
        self._draw_angle_label(painter)
        self._draw_help(painter)

    def _draw_protractor_body(self, painter: QPainter):
        cx, cy = self.center.x(), self.center.y()
        base_rad = math.radians(self.base_angle)

        path = QPainterPath()
        rect = QRectF(cx - self.RADIUS, cy - self.RADIUS, self.RADIUS * 2, self.RADIUS * 2)
        path.moveTo(cx, cy)
        path.arcTo(rect, self.base_angle, 180)
        path.closeSubpath()

        painter.setPen(QPen(QColor(30, 30, 30, 200), 2))
        painter.setBrush(QBrush(QColor(255, 255, 255, 180)))
        painter.drawPath(path)

        bl_end = QPointF(
            cx + self.RADIUS * math.cos(base_rad),
            cy - self.RADIUS * math.sin(base_rad),
        )
        bl_start = QPointF(
            cx - self.RADIUS * math.cos(base_rad),
            cy + self.RADIUS * math.sin(base_rad),
        )
        painter.setPen(QPen(QColor(20, 20, 20, 220), 2))
        painter.drawLine(bl_start, bl_end)

        painter.setFont(QFont("Sans Serif", 9))
        for deg in range(0, 181):
            is_major = deg % 10 == 0
            is_mid = deg % 5 == 0
            tick_len = 16 if is_major else (10 if is_mid else 5)
            angle = math.radians(self.base_angle + deg)
            p1 = QPointF(
                cx + self.RADIUS * math.cos(angle),
                cy - self.RADIUS * math.sin(angle),
            )
            p2 = QPointF(
                cx + (self.RADIUS - tick_len) * math.cos(angle),
                cy - (self.RADIUS - tick_len) * math.sin(angle),
            )
            painter.setPen(QPen(QColor(30, 30, 30, 220), 2 if is_major else 1))
            painter.drawLine(p1, p2)

            if is_major:
                label_r = self.RADIUS - 28
                lx = cx + label_r * math.cos(angle)
                ly = cy - label_r * math.sin(angle)
                painter.drawText(QRectF(lx - 14, ly - 8, 28, 16), Qt.AlignCenter, str(deg))

    def _draw_arms(self, painter: QPainter):
        colors = (QColor(220, 50, 50, 230), QColor(50, 100, 220, 230))

        for angle, color in zip((self.arm1_angle, self.arm2_angle), colors):
            end = self._arm_endpoint(angle)
            painter.setPen(QPen(color, 3))
            painter.drawLine(self.center, end)

            total = math.radians(self.base_angle + angle)
            ah = 14
            spread = math.radians(22)
            tip = end
            left = QPointF(
                tip.x() - ah * math.cos(total - spread),
                tip.y() + ah * math.sin(total - spread),
            )
            right = QPointF(
                tip.x() - ah * math.cos(total + spread),
                tip.y() + ah * math.sin(total + spread),
            )
            painter.setBrush(QBrush(color))
            painter.drawPolygon(QPolygonF([tip, left, right]))

            painter.setPen(QPen(QColor(255, 255, 255, 200), 1))
            painter.setBrush(QBrush(color.lighter(120)))
            painter.drawEllipse(end, 8, 8)

    def _draw_center_handle(self, painter: QPainter):
        painter.setPen(QPen(QColor(40, 40, 40, 220), 2))
        painter.setBrush(QBrush(QColor(255, 220, 80, 230)))
        painter.drawEllipse(self.center, 10, 10)

    def _draw_angle_label(self, painter: QPainter):
        cx, cy = self.center.x(), self.center.y()
        rect = QRectF(cx - 60, cy - self.RADIUS - 36, 120, 32)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(20, 20, 20, 200)))
        painter.drawRoundedRect(rect, 8, 8)

        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Sans Serif", 16, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, f"{self.measured_angle():.1f}°")

    def _draw_help(self, painter: QPainter):
        text = "Drag to move  |  Tips: arms  |  Arc: rotate  |  Arrows: nudge  |  Esc: quit"
        painter.setFont(QFont("Sans Serif", 8))
        painter.setPen(QPen(QColor(60, 60, 60, 180)))
        painter.drawText(QRectF(8, self.height() - 24, self.width() - 16, 18), Qt.AlignCenter, text)


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    app.setApplicationName("Checkpoint Protractor")
    app.setQuitOnLastWindowClosed(True)

    window = ProtractorWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
