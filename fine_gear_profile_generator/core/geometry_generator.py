import numpy as np
from . import gear_math
from . import transformations

def involute_curve(M, Z, SEG_INVOLUTE, THETA_IS, THETA_IE, ALPHA_0, ALPHA_IS):
    """Generates the involute part of the tooth flank."""
    THETA1 = np.linspace(THETA_IS, THETA_IE, SEG_INVOLUTE)
    X11 = (1/2) * M * Z * np.cos(ALPHA_0) * np.sqrt(1 + THETA1**2) * np.cos(ALPHA_IS + THETA1 - np.arctan(THETA1))
    Y11 = (1/2) * M * Z * np.cos(ALPHA_0) * np.sqrt(1 + THETA1**2) * np.sin(ALPHA_IS + THETA1 - np.arctan(THETA1))
    return X11, Y11

def edge_round_curve(M, E, X11, Y11, X_E, Y_E, X_E0, Y_E0, SEG_EDGE_R):
    """Generates the rounded edge curve at the tooth tip."""
    THETA3_MIN = np.arctan2((Y11[-1] - Y_E0), (X11[-1] - X_E0))
    THETA3_MAX = np.arctan2((Y_E - Y_E0), (X_E - X_E0))
    THETA3 = np.linspace(THETA3_MIN, THETA3_MAX, SEG_EDGE_R)
    X21 = M * E * np.cos(THETA3) + X_E0
    Y21 = M * E * np.sin(THETA3) + Y_E0
    return X21, Y21

def root_round_curve(M, Z, X, D, C, B, THETA_TE, ALPHA_TS, SEG_ROOT_R):
    """Generates the trochoidal root fillet curve."""
    THETA_T = np.linspace(0, THETA_TE, SEG_ROOT_R)
    denominator = M * D - M * X - M * C
    if (C != 0) and (denominator == 0):
        THETA_S = (np.pi / 2) * np.ones(len(THETA_T))
    elif denominator != 0:
        THETA_S = np.arctan((M * Z * THETA_T / 2) / denominator)
    else:
        THETA_S = np.zeros(len(THETA_T))
    X31 = M * ((Z / 2 + X - D + C) * np.cos(THETA_T + ALPHA_TS) + (Z / 2) * THETA_T * np.sin(THETA_T + ALPHA_TS) - C * np.cos(THETA_S + THETA_T + ALPHA_TS))
    Y31 = M * ((Z / 2 + X - D + C) * np.sin(THETA_T + ALPHA_TS) - (Z / 2) * THETA_T * np.cos(THETA_T + ALPHA_TS) - C * np.sin(THETA_S + THETA_T + ALPHA_TS))
    return X31, Y31

def outer_arc(M, Z, X, A, ALPHA_E, ALPHA_M, SEG_OUTER):
    """Generates the outer arc at the tooth tip (addendum circle)."""
    THETA6 = np.linspace(ALPHA_E, ALPHA_M, SEG_OUTER)
    X41 = M * (Z / 2 + A + X) * np.cos(THETA6)
    Y41 = M * (Z / 2 + A + X) * np.sin(THETA6)
    return X41, Y41

def root_arc(M, Z, X, D, ALPHA_TS, SEG_ROOT):
    """Generates the root arc at the bottom of the tooth space (dedendum circle)."""
    THETA7 = np.linspace(0, ALPHA_TS, SEG_ROOT)
    X51 = M * (Z / 2 - D + X) * np.cos(THETA7)
    Y51 = M * (Z / 2 - D + X) * np.sin(THETA7)
    return X51, Y51

def combine_tooth_profile(X11, Y11, X21, Y21, X31, Y31, X41, Y41, X51, Y51, X12, Y12, X22, Y22, X32, Y32, X42, Y42, X52, Y52):
    """Combines all curve segments into a single, continuous tooth profile."""
    X1 = np.concatenate((X42[1:], X22[1:], X12[1:], X32[1:], X52[1:], X51, X31[1:], X11[1:], X21[1:], X41[1:]))
    Y1 = np.concatenate((Y42[1:], Y22[1:], Y12[1:], Y32[1:], Y52[1:], Y51, Y31[1:], Y11[1:], Y21[1:], Y41[1:]))
    return X1, Y1

