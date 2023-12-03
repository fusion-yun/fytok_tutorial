from __future__ import annotations

import collections.abc
import pathlib
from spdm.data.sp_property import sp_tree
from fytok.modules.Magnetics import Magnetics
from fytok.modules.TF import TF
from fytok.modules.Wall import Wall
from fytok.modules.PFActive import PFActive
from fytok.modules.Equilibrium import Equilibrium


from fytok.plugins.equilibrium.fy_eq import FyEqAnalyze


@Equilibrium.register(["eq_demo"])
@sp_tree
class EquilibriumDemo(FyEqAnalyze):
    code = {"name": "eq_demo", "copyright": "FyTok Demo"}

    def execute(self, current: Equilibrium.TimeSlice, *previous, working_dir: pathlib.Path):
        super().execute(current, *previous, working_dir=working_dir)
        tf: TF = self.inputs.get_source("tf")
        wall: Wall = self.inputs.get_source("wall")
        magnetics: Magnetics = self.inputs.get_source("magnetics")
        pf_active: PFActive = self.inputs.get_source("pf_active")

        ####################
        # 在这里添加，调用外部程序代码
        # 工作目录为 working_dir

        with self.working_dir() as current_dir:
            res = np.zeros([128, 128])

            time = current.time

            coil_current = [coil.current(time) for coil in pf_active.coil]

            flux = [flux_loop.flux(time) for flux_loop in magnetics.flux_loop]

        ####################
        current.profiles_2d.psi = res

    def refresh(
        self,
        *args,
        time=None,
        wall: Wall = None,
        tf: TF = None,
        magnetics: Magnetics = None,
        pf_active: PFActive = None,
        **kwargs,
    ) -> None:
        return super().refresh(
            *args,
            time=time,
            tf=tf,
            wall=wall,
            magnetics=magnetics,
            pf_active=pf_active,
            **kwargs,
        )
