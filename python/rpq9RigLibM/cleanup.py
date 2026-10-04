# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

import maya.cmds as cmds
import maya.api.OpenMaya as om2


def deleteMayaNodeEditorSavedTabsInfo():
    node = cmds.ls('MayaNodeEditorSavedTabsInfo')
    if node:
        connected_attr = cmds.listConnections('MayaNodeEditorSavedTabsInfo', p=True, c=True)
        if connected_attr:
            for i in range(0, len(connected_attr), 2):
                cmds.disconnectAttr(connected_attr[i+1], connected_attr[i])
        cmds.delete('MayaNodeEditorSavedTabsInfo')


def cleanupSkinClusterName():
    skinClusters = cmds.ls(type='skinCluster')
    for node in skinClusters:
        bindObjectShape = cmds.skinCluster(node, q=True, g=True)[0]
        bindObject = cmds.listRelatives(bindObjectShape, p=True)[0]
        cmds.rename(node, f'{bindObject}_skinCluster')


DEFAULT_HIDE_DEPENDENCY_NODES = {
                    'sum',
                    'subtract',
                    'multiply',
                    'divide',
                    'addDoubleLinear',
                    'multDoubleLinear',
                    'addDL',
                    'plusMinusAverage',

                    'addMatrix',
                    'aiFloatToMatrix',
                    'aiMatrixInterpolate',
                    'aiMatrixMultiplyVector',
                    'aiMatrixTransform',
                    'aimMatrix',
                    'axisFromMatrix',
                    'blendMatrix',
                    'columnFromMatrix',
                    'composeMatrix',
                    'decomposeMatrix',
                    'fourByFourMatrix',
                    'holdMatrix',
                    'inverseMatrix',
                    'multMatrix',
                    'parentMatrix',
                    'passMatrix',
                    'pickMatrix',
                    'rotationFromMatrix',
                    'rowFromMatrix',
                    'scaleFromMatrix',
                    'translationFromMatrix',
                    'transposeMatrix',
                    'wtAddMatrix',
                    'determinant',

                    'quatAdd',
                    'quatConjugate',
                    'quatInvert',
                    'quatNegate',
                    'quatNormalize',
                    'quatProd',
                    'quatSlerp',
                    'quatSub',
                    'quatToAxisAngle',
                    'quatToEuler',
                    'axisAngleToQuat',
                    'eulerToQuat',

                    'sin',
                    'cos',
                    'tan',
                    'asin',
                    'acos',
                    'atan',
                    'atan2',

                    'pointMatrixMult',
                    'multiplyPointByMatrix',
                    'multiplyVectorByMatrix',
                    'dotProduct',
                    'crossProduct',
                    'distanceBetween',
                    'angleBetween',
                    'rotateVector'
                    'aimConstraint',
                    'dynamicConstraint',
                    'geometryConstraint',
                    'hairConstraint',
                    'normalConstraint',
                    'oldGeometryConstraint',
                    'oldNormalConstraint',
                    'oldTangentConstraint',
                    'orientConstraint',
                    'parentConstraint',
                    'pointConstraint',
                    'pointOnPolyConstraint',
                    'poleVectorConstraint',
                    'rigidConstraint',
                    'scaleConstraint',
                    'symmetryConstraint',
                    'tangentConstraint',

                    'nurbsCurve',
                    'nurbsSurface',
                    'absolute',
                    'log',
                    'pi',
                    'max',
                    'power',
                    'and',
                    'equal',
                    'min',
                    'round',
                    'floor',
                    'modulo',
                    'greaterThan',
                    'inverseLerp',
                    'negate',
                    'smoothStep',
                    'average',
                    'length',
                    'normalize',
                    'ceil',
                    'lerp',
                    'not',
                    'truncate',
                    'clampRange',
                    'lessThan',
                    'or',
                    'pairBlend',
                    'controller',
                    'curveInfo',
                    'choice',
                    'determinantDL',
                    'dotProductDL',
                    'divideDL',
                    'acosDL',
                    'asinDL',
                    'atanDL',
                    'atan2DL'
    }


def hideDGNodeFromChannelBox(hideTypes:set[str]=DEFAULT_HIDE_DEPENDENCY_NODES) -> None:
    '''
    Overview:
        Hides nodes of the specified type from the Channel Box display.

    Args:
        hideTypes    (set[str]): node types for hide.

    Return:
        None
    '''
    nodes = cmds.ls()
    for node in nodes:
        if cmds.nodeType(node) in hideTypes:
            cmds.setAttr(f'{node}.ihi', 0)


def removeUnusedIntermediateObject():
    shapes = cmds.ls(type='shape')
    for shape in shapes:
        isIntermediateObject = cmds.getAttr(f'{shape}.intermediateObject')
        if not isIntermediateObject:
            continue

        connections = cmds.listConnections(shape)
        if not connections:
            cmds.delete(shape)


def removeUnknownNodesAndPlugins():
    unknownNodes = cmds.ls(type='unknown') or []
    for node in unknownNodes:
        try:
            cmds.delete(node)
            om2.MGlobal.displayInfo('Deleted unknown node: {}'.format(node))
        except Exception as e:
            om2.MGlobal.displayInfo('Failed to delete unknown node: {} / {}'.format(node, e))

    # delete unknown plugin
    unknown_plugins = cmds.unknownPlugin(query=True, list=True)

    for plugin in unknown_plugins:
        try:
            cmds.unknownPlugin(plugin, remove=True)
            om2.MGlobal.displayInfo('Removed unknown plugin: {}'.format(plugin))
        except Exception as e:
            om2.MGlobal.displayInfo('Failed to remove unknown plugin: {} / {}'.format(plugin, e))