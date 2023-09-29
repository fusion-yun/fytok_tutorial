import pathlib

import numpy as np
import pandas as pd
import scipy.constants
from fytok.Tokamak import Tokamak
from fytok.utils.load_scenario import load_scenario
from fytok.utils.plot_profiles import plot_profiles
from spdm.data.File import File
from spdm.data.Function import function_like
from fytok.utils.logger import logger
from spdm.view.View import display
import os

WORKSPACE = "/home/salmon/workspace"  # "/ssd01/salmon_work/workspace/"


os.environ["SP_DATA_MAPPING_PATH"] = f"{WORKSPACE}/fytok_data/mapping"

if __name__ == "__main__":

    logger.info("====== START ========")

    output_path = pathlib.Path(f"{WORKSPACE}/output")

    data_path = pathlib.Path(f"{WORKSPACE}/data/15MA inductive - burn")

    ###################################################################################################
    # baseline

    eqdsk_file = File(
        data_path/"Standard domain R-Z/High resolution - 257x513/g900003.00230_ITER_15MA_eqdsk16HR.txt", format="GEQdsk").read()
    R0 = eqdsk_file.get("vacuum_toroidal_field/r0")
    B0 = eqdsk_file.get("vacuum_toroidal_field/b0")
    psi_axis = eqdsk_file.get("time_slice/0/global_quantities/psi_axis")
    psi_boundary = eqdsk_file.get("time_slice/0/global_quantities/psi_boundary")
    bs_eq_psi = eqdsk_file.get("time_slice/0/profiles_1d/psi")
    bs_eq_psi_norm = (bs_eq_psi-psi_axis)/(psi_boundary-psi_axis)
    bs_eq_fpol = function_like(eqdsk_file.get("time_slice/0/profiles_1d/f"), bs_eq_psi)

    profiles = pd.read_excel(data_path/'15MA Inductive at burn-ASTRA.xls',
                             sheet_name='15MA plasma', header=10, usecols="B:BN")

    bs_r_norm = profiles["x"].values

    b_Te = profiles["TE"].values*1000
    b_Ti = profiles["TI"].values*1000
    b_ne = profiles["NE"].values*1.0e19

    b_nHe = profiles["Nalf"].values * 1.0e19
    b_ni = profiles["Nd+t"].values * 1.0e19*0.5
    b_nImp = profiles["Nz"].values * 1.0e19
    b_zeff = profiles["Zeff"].values
    bs_psi_norm = profiles["Fp"].values
    bs_psi = bs_psi_norm*(psi_boundary-psi_axis)+psi_axis

    bs_xq = profiles["xq"].values
    bs_q = profiles["q"].values

    bs_r_norm = profiles["x"].values
    bs_line_style = {"marker": '.', "linestyle": ''}
    # Core profile
    r_ped = 0.96  # np.sqrt(0.88)
    i_ped = np.argmin(np.abs(bs_r_norm-r_ped))

    time_slice = -1
    ###################################################################################################
    # Initialize Tokamak
    scenario = load_scenario(data_path)

    tok = Tokamak("ITER",
                  time=0.0,
                  name=scenario["name"],
                  description=scenario["description"],
                  core_profiles={
                      **scenario["core_profiles"],
                      "$default_value": {
                          "profiles_1d": {
                              "grid": {
                                  "rho_tor_norm": np.linspace(0, 1.0, 100),
                                  "psi": np.linspace(0, 1.0, 100),
                                  "psi_magnetic_axis": 0.0,
                                  "psi_boundary": 1.0,
                              }}}
                  },
                  equilibrium={
                      **scenario["equilibrium"],
                      "code": {
                          "name": "eq_analyze",  # "freegs",
                          "parameters": {
                              "boundary": "fixed",
                              "psi_norm": np.linspace(0, 1.0, 128)
                          }},
                      "$default_value": {
                          "time_slice": {
                              "boundary": {"psi_norm": 0.99},
                              "profiles_2d": {"grid": {"dim1": 256, "dim2": 128}},
                              "coordinate_system": {"grid": {"dim1": 128, "dim2": 128}}
                          }}},
                  core_transport={
                      **scenario["core_transport"],
                  },
                  core_sources={
                      **scenario["core_sources"],
                  }
                  )
 
    eq = tok.equilibrium

    eq_time_slice = tok.equilibrium.time_slice.current

    eq_profiles_1d = eq_time_slice.profiles_1d

    eq_global_quantities = eq_time_slice.global_quantities

    if True:  # plot equilibrium
        display(  # plot equilibrium
            tok,
            title=f"{tok.name} time={tok.time}s",
            output=output_path/"tokamak_prev.svg")

        # logger.debug(eq_profiles_1d.dphi_dpsi.antiderivative()(eq_profiles_1d.psi))

    if True:
        display(  # plot tokamak geometric profile
            [
                ((eq_profiles_1d.dvolume_dpsi, {"label": r"$\frac{dV}{d\psi}$"}), {"y_label": r"$[Wb]$"}),

                (eq_profiles_1d.dpsi_drho_tor, {"label": r"$\frac{d\psi}{d\rho_{tor}}$"}),
                ([
                    (bs_eq_fpol,  {"label": "astra", **bs_line_style}),
                    (eq_profiles_1d.f,  {"label": r"fytok"}),
                ], {"y_label": r"$F_{pol} [Wb\cdot m]$"}),
                ([
                    (function_like(profiles["q"].values, bs_psi), {"label": r"astra", **bs_line_style}),
                    (eq_profiles_1d.q,  {"label": r"$fytok$"}),
                ], {"y_label": r"$q [-]$"}),
                ([
                    (function_like(profiles["rho"].values, bs_psi), {"label": r"astra", **bs_line_style}),
                    (eq_profiles_1d.rho_tor,   {"label": r"$\rho$"}),
                ], {"y_label":  r"$\rho_{tor}[m]$", }),

                ([
                    (function_like(profiles["x"].values, bs_psi), {
                     "label": r"$\frac{\rho_{tor}}{\rho_{tor,bdry}}$ astra", **bs_line_style}),
                    (eq_profiles_1d.rho_tor_norm,   {"label": r"$\bar{\rho}$"}),
                ], {"y_label":  r"[-]", }),



                ([
                    (function_like(4*(scipy.constants.pi**2) * R0 * profiles["rho"].values, bs_psi),
                     {"label": r"$4\pi^2 R_0 \rho$", **bs_line_style}),
                    (eq_profiles_1d.dvolume_drho_tor,  {"label": r"$dV/d\rho_{tor}$", }),
                ], {"y_label":  r"$4\pi ^ 2 R_0 \rho[m ^ 2]$"}),

                (eq_profiles_1d.gm1,   {"label": r"$gm1=\left<\frac{1}{R^2}\right>$"}),
                (eq_profiles_1d.gm2,   {"label": r"$gm2=\left<\frac{\left|\nabla \rho\right|^2}{R^2}\right>$"}),
                (eq_profiles_1d.gm3,   {"label": r"$gm3=\left<\left|\nabla \rho\right|^2\right>$"}),
                (eq_profiles_1d.gm4,   {"label": r"$gm4=\left<1/B^2\right>$"}),
                (eq_profiles_1d.gm5,   {"label": r"$gm5=\left<B^2\right>$"}),
                (eq_profiles_1d.gm6,   {"label": r"$gm6=\left<\nabla \rho_{tor}^2/ B^2 \right>$"}),
                (eq_profiles_1d.gm7,   {"label": r"$gm7=\left<\left|\nabla \rho\right|\right>$"}),
                (eq_profiles_1d.gm8,   {"label": r"$gm8=\left<R\right>$"}),

            ],
            x_axis=(eq_profiles_1d.rho_tor_norm,
                    {"value": eq_profiles_1d.psi, "label":  r"$\bar{\rho}_{tor}$"}),
            title="Equilibrium",
            output=output_path/"equilibrium_coord.svg",
            grid=True, fontsize=16)

    if False:
        display(  # plot tokamak geometric profile
            [

                ([
                    (function_like(profiles["q"].values, bs_psi),   {"label": r"astra", **bs_line_style}),
                    (eq_profiles_1d.q,                              {"label": r"fytok", }),
                    (eq_profiles_1d.dphi_dpsi*np.sign(B0)/scipy.constants.pi/2.0,
                     {"label": r"$\frac{\sigma_{B_{p}}}{\left(2\pi\right)^{1-e_{B_{p}}}}\frac{d\Phi_{tor}}{d\psi_{ref}}$"}),
                ], {"y_label": r"$q [-]$"}),
                ([
                    (function_like(profiles["rho"].values, bs_psi), {"label": r"astra", **bs_line_style}),
                    (eq_profiles_1d.rho_tor,                        {"label": r"fytok"}),
                ], {"y_label": r"$\rho_{tor}[m]$", }),
                ([
                    (function_like(profiles["x"].values, bs_psi),   {"label": r"astra", **bs_line_style}),
                    (eq_profiles_1d.rho_tor_norm,                   {"label": r"fytok"}),
                ], {"y_label": r"$\frac{\rho_{tor}}{\rho_{tor,bdry}}$"}),

                ([
                    (function_like(profiles["shif"].values, bs_psi),    {"label": r"astra", ** bs_line_style}),
                    (eq_profiles_1d.geometric_axis.r - R0,              {"label": r"fytok", }),
                ], {"y_label": "$\Delta$ shafranov \n shift $[m]$ "}),

                ([
                    (function_like(profiles["k"].values, bs_psi),       {"label": r"astra", **bs_line_style}),
                    (eq_profiles_1d.elongation,                         {"label": r"fytok", }),
                ], {"y_label": r"$elongation[-]$", }),

                ([
                    (function_like(profiles["del"].values, bs_psi),     {"label": r"astra", **bs_line_style}),
                    (eq_profiles_1d.triangularity,                      {"label": r"$\Delta[-]$          fytok"}),
                    (eq_profiles_1d.triangularity_upper,                {"label": r"$\Delta_{upper}[-]$  fytok"}),
                    (eq_profiles_1d.triangularity_lower,                {"label": r"$\Delta_{lower}[-]$  fytok"}),
                ], {"y_label": r"$triangularity[-]$", }),
                ([
                    (4*(scipy.constants.pi**2) * R0*eq_profiles_1d.rho_tor,   {"label": r"$4\pi^2 R_0 \rho$", }),
                    (eq_profiles_1d.dvolume_drho_tor,                   {"label": r"$V^{\prime}$", }),
                ], {"y_label": r"$4\pi^2 R_0 \rho , dV/d\rho$"}),

                [
                    (eq_profiles_1d.geometric_axis.r,                   {"label":   r"$geometric_{axis.r}$"}),
                    (eq_profiles_1d.r_inboard,                          {"label":          r"$r_{inboard}$"}),
                    (eq_profiles_1d.r_outboard,                         {"label":         r"$r_{outboard}$"}),
                ],

                ([
                    (eq_profiles_1d.volume,                          {"label":   r"$V$",  **bs_line_style}),
                    (eq_profiles_1d.dvolume_dpsi.antiderivative(),   {"label":   r"$\int \frac{dV}{d\psi}  d\psi$"}),
                ], {"y_label": r"volume", }),

                # ([
                #     (function_like(profiles["Jtot"].values*1e6),   {"label": r"astra", ** bs_line_style}),
                #     (eq_profiles_1d.j_parallel,                       {"label": r"fytok", }),
                # ], {"y_label": r"$j_{\parallel} [A\cdot m^{-2}]$", })

                # [
                #     (eq.coordinate_system.surface_integrate2(lambda r, z:1.0/r**2),
                #      r"$\left<\frac{1}{R^2}\right>$"),
                #     (eq.coordinate_system.surface_integrate(1/eq.coordinate_system.r**2),
                #      r"$\left<\frac{1}{R^2}\right>$"),
                # ]
            ],
            x_axis=(eq_profiles_1d.psi,  {"label": r"$\psi/\psi_{bdry}$"}),
            title="Equilibrium Geometric Shape",
            grid=True, fontsize=16, transparent=True,
            output=output_path/"equilibrium_profiles.svg")

        logger.info("Solve Equilibrium ")

    if False:  # initialize CoreProfile  value
        logger.info("Initialize Core Profiles ")

        core_profiles_1d = tok.core_profiles.profiles_1d.current
        x_axis = np.linspace(0, 1.0, bs_psi_norm.size)

        display(  # CoreProfile initialize value
            [
                ([
                    (bs_psi_norm,                       {"label": "astra",   **bs_line_style}),
                    (core_profiles_1d.grid.psi_norm,    {"label":  r"fytok"}),
                ], {"y_label": r"$\psi_{nrom}$"}),
                ([
                    (function_like(bs_q, bs_xq),        {"label":  "astra", **bs_line_style}),
                ], {"y_label": r"$q[-]$"}),
                ([
                    (b_ne,                              {"label": "electron astra", **bs_line_style}),
                    (b_ni,                              {"label": "D astra",  **bs_line_style}),
                    (b_nHe,                             {"label": "He astra", **bs_line_style}),
                    (core_profiles_1d.electrons.density, {"label": r"$electron$", }),
                    *[(ion.density, {"label": f"${ion.label}$"})
                      for ion in core_profiles_1d.ion if not ion.is_impurity],
                ], {"y_label": r"Density $n [m \cdot s^{-3}]$"}),

                ([
                    (b_Te,    {"label":  r"astra $T_e$",      **bs_line_style}),
                    (b_Ti,    {"label":  r"astra $T_i$",      **bs_line_style}),
                    (core_profiles_1d.electrons.temperature, {"label":   r"$e$", }),
                    # *[(ion.temperature, {"label": f"${ion.label}$"})
                    #   for ion in core_profiles_1d.ion if not ion.is_impurity],
                ], {"y_label":  r"$T [eV]$", }),

                # [
                #     (function_like( profiles["Zeff"].values, bs_r_norm),       r"astra",
                #      r"$Z_{eff}  [-]$", bs_line_style),
                #     (core_profiles_1d.zeff, r"$fytok$"),
                # ],

            ],
            x_axis=(np.linspace(0, 1.0, bs_psi_norm.size), {"label":  r"$\rho=\sqrt{\Phi/\Phi_{bdry}}$"}),

            output=output_path/"core_profiles_initialize.svg")

    if False:  # initialize CoreTransport value

        logger.info("Initialize Core Transport ")

        tok.core_transport.model.insert([
            # {"code": {"name": "alpha_ep"}},
            {"code": {"name": "tglf"}},
            # {"code": {"name": "spitzer"}},

            # {"code": {"name": "neoclassical"}},

            # {"code": {"name": "nclass"}},
        ])

        logger.debug(tok.core_transport.model[:].profiles_1d.current.__value__)

        core_transport_profiles_1d = tok.core_transport.model[0].profiles_1d.current

        tok.core_transport.refresh(equilibrium=tok.equilibrium.time_slice.current,
                                   core_profiles_1d=tok.core_profiles.profiles_1d.current)

        # x_axis = np.linspace(0, 1.0, bs_psi_norm.size)
        for model in tok.core_transport.model:
            logger.debug((model.code.name, model.identifier.name))

        # for ion in core_transport_profiles_1d.ion:
        #     logger.debug(ion.label)
        #     d = ion.energy.d
        #     logger.debug(d(x_axis))

        display(  # CoreTransport  initialize value
            [
                ([
                    (function_like(profiles["He"].values, bs_r_norm), {"label": "astra", **bs_line_style}),
                    (core_transport_profiles_1d.electrons.energy.d,   {"label":  "fytok", }),
                ], {"y_label": r"$\chi_{e}$", }),

                ([
                    (function_like(profiles["Joh"].values*1.0e6 / profiles["U"].values * (2.0*scipy.constants.pi * R0), bs_r_norm),
                     {"label": r"astra", **bs_line_style}),
                    (core_transport_profiles_1d.conductivity_parallel,  {"label": r"fytok", }),
                ], {"y_label": r"$\sigma_{\parallel}$", }),

                ([
                    (function_like(profiles["Xi"].values, bs_r_norm), {"label": r"astra", **bs_line_style}),
                    *[(ion.energy.d, {"label": f"{ion.label}", }) for ion in core_transport_profiles_1d.ion],
                ], {"y_label": r"$\chi_{i}$", }),

                # [(ion.particles.d_fast_factor, f"{ion.label}", r"$D_{\alpha}/D_{He}$")
                #  for ion in fast_alpha_profiles_1d.ion],
                # [
                #     (function_like(np.log(profiles["XiNC"].values, bs_r_norm)),
                #      "astra", r"$ln \chi_{i,nc}$", bs_line_style),
                #     # * [(np.log(core_transport1d_nc.ion[{"label": label}].energy.d),   f"${label}$", r"$ln \chi_{i,nc}$")
                #     #     for label in ("H", "D", "He")],
                # ],
                # [
                #     (function_like(profiles["XiNC"].values, bs_r_norm), "astra",
                #      "neoclassical  $\\chi_{NC}$ \n ion heat conductivity", bs_line_style),
                #     # *[(ion.energy.d,  f"{ion.label}", r"Neoclassical $\chi_{NC}$")
                #     #   for ion in nc_profiles_1d.ion if not ion.is_impurity],
                # ],
                # [(ion.particles.d,  f"{ion.label}", r"Neoclassical $D_{NC}$")
                #  for ion in nc_profiles_1d.ion if not ion.is_impurity],

            ],
            x_axis=(np.linspace(0, 1.0, bs_psi_norm.size),  {"label":   r"$\sqrt{\Phi/\Phi_{bdry}}$"}),
            title="Transport", transparent=True,
            output=output_path/"core_transport.svg")

    if False:  # initialize CoreSources
        logger.info("Initialize Core Source  ")

        tok.core_sources.source.insert([
            {"code": {"name": "bootstrap_current"}},
            {"code": {"name": "fusion_reaction"}},
        ])
        tok.core_sources.refresh(equilibrium=tok.equilibrium.time_slice.current,
                                 core_profiles_1d=tok.core_profiles.profiles_1d.current)

        core_source_profiles_1d = tok.core_sources.source[0].profiles_1d.current

        display(
            [
                ([
                    (function_like(profiles["Jtot"].values, bs_r_norm), {"label": "astra", **bs_line_style}),
                    (core_source_profiles_1d.j_parallel*1e-6,           {"label": "fytok"}),
                ], {"y_label": "$J_{total}=j_{bootstrap}+j_{\\Omega}$ \n $[MA\\cdot m^{-2}]$", }),

                # [
                #     (function_like(profiles["Joh"].values, bs_r_norm), "astra",
                #      r"$j_{ohmic} [MA\cdot m^{-2}]$", bs_line_style),
                #     (core_source_profiles_1d.j_ohmic*1e-6, "fytok", r"$j_{\Omega} [MA\cdot m^{-2}]$"),
                # ],
                ([
                    (core_source_profiles_1d.electrons.particles,  {"label": "e"},),
                    *[(ion.particles,  {"label": f"{ion.label}"}) for ion in core_source_profiles_1d.ion],
                ], {"y_label":  r"$S[m ^ {-3} s ^ {-1}]$"}),

                ([
                    (core_source_profiles_1d.electrons.energy,  {"label":  "e", }),
                    *[(ion.energy,  {"label":  f"{ion.label}", }) for ion in core_source_profiles_1d.ion],
                    # (core_source_profiles_1d.ion[{"label": "D"}].energy,   "D",   r"$Q$"),
                    # (core_source_profiles_1d.ion[{"label": "T"}].energy,   "T",   r"$Q$"),
                    # (core_source_profiles_1d.ion[{"label": "He"}].energy,  "He",  r"$Q$"),
                ], {"y_label":   r"$Q$"}),

                # [
                # (function_like(profiles["Jbs"].values, bs_r_norm),
                #  r"astra", "bootstrap current \n $[MA\\cdot m^{-2}]$", bs_line_style),
                # # (tok.core_sources.source[{"code/name": "bootstrap_current"}].profiles_1d.j_parallel*1e-6,
                #  r"fytok",                     ),
                # ],
                # [
                #     (rms_residual(function_like(profiles["Jbs"].values*1e6,bs_r_norm),
                #                   tok.core_sources.source[{"code.name": "bootstrap_current"}].profiles_1d.j_parallel),
                #      r"bootstrap current", r"  rms residual $[\%]$"),
                #     (rms_residual(function_like(profiles["Jtot"].values, bs_r_norm), core_source.j_parallel*1e-6),
                #      r"total current", r"  rms residual $[\%]$"),
                # ],
                # [
                #     (core_source_profiles_1d.ion[{"label": "D"}].particles,    r"D",  r"$S_{DT} [m^3 s^{-1}]$",),
                #     (core_source_profiles_1d.ion[{"label": "T"}].particles,    r"T",  r"$S_{DT} [m^3 s^{-1}]$",),
                #     (core_source_profiles_1d.ion[{"label": "He"}].particles_fast,
                #      r"fast", r"$S_{\alpha} [m^3 s^{-1}]$",),
                # ],
                # [
                #     (core_source_profiles_1d.ion[{"label": "He"}].particles,
                #      r"thermal", r"$S_{\alpha} [m^3 s^{-1}]$",),
                # ],
                # (core_source_profiles_1d.ion[{"label": "D"}].particles,           r"$D_{total}$", r"$S_{DT} [m^3 s^{-1}]$",),
                # [
                #     (core_source_profiles_1d.electrons.energy,  "electron",      r"$Q [eV\cdot m^{-3} s^{-1}]$"),
                #     # *[(ion.energy*1e-6,             f"{ion.label}",  r"$Q [eV\cdot m^{-3} s^{-1}]$")
                #     #   for ion in core_source_profiles_1d.ion if not ion.is_impurity],
                # ],
            ],
            x_axis=(np.linspace(0, 1.0, bs_psi_norm.size), {"label": r"$\sqrt{\Phi/\Phi_{bdry}}$"}),
            grid=True, fontsize=10, transparent=True,
            output=output_path/"core_sources.svg")

    if False:  # TransportSolver

        tok.transport_solver.update({
            "code": {
                "name": "bvp_solver_nonlinear",
                "parameters": {
                        "tolerance": 1.0e-4,
                        "particle_solver": "ion",
                        "max_nodes": 500,
                        "verbose": 2,
                        "bvp_rms_mask": [r_ped],
                }
            },
            "fusion_reaction": [r"D(t,n)\alpha"],
            "boundary_conditions_1d": {
                "current": {"identifier": {"index": 1}, "value": [psi_boundary]},
                "electrons": {"particles": {"identifier": {"index": 1}, "value": [b_ne[-1]]},
                              "energy": {"identifier": {"index": 1}, "value": [b_Te[-1]]}},

                "ion": [
                    {"label": "D",
                     "particles": {"identifier": {"index": 1}, "value": [b_ni[-1]]},
                     "energy": {"identifier": {"index": 1}, "value": [b_Ti[-1]]}},
                    {"label": "T",
                     "particles": {"identifier": {"index": 1}, "value": [b_ni[-1]]},
                     "energy": {"identifier": {"index": 1}, "value": [b_Ti[-1]]}},
                    {"label": "He",
                     "particles": {"identifier": {"index": 1}, "value": [b_nHe[-1]]},
                     "energy": {"identifier": {"index": 1}, "value": [b_Ti[-1]]},
                     "particles_thermal": {"identifier": {"index": 1}, "value": [b_nHe[-1]]},
                     "particles_fast": {"identifier": {"index": 1}, "value": [0]},
                     }
                ]
            }}
        )

        logger.debug([ion.label for ion in tok.transport_solver.boundary_conditions_1d.current.ion])

        # logger.debug(core_profiles_1d.ion["D"].label)

        particle_solver = tok.transport_solver.code.parameters.get('particle_solver', 'ion')

        logger.info("Transport solver Start")

        core_profile_1d = tok.refresh()

        logger.info("Transport solver End")

        b_nHe_fast = function_like(profiles["Naff"].values * 1.0e19, bs_r_norm)

        b_nHe_thermal = function_like(profiles["Nath"].values * 1.0e19, bs_r_norm)

        ionHe = core_profile_1d.ion["He"]

        plot_profiles(
            [
                # psi ,current
                [
                    (function_like(bs_psi, bs_r_norm),             r"astra", r"$\psi [Wb]$", bs_line_style),
                    (core_profile_1d["psi"],  r"fytok", r"$\psi  [Wb]$", {"marker": '+', "linestyle": '-'}),
                ],

                # (core_profile_1d["psi_flux"],  r"fytok", r"$\Gamma_{\psi}$", {"marker": '+', "linestyle": '-'}),

                # electron
                # [
                #     (b_ne/1.0e19, r"astra",  r"$n_e [10^{19} m^{-3}]$",  bs_line_style),
                #     (core_profile_1d.electrons.density/1.0e19,  r"fytok", r"$n_e [10^{19} m^{-3}]$"),
                # ],

                [
                    (b_Te/1000.0, r"astra",  r"$T_e [keV]$",  bs_line_style),
                    (core_profile_1d.electrons.temperature / 1000.0, r"fytok", r"$T_e [keV]$"),
                ],

                # ion
                [
                    (b_ni*1.0e-19,    r"$D_{astra}$",  r"$n_i  \, [10^{19} m^-3]$", bs_line_style),
                    (b_nHe*1.0e-19,   r"$He_{astra}$", r"$n_i  \,  [10^{19} m^-3]$", bs_line_style),
                    *[(core_profile_1d.ion[{"label": label}].density*1.0e-19,   f"${label}$", r"$n_i  \, [10^{19} m^-3]$")
                      for label in ['D', 'T', 'He']],
                ],


                [
                    (ionHe.density_thermal * 1.0e-19,  r"$n_{thermal}$", r"$n_{He}  \, [10^{19} m^-3]$"),
                    (ionHe.density_fast*1.0e-19,     r"$n_{\alpha}$", r"$n_{\alpha}  \, [10^{19} m^-3]$"),
                    (ionHe.density*1.0e-19,             r"$n_{He}$", r"$n_{He}  \, [10^{19} m^-3]$"),

                    (b_nHe*1.0e-19,   r"${astra}$", r"$n_{He}  \, [10^{19} m^-3]$", bs_line_style),
                ],

                [
                    (b_Ti/1000.0,    r"astra", r"$T_{i} \, [keV]$", bs_line_style),
                    * [(core_profile_1d.ion[{"label": label}].temperature/1000.0,  f"fytok ${label}$", r"$T_{i} [keV]$")
                        for label in ['D', 'T', 'He']],
                ],

                # ---------------------------------------------------------------------------------------------------

                # (core_profile_1d["rms_residuals"] * 100, r"bvp", r"residual $[\%]$"),

                # [
                #     # (rms_residual(function_like(bs_psi,bs_r_norm),
                #     #  core_profile_1d["psi"]), r"$\psi$", " rms residual [%]"),

                #     # (rms_residual(b_ne, core_profile_1d.electrons.density), r"$n_e$"),

                #     (rms_residual(b_Te, core_profile_1d.electrons.temperature), r"$T_e$", " rms residual [%]"),

                #     *[(rms_residual(b_ni, ion.density), f"$n_{ion.label}$")
                #       for ion in core_profile_1d.ion if not ion.is_impurity],
                #     # *[(rms_residual(b_Ti, ion.temperature), f"$T_{ion.label}$")
                #     #   for ion in core_profile_1d.ion if not ion.is_impurity],

                # ],
            ],
            x=([0, 1.0],  r"$\sqrt{\Phi/\Phi_{bdry}}$"),
            title=f" Particle solver '{particle_solver}'",
            grid=True, fontsize=10).savefig(output_path/f"core_profiles_result_{particle_solver}.svg", transparent=True)

        plot_profiles(
            [
                # psi ,current
                [
                    (function_like(bs_psi, bs_r_norm),            r"astra", r"$\psi [Wb]$", bs_line_style),
                    (core_profile_1d.grid.psi,  r"fytok", r"$\psi  [Wb]$", {"marker": '+', "linestyle": '-'}),
                ],

                # (core_profile_1d.grid.psi_flux,  r"fytok", r"$\Gamma_{\psi}$", {"marker": '+', "linestyle": '-'}),

                # electron
                [
                    (b_ne/1.0e19, r"astra",  r"$n_e [10^{19} m^{-3}]$",  bs_line_style),
                    (core_profile_1d.electrons.density/1.0e19,  r"fytok", r"$n_e [10^{19} m^{-3}]$"),
                ],
                [
                    (b_Te/1000.0, r"astra",  r"$T_e [keV]$",  bs_line_style),
                    (core_profile_1d.electrons.temperature / 1000.0, r"fytok", r"$T_e [keV]$"),
                ],

                # ion
                [
                    (b_ni*1.0e-19,    r"$D_{astra}$",  r"$n_i  \, [10^{19} m^-3]$", bs_line_style),
                    (b_nHe*1.0e-19,   r"$He_{astra}$", r"$n_i  \,  [10^{19} m^-3]$", bs_line_style),
                    *[(core_profile_1d.ion[{"label": label}].density*1.0e-19,   f"${label}$", r"$n_i  \, [10^{19} m^-3]$")
                        for label in ["D", "T", "He"]],
                ],

                # (fast_alpha_profiles_1d.ion[{"label": "He"}].particles.d_fast_factor,
                #  f""r"$D_{\alpha}/D_{He}$", r"$D_{\alpha}/D_{He}$"),

                # [
                #     (core_source_fusion.ion[{"label": "He"}].particles,
                #      r"$[ n_{\alpha}/\tau^{*}_{SD}]$", r"$S_{He} [m^3 s^{-1}]$",),

                #     (core_source_fusion.ion[{"label": "He"}].particles_fast,
                #         r"$n_{D} n_{T} \left<\sigma_{DT}\right>- n_{\alpha}/\tau^{*}_{SD}$", r"$S_{\alpha} [m^3 s^{-1}]$",),
                # ],


                [
                    (b_nHe_fast*1.0e-19,   r"$astra$",  r"$n_{He}  \, [10^{19} m^-3]$", bs_line_style),
                    (ionHe.density_fast*1.0e-19, r"fytok", r"$n_{\alpha} [10^{19} m^-3]$"),
                ],
                [
                    (b_nHe_thermal*1.0e-19,   r"astra",  r"$n_{He}  \, [10^{19} m^-3]$", bs_line_style),
                    (ionHe.density_thermal * 1.0e-19,   r"fytok", r"$n_{He}  \, [10^{19} m^-3]$"),
                ],
                [
                    (b_nHe*1.0e-19,   r"astra", r"$n_{total}  \, [10^{19} m^-3]$", bs_line_style),
                    (ionHe.density*1.0e-19, r"fytok$", r"$n_{total}  \, [10^{19} m^-3]$"),
                ]


                # ---------------------------------------------------------------------------------------------------


            ],
            x=([0, 1.0],  r"$\sqrt{\Phi/\Phi_{bdry}}$"),
            title=f" Particle solver '{particle_solver}'",
            grid=True, fontsize=10).savefig(output_path/f"core_profiles_result_{particle_solver}_alpha.svg", transparent=True)

    logger.info("====== DONE ========")
