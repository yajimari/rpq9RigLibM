# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

from PySide6.QtCore import (
    Qt,
    QPoint,
    QRect,
    QSize
)

from PySide6.QtWidgets import (
    QWidget,
    QLayout,
    QSizePolicy
)

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

class BaseWidget(MayaQWidgetDockableMixin, QWidget):
    _instance = None

    def __new__(cls):
        if not cls._instance is None:
            cls._instance.close()
        cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__(parent=None)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.buildUI()

    def buildUI(self):
        raise NotImplementedError('buildUI must be implemented.')
    
    def closeEvent(self, event):
        type(self)._instance = None
        super().closeEvent(event)


STRETCH_SIZE_POLICY = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)


class FlowLayout(QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []

    def __del__(self):
        while self.count():
            self.takeAt(0)

    #--- QLayout required methods
    def addItem(self, item):
        self._items.append(item)
        self.invalidate()

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if self._isValidIndex(index):
            return self._items[index]
        return None

    def takeAt(self, index):
        if self._isValidIndex(index):
            return self._items.pop(index)
        return None

    def sizeHint(self):
        return self.minimumSize()

    #--- QLayout behavior
    def expandingDirections(self):
        try:
            return Qt.Orientations(Qt.Orientation(0))
        except Exception:
            return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._doLayout(QRect(0, 0, width, 0), isSetGeometry=False)

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._doLayout(rect, isSetGeometry=True)

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())

        left, top, right, bottom = self.getContentsMargins()
        size += QSize(left + right, top + bottom)
        return size

    #--- Public utility
    def clear(self):
        while self.count():
            item = self.takeAt(0)
            if not item:
                continue

            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        self.invalidate()

    #--- Internal helpers
    def _isValidIndex(self, index):
        return 0 <= index < len(self._items)

    def _doLayout(self, rect, isSetGeometry=True):
        left, top, right, bottom = self.getContentsMargins()

        effectiveRect = rect.adjusted(left, top, -right, -bottom)

        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0

        spacing = self.spacing()
        if spacing < 0:
            spacing = 8

        for item in self._items:
            if item.isEmpty():
                continue

            itemSize = item.sizeHint()
            nextX = x + itemSize.width() + spacing

            if (nextX - spacing > effectiveRect.right() and lineHeight > 0):
                x = effectiveRect.x()
                y = y + lineHeight + spacing
                nextX = x + itemSize.width() + spacing
                lineHeight = 0

            if isSetGeometry:
                item.setGeometry(QRect(QPoint(x, y), itemSize))

            x = nextX
            lineHeight = max(lineHeight, itemSize.height())

        return y + lineHeight - rect.y() + bottom