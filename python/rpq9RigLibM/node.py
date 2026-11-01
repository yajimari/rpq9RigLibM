# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
import csv

import maya.cmds as cmds


def getNodesFromObjectSetRecursive(objectSet:str, nodeTypes:set[str]) -> set[str]:
    '''
    Overview:
        Retrieves all nodes of the specified type within the objectSet.

    Args:
        objectSet    (str): objectSet name.
        nodeTypes    (set[str]): get node types.

    Return:
        nodes (set[str]): node names.
    '''
    setObjs = cmds.sets(objectSet, q=True)
    res = set()
    for node in setObjs:
        nodeType = cmds.nodeType(node)
        if nodeType == 'objectSets':
            res |= getNodesFromObjectSetRecursive(node, nodeTypes)
        if nodeType in nodeTypes:
            res.add(node)
    return res


def listDGNodeTypes() -> set[str]:
    allTypes = set(cmds.allNodeTypes())
    dagTypes = set(cmds.nodeType('dagNode', derived=True, isTypeName=True))
    return allTypes - dagTypes