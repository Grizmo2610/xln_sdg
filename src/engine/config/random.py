"""
config/random.py
Global NumPy RNG singleton.
Import `rng` from here everywhere — never create local np.random instances.
Seed is set once at startup via init_seed(); default seed = 42 for reproducibility.
"""
from __future__ import annotations

import numpy as np

_seed: int = 42
rng: np.random.Generator = np.random.default_rng(_seed)


def init_seed(seed: int) -> None:
    """Re-initialise the global RNG with a new seed. Call before any generation."""
    global rng, _seed
    _seed = seed
    rng = np.random.default_rng(seed)
