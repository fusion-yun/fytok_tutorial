import pathlib

from spdm.data.Function import Function
from spdm.data.Expression import Variable
from spdm.view import View as sp_view
import numpy as np
import scipy.constants


if __name__ == "__main__":
    x = np.linspace(0, 1.0, 100)
    fun = Function(np.sin(x), x, label="y")
    sp_view.plot(fun)