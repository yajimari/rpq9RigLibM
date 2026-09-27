# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

import maya.api.OpenMaya as om2

from .apiUtils import getDagPath


def getBoundingBox(node:str) -> om2.MBoundingBox:
    mfn = om2.MFnDagNode(getDagPath(node))
    return mfn.boundingBox