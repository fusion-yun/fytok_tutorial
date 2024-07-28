import typing
import numpy as np
import scipy.constants

from spdm.utils.type_hint import array_type
from fytok.utils.logger import logger

from fytok.modules.equilibrium import Equilibrium
from fytok.modules.core_profiles import CoreProfiles
from fytok.modules.core_transport import CoreTransportModel
from fytok.modules.utilities import CoreRadialGrid


class SpitzerDemo(
    CoreTransportModel,
    category="neoclassical",
    code={"name": "spitzer_demo"},
):
    """Spitzer resistivity model"""

    def execute(
        self, *args, equilibrium: Equilibrium, core_profiles: CoreProfiles, **kwargs
    ) -> typing.Self:

        res: typing.Self = super().execute(
            *args, equilibrium=equilibrium, core_profiles=core_profiles, **kwargs
        )

        eq1d: Equilibrium.Profiles1D = equilibrium.profiles_1d

        prof1d: CoreProfiles.Profiles1D = core_profiles.profiles_1d

        radial_grid: CoreRadialGrid = res.profiles_1d.grid

        rho_tor_norm = radial_grid.rho_tor_norm
        rho_tor = radial_grid.rho_tor
        psi_norm = radial_grid.psi_norm
        # psi = radial_grid.psi
        # psi_axis = radial_grid.psi_axis
        # psi_boundary = radial_grid.psi_boundary

        B0 = res.vacuum_toroidal_field.b0
        R0 = res.vacuum_toroidal_field.r0

        eV = scipy.constants.electron_volt

        q = eq1d.q(psi_norm)

        # Tavg = np.sum([ion.density*ion.temperature for ion in core_profile.ion]) / \
        #     np.sum([ion.density for ion in core_profile.ion])

        Te = prof1d.electrons.temperature(rho_tor_norm)
        ne = prof1d.electrons.density(rho_tor_norm)
        # Pe = core_profile.electrons.pressure(rho_tor_norm)

        # Coulomb logarithm
        #  Ch.14.5 p727 Tokamaks 2003
        # lnCoul = (14.9 - 0.5*np.log(Ne/1e20) + np.log(Te/1000)) * (Te < 10) +\
        #     (15.2 - 0.5*np.log(Ne/1e20) + np.log(Te/1000))*(Te >= 10)
        # (17.3 - 0.5*np.log(Ne/1e20) + 1.5*np.log(Te/1000))*(Te >= 10)

        # lnCoul = 14
        ln_coul = prof1d.coulomb_logarithm(rho_tor_norm)

        # electron collision time , eq 14.6.1
        tau_e = 1.09e16 * ((Te / 1000) ** (3 / 2)) / ne / ln_coul

        vTe = np.sqrt(Te * eV / scipy.constants.electron_mass)

        # Larmor radius,   eq 14.7.2
        # rho_e = 1.07e-4*((Te/1000)**(1/2))/B0

        # rho_tor[0] = max(rho_e[0], rho_tor[0])

        epsilon = rho_tor / R0
        # epsilon12 = np.sqrt(epsilon)
        epsilon32 = epsilon ** (3 / 2)
        ###########################################################################################
        #  Sec 14.10 Resistivity
        #
        eta_s = 1.65e-9 * (ln_coul * (Te / 1000) ** (-3.0 / 2.0))
        Zeff = np.asarray(prof1d.zeff(rho_tor_norm))
        fT = 1.0 - (1 - epsilon) ** 2 / np.sqrt(1.0 - epsilon**2) / (
            1 + 1.46 * np.sqrt(epsilon)
        )

        phi = np.zeros_like(rho_tor_norm)
        nu_e = R0 * q[1:] / vTe[1:] / tau_e[1:] / epsilon32[1:]
        phi[1:] = fT[1:] / (1.0 + (0.58 + 0.20 * Zeff[1:]) * nu_e)
        phi[0] = 0

        C = 0.56 / Zeff * (3.0 - Zeff) / (3.0 + Zeff)

        eta = (
            eta_s
            * Zeff
            / (1 - phi)
            / (1.0 - C * phi)
            * (1.0 + 0.27 * (Zeff - 1.0))
            / (1.0 + 0.47 * (Zeff - 1.0))
        )

        res.profiles_1d.conductivity_parallel = 1.0 / eta

        return res
