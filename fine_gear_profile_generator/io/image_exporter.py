import os
import matplotlib.pyplot as plt
from ..core import transformations

def export_gear_pair_to_image(working_dir, gear1_data, gear2_data, center_dist, m_val, z1_val, z2_val, x_offset=0.0, y_offset=0.0):
    """
    Generates and saves a PNG image preview of the gear pair.

    Args:
        working_dir (str): Directory to save the image.
        gear1_data (tuple): (X_tooth, Y_tooth, Z, P_ANGLE, ALIGN_ANGLE) for gear 1.
        gear2_data (tuple): (X_tooth, Y_tooth, Z, P_ANGLE, ALIGN_ANGLE) for gear 2.
        center_dist (float): Distance between gear centers.
        m_val (float): Module of the gears.
        z1_val (int): Number of teeth for gear 1.
        z2_val (int): Number of teeth for gear 2.
        x_offset (float): X-coordinate of the center of the first gear.
        y_offset (float): Y-coordinate of the center of the first gear.
    """
    if 'DISPLAY' not in os.environ and 'XDG_SESSION_TYPE' not in os.environ:
        plt.switch_backend('Agg')

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    ax.set_title('Fine Gear Profile Generator - Gear Pair Preview')
    ax.grid(True)

    # --- Plot Gear 1 ---
    X_tooth1, Y_tooth1, Z1, P_ANGLE1, ALIGN_ANGLE1 = gear1_data
    X_rot1, Y_rot1 = transformations.rotate(X_tooth1, Y_tooth1, ALIGN_ANGLE1)
    for i in range(int(Z1)):
        X_temp, Y_temp = transformations.rotate(X_rot1, Y_rot1, P_ANGLE1 * i)
        X_final, Y_final = transformations.translate(X_temp, Y_temp, x_offset, y_offset)
        ax.plot(X_final, Y_final, '-', linewidth=1.5, color='blue')

    # --- Plot Gear 2 ---
    X_tooth2, Y_tooth2, Z2, P_ANGLE2, ALIGN_ANGLE2 = gear2_data
    import numpy as np
    initial_rotation2 = np.pi + (np.pi / Z2)
    X_rot2, Y_rot2 = transformations.rotate(X_tooth2, Y_tooth2, ALIGN_ANGLE2 + initial_rotation2)
    for i in range(int(Z2)):
        X_temp, Y_temp = transformations.rotate(X_rot2, Y_rot2, P_ANGLE2 * i)
        X_final, Y_final = transformations.translate(X_temp, Y_temp, x_offset + center_dist, y_offset)
        ax.plot(X_final, Y_final, '-', linewidth=1.5, color='red')

    # Set plot limits for a good view
    ax.set_xlim(-m_val * z1_val / 1.5, center_dist + m_val * z2_val / 1.5)
    ax.set_ylim(-m_val * max(z1_val, z2_val) * 1.2, m_val * max(z1_val, z2_val) * 1.2)

    # Save the figure
    output_path = os.path.join(working_dir, 'Result1.png')
    try:
        fig.savefig(output_path, dpi=100)
    except Exception as e:
        print(f"Error saving image: {e}")
    finally:
        plt.close(fig) # Ensure the figure is closed to free memory