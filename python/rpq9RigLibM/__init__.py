# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

from . import attribute, cleanup, dataTypes, moduleLoader, node, optimize, shapeEditorManager, dataManager

showDataManager = lambda *args, **kwargs: dataManager.MainUI().show(*args, **kwargs)