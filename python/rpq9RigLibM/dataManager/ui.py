# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

import os

from PySide6.QtCore import  Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStyle,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget
)

from PySide6.QtGui import (
    QAction,
    QKeySequence,
    QTextOption
)

import maya.api.OpenMaya as om2
from maya.internal.common.utils.ui import makeUndoable

from ..ui import BaseWidget, STRETCH_SIZE_POLICY, FlowLayout
from .dataIO import getDataIOClasses
from .path import DataPath, AssetToken


RIG_DATA_DIR_KEY = 'RPQ9_RIGLIBM_DATA_PATH'



#***************************************
# NewAssetDialog
#***************************************
class NewAssetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.buildUI()
        self.updateAssets()
        self._connect_signals()


    def buildUI(self):
        self.setWindowTitle('New Asset')
        rootLayout = QVBoxLayout(self)

        formLayout = QFormLayout()
        formLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.categoryCombo = QComboBox()
        self.nameCombo = QComboBox()
        self.targetCombo = QComboBox()

        self.categoryCombo.setEditable(True)
        self.nameCombo.setEditable(True)
        self.targetCombo.setEditable(True)

        self.categoryCombo.setInsertPolicy(QComboBox.NoInsert)
        self.nameCombo.setInsertPolicy(QComboBox.NoInsert)
        self.targetCombo.setInsertPolicy(QComboBox.NoInsert)

        formLayout.addRow('Category', self.categoryCombo)
        formLayout.addRow('Name', self.nameCombo)
        formLayout.addRow('Target', self.targetCombo)
        rootLayout.addLayout(formLayout)

        rootLayout.addStretch()
        self.createButton = QPushButton("Create")
        rootLayout.addWidget(self.createButton)


    def _connect_signals(self):
        self.categoryCombo.currentTextChanged.connect(lambda *args: self.updateNameCombo())
        self.nameCombo.currentTextChanged.connect(lambda *args: self.updateTargetCombo())
        self.createButton.clicked.connect(lambda *args: self.accept())


    def updateTargetCombo(self) -> None:
        self.targetCombo.clear()
        currentCategory = self.categoryCombo.currentText()
        currentName = self.nameCombo.currentText()
        if not currentCategory or not currentName:
            return

        names = self.dataPath.listTarget(AssetToken(currentCategory, currentName))
        self.targetCombo.addItems(names)


    def updateNameCombo(self) -> None:
        self.nameCombo.clear()
        currentCategory = self.categoryCombo.currentText()
        if not currentCategory:
            return

        names = self.dataPath.listName(AssetToken(currentCategory))
        self.nameCombo.addItems(names)
        self.updateTargetCombo()


    def updateAssets(self) -> None:
        envvarval = os.environ.get(RIG_DATA_DIR_KEY, '')
        if not envvarval or not os.path.isdir(envvarval):
            raise RuntimeError(f'A valid file path has not been set for "{RIG_DATA_DIR_KEY}".')

        self.dataPath = DataPath(envvarval)

        self.categoryCombo.clear()
        categories = self.dataPath.listCategory()
        self.categoryCombo.addItems(categories)
        self.updateNameCombo()


    def getAssetToken(self):
        currentCategory = self.categoryCombo.currentText()
        currentName = self.nameCombo.currentText()
        currentTarget = self.targetCombo.currentText()
        return AssetToken(currentCategory, currentName, currentTarget)



