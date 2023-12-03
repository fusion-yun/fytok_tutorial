import sys
# sys.path
sys.path.append("/gpfs/fuyun/projects/fuyun/fytok_ext/python")
sys.path.append("/scratch/liuxj/workspace_plugins/fytok_tutorial/python")

# sys.path.append("/scratch/liuxj/workspace_plugins/fytok_ext/python")

from fytok.Tokamak import Tokamak

tokamak = Tokamak(
    f"mdsplus://202.127.204.12?enable_efit_east=True",
    device="east",
    shot=70754,
    equilibrium={"code": {"name": "efit_east"}},
)
tokamak.equilibrium._entry = None

tokamak.equilibrium.refresh(time=0.5)