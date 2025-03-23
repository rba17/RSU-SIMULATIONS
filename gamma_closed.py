import scipy.special as sp
import numpy as np


def compute_erf_expression(Vehicle_Lambda):
    FLOW_MAP = {
        0.1: (45, 13.5),
        0.125: (43.54, 13.062),
        0.15: (41.95, 12.585),
        0.175: (40.21, 12.063),
        0.2: (38.23, 11.469),
        0.225: (35.89, 10.767),
        0.25: (32.9, 9.87),
        0.2777: (24.78, 7.434),
    }
    MU, SIGMA = FLOW_MAP.get(Vehicle_Lambda, (None, None))
    # 1/(σ√(2π))*exp(-((V-μ)^2)/(2σ^2))
    term1 = sp.erf((MU - 10) / (np.sqrt(2) * SIGMA))
    term2 = sp.erf((MU - 50) / (np.sqrt(2) * SIGMA))

    return (term1 - term2) / 2
