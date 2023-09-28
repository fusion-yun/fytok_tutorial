import collections
import collections.abc
import functools
import typing
from enum import Enum

import numpy as np
import scipy.constants
from fytok.modules.CoreProfiles import CoreProfiles
from fytok.modules.Equilibrium import Equilibrium
from fytok.modules.Magnetics import Magnetics
from fytok.modules.PFActive import PFActive
from fytok.modules.Wall import Wall
from fytok.plugins.equilibrium.eq_analyze import FyEqAnalyze
from spdm.data.TimeSeries import TimeSlice
from spdm.mesh.Mesh import Mesh
from spdm.utils.constants import *
from spdm.utils.logger import logger
from spdm.utils.numeric import bitwise_and, squeeze
from spdm.utils.tags import _not_found_
from spdm.utils.typing import (ArrayLike, ArrayType, NumericType, array_type,
                               as_array, as_scalar, is_array, scalar_type)


@Equilibrium.register(["demo_eq"])
class EquilibriumDeomEQ(Equilibrium):

    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)

    def refresh(self, *args, core_profiles_1d: CoreProfiles.Profiles1d = None,  **kwargs) -> TimeSlice:
        """ update the last time slice, base on profiles_2d[-1].psi, and core_profiles_1d, wall, pf_active    """

        logger.info(f"Refresh Equilibrium: {self.__class__.__name__} Done")

        return self.time_slice.current

    def advance(self, *args, time: float = 0.0,
                core_profile_1d: CoreProfiles.Profiles1d = None,
                pf_active: PFActive = None,
                wall: Wall = None, **kwargs) -> Equilibrium.TimeSlice:

        return super().advance(*args, time=time, **kwargs)


