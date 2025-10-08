import ezdxf
import numpy as np
import os
from ..core import transformations

def export_gear_pair_to_dxf(working_dir, gear1_data, gear2_data, center_dist, x_offset, y_offset):
    """
    Exports a pair of gears to a DXF file.

    Args:
        working_dir (str): The directory to save the file in.
        gear1_data (tuple): Contains (X_tooth, Y_tooth, Z, P_ANGLE, ALIGN_ANGLE) for gear 1.
        gear2_data (tuple): Contains (X_tooth, Y_tooth, Z, P_ANGLE, ALIGN_ANGLE) for gear 2.
        center_dist (float): The distance between the centers of the two gears.
        x_offset (float): The X-coordinate of the center of the first gear.
        y_offset (float): The Y-coordinate of the center of the first gear.
    """
    doc = ezdxf.new('R2000')
    msp = doc.modelspace()

    # --- Draw Gear 1 ---
    X_tooth1, Y_tooth1, Z1, P_ANGLE1, ALIGN_ANGLE1 = gear1_data
    # First, align the tooth profile
    X_rot1, Y_rot1 = transformations.rotate(X_tooth1, Y_tooth1, ALIGN_ANGLE1)
    # Then, create the full gear by rotating the single tooth
    for i in range(int(Z1)):
        X_temp, Y_temp = transformations.rotate(X_rot1, Y_rot1, P_ANGLE1 * i)
        # Finally, move the gear to its final position
        X_final, Y_final = transformations.translate(X_temp, Y_temp, x_offset, y_offset)
        msp.add_lwpolyline(list(zip(X_final, Y_final)), close=True, dxfattribs={'color': 5})  # Blue

    # --- Draw Gear 2 ---
    X_tooth2, Y_tooth2, Z2, P_ANGLE2, ALIGN_ANGLE2 = gear2_data
    # The second gear needs an initial rotation to mesh correctly
    initial_rotation2 = np.pi + (np.pi / Z2)
    # First, align the tooth profile with the initial meshing rotation
    X_rot2, Y_rot2 = transformations.rotate(X_tooth2, Y_tooth2, ALIGN_ANGLE2 + initial_rotation2)
    # Then, create the full gear
    for i in range(int(Z2)):
        X_temp, Y_temp = transformations.rotate(X_rot2, Y_rot2, P_ANGLE2 * i)
        # Finally, move the gear to its final position (offset by center distance)
        X_final, Y_final = transformations.translate(X_temp, Y_temp, x_offset + center_dist, y_offset)
        msp.add_lwpolyline(list(zip(X_final, Y_final)), close=True, dxfattribs={'color': 1})  # Red

    # Save the DXF file
    output_path = os.path.join(working_dir, 'Result_Gear_Pair.dxf')
    try:
        doc.saveas(output_path)
    except IOError:
        print(f"Error: Could not save DXF file to {output_path}.")