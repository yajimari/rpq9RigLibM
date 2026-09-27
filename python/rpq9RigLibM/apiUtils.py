# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

import maya.api.OpenMaya as om2


def getDagPath(nodeName:str) -> om2.MDagPath:
    selList = om2.MSelectionList()
    selList.add(nodeName)
    return selList.getDagPath(0)


def extendToShape(dagPath:om2.MDagPath):
    if not dagPath.hasFn(om2.MFn.kTransform):
        return dagPath
    return dagPath.extendToShape()


def getNodeMObject(nodeName:str) -> om2.MObject:
    selList = om2.MSelectionList()
    selList.add(nodeName)
    return selList.getDependNode(0)