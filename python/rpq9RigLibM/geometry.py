# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

import maya.cmds as cmds
import maya.api.OpenMaya as om2

from .apiUtils import getDagPath


def cleanDuplicate(geo:str):
    originalParent = cmds.listRelatives(geo, p=True)
    originalShapes = cmds.listRelatives(geo, s=True, noIntermediate=True)
    duplicated = cmds.duplicate(geo)[0]
    cmds.delete(duplicated, ch=True)
    
    sourceShapes = cmds.listRelatives(duplicated, s=True, noIntermediate=True)
    
    inOutPair = {
                'mesh': ['outMesh', 'inMesh'],
                'nurbsCurve': ['local', 'create'],
                'nurbsSurface': ['local', 'create']
                }

    kwargs = {'name': f'{geo}_duplicated'}
    if originalParent:
        kwargs['parnet'] = originalParent[0]
    transform = cmds.createNode('transform', **kwargs)
    for attr in ['translate', 'rotate', 'scale', 'shear', 'localRotatePivot', 'localScalePivot']:
        cmds.setAttr(f'{transform}.{attr}', cmds.getAttr(f'{geo}.{attr}'), type='double3')

    for originalShape, sourceShape in zip(originalShapes, sourceShapes):
        nodeType = cmds.nodeType(sourceShape)
    
        shape = cmds.createNode(nodeType, p=transform, n=f'{originalShape.replace(geo, f"{geo}_duplicated")}')
        outAttr, inAttr = inOutPair[nodeType]

        cmds.connectAttr(f'{sourceShape}.{outAttr}', f'{shape}.{inAttr}', f=True)
        cmds.dgdirty(shape)
        cmds.refresh(f=True)
        cmds.disconnectAttr(f'{sourceShape}.{outAttr}', f'{shape}.{inAttr}')

        cmds.sets(shape, e=True, forceElement='initialShadingGroup')


    shapes = cmds.listRelatives(transform, s=True)
    cmds.delete(duplicated)
    cmds.select(transform)

    return [transform] + shapes



def getRaycastPoint(geo:str,
                    raySource:om2.MFloatPoint,
                    rayDirection:om2.MFloatVector,
                    space:om2.MSpace,
                    maxParam:float,
                    tolerance=om2.MFnMesh.kIntersectTolerance) -> om2.MFloatPoint|None:
    dagPath = getDagPath(geo)
    mfn = om2.MFnMesh(dagPath)
    accelParams = mfn.autoUniformGridParams()
    hit = mfn.closestIntersection(raySource, rayDirection, space, maxParam, tolerance=tolerance)
    if hit is None:
        return None
    return hit[0]


def getClosestPoint(geo:str, point:om2.MPoint, space:om2.MSpace) -> tuple[om2.MPoint, int]:
    dagPath = getDagPath(geo)
    mfn = om2.MFnMesh(dagPath)
    return mfn.getClosestPoint(point, space=space)


def getUVAtPoint(geo:str, point:om2.MPoint, space:om2.MSpace, uvSet:str='') -> tuple[float, float, int]:
    dagPath = getDagPath(geo)
    mfn = om2.MFnMesh(dagPath)
    return mfn.getUVAtPoint(point, space=space, uvSet=uvSet)
