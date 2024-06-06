from __future__ import annotations
import os
import collections.abc
import pathlib
from spdm.core.sp_property import sp_tree
from spdm.utils.tags import _not_found_
from fytok.modules.magnetics import Magnetics
from fytok.modules.tf import TF
from fytok.modules.wall import Wall
from fytok.modules.pf_active import PFActive
from fytok.modules.equilibrium import Equilibrium
from fytok.plugins.equilibrium.fy_eq import FyEqAnalyze
from fytok.utils.logger import logger


@sp_tree
class EquilibriumDemo(FyEqAnalyze):
    code = {"name": "eq_demo", "copyright": "FyTok Demo"}

    def execute(self, current: Equilibrium.TimeSlice, *previous, **kwargs):
        super().execute(current, *previous, **kwargs)
        tf: TF = self.inputs.get_source("tf")
        wall: Wall = self.inputs.get_source("wall")
        magnetics: Magnetics = self.inputs.get_source("magnetics")
        pf_active: PFActive = self.inputs.get_source("pf_active")

        ####################
        # 在这里添加，调用外部程序代码
        # 工作目录为 working_dir

        with self.working_dir() as current_dir:
            logger.debug((pathlib.Path.cwd(), current_dir))
            # res = np.zeros([128, 128])

            time = current.time

            shot = getattr(self._root, "shot", self.code.parameters.shot)
            if shot is None or shot is _not_found_:
                logger.exception("shot is not defined")
                raise RuntimeError("shot is not defined")

            coil_current = [coil.current(time) for coil in pf_active.coil]
            logger.debug(coil_current)

            # flux = [flux_loop.flux(time) for flux_loop in magnetics.flux_loop]

        ####################
        # current.update({ ... })
        # current.profiles_2d.psi = ...


Equilibrium.register(["eq_demo"], EquilibriumDemo)
