# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

import os
import re
import inspect
from pathlib import Path
import shutil
from abc import ABC, abstractmethod
from typing import Type
from collections.abc import Callable
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction

import maya.api.OpenMaya as om2

from .path import DataPath, AssetToken
from ..moduleLoader import dynamicLoadModule


BUILT_IN_MODULE_PATH = Path(__file__).parent.joinpath('builtInIO').as_posix()

DATA_IO_MODULE_ENV_KEY = 'RPQ9_RIGLIBM_DATA_IO_MODULE_PATH'

MODULE_EXTENSIONS = {'.py', '.pyd', '.so'}

_classesCache = {'built_in': {}, 'custom': {}}


class DataIOBase(ABC):
    def description(self) -> str:
        return ''

    def color(self) -> list[int]:
        return[30, 30, 30]

    def isHideGUI(self) -> bool:
        return False

    def customImportButtonContextMenu(self, menu:QMenu) -> list[tuple[QAction, Callable[[QAction, DataPath, AssetToken], None]]]:
        return []

    def customExportButtonContextMenu(self, menu:QMenu) -> list[tuple[QAction, Callable[[QAction, DataPath, AssetToken], None]]]:
        return []

    def getListOfExistingData(self, dataPath:DataPath, assetToken:AssetToken) -> list[str]:
        raise NotImplementedError()

    @abstractmethod
    def exportData(self, dataPath:DataPath, assetToken:AssetToken, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def importData(self, dataPath:DataPath, assetToken:AssetToken, *args, **kwargs) -> None:
        pass

    def backup(self, path:Path) -> str:
        if not path.exists():
            return ''

        rootDir = path.parent
        stem = path.stem
        suffix = path.suffix

        backupDir = rootDir / '_bk'
        os.makedirs(backupDir, exist_ok=True)

        pattern = f'{stem}.bk[0-9][0-9][0-9][0-9]*'
        regex = re.compile(rf"^{re.escape(stem)}\.bk(\d{{4}})(?:\..+)?$")

        numbers = []
        for path in backupDir.glob(pattern):
            match = regex.match(path.name)
            if match:
                numbers.append(int(match.group(1)))

        nextNumber = max(numbers, default=-1) + 1
        nextBk = f'{nextNumber:04d}'

        dstPath = backupDir / f'{stem}.bk{nextNumber:04d}{suffix}'

        if path.is_file():
            shutil.copy2(path, dstPath)
        else:
            shutil.copytree(path, dstPath, dirs_exist_ok=True)

        return path.as_posix()

    _WINDOWS_RESERVED_NAMES = {
        'CON', 'PRN', 'AUX', 'NUL',
        *(f'COM{i}' for i in range(1, 10)),
        *(f'LPT{i}' for i in range(1, 10)),
    }
    _INVALID_CHARS = re.compile(r'[<>:"/\\|?*\0]')

    @classmethod
    def isSafeFolderName(cls, name: str) -> bool:
        if not name:
            return False

        if name in {".", ".."}:
            return False

        # Windows prohibited characters + NUL and / which cannot be used in Linux
        if cls._INVALID_CHARS.search(name):
            return False

        # In Windows, trailing spaces and dots are not allowed.
        if name.endswith((' ', '.')):
            return False

        baseName = name.split('.')[0].upper()
        if baseName in cls._WINDOWS_RESERVED_NAMES:
            return False

        # Many file systems have a limit of 255 bytes per element.
        # Check in UTF-8 conversion.
        if len(name.encode('utf-8')) > 255:
            return False
        return True



def _loadDataIOClasses(rootDir:Path) -> dict[str, Type[DataIOBase]]:
    if not rootDir.is_dir():
        raise FileNotFoundError(f'"{rootDir.as_posix()}" is not dir.')

    res = {}
    for filePath in rootDir.iterdir():
        if not filePath.is_file():
            continue

        if not filePath.suffix in MODULE_EXTENSIONS:
            continue

        if filePath.name.startswith("_"):
            continue

        try:
            module = dynamicLoadModule(filePath)
            attr = getattr(module, 'DataIO', None)
            if not inspect.isclass(attr) or not issubclass(attr, DataIOBase):
                raise RuntimeError('The subclass DataIO could not be found for DataIOBase.')

            instance = attr()
            res[module.__name__] = instance

        except Exception as e:
            om2.MGlobal.displayWarning(f'Faild import {filePath.name}: {e}')

    return res


def reloadDataIOClasses():
    _classesCache['built_in'] = _loadDataIOClasses(Path(BUILT_IN_MODULE_PATH))
    _classesCache['custom'] = {}

    envvarval = os.environ.get(DATA_IO_MODULE_ENV_KEY, '')
    for path in envvarval.split(os.pathsep):
        if not path or not os.path.exists(path):
            continue

        currentData = _loadDataIOClasses(Path(path))
        commonKeys = _classesCache['custom'].keys() & currentData.keys()
        if commonKeys:
            om2.MGlobal.displayWarning(f'The module name is clashing: {commonKeys}(This module will be overwritten.)')
        _classesCache['custom'].update(currentData)


def getDataIOClasses(reload:bool=True):
    if not _classesCache['built_in'] or reload:
        reloadDataIOClasses()
    return _classesCache


def getBuiltInClass(name:str):
    data = getDataIOClasses()
    return data['built_in'].get(name, None)


def getCustomClass(name:str):
    data = getDataIOClasses()
    return data['custom'].get(name, None)