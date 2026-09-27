# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path



def createFolders(rootPath:Path, folders:list[str]):
    for folder in folders:
        os.makedirs(rootPath/folder, exist_ok=True)