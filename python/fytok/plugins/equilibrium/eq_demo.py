from __future__ import annotations

import collections.abc
import pathlib
from fytok.modules.Magnetics import Magnetics
from fytok.modules.PFActive import PFActive
from fytok.modules.Equilibrium import Equilibrium
from fytok.plugins.equilibrium.fy_eq import FyEqAnalyze
from spdm.utils.constants import *


@Equilibrium.register(["eq_demo"])
class EquilibriumDemo(FyEqAnalyze):
    def execute(self, current: Equilibrium.TimeSlice, *previous, working_dir: pathlib.Path):
        super().execute(current, *previous, working_dir=working_dir)
        ####################
        # 在这里添加，调用外部程序代码
        # 工作目录为 working_dir
        #################

    def refresh(self, *args, time=None, magnetics: Magnetics = None, pf_active: PFActive = None, **kwargs) -> None:
        return super().refresh(*args, time=time, magnetics=magnetics, pf_active=pf_active, **kwargs)
