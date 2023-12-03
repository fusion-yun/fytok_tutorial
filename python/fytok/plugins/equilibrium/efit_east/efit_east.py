import os
import pathlib
import shutil
import subprocess
import tempfile

import numpy as np
from fytok.modules.Equilibrium import Equilibrium
from fytok.modules.Magnetics import Magnetics
from fytok.modules.PFActive import PFActive
from fytok.modules.TF import TF
from fytok.modules.Wall import Wall
from fytok.plugins.equilibrium.fy_eq import FyEqAnalyze
from fytok.utils.logger import logger
from spdm.data.File import File
from fytok.modules.Utilities import *
from spdm.utils.constants import *

@Equilibrium.register(["efit_east"])
class EquilibriumEFITEAST(FyEqAnalyze):
    code = {"name": "efit_east", "copyright": "Third-party Plugin for FyTok"}
    """
        EFIT is part of GACODE and use of this module requires a license from GA.
        See https://gacode.io/license.html.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self._shot = self.code.parameters.get("shot", None) or kwargs.get("shot", 0)

    def _run_backend(self, *args, shot: int, time: float, magnetics: Magnetics,
                     pf_active: PFActive, tf: TF, wall: Wall, **kwargs):
        """run efit on shot batch way."""

        itime = int(np.round(time * 1000))

        mdsdata = {}

        mdsdata["coils"] = [flux_loop.flux(time) / (2.0 * np.pi) for flux_loop in magnetics.flux_loop]

        mdsdata["expmp2"] = [bpol.field(time) for bpol in magnetics.b_field_pol_probe]

        # for IP
        mdsdata["plasma"] = magnetics.ip[0](time)

        # pf_active: PFActive
        mdsdata["brsp"] = [coil.element[0].turns_with_sign * coil.current(time) for coil in pf_active.coil]

        # tf: TF   1 tesla@r=1.7m with 4086A in IT coils
        try:
            mdsdata["btor"] = (np.mean([coil.current(time) for coil in tf.coil]) * 1.7 / (4086 * 1.85))
        except Exception:
            logger.error("Can not find TF coil")
            mdsdata["btor"] = 8000 * 1.7 / (4086 * 1.85)

        mdsdata["ishot"] = shot

        mdsdata["itime"] = itime

        ##################################################################################################################

        snap_filepath = pathlib.Path(__file__).parent / "snap_files"

        # for EAST ,on SHENMA cluster

        EFIT_ROOT = pathlib.Path(os.environ.get("EFIT_ROOT", "/project/imd/codes/EFIT_Qian"))

        EFIT_LIBRARY_PATH = os.environ.get("EFIT_LIBRARY_PATH",
                                           "/project/imd/codes/utilities/pgplot/:/home/users/ligq/lib64:/pkg/pgi/linux86/14.10/lib",
                                           )

        if shot <= 44326 and shot > 4774:
            snap_file = snap_filepath / "snap.nam_12"
            efit_exec = EFIT_ROOT / "bin/efitd129d_east_2010"
        elif shot > 44326 and shot <= 52804:
            snap_file = snap_filepath / "snap.nam_14"
            efit_exec = EFIT_ROOT / "bin/efitd129d_east_2014"
        elif shot > 52804 and shot <= 96915:
            snap_file = snap_filepath / "snap.nam_15"
            efit_exec = EFIT_ROOT / "bin/efitd129d_east_2015"
        elif shot > 96915:
            snap_file = snap_filepath / "snap.nam_21"
            efit_exec = EFIT_ROOT / "bin/efitd129d_east_2021"
        else:
            raise Exception("no such shot")

        envs = {"LD_LIBRARY_PATH": f"{EFIT_LIBRARY_PATH}:{os.environ.get('LD_LIBRARY_PATH')}", }

        with self.working_dir as working_dir:
            working_dir = pathlib.Path(working_dir)

            File(working_dir / "temp", format="namelist", template=snap_file).write({"in1": mdsdata})

            pwd = os.getcwd()

            if not efit_exec.is_file():
                raise Exception(f"no such file {efit_exec}")

            try:
                procss = subprocess.run(
                    [efit_exec.as_posix()], shell=True, check=True, env=envs, cwd=working_dir
                )
            except Exception as error:
                logger.debug(File(working_dir / "temp", format="namelist").read().dump())
                raise RuntimeError(f"Fail to run {efit_exec}") from error

            # if FY_DEBUG > -1 or procss.returncode > 0:  # for debug
            #     shutil.copytree(working_dir, f"{pwd}/{shot:06d}.{itime:05d}", dirs_exist_ok=True)
            #     logger.debug(f"OUTPUT {pwd}")

            if procss.returncode > 0:
                raise RuntimeError(f"Fail to run {efit_exec}! error code={procss.returncode}")

            output = working_dir / f"g{shot:06d}.{itime:05d}"

            if not output.exists():
                raise RuntimeError(f"Can not find output {output}")

            eq = File(output, format="GEQdsk").read().dump()

            # os.chdir(pwd)

        logger.debug(eq)

        return eq
    
    def execute(self,current: Equilibrium.TimeSlice,*previous, **kwargs):
        super().execute(current, *previous, **kwargs)

        tf: TF = self.inputs.get_source("tf")
        wall: Wall = self.inputs.get_source("wall")
        magnetics: Magnetics = self.inputs.get_source("magnetics")
        pf_active: PFActive = self.inputs.get_source("pf_active",)
      
        ####################
        # 在这里添加，调用外部程序代码
        # 工作目录为 working_dir
        #################
        
        """run efit on shot batch way."""
        print("execute")
        # current_slice = self.time_slice.current
        
        itime = int(np.round(self.time * 1000))

        mdsdata = {}
        # logger.debug(magnetics.flux_loop[10].flux(time))  
        mdsdata["coils"] = [flux_loop.flux(self.time) / (2.0 * np.pi) for flux_loop in magnetics.flux_loop]

        # logger.debug(mdsdata["coils"])
        
        # logger.debug(magnetics.b_field_pol_probe[0].field(time)) 
        mdsdata["expmp2"] = [bpol.field(self.time) for bpol in magnetics.b_field_pol_probe]

        # for IP
        mdsdata["plasma"] = magnetics.ip[0](self.time)

        # pf_active: PFActive
        # logger.debug(pf_active.coil[0].element[0].turns_with_sign * pf_active.coil[0].current(time))
        mdsdata["brsp"] = [coil.element[0].turns_with_sign * coil.current(self.time) for coil in pf_active.coil]

        # tf: TF   1 tesla@r=1.7m with 4086A in IT coils
        try:
            # logger.debug(tf.coil[0].current(time))
            mdsdata["btor"] = (np.mean([coil.current(self.time) for coil in tf.coil]) * 1.7 / (4086 * 1.85))
        except Exception:
            logger.error("Can not find TF coil")
            mdsdata["btor"] = 8000 * 1.7 / (4086 * 1.85)

        mdsdata["ishot"] = self.shot

        mdsdata["itime"] = itime

        ##################################################################################################################

        snap_filepath = pathlib.Path(__file__).parent / "snap_files"

        # for EAST ,on SHENMA cluster

        EFIT_ROOT = pathlib.Path(os.environ.get("EFIT_ROOT", "/project/imd/codes/EFIT_Qian"))

        EFIT_LIBRARY_PATH = os.environ.get("EFIT_LIBRARY_PATH",
                                           "/project/imd/codes/utilities/pgplot/:/home/users/ligq/lib64:/pkg/pgi/linux86/14.10/lib",
                                           )

        if self.shot <= 44326 and self.shot > 4774:
            snap_file = snap_filepath / "snap.nam_12"
            efit_exec = EFIT_ROOT / "bin/efitd129d_east_2010"
        elif self.shot > 44326 and self.shot <= 52804:
            snap_file = snap_filepath / "snap.nam_14"
            efit_exec = EFIT_ROOT / "bin/efitd129d_east_2014"
        elif self.shot > 52804 and self.shot <= 96915:
            snap_file = snap_filepath / "snap.nam_15"
            efit_exec = EFIT_ROOT / "bin/efitd129d_east_2015"
        elif self.shot > 96915:
            snap_file = snap_filepath / "snap.nam_21"
            efit_exec = EFIT_ROOT / "bin/efitd129d_east_2021"
        else:
            raise Exception("no such shot")

        envs = {"LD_LIBRARY_PATH": f"{EFIT_LIBRARY_PATH}:{os.environ.get('LD_LIBRARY_PATH')}", }
        
        logger.debug(self.working_dir)
        # with tempfile.TemporaryDirectory() as working_dir:
        with self.working_dir() as working_dir:
            # working_dir = pathlib.Path(working_dir)
            logger.debug(working_dir)

            File(working_dir / "temp", format="namelist", template=snap_file).write({"in1": mdsdata})

            pwd = os.getcwd()
            logger.debug(pwd)
            ## copy pwd to working_dir
            # new_dir = "/scratch/jupytertest/workspace_fytok/fytok_ext.old/python/fytok/plugins/equilibrium/efit_east/examples"
            # shutil.copytree(working_dir, new_dir, dirs_exist_ok=True)
            
            if not efit_exec.is_file():
                raise Exception(f"no such file {efit_exec}")

            try:
                procss = subprocess.run(
                    [efit_exec.as_posix()], shell=True, check=True, env=envs, cwd=working_dir
                )
            except Exception as error:
                # logger.debug(File(working_dir / "temp", format="namelist").read().dump())
                raise RuntimeError(f"Fail to run {efit_exec}") from error

            if procss.returncode > 0:  # for debug
                shutil.copytree(working_dir, f"{pwd}/{self.shot:06d}.{itime:05d}", dirs_exist_ok=True)
                logger.debug(f"OUTPUT {pwd}")

            if procss.returncode > 0:
                raise RuntimeError(f"Fail to run {efit_exec}! error code={procss.returncode}")

            output = working_dir / f"g{self.shot:06d}.{itime:05d}"

            if not output.exists():
                raise RuntimeError(f"Can not find output {output}")

            eq = File(output, format="GEQdsk").read().dump()
            
            current.update(eq["time_slice"][0])
            # os.chdir(pwd)

        # logger.debug(eq)
        
        # self.time_slice.refresh(eq["time_slice"][0])

        logger.info(f"Refresh Equilibrium: {self.__class__.__name__} Done")

        # logger.info(f"Refresh Equilibrium: {self.__class__.__name__} Done")

        # return eq
    
    
    # def refresh(
    #     self,
    #     *args,
    #     time: float | None = None,  # unit: s
    #     magnetics: Magnetics | None = None,
    #     pf_active: PFActive | None = None,
    #     tf: TF | None = None,
    #     wall: Wall | None = None,
    #     **kwargs,
    # ):
    #     """update the last time slice, base on profiles_2d[-1].psi, and core_profiles_1d, wall, pf_active"""

    #     super().refresh(*args, time=time, **kwargs)

    #     current_slice = self.time_slice.current

    #     if self._parent is not None:
    #         if magnetics is None:
    #             magnetics = self._parent.magnetics  # type:ignore

    #         if pf_active is None:
    #             pf_active = self._parent.pf_active  # type:ignore

    #         if tf is None:
    #             tf = self._parent.tf  # type:ignore

    #         if wall is None:
    #             wall = self._parent.wall  # type:ignore

    #     time = time or kwargs.pop("time", None) or current_slice.time

    #     eq = self._run_backend(
    #         shot=self._shot, time=time, magnetics=magnetics, pf_active=pf_active, tf=tf, wall=wall,
    #     )

    #     self.time_slice.refresh(eq["time_slice"][0])

    #     logger.info(f"Refresh Equilibrium: {self.__class__.__name__} Done")

    #     return current_slice

    # def advance(self, *args, dt=0.1, **kwargs):
    #     return super().advance(*args, **kwargs)
