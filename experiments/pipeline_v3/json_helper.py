#!/usr/bin/env python3
"""
Helper to convert numpy types for JSON serialization.
"""

import numpy as np


def convert_for_json(obj):
    """
    Recursively convert numpy types to native Python types.
    """
    if isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_for_json(item) for item in obj]
    else:
        return obj