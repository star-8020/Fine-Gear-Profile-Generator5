"""Core calculation orchestrator for the Fine Gear Profile Generator."""

from __future__ import annotations

from typing import Dict, Any

from . import gear_math, geometry_generator


def generate_gear_pair(params: Dict[str, Any]) -> Dict[str, Any]:
    """Compute all derived data required to describe a gear pair."""
    contact_ratio, center_dist = gear_math.calculate_contact_ratio(
        params['M'],
        params['Z'],
        params['z2'],
        params['X'],
        params['x2'],
        params['ALPHA'],
        params['A']
    )

    undercut_status1 = gear_math.check_undercut(
        params['Z'], params['ALPHA'], params['X'], params['A']
    )
    undercut_status2 = gear_math.check_undercut(
        params['z2'], params['ALPHA'], params['x2'], params['A']
    )

    gear1_profile = geometry_generator.generate_tooth_profile(
        params['M'], params['Z'], params['ALPHA'], params['X'], params['B'],
        params['A'], params['D'], params['C'], params['E'],
        params['SEG_INVOLUTE'], params['SEG_EDGE_R'], params['SEG_ROOT_R'],
        params['SEG_OUTER'], params['SEG_ROOT']
    )

    gear2_profile = geometry_generator.generate_tooth_profile(
        params['M'], params['z2'], params['ALPHA'], params['x2'], params['B'],
        params['A'], params['D'], params['C'], params['E'],
        params['SEG_INVOLUTE'], params['SEG_EDGE_R'], params['SEG_ROOT_R'],
        params['SEG_OUTER'], params['SEG_ROOT']
    )

    return {
        'analysis': {
            'contact_ratio': contact_ratio,
            'center_distance': center_dist,
        },
        'gear1': {
            'profile': gear1_profile,
            'undercut_status': undercut_status1,
        },
        'gear2': {
            'profile': gear2_profile,
            'undercut_status': undercut_status2,
        },
    }
