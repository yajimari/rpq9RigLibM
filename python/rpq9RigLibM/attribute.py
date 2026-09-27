# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

import maya.cmds as cmds


def setEnumByLabel(attr:str, label:str):
    enumStr = cmds.addAttr(attr, q=True, enumName=True)
    items = enumStr.split(':')
    for i, item in enumerate(items):
        if label != item:
            continue
        cmds.setAttr(attr, i)
        return

    raise ValueError(f'"{label}" is not exist in "{attr}".')




def replaceEnumName(attr:str, replaceData:dict[str, str]):
    '''
    Overview:
        Replaces the enumName of attribute based on replaceData.

    Args:
        attr        (str): Attribute name that replace enumName.
        replaceData (dict[str, str]) replace data {source: target,...}

    Return:
        None
    '''
    enumStr = cmds.addAttr(attr, q=True, enumName=True)
    items = enumStr.split(':')
    newEnumNames = []
    for item in items:
        setName = item
        if newName := replaceData.get(item):
            setName = newName
        newEnumNames.append(setName)

    cmds.addAttr(attr, e=True, en=':'.join(newEnumNames))


NODE_COMMON_ATTRIBUTES = (  'message',
                            'caching',
                            'frozen',
                            'isHistoricallyInteresting',
                            'nodeState',
                            'binMembership')


def listOriginalAttr(node:str) -> list[str]:
    '''
    Overview:
        get node original attribute name list.

    Args:
        node        (str): node name.

    Return:
        attrs       (list[str]): oritinal attribute list.
    '''
    return [attr for attr in cmds.listAttr(node) if attr not in NODE_COMMON_ATTRIBUTES]


def resetJointLabel(joint:str):
    cmds.setAttr(f'{joint}.side', 0)
    cmds.setAttr(f'{joint}.type', 0)
    cmds.setAttr(f'{joint}.otherType', 'jaw', type='string')
    cmds.setAttr(f'{joint}.drawLabel', 0)


def resetJointLabels(root:str=''):
    joints = cmds.listRelatives(root, ad=True, type='joint') if root else cmds.ls(type='joint')
    for joint in joints:
        resetJointLabel(joint)


def addWeightAttr(node:str, prefix:str='', minValue:float=0.0, maxValue:float=1.0, defaultValue:float=1.0, isDouble:bool=False) -> str:
    '''
    Overview:
        add weight attribute.

    Args:
        node        (str): node name.
        prefix      (str): prefix of attribute name. Defaults to "".
        minValue    (float): attribute min value. Defaults to 0.0.
        maxValue    (float): attribute max value. Defaults to 1.0.
        defaultValue (float): attribute default value. Defaults to 1.0.
        isDouble     (bool): use attribute type double.

    Return:
        attrName       (str): created attribute name.
    '''
    longName = f'{prefix}Weight' if prefix else 'weight'
    attributeType = 'double' if isDouble else 'float'
    cmds.addAttr(node, ln=longName, at=attributeType, minValue=min, maxValue=max, dv=defaultValue, k=True)
    return f'{node}.{longName}'

