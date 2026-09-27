# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

import importlib
from pathlib import Path


def dynamicLoadModule(filePath:Path):
    module_name = filePath.stem

    spec = importlib.util.spec_from_file_location(module_name, filePath)
    if spec is None or spec.loader is None:
        raise ImportError(f'Failed to create module information: {filePath.as_posix()}')

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module