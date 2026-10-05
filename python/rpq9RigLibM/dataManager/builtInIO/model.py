# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path

import maya.cmds as cmds
import maya.api.OpenMaya as om2

from rpq9RigLibM.dataManager import DataIOBase, DataPath, AssetToken


class DataIO(DataIOBase):
    def description(self) -> str:
        return 'selection model IO'

    def getFilePath(self, dataPath:DataPath, assetToken:AssetToken) -> Path:
        return dataPath.getTargetDataDir(assetToken) / 'model' / f'{assetToken.name}_{assetToken.target}_geo.mb'

    def getListOfExistingData(self, dataPath:DataPath, assetToken:AssetToken) -> list[str]:
        return [self.getFilePath(dataPath, assetToken).as_posix()] if self.getFilePath(dataPath, assetToken).is_file() else []

    def exportData(self, dataPath:DataPath, assetToken:AssetToken, objs:list[str]|None=None, *args, **kwargs) -> None:
        kwargs = {
            'force': True,
            'options': 'v=0;',
            'type': 'mayaBinary',
        }

        if not objs:
            objs = cmds.ls(sl=True)

        if objs:
            kwargs['exportSelected'] = True
            cmds.select(objs)
        else:
            kwargs['exportAll'] = True

        savePath = self.getFilePath(dataPath, assetToken)
        os.makedirs(savePath.parent, exist_ok=True)
        self.backup(savePath)

        cmds.file(savePath.as_posix(), **kwargs)
        om2.MGlobal.displayInfo(f'Export Model: {savePath.as_posix()}')


    def importData(self, dataPath:DataPath, assetToken:AssetToken, *args, **kwargs) -> None:
        loadPath = self.getFilePath(dataPath, assetToken)
        if not loadPath.is_file():
            raise FileNotFoundError(f'Not found file: {loadPath.as_posix()}')

        cmds.file(loadPath.as_posix(), i=True)
        om2.MGlobal.displayInfo(f'Import Model: {loadPath.as_posix()}')