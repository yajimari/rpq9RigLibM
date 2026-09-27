# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

import maya.cmds as cmds
import maya.api.OpenMaya as om2


class Attribute:
    def __init__(self, arg:om2.MPlug|str|om2.MObject, attribute:om2.MObject=None):
        if type(arg) is str:
            try:
                selList = om2.MSelectionList()
                selList.add(arg)
            except RuntimeError as e:
                raise RuntimeError(f'"{arg}" is not valid name.')
            arg = selList.getPlug(0)
        elif type(arg) is om2.MObject:
            if attribute is None:
                raise RuntimeError('attribute argument is None.')
            arg = om2.MPlug(arg, attribute)

        self._mplug = om2.MPlug(arg)

    def __str__(self) -> str:
        return self.partialPathName(True, True, True, False, True)
    
    def __repr__(self) -> str:
        return f'Attribute("{self.partialPathName(True, True, True, False, True)}")'
    
    def __eq__(self, other:'Attribute') -> bool:
        return self._mplug == other._mplug
    
    def __ne__(self, other:'Attribute') -> bool:
        return self._mplug != other._mplug


    def array(self) -> 'Attribute':
        return Attribute(self._mplug.array())

    def child(self, attribute:om2.MObject|int) -> 'Attribute':
        return Attribute(self._mplug.child(attribute))

    def source(self) -> 'Attribute':
        return Attribute(self._mplug.source())

    def destinations(self) -> list['Attribute']:
        destinations =  self._mplug.destinations()
        return [Attribute(plug) for plug in destinations]

    def elementByLogicalIndex(self, index:int) -> 'Attribute':
        return Attribute(self._mplug.elementByLogicalIndex(index))

    def elementByPhysicalIndex(self, index:int) -> 'Attribute':
        return Attribute(self._mplug.elementByPhysicalIndex(index))

    def typeStr(self) -> str:
        return self.attribute().apiTypeStr
    
    def apiType(self) -> om2.MFn:
        return self.attribute().apiType()

    def isSingleAttribute(self) -> bool:
        return False if self.isArray or self.isCompound else True

    def getExistingArrayAttributeIndices(self):
        numElements = self._mplug.evaluateNumElements()
        return [self._mplug.elementByPhysicalIndex(i).logicalIndex() for i in range(numElements)]


    def getValue(self):
        if not self.isSingleAttribute():
            raise RuntimeError('Attribute is not single.')
        
        apiType = self.apiType()
        if apiType == om2.MFn.kTypedAttribute:
            mobj = self._mplug.asMObject()
            attrType = om2.MFnTypedAttribute(mobj).attrType()
            if attrType == om2.MFnData.kMatrix:
                return om2.MFnMatrixData(mobj).matrix()
            elif attrType == om2.MFnData.kString:
                return om2.MFnStringData(mobj).string()
            else:
                raise TypeError('Not implemented type.')
        elif apiType == om2.MFn.kMessageAttribute:
            return None
        else:
            return self._mplug.asDouble()
        
    def setValue(self, *args, **kwargs):
        cmds.setAttr(self.partialPathName(True, True, True, False, True), *args, **kwargs)



    def inputEqual(self, other:'Attribute') -> bool:
        if not self.attribute() == other.attribute():
            #return False
            raise TypeError(f'Not equal attribute define.({self.partialName(includeNodeName=True)}, {other.partialName(includeNodeName=True)})')

        if self.isArray:
            selfElementIndeces = self.getExistingArrayAttributeIndices()
            otherElementIndeces = other.getExistingArrayAttributeIndices()
            if not len(selfElementIndeces) == len(otherElementIndeces):
                return False

            for selfIndex, otherIndex in zip(selfElementIndeces, otherElementIndeces):
                if not selfIndex == otherIndex:
                    return False
                isEqual = self.elementByLogicalIndex(selfIndex).inputEqual(other.elementByLogicalIndex(otherIndex))
                if not isEqual:
                    return False
            return True

        elif self.isCompound:
            if self.isDestination:
                if not other.isDestination:
                    return False
                return True if self.source().isExactlyEqual(other.source()) else False
            else:
                childrenNum = self.numChildren()
                for i in range(childrenNum):
                    isEqual = self.child(childrenNum).inputEqual(other.child(childrenNum))
                    if not isEqual:
                        return False

        else:
            if self.isDestination:
                return True if self.source().isExactlyEqual(other.source()) else False
            else:
                return True if self.getValue() == other.getValue() else False
        return True


    def swapOutput(self, other:'Attribute'):
        otherAttr = other.partialName(includeNodeName=True)
        outputs = self.destinations()
        if outputNum := len(outputs):
            for output in outputs:
                if output.partialName(True, False, True, False, False, True) == 'defaultRenderUtilityList1.utilities':
                    continue
                cmds.connectAttr(otherAttr, output.partialName(includeNodeName=True), f=True)

    def partialPathName(self, includeNonMandatoryIndices=False, includeInstancedIndices=False, useAlias=False, useFullAttributePath=False, useLongNames=False):
        mobj = self.node()
        if mobj.hasFn(om2.MFn.kDagNode):
            mfn = om2.MFnDagNode(mobj)
            return f'{mfn.partialPathName()}.{self.partialName(False, includeNonMandatoryIndices, includeInstancedIndices, useAlias, useFullAttributePath, useLongNames)}'
        else:
            return self.partialName(True, includeNonMandatoryIndices, includeInstancedIndices, useAlias, useFullAttributePath, useLongNames)
	

    #-- simple wrapper
    def attribute(self):
        return self._mplug.attribute()
    
    def name(self):
        return self._mplug.name()

    def node(self):
        return self._mplug.node()
    
    def numChildren(self):
        return self._mplug.numChildren()
    
    def numConnectedChildren(self):
        return self._mplug.numConnectedChildren()
    
    def numConnectedElements(self):
        return self._mplug.numConnectedElements()
    
    def numElements(self):
        return self._mplug.numElements()
    
    def partialName(self, includeNodeName=False, includeNonMandatoryIndices=False, includeInstancedIndices=False, useAlias=False, useFullAttributePath=False, useLongNames=False):
        return self._mplug.partialName(includeNodeName, includeNonMandatoryIndices, includeInstancedIndices, useAlias, useFullAttributePath, useLongNames)

    def proxied(self):
        return self._mplug.proxied()

    def isExactlyEqual(self, other:'Attribute'):
        return self._mplug.isExactlyEqual(other._mplug) 

    #-- property wrap
    @property
    def info(self):
        return self._mplug.info

    @property
    def isArray(self):
        return self._mplug.isArray

    @property
    def isCaching(self):
        return self._mplug.isCaching

    @property
    def isChannelBox(self):
        return self._mplug.isChannelBox

    @property
    def isChild(self):
        return self._mplug.isChild

    @property
    def isCompound(self):
        return self._mplug.isCompound

    @property
    def isConnected(self):
        return self._mplug.isConnected

    @property
    def isDestination(self):
        return self._mplug.isDestination

    @property
    def isDynamic(self):
        return self._mplug.isDynamic
    
    @property
    def isElement(self):
        return self._mplug.isElement
    
    @property
    def isFromReferencedFile(self):
        return self._mplug.isFromReferencedFile
    
    @property
    def isIgnoredWhenRendering(self):
        return self._mplug.isIgnoredWhenRendering

    @property
    def isKeyable(self):
        return self._mplug.isKeyable

    @property
    def isLocked(self):
        return self._mplug.isLocked

    @property
    def isNetworked(self):
        return self._mplug.isNetworked

    @property
    def isNull(self):
        return self._mplug.isNull

    @property
    def isProcedural(self):
        return self._mplug.isProcedural

    @property
    def isProxy(self):
        return self._mplug.isProxy

    @property
    def isSource(self):
        return self._mplug.isSource

    # form MFn
    @property
    def readable(self):
        return om2.MFnAttribute(self.attribute()).readable

    @property
    def writable(self):
        return om2.MFnAttribute(self.attribute()).writable

    @property
    def hidden(self):
        return om2.MFnAttribute(self.attribute()).hidden

    @property
    def parent(self):
        return om2.MFnAttribute(self.attribute()).parent



