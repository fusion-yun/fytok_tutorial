from fytok.Tokamak import Tokamak
from fytok.utils.logger import logger
from spdm.view import View as sp_view
import pathlib

if __name__ == "__main__":
    output_path = pathlib.Path(f"/home/salmon/workspace/output")

    tok = Tokamak(f"file+geqdsk://{pathlib.Path(__file__).parent.as_posix()}/data/g900003.00230_ITER_15MA_eqdsk16HR.txt",
                  device='ITER', shot='900003', time=2.3)
    eq_profiles_1d = tok.equilibrium.time_slice.current.profiles_1d


    if True:
        sp_view.display(tok, title=tok.short_description,
                        styles={"interferometer": False},
                        output=output_path/f"{tok.tag}_rz.svg")

    if True:  # plot tokamak geometric profile

        sp_view.profiles(
            [
                ((eq_profiles_1d.dvolume_dpsi, {"label": r"$\frac{dV}{d\psi}$"}), {"y_label": r"$[Wb]$"}),

                (eq_profiles_1d.dphi_dpsi, {"label": r"$\frac{d\phi}{d\psi}$"}),

                (eq_profiles_1d.rho_tor, {"label": r"$\rho_{tor}$"}),

                ((eq_profiles_1d.dpsi_drho_tor, {"label": r"$\frac{d\psi}{d\rho_{tor}}$"}),
                 {"y_label": r"$\frac{d\psi}{d\rho_{tor}}$"}),

                ([
                    # (bs_eq_fpol,  {"label": "astra", **bs_line_style}),
                    (eq_profiles_1d.f,  {"label": r"fytok"}),
                ], {"y_label": r"$F_{pol} [Wb\cdot m]$"}),
                ([
                    # (function_like(profiles["q"].values, bs_psi), {"label": r"astra", **bs_line_style}),
                    (eq_profiles_1d.q,  {"label": r"$fytok$"}),
                ], {"y_label": r"$q [-]$"}),
                ([
                    # (function_like(profiles["rho"].values, bs_psi), {"label": r"astra", **bs_line_style}),
                    (eq_profiles_1d.rho_tor,   {"label": r"$\rho$"}),
                ], {"y_label":  r"$\rho_{tor}[m]$", }),

                ([
                    # (function_like(profiles["x"].values, bs_psi), {
                    #     "label": r"$\frac{\rho_{tor}}{\rho_{tor,bdry}}$ astra", **bs_line_style}),
                    (eq_profiles_1d.rho_tor_norm,   {"label": r"$\bar{\rho}$"}),
                ], {"y_label":  r"[-]", }),

                ([
                    # (function_like(4*(scipy.constants.pi**2) * R0 * profiles["rho"].values, bs_psi),
                    #  {"label": r"$4\pi^2 R_0 \rho$", **bs_line_style}),
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
            x_axis=tok.equilibrium.time_slice.current.profiles_1d.psi[1:],
            x_label=r"$\bar{\psi}[-]$",
            # styles={"$matplotlib": {"grid": True}},
            output=output_path/f"{tok.tag}_profiles.svg"
        )
