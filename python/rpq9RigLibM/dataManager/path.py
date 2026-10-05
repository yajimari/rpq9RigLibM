# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import dataclasses

from ..file import createFolders


@dataclasses.dataclass
class AssetToken:
    category: str = ''
    name: str = ''
    target: str = ''

    def hasAllData(self) -> bool:
        return all([self.category, self.name, self.target])


class DataPath:
    def __init__(self, rootPath:str|Path):
        pathObj = Path(rootPath)
        if not pathObj.is_dir():
            raise FileNotFoundError(f'"{pathObj.as_posix()}" does not exist dir.')

        self._rootPath = pathObj.resolve()

    #---
    def getRootDir(self) -> Path:
        return self._rootPath

    def getRootSharedDir(self) -> Path:
        return self.getRootDir() / '_shared'

    def getRootSharedDataDir(self) -> Path:
        return self.getRootSharedDir() / 'data'

    #--- category
    def getCategoryDir(self, token:AssetToken) -> Path:
        if not token.category:
            raise ValueError(f'token.category is default.')

        return self.getRootDir() / token.category

    def getCategorySharedDir(self, token:AssetToken) -> Path:
        return self.getCategoryDir(token) / '_shared'

    def getCategorySharedDataDir(self, token:AssetToken) -> Path:
        return self.getCategorySharedDir(token) / 'data'

    def listCategory(self) -> list[str]:
        res = []
        if self.getRootDir().is_dir():
            for child in self.getRootDir().iterdir():
                if child.is_dir() and not child.name.startswith('_'):
                    res.append(child.name)
        return res

    #--- name
    def getNameDir(self, token:AssetToken) -> Path:
        if not token.name:
            raise ValueError(f'token.name is default.')
        return self.getCategoryDir(token) / token.name

    def getNameSharedDir(self, token:AssetToken) -> Path:
        return self.getNameDir(token) / '_shared'

    def getNameSharedDataDir(self, token:AssetToken) -> Path:
        return self.getNameSharedDir(token) / 'data'

    def listName(self, token:AssetToken) -> list[str]:
        res = []
        if self.getCategoryDir(token).is_dir():
            for child in self.getCategoryDir(token).iterdir():
                if child.is_dir() and not child.name.startswith('_'):
                    res.append(child.name)
        return res

    #--- target
    def getTargetDir(self, token:AssetToken) -> Path:
        if not token.target:
            raise ValueError(f'token.target is default.')
        return self.getNameDir(token) / token.target

    def getTargetDataDir(self, token:AssetToken) -> Path:
        return self.getTargetDir(token) / 'data'

    def listTarget(self, token:AssetToken) -> list[str]:
        res = []
        if self.getNameDir(token).is_dir():
            for child in self.getNameDir(token).iterdir():
                if child.is_dir() and not child.name.startswith('_'):
                    res.append(child.name)
        return res

    #---
    def getAssetTokenFromPath(self, path:str|Path) -> AssetToken:
        pathObj = Path(path)
        relativePathObj = pathObj.relative_to(self.getRootDir())

        token = {key : value for key, value in zip([field.name for field in dataclasses.fields(AssetToken)], relativePathObj.parts)}
        return AssetToken(**token)

    # create folder
    def createAssetDirectory(self, assetToken:AssetToken):
        if not assetToken.hasAllData():
            raise ValueError('Some elements in "AssetToken" have no value.')

        rootDir = self.getRootDir()
        category = assetToken.category
        name = assetToken.name
        target = assetToken.target

        createFolders(rootDir, ['_shared', category])
        createFolders(rootDir/'_shared', ['data'])
        createFolders(rootDir/category, ['_shared', name])
        createFolders(rootDir/category/'_shared', ['data'])
        createFolders(rootDir/category/name, ['_shared', target])
        createFolders(rootDir/category/name/'_shared', ['data'])
        createFolders(rootDir/category/name/target, ['data'])