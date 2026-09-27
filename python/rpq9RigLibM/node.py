# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

from typing import Any
import maya.cmds as cmds


def getNodesFromObjectSet(objectSet:str, nodeTypes:set[str]) -> set[str]:
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
            res |= getNodesFromObjectSet(node, nodeTypes)
        if nodeType in nodeTypes:
            res.add(node)
    return res