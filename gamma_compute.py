import numpy as np
import scipy.integrate as integrate
import scipy.stats as stats


def f_V(V, mu, sigma):
    return (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(
        -((V - mu) ** 2) / (2 * sigma**2)
    )


def f_C(C, C_min, C_max):
    return 1 / (C_max - C_min) if C_min <= C <= C_max else 0


def integrand(C, V, p, d_R, C_min, C_max, mu, sigma):
    if V <= 0:  # Avoid division by zero
        return 0
    term = 1 - (1 - p) ** np.floor((d_R * C) / V)
    return term * f_V(V, mu, sigma) * f_C(C, C_min, C_max)


def compute_gamma(p, d_R, C_min, C_max, V_min, V_max, mu, sigma):
    result, _ = integrate.dblquad(
        lambda C, V: integrand(C, V, p, d_R, C_min, C_max, mu, sigma),
        V_min,
        V_max,  # Limits for V
        lambda V: C_min,
        lambda V: C_max,  # Limits for C
    )
    return result


p = 1 / 3e9
d_R = 1000
C_min, C_max = 2e9, 4e9
V_min, V_max = 10, 50
mu, sigma = 45, 13.5

gamma_value = compute_gamma(p, d_R, C_min, C_max, V_min, V_max, mu, sigma)
print(f"Computed gamma: {gamma_value}")
