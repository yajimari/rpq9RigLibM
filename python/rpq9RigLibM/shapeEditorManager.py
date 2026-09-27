# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

import weakref
from typing import Callable

import maya.cmds as cmds

SHAPE_EDITOR_MANAGER = 'shapeEditorManager'


def getBlendShapeIndexData(manager:str):
    mi = cmds.getAttr(f'{manager}.blendShapeParent', mi=True)
    return {cmds.listConnections(f'{manager}.blendShapeParent[{i}]', d=False)[0]: i for i in mi}



class Group:
    def __init__(self, name:str):
        self._directoryName = name
        self._parent:weakref.ReferenceType['Group']|Callable = lambda: None
        self._children:list[int] = []
        self._index = -1
        self._isCreated = False

    @property
    def name(self):
        return self._directoryName

    @property
    def parent(self):
        return self._parent()

    @property
    def children(self):
        return self._children

    @property
    def index(self):
        return self.create() if self._index < 0 else self._index

    @property
    def isCreated(self):
        return self._isCreated


    def addChild(self, child):#child:'Group'|'BlendShape'
        self._children.append(child)
        child._parent = weakref.ref(self)


    def create(self) -> int:
        if self.isCreated:
            raise RuntimeError('This Group is already created.')

        mi = cmds.getAttr(f'{SHAPE_EDITOR_MANAGER}.blendShapeDirectory', mi=True)
        self._index = max(mi) + 1
        cmds.setAttr(f'{SHAPE_EDITOR_MANAGER}.blendShapeDirectory[{self.index}].directoryName', self.name, type='string')
        self._isCreated = True
        return self.index


    def isValidChild(self, item):
        return False if item.parent is self else False


    def getChildIndices(self) -> tuple[list[int], list[int]]:
        blendShapes = []
        groups = []
        for child in self.children:
            if not self.isValidChild(child):
                continue
            childType = type(child)
            if childType is type(self):
                childBlendShapes, childGroups = child.getChildIndices()
                blendShapes += childBlendShapes
                groups.append(child.index)
            elif childType is BlendShape:
                blendShapes.append(child.index)
            else:
                raise TypeError(f'"{childType}" is unknown type.')
        return blendShapes, groups


    def setDataToNode(self):
        parentIndex = 0 if self.parent is None else self.parent.index
        cmds.setAttr(f'{SHAPE_EDITOR_MANAGER}.blendShapeDirectory[{self.index}].parentIndex', parentIndex)
        blendShapeIndices, groupIndices = self.getChildIndices()
        blendShapeIndices.sort()
        groupIndices = sorted([-i for i in groupIndices])
        cmds.setAttr(f'{SHAPE_EDITOR_MANAGER}.blendShapeDirectory[{self.index}].childIndices', blendShapeIndices + groupIndices, type='Int32Array')


    def setDataToNodeDescendents(self):
        self.setDataToNode()
        for child in self.children:
            if not self.isValidChild(child):
                continue
            if type(child) is not Target:
                child.setDataToNodeDescendents()



class BlendShape:
    def __init__(self, name:str):
        self._name = name
        self._parent:weakref.ReferenceType[Group]|Callable = lambda: None
        self._children:list[int] = []
        self._index = -1

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent()

    @property
    def children(self):
        return self._children

    @property
    def index(self):
        return self._getManagerIndex() if self._index < 0 else self._index


    def addChild(self, child):#child:'TargetGroup'|'Target'
        self._children.append(child)
        child._parent = weakref.ref(self)


    def getTargetNames(self):
        res = cmds.aliasAttr(self.name, q=True)
        return res[0::2]


    def isValidChild(self, item):
        return True if item.parent is self else False


    def _getManagerIndex(self):
        blendShapeIndexData = getBlendShapeIndexData(SHAPE_EDITOR_MANAGER)
        index = blendShapeIndexData.get(self.name)
        if index is not None:
            self._index = index
        else:
            raise RuntimeError(f'Not found "{self.name}" in "{SHAPE_EDITOR_MANAGER}"')
        return self._index


    def setDataToNode(self):
        cmds.setAttr(f'{self.name}.midLayerParent', self.parent.index)


    def setDataToNodeDescendents(self):
        self.setDataToNode()
        for child in self.children:
            if not self.isValidChild(child):
                continue
            if type(child) is not Target:
                child.setDataToNodeDescendents()