def generate_tooth_profile(M, Z, ALPHA, X, B, A, D, C, E, SEG_INVOLUTE, SEG_EDGE_R, SEG_ROOT_R, SEG_OUTER, SEG_ROOT):
    """
    Main function to generate a single gear tooth profile by calling all necessary
    calculation and geometry generation sub-functions.
    """
    Z_calc, X_calc, B_calc, A_calc, D_calc, C_calc, E_calc = gear_math.handle_internal_gear_parameters(Z, X, B, A, D, C, E)

    ALPHA_0, ALPHA_M, ALPHA_IS, THETA_IS, THETA_IE, ALPHA_E, E_calc, P_ANGLE, ALIGN_ANGLE = gear_math.calculate_gear_parameters(
        M, Z_calc, ALPHA, X_calc, B_calc, A_calc, D_calc, C_calc, E_calc
    )

    # Generate one flank of the tooth
    X11, Y11 = involute_curve(M, Z_calc, SEG_INVOLUTE, THETA_IS, THETA_IE, ALPHA_0, ALPHA_IS)

    # Generate the symmetrical other flank
    X12, Y12 = transformations.reflect_y(X11, Y11)

    # Calculate points for edge rounding
    X_E = M * ((Z_calc / 2) + X_calc + A_calc) * np.cos(ALPHA_E)
    Y_E = M * ((Z_calc / 2) + X_calc + A_calc) * np.sin(ALPHA_E)
    X_E0 = M * (Z_calc / 2 + X_calc + A_calc - E_calc) * np.cos(ALPHA_E)
    Y_E0 = M * (Z_calc / 2 + X_calc + A_calc - E_calc) * np.sin(ALPHA_E)

    # Generate curve segments
    X21, Y21 = edge_round_curve(M, E_calc, X11, Y11, X_E, Y_E, X_E0, Y_E0, SEG_EDGE_R)
    X22, Y22 = transformations.reflect_y(X21, Y21)

    ALPHA_TS = (2 * (C_calc * (1 - np.sin(ALPHA_0)) - D_calc) * np.sin(ALPHA_0) + B_calc) / (Z_calc * np.cos(ALPHA_0)) - 2 * C_calc * np.cos(ALPHA_0) / Z_calc + np.pi / (2 * Z_calc)
    THETA_TE = 2 * C_calc * np.cos(ALPHA_0) / Z_calc - 2 * (D_calc - X_calc - C_calc * (1 - np.sin(ALPHA_0))) * np.cos(ALPHA_0) / (Z_calc * np.sin(ALPHA_0))

    X31, Y31 = root_round_curve(M, Z_calc, X_calc, D_calc, C_calc, B_calc, THETA_TE, ALPHA_TS, SEG_ROOT_R)
    X32, Y32 = transformations.reflect_y(X31, Y31)

    X41, Y41 = outer_arc(M, Z_calc, X_calc, A_calc, ALPHA_E, ALPHA_M, SEG_OUTER)
    X42, Y42 = transformations.reflect_y(X41, Y41)

    X51, Y51 = root_arc(M, Z_calc, X_calc, D_calc, ALPHA_TS, SEG_ROOT)
    X52, Y52 = transformations.reflect_y(X51, Y51)

    # Combine all segments into a single tooth profile
    X_tooth, Y_tooth = combine_tooth_profile(
        X11, Y11, X21, Y21, X31, Y31, X41, Y41, X51, Y51,
        X12, Y12, X22, Y22, X32, Y32, X42, Y42, X52, Y52
    )

    return X_tooth, Y_tooth, Z_calc, P_ANGLE, ALIGN_ANGLE