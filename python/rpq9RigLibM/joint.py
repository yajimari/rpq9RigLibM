# Copyright 2026 Ryoya Yajima
# SPDX-License-Identifier: Apache-2.0

from enum import IntEnum

class JointSide(IntEnum):
    Center = 0
    Left = 1
    Right = 2
    NONE = 3

OTHER_JOINT_TYPE = 18