class TargetGroup:
    def __init__(self, name:str, blendShape:BlendShape):
        self._directoryName = name
        self._parent:weakref.ReferenceType[BlendShape|'TargetGroup']|Callable = lambda: None
        self._children:list[int] = []
        self._index = -1
        self._blendShape = weakref.ref(blendShape)
        self._isCreated = False

    @property
    def name(self):
        return self._directoryName

    @property
    def parent(self):
        return self._parent()

    @property
    def children(self):
        return self._children

    @property
    def index(self):
        return self.create() if self._index < 0 else self._index

    @property
    def blendShape(self):
        return self._blendShape()

    @property
    def isCreated(self):
        return self._isCreated


    def addChild(self, child):#child:'TargetGroup'|'Target'
        self._children.append(child)
        child._parent = weakref.ref(self)


    def create(self) -> int:
        if self.isCreated:
            raise RuntimeError('This Group is already created.')

        mi = cmds.getAttr(self.blendShape.name, mi=True)
        self._index = max(mi) + 1
        cmds.setAttr(f'{self.blendShape.name}.targetDirectory[{self.index}].directoryName', self.name)
        self._isCreated = True
        return self._index


    def isValidChild(self, item):
        return False if item.parent is self else False


    def getChildIndices(self) -> tuple[list[int], list[int]]:
        blendShapes = []
        groups = []
        for child in self.children:
            if not self.isValidChild(child):
                continue
            childType = type(child)
            if childType is type(self):
                childBlendShapes, childGroups = child.getChildIndices()
                blendShapes += childBlendShapes
                groups.append(child.index)
            elif childType is Target:
                blendShapes.append(child.index)
            else:
                raise TypeError(f'"{childType}" is unknown type.')
        return blendShapes, groups


    def setDataToNode(self):
        parentIndex = 0 if self.parent is None else self.parent.index
        cmds.setAttr(f'{self.blendShape.name}.targetDirectory[{self.index}].parentIndex', parentIndex)
        blendShapeIndices, groupIndices = self.getChildIndices()
        blendShapeIndices.sort()
        groupIndices = sorted([-i for i in groupIndices].sorted)
        cmds.setAttr(f'{self.blendShape.name}.targetDirectory[{self.index}].childIndices', blendShapeIndices + groupIndices, type='Int32Array')


    def setDataToNodeDescendents(self):
        self.setDataToNode()
        for child in self.children:
            if not self.isValidChild(child):
                continue
            if type(child) is not Target:
                child.setDataToNodeDescendents()



class Target:
    def __init__(self, name:str, blendShape:BlendShape):
        self._name = name
        self._parent:weakref.ReferenceType[BlendShape|'TargetGroup']|Callable = lambda: None
        self._index = -1
        self._blendShape = weakref.ref(blendShape)

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent()

    @property
    def index(self):
        return self._getTargetIndex() if self._index < 0 else self._index

    @property
    def blendShape(self):
        return self._blendShape()

    def _getTargetIndex(self):
        targetNames = self.blendShape.getTargetNames()
        self._index = targetNames.index(self.name)
        return self.index


def getRootGroup() -> Group:
    group = Group('Group')
    group._index  = 0
    return group


def getRootTargetGroup(blendShape:BlendShape) -> TargetGroup:
    group = TargetGroup('Group', blendShape)
    group._index  = 0
    return group


def resetShapeEditor():
    cmds.removeMultiInstance(f'{SHAPE_EDITOR_MANAGER}.blendShapeDirectory', all=True)
    group = Group('Group')

    blendShapes = cmds.ls(type='blendShape')
    for blendShape in blendShapes:
        blendShapeObj = BlendShape(blendShape)
        targetGroup = TargetGroup('Group', blendShapeObj)
        group.addChild(blendShapeObj)
        blendShapeObj.addChild(targetGroup)
        targetNames = blendShapeObj.getTargetNames()
        for targetName in targetNames:
            targetObj = Target(targetName, blendShapeObj)
            targetGroup.addChild(targetObj)
        
        cmds.removeMultiInstance(f'{blendShape}.targetDirectory', all=True)

    group.setDataToNodeDescendents()