class DependencyNode:
    def __init__(self, arg:om2.MObject|str):
        if type(arg) is str:
            try:
                selList = om2.MSelectionList()
                selList.add(arg)
            except RuntimeError as e:
                raise RuntimeError(f'"{arg}" is not valid name.')
            arg = selList.getDependNode(0)

        self._mfn = om2.MFnDependencyNode(arg)
        self._mobj = self._mfn.object()


    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'DependencyNode(om2.MObject of "{self.name}".)'

    def __eq__(self, other:'DependencyNode') -> bool:
        return self._mfn == other._mfn

    def __ne__(self, other:'DependencyNode') -> bool:
        return self._mfn != other._mfn

    def attribute(self, arg:int|str) -> Attribute:
        return Attribute(self.mobject(), self._mfn.attribute(arg))

    def attributes(self) -> dict[Attribute]:
        res = {}
        for i in range(self.attributeCount()):
            attr = Attribute(self.mobject(), self._mfn.attribute(i))
            if attr.parent.isNull():
                res[attr.partialName()] = attr
        return res

    def getConnections(self):
        connections = self._mfn.getConnections()
        return [Attribute(plug) for plug in connections]

    def dependEqual(self, other:'DependencyNode') -> bool:
        if self.mobject().hasFn(om2.MFn.kDagNode):
            return False
        if not self.typeName == other.typeName:
            return False
        if not self.namespace == other.namespace:
            return False
        
        if not self.attributeCount() == other.attributeCount():
            return False

        selfAttrs = self.attributes()
        otherAttrs = other.attributes()
        for attrName, attr in selfAttrs.items():
            if not attrName in otherAttrs:
                return False

            if not attr.writable or attr.hidden:
                continue

            if not attr.inputEqual(otherAttrs[attrName]):
                return False

        return True

    def swapOutputs(self, other:'DependencyNode'):
        if not self.typeName == other.typeName:
            raise TypeError(f'{other} is not DependencyNode instance.')
        
        selfAttrs = self.attributes()
        otherAttrs = other.attributes()

        skipped = []
        for attrName, attr in selfAttrs.items():
            if not attrName in otherAttrs:
                skipped.append(attrName)
                om2.MGlobal.displayWarning(f'skipped swap output. (Not found "{other.name()}.{attrName}".)')
            attr.swapOutput(otherAttrs[attrName])
        return skipped

    def mfn(self) -> om2.MFnDependencyNode:
        mobj = self.mobject()
        return om2.MFnDependencyNode(mobj)
    
    def mobject(self) -> om2.MObject:
        return self._mfn.object()


    #-- simple wrapper
    def name(self) -> str:
        return self._mfn.name()

    def absoluteName(self):
        return self._mfn.absoluteName()
    
    def affectsAnimation(self):
        return self._mfn.affectsAnimation()

    def attributeCount(self):
        return self._mfn.attributeCount()

    def canBeWritten(self):
        return self._mfn.canBeWritten()
    
    def hasAttribute(self, name:str):
        return self._mfn.hasAttribute(name)
    
    def hasUniqueName(self):
        return self._mfn.hasUniqueName()
    
    def isFlagSet(self):
        return self._mfn.isFlagSet()

    #-- property wrap
    @property
    def isDefaultNode(self):
        return self._mfn.isDefaultNode
    
    @property
    def isFromReferencedFile(self):
        return self._mfn.isFromReferencedFile
    
    @property
    def isLocked(self):
        return self._mfn.isLocked
    
    @property
    def namespace(self):
        return self._mfn.namespace
    
    @property
    def typeId(self):
        return self._mfn.typeId
    
    @property
    def typeName(self):
        return self._mfn.typeName