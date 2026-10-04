# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path

import maya.cmds as cmds
import maya.api.OpenMaya as om2

from rpq9RigLibM.dataManager import DataIOBase, DataPath, AssetToken


class DataIO(DataIOBase):
    FILE_EXT = '.mb'

    def description(self) -> str:
        return 'export selection'

    def getDataRootDir(self, dataPath:DataPath, assetToken:AssetToken) -> Path:
        return dataPath.getCategorySharedDataDir(assetToken) / 'selectedItem'

    def getListOfExistingData(self, dataPath:DataPath, assetToken:AssetToken) -> list[str]:
        rootPath = self.getDataRootDir(dataPath, assetToken)
        res = []
        for p in rootPath.iterdir():
            if not p.is_file():
                continue

            if p.suffix == DataIO.FILE_EXT:
                res.append(p.as_posix())
        return res

    def exportData(self, dataPath:DataPath, assetToken:AssetToken, itemName:str='', objs:list[str]|None=None, *args, **kwargs) -> None:
        if not itemName:
            result = cmds.promptDialog(
                        title='Scene File Name',
                        message='Enter Item Name:',
                        button=['OK', 'Cancel'],
                        defaultButton='OK',
                        cancelButton='Cancel',
                        dismissString='Cancel')
            if result != 'OK':
                  return None
            if text := cmds.promptDialog(q=True, text=True):
                if not DataIO.isSafeFolderName(text):
                    raise ValueError(f'"{text}" is not safe folder name.')
                itemName = text
            else:
                raise ValueError('Item Name is empty.')

        if not objs:
            objs = cmds.ls(sl=True)
        else:
            cmds.select(objs)

        savePath = self.getDataRootDir(dataPath, assetToken) / f'{itemName}{DataIO.FILE_EXT}'
        os.makedirs(savePath.parent, exist_ok=True)
        self.backup(savePath)
        cmds.file(savePath.as_posix(), exportSelected=True, type='mayaBinary', force=True, options='v=0;')
        om2.MGlobal.displayInfo(f'Export Scene: {savePath.as_posix()}')


    def importData(self, dataPath:DataPath, assetToken:AssetToken, itemName:str='', *args, **kwargs) -> None:
        loadRootPath = self.getDataRootDir(dataPath, assetToken)
        if not itemName:
            itemNames = []
            for p in loadRootPath.iterdir():
                if not p.is_file():
                    continue
                if p.suffix == DataIO.FILE_EXT:
                    itemNames.append(p.stem)

            if not itemNames:
                raise RuntimeError('Not found scene file.')

            if len(itemNames) >= 2:
                dialogRes = cmds.layoutDialog(ui=lambda *args: DataIO.selectGroupUI(itemNames))
                if dialogRes == 'dismiss':
                    return None
                itemName = dialogRes
            else:
                itemName = itemNames[0]

        loadPath = loadRootPath / f'{itemName}{DataIO.FILE_EXT}'
        if not loadPath.is_file():
            om2.MGlobal.displayError(f'Not found file: {loadPath.as_posix()}')
            return None
        cmds.file(loadPath.as_posix(), i=True)
        om2.MGlobal.displayInfo(f'Import Scene: {loadPath.as_posix()}')


    @staticmethod
    def selectGroupUI(items:list[str]):
        form = cmds.setParent(q=True)

        optionMenu = cmds.optionMenuGrp(l='Select Item Name:', ad2=2)
        for item in items:
            cmds.menuItem(label=item)

        button = cmds.button(l='OK', c=lambda *args: cmds.layoutDialog( dismiss=cmds.optionMenuGrp(optionMenu, q=True, v=True)))

        cmds.formLayout(form, e=True,
                        af=[
                            [optionMenu, 'top', 10],
                            [optionMenu, 'left', 0],
                            [optionMenu, 'right', 0],
                            [button, 'left', 0],
                            [button, 'right', 0],
                            [button, 'bottom', 0],
                            ],
                        ac = [[button, 'top', 10, optionMenu]],
                        an = [[optionMenu, 'bottom']]
                    )