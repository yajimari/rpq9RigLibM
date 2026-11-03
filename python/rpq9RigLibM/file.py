# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path
import configparser

import maya.cmds as cmds


def createFolders(rootPath:Path, folders:list[str]):
    for folder in folders:
        os.makedirs(rootPath/folder, exist_ok=True)



class ConfigManager:
    _ins = None
    _UNSET = object()

    def __new__(cls):
        if cls._ins is None:
            cls._ins = super().__new__(cls)
        return cls._ins


    def __init__(self):
        self._file_path = ConfigManager.getFilePath()
        self._config = configparser.ConfigParser()
        self.reload()


    @staticmethod
    def getFilePath():
        appDir = Path(cmds.internalVar(userAppDir=True))
        configPath = appDir / 'rpq9RigLibM_config.ini'
        return configPath


    def reload(self) -> None:
        config = configparser.ConfigParser()
        loaded = config.read(self._file_path, encoding='utf-8')

        if loaded:
            self._config = config


    def write(self):
        with open(self._file_path, 'w', encoding='utf-8') as f:
            self._config.write(f)


    def defaults(self):
        return self._config.defaults()

    def sections(self):
        return self._config.sections()

    def add_section(self, section):
        return self._config.add_section(section)

    def has_section(self, section):
        return self._config.has_section(section)

    def options(self, section):
        return self._config.options(section)

    def has_option(self, section, option):
        return self._config.has_option(section, option)

    def get(self, section, option, *, raw=False, vars=None, fallback=_UNSET):
        if fallback is ConfigManager._UNSET:
            return self._config.get(section, option, raw=raw, vars=vars)
        else:
            return self._config.get(section, option, raw=raw, vars=vars, fallback=fallback)

    def getint(self, section, option, *, raw=False, vars=None, fallback=_UNSET):
        if fallback is ConfigManager._UNSET:
            return self._config.getint(section, option, raw=raw, vars=vars)
        else:
            return self._config.getint(section, option, raw=raw, vars=vars, fallback=fallback)

    def getfloat(self, section, option, *, raw=False, vars=None, fallback=_UNSET):
        if fallback is ConfigManager._UNSET:
            return self._config.getfloat(section, option, raw=raw, vars=vars)
        else:
            return self._config.getfloat(section, option, raw=raw, vars=vars, fallback=fallback)

    def getboolean(self, section, option, *, raw=False, vars=None, fallback=_UNSET):
        if fallback is ConfigManager._UNSET:
            return self._config.getboolean(section, option, raw=raw, vars=vars)
        else:
            return self._config.getboolean(section, option, raw=raw, vars=vars, fallback=fallback)

    def items(self, section=_UNSET, raw=False, vars=None):
        if section is ConfigManager._UNSET:
            return self._config.items(raw=raw, vars=vars)
        else:
            return self._config.items(section, raw=raw, vars=vars)

    def set(self, section, option, value):
        return self._config.set(section, option, value)

    def remove_option(self, section, option):
        return self._config.remove_option(section, option)

    def remove_section(self, section):
        return self._config.remove_section(section)