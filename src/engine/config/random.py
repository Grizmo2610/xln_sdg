from __future__ import annotations

import numpy as np

_seed: int = 42
rng: np.random.Generator = np.random.default_rng(_seed)


def init_seed(seed: int) -> None:
    """Re-initialise the global RNG. Call before any generation."""
    global rng, _seed
    _seed = seed
    rng = np.random.default_rng(seed)
