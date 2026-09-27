# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

import maya.cmds as cmds
import maya.api.OpenMaya as om2

from .dataTypes import DependencyNode


def _buildNodeData(nodeTypes:set[str]) -> dict[str, DependencyNode]:
    nodeData = {}

    iter = om2.MItDependencyNodes()
    while not iter.isDone():
        mobj = iter.thisNode()
        if mobj.hasFn(om2.MFn.kDagNode):
            iter.next()
            continue

        dependObj = DependencyNode(mobj)
        if dependObj.isFromReferencedFile:
            iter.next()
            continue

        typeName = dependObj.typeName
        if not typeName in nodeTypes:
            iter.next()
            continue

        if not typeName in nodeData:
            nodeData[dependObj.typeName] = []

        nodeData[dependObj.typeName].append(dependObj)
        iter.next()

    return nodeData


def _evaluteSamePurposeNode(currentData:dict[str, list[DependencyNode]], updatedData:dict[str, list[DependencyNode]]) -> list[DependencyNode]:
    removeNodes = []
    for nodeType, nodes in currentData.items():
        updatedData[nodeType] = []

        for node in nodes:
            isCrash = False
            for keepObj in updatedData[nodeType]:
                if node.dependEqual(keepObj):
                    isCrash = True
                    node.swapOutputs(keepObj)
                    break
            if isCrash:
                removeNodes.append(node)
            else:
                updatedData[nodeType].append(node)

    return removeNodes



def mergeSamePurposeNodes(nodeTypes:set[str], maxIteration:int=10, verbose:bool=False) -> int:
    '''
    Overview:
        Merge nodes with the same purpose on the DG.

    Args:
        nodeTypes    (set[str]): node type for merge.
        maxIteration (int): Maximum number of iterations to check whether nodes have the same purpose. Defaults to 10.
        verbose     (bool): If true, the names of deleted nodes are output. Defaults to False.

    Return:
        removeNum (int): remove node number.
    '''
    removeNodes = []
    nodeData = _buildNodeData(nodeTypes)

    for _ in range(maxIteration):
        updatedData = {}
        currentRemoveNodes = _evaluteSamePurposeNode(nodeData, updatedData)
        nodeData = updatedData
        isUpdatedByFainalIteration = bool(len(currentRemoveNodes))

        removeNodes += currentRemoveNodes
        if not isUpdatedByFainalIteration:
            break

    removeNodeNames = [node.name() for node in removeNodes]
    removeNum = len(removeNodeNames)
    if removeNum:
        cmds.delete(*removeNodeNames)

    if verbose:
        for node in removeNodeNames:
            om2.MGlobal.displayInfo(f'Delete "{node}".')
        
    if isUpdatedByFainalIteration:
        om2.MGlobal.displayWarning('There was also an update in the last iteration.')

    return removeNum


def removeUnusedInfluences():
    nodes = cmds.ls(type='skinCluster')
    for node in nodes:
        cmds.skinCluster(node, e=True, rui=True)