# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

import dataclasses
from numbers import Real
from enum import StrEnum
from typing import Any

import maya.cmds as cmds


class TangentType(StrEnum):
    AUTO = 'auto'
    AUTOCUSTOM = 'autocustom'
    AUTOEASE = 'autoease'
    AUTOMIX = 'automix'
    CLAMPED = 'clamped'
    FAST = 'fast'
    FLAT = 'flat'
    LINEAR = 'linear'
    PLATEAU = 'plateau'
    SLOW = 'slow'
    SPLINE = 'spline'
    STEP = 'step'
    STEPNEXT = 'stepnext'


@dataclasses.dataclass
class DrivenKeyData:
    driverValue: Real = 0.0
    drivenValue: Real = 0.0
    inTangetType: TangentType = TangentType.AUTO
    outTangetType: TangentType = TangentType.AUTO

    def getCmdsArguments(self) -> dict[str, Any]:
        return {'value': self.drivenValue,
                'driverValue': self.driverValue,
                'inTangetType': str(self.inTangetType),
                'outTangetType': str(self.outTangetType)}


def setDrivenKeyframes(driver:str, driven:str, drivenKeyData:list[DrivenKeyData]) -> None:
    '''
    Overview:
        Set drivenkey by DrivenKeyData list.

    Args:
        driver    (str): driver attribute name.
        driven    (str): driven attribute name.
        drivenKeyData    (list[DrivenKeyData]): set drivenKey data.

    Return:
        None

    Examples:
        setDrivenKeyframes("locator1.tx", "locator2.tx", [DrivenKeyData(), DrivenKeyData(10, 20)])
    '''

    for currentData in drivenKeyData:
        kwargs = {'currentDriver': driver} | currentData.getCmdsArguments()
        cmds.setDrivenKeyframe(driven, **kwargs)