#***************************************
# MainUI
#***************************************
class MainUI(BaseWidget):
    CARD_WIDTH = 170
    CARD_HEIGHT = 220

    def buildUI(self):
        self.setWindowTitle('rpq9 dataManager')

        self.dataPath = None
        self.dataIOClasses = {}

        rootLayout = QVBoxLayout(self)
        rootLayout.setContentsMargins(0, 0, 0, 0)

        #--- menu
        self.menuBar = QMenuBar()
        self.menuBar.setNativeMenuBar(False)

        assetMenu = self.menuBar.addMenu('Asset')
        self.newAssetAction = QAction('Add New Asset',  self)
        self.newAssetAction.setShortcut(QKeySequence.StandardKey.New)
        assetMenu.addAction(self.newAssetAction)

        assetMenu.addSeparator()

        self.updateDataDirAction = QAction('Update Data Dir',  self)
        assetMenu.addAction(self.updateDataDirAction)

        dataIOMenu = self.menuBar.addMenu('Data IO')
        self.reloadDataIOAction = QAction('Reload Data IO',  self)
        dataIOMenu.addAction(self.reloadDataIOAction)

        dataIOMenu.addSeparator()

        self.showBuiltinAction = QAction('Show Builtin',  self)
        dataIOMenu.addAction(self.showBuiltinAction)
        self.showBuiltinAction.setCheckable(True)
        self.showBuiltinAction.setChecked(True)
        rootLayout.addWidget(self.menuBar)
        #---

        #--- asset token
        assetGroup = QGroupBox('Asset')
        tokenLayout = QHBoxLayout(assetGroup)

        self.categoryCombo = QComboBox()
        self.nameCombo = QComboBox()
        self.targetCombo = QComboBox()

        tokenLayout.addWidget(QLabel('Category'), 0)
        tokenLayout.addWidget(self.categoryCombo, 1)
        tokenLayout.addWidget(QLabel('Name'), 0)
        tokenLayout.addWidget(self.nameCombo, 1)
        tokenLayout.addWidget(QLabel('Target'), 0)
        tokenLayout.addWidget(self.targetCombo, 1)
        tokenLayout.addSpacing(5)

        self.reloadButton = QToolButton()
        icon = self.style().standardIcon(QStyle.SP_BrowserReload)
        self.reloadButton.setIcon(icon)
        tokenLayout.addWidget(self.reloadButton, 0)

        rootLayout.addWidget(assetGroup)
        #---

        #--- data io
        dataIOGroup = QGroupBox('Data IO')
        dataIOLayout = QVBoxLayout(dataIOGroup)

        self.dataIOScrollArea = QScrollArea()
        self.dataIOScrollArea.setWidgetResizable(True)
        self.dataIOScrollArea.setFrameShape(QFrame.NoFrame)
        self.dataIOScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.dataIOScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.dataIOScrollWidget = QWidget()
        self.dataIOScrollWidget.setSizePolicy(STRETCH_SIZE_POLICY)

        self.dataIOFlowLayout = FlowLayout()
        self.dataIOFlowLayout.setContentsMargins(2, 2, 2, 2)
        self.dataIOFlowLayout.setSpacing(8)
        self.dataIOFlowLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)

        self.dataIOScrollWidget.setLayout(self.dataIOFlowLayout)
        self.dataIOScrollArea.setWidget(self.dataIOScrollWidget)
        dataIOLayout.addWidget(self.dataIOScrollArea)

        rootLayout.addWidget(dataIOGroup, 1)
        #---

        self._connectSignals()

        self.updateAssets()
        self.updateDataIOClasses()


    def _connectSignals(self):
        self.newAssetAction.triggered.connect(lambda *args: self.showNewAssetDialog())
        self.updateDataDirAction.triggered.connect(lambda *args: self.updateAssets())

        self.reloadDataIOAction.triggered.connect(lambda *args: self.updateDataIOClasses(reload=True, showBuiltin=self.showBuiltinAction.isChecked()))
        self.showBuiltinAction.toggled.connect(lambda checked: self.updateDataIOClasses(showBuiltin=checked))

        self.categoryCombo.currentIndexChanged.connect(lambda *args: self.updateNameCombo())
        self.nameCombo.currentIndexChanged.connect(lambda *args: self.updateTargetCombo())
        
        self.reloadButton.clicked.connect(lambda *args: self.updateAssets())


    def updateTargetCombo(self) -> None:
        self.targetCombo.clear()
        currentCategory = self.categoryCombo.currentText()
        currentName = self.nameCombo.currentText()
        if not currentCategory or not currentName:
            return

        names = self.dataPath.listTarget(AssetToken(currentCategory, currentName))
        self.targetCombo.addItems(names)


    def updateNameCombo(self) -> None:
        self.nameCombo.clear()
        currentCategory = self.categoryCombo.currentText()
        if not currentCategory:
            return

        names = self.dataPath.listName(AssetToken(currentCategory))
        self.nameCombo.addItems(names)
        self.updateTargetCombo()


    def updateAssets(self) -> None:
        envvarval = os.environ.get(RIG_DATA_DIR_KEY, '')
        if not envvarval or not os.path.isdir(envvarval):
            raise RuntimeError(f'A valid file path has not been set for "{RIG_DATA_DIR_KEY}".')

        self.dataPath = DataPath(envvarval)

        self.categoryCombo.clear()
        categories = self.dataPath.listCategory()
        self.categoryCombo.addItems(categories)
        self.updateNameCombo()


    def createIOCard(self, name, ioIns, isBuiltIn:bool=True):
        card = QFrame()
        card.setObjectName('DataIOCard')
        card.setFrameShape(QFrame.StyledPanel)
        card.setFrameShadow(QFrame.Raised)

        card.setFixedSize(self.CARD_WIDTH, self.CARD_HEIGHT)

        if isBuiltIn:
            styleSheet = '''
                            QFrame#DataIOCard {
                                border: 1px solid rgb(0, 96, 105);
                                border-radius: 6px;
                                background-color: rgb(30, 30, 30);
                            }
                        '''
        else:
            color = ioIns.color()
            styleSheet ='''QFrame#DataIOCard {
                                border: 1px solid rgb('''
            styleSheet += f'{color[0]}, {color[1]}, {color[2]}'
            styleSheet += ''');
                border-radius: 6px;
                background-color: rgb('''
            styleSheet += f'{color[0]}, {color[1]}, {color[2]});'
            styleSheet +='}'

        styleSheet +='''
            QLabel#IONameLabel {
                font-weight: bold;
                font-size: 15px;
            }
        '''
        card.setStyleSheet(styleSheet)

        layout = QVBoxLayout(card)
        headerLayout = QHBoxLayout()
        headerLayout.setContentsMargins(0, 0, 0, 0)
        nameLabel = QLabel(name)
        nameLabel.setObjectName('IONameLabel')

        headerLayout.addWidget(nameLabel)
        headerLayout.addStretch()
        layout.addLayout(headerLayout, 0)

        description = ioIns.description()
        if not description:
            description = 'No description.'

        descriptionTextEdit = QTextEdit()
        descriptionTextEdit.setPlainText(description)
        descriptionTextEdit.setWordWrapMode(QTextOption.WrapMode.WrapAnywhere)
        descriptionTextEdit.setReadOnly(True)
        layout.addWidget(descriptionTextEdit, 1)

        buttonLayout = QHBoxLayout()
        buttonLayout.setContentsMargins(0, 0, 0, 0)
        importButton = QPushButton('Import')
        exportButton = QPushButton('Export')

        importButton.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        importButton.customContextMenuRequested.connect(lambda point, button=importButton, ioIns=ioIns, **kwargs: self.showImportButtonContextMenu(pos=point, button=button, ioIns=ioIns))

        exportButton.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        exportButton.customContextMenuRequested.connect(lambda point, button=exportButton, ioIns=ioIns, **kwargs: self.showExportButtonContextMenu(pos=point, button=button, ioIns=ioIns))

        importButton.clicked.connect(lambda *args: makeUndoable(lambda *args: ioIns.importData(self.dataPath, self.getAssetToken()))())
        exportButton.clicked.connect(lambda *args: makeUndoable(lambda *args: ioIns.exportData(self.dataPath, self.getAssetToken()))())

        buttonLayout.addWidget(importButton)
        buttonLayout.addWidget(exportButton)

        layout.addLayout(buttonLayout, 0)

        return card


    def showImportButtonContextMenu(self, pos, button, ioIns):
        menu = QMenu(self)
        showExistingDataAction = menu.addAction('Show Existing Data')
        menu.addSeparator()
        customMenuData = ioIns.customImportButtonContextMenu(menu)

        selected = menu.exec(button.mapToGlobal(pos))

        if selected == showExistingDataAction:
            dataList = ioIns.getListOfExistingData(self.dataPath, self.getAssetToken())
            for d in dataList:
                om2.MGlobal.displayInfo(d)

        else:
            for action, func in customMenuData:
                if selected == action:
                    func(action, self.dataPath, self.getAssetToken())
                    break


    def showExportButtonContextMenu(self, pos, button, ioIns):
        menu = QMenu(self)
        customMenuData = ioIns.customExportButtonContextMenu(menu)

        selected = menu.exec(button.mapToGlobal(pos))

        for action, func in customMenuData:
            if selected == action:
                func(action, self.dataPath, self.getAssetToken())
                break


    def updateDataIOClasses(self, reload:bool=False, showBuiltin:bool=True):
        self.dataIOClasses = getDataIOClasses(reload)
        self.dataIOFlowLayout.clear()

        if showBuiltin:
            for name, ioIns in self.dataIOClasses['built_in'].items():
                if ioIns.isHideGUI():
                    continue
                card = self.createIOCard(name, ioIns, True)
                self.dataIOFlowLayout.addWidget(card)

        for name, ioIns in self.dataIOClasses['custom'].items():
            if ioIns.isHideGUI():
                continue
            card = self.createIOCard(name, ioIns, False)
            self.dataIOFlowLayout.addWidget(card)

        self.dataIOFlowLayout.invalidate()
        self.dataIOScrollWidget.updateGeometry()


    def getAssetToken(self):
        currentCategory = self.categoryCombo.currentText()
        currentName = self.nameCombo.currentText()
        currentTarget = self.targetCombo.currentText()
        return AssetToken(currentCategory, currentName, currentTarget)


    def showNewAssetDialog(self):
        dialog = NewAssetDialog(parent=self)
        dialogResult = dialog.exec()
        if dialogResult != QDialog.Accepted:
            return

        assetToken = dialog.getAssetToken()
        if not isValidToken(assetToken.category):
            raise RuntimeError(f'"{assetToken.category}" is invalid token.')

        if not isValidToken(assetToken.name):
            raise RuntimeError(f'"{assetToken.name}" is invalid token.')

        if not isValidToken(assetToken.target):
            raise RuntimeError(f'"{assetToken.target}" is invalid token.')

        asset_path = self.dataPath.createAssetDirectory(assetToken)
        self.updateAssets()
        QMessageBox.information(self, 'Info', f'Created asset dir: {assetToken.category} / {assetToken.name} / {assetToken.target}')



def isValidToken(value):
    invalidChars = ('\\', '/', ':', '*', '?', '\'', '<', '>', '|', ' ', '.', ',', '+', '-')
    return all(char not in invalidChars for char in value)