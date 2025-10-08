import numpy as np

FULL_TURN = 2 * np.pi
RIGHT_ANGLE = np.pi / 2

def inv(alpha_rad):
    """Calculates the involute function (tan(a) - a)"""
    return np.tan(alpha_rad) - alpha_rad

def calculate_operating_pressure_angle(z1, z2, x1, x2, alpha_deg):
    """Calculates the operating pressure angle."""
    alpha_rad = np.deg2rad(alpha_deg)
    inv_alpha_w = inv(alpha_rad) + 2 * (x1 + x2) * np.tan(alpha_rad) / (z1 + z2)
    # Using a simple iterative solver to find the angle from its involute
    alpha_w = alpha_rad  # Start with the standard pressure angle as an initial guess
    for _ in range(10): # 10 iterations are usually more than enough
        f = inv(alpha_w) - inv_alpha_w
        f_prime = np.tan(alpha_w)**2
        if abs(f_prime) < 1e-9:  # Avoid division by zero
            break
        alpha_w = alpha_w - f / f_prime
    return alpha_w

def calculate_contact_ratio(m, z1, z2, x1, x2, alpha_deg, a1=1.0):
    """Calculates the contact ratio for a pair of spur gears."""
    alpha_rad = np.deg2rad(alpha_deg)
    alpha_w_rad = calculate_operating_pressure_angle(z1, z2, x1, x2, alpha_deg)

    # Center distance modification due to profile shift
    c = m * (z1 + z2) / 2 * (np.cos(alpha_rad) / np.cos(alpha_w_rad))

    # Base circle radii
    rb1 = m * z1 * np.cos(alpha_rad) / 2
    rb2 = m * z2 * np.cos(alpha_rad) / 2

    # Addendum circle radii
    ra1 = m * (z1 / 2 + a1 + x1)
    ra2 = m * (z2 / 2 + a1 + x2)

    # Check for valid square root arguments
    val1 = ra1**2 - rb1**2
    val2 = ra2**2 - rb2**2
    if val1 < 0 or val2 < 0:
        return 0, c # Cannot calculate contact ratio if addendum is below base circle

    # Length of the path of contact
    g_alpha = (np.sqrt(val1) + np.sqrt(val2)) - c * np.sin(alpha_w_rad)

    # Base pitch
    pb = m * np.pi * np.cos(alpha_rad)

    # Contact ratio
    epsilon_alpha = g_alpha / pb
    return epsilon_alpha, c

def check_undercut(Z, ALPHA, X, A):
    """Checks for undercut on a single gear."""
    if Z <= 0:
        return "Not applicable for internal gears in this context"
    alpha_rad = np.deg2rad(ALPHA)
    # Minimum profile shift coefficient to avoid undercut
    x_min = A - (Z / 2.0) * (np.sin(alpha_rad)**2)
    if X < x_min:
        return f"Warning: Risk of undercut (x < {x_min:.3f})"
    return "OK"

def handle_internal_gear_parameters(Z, X, B, A, D, C, E):
    """Normalizes parameters for internal gears by inverting them."""
    if Z < 0:
        # For internal gears, conventions are often inverted
        Z, X, B = -Z, -X, -B
        A, D = D, A
        C, E = E, C
    return Z, X, B, A, D, C, E

def calculate_gear_parameters(M, Z, ALPHA, X, B, A, D, C, E):
    """
    Calculates various geometric parameters and angles for tooth profile generation.
    This function is complex and seems highly specific to the generating process.
    """
    ALPHA_0 = np.deg2rad(ALPHA)
    TOOTH_CENTER_ANGLE = np.pi / Z
    HALF_TOOTH_CENTER_ANGLE = TOOTH_CENTER_ANGLE / 2
    PITCH_ANGLE = FULL_TURN / Z
    ALPHA_M = TOOTH_CENTER_ANGLE
    ALPHA_IS = ALPHA_0 + HALF_TOOTH_CENTER_ANGLE + B / (Z * np.cos(ALPHA_0)) - (1 + 2 * X / Z) * np.sin(ALPHA_0) / np.cos(ALPHA_0)
    THETA_IS = np.tan(ALPHA_0) + 2 * (C * (1 - np.sin(ALPHA_0)) + X - D) / (Z * np.cos(ALPHA_0) * np.sin(ALPHA_0))

    sqrt_val_ie = ((Z + 2 * (X + A - E)) / (Z * np.cos(ALPHA_0)))**2 - 1
    if sqrt_val_ie < 0:
        sqrt_val_ie = 0
    THETA_IE = 2 * E / (Z * np.cos(ALPHA_0)) + np.sqrt(sqrt_val_ie)

    sqrt_val_ae = ((Z + 2 * (X + A - E)) / (Z * np.cos(ALPHA_0)))**2 - 1
    if sqrt_val_ae < 0:
        sqrt_val_ae = 0
    ALPHA_E = ALPHA_IS + THETA_IE - np.arctan(np.sqrt(sqrt_val_ae))

    if (ALPHA_E > ALPHA_M) and (ALPHA_M > ALPHA_IS + THETA_IE - np.arctan(THETA_IE)):
        sqrt_val_e = (1 / np.cos(ALPHA_IS + THETA_IE - ALPHA_M))**2 - 1
        if sqrt_val_e < 0:
            sqrt_val_e = 0
        E = (E / 2) * np.cos(ALPHA_0) * (THETA_IE - np.sqrt(sqrt_val_e))

    ALIGN_ANGLE = RIGHT_ANGLE - TOOTH_CENTER_ANGLE

    return ALPHA_0, ALPHA_M, ALPHA_IS, THETA_IS, THETA_IE, ALPHA_E, E, PITCH_ANGLE, ALIGN_ANGLE