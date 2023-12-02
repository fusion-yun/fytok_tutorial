import collections.abc
import pathlib

from fytok.modules.Equilibrium import Equilibrium
from fytok.plugins.equilibrium.fy_eq import FyEqAnalyze
from spdm.utils.constants import *


@Equilibrium.register(["eq_demo"])
class EquilibriumDemo(FyEqAnalyze):

    def execute(self, current: Equilibrium.TimeSlice, *previous, working_dir: pathlib.Path = None):
        pass
