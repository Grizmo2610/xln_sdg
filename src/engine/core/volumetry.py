from __future__ import annotations

import math
import numpy as np

from config import propensity as prop
from config.constant import VOLUMETRY_NOISE_PCT
from config.random import rng


class VolumetryManager:
    """
    Calculate the number of records to generate (seed or daily).

    Usage:
        vm = VolumetryManager(init_customers=1000)

        # For seed:
        n_contract = vm.get_n("DIM_XLN_CONTRACT", is_seed=True)

        # For daily:
        n_txn = vm.get_n("FCT_XLN_LOAN_TXN", is_seed=False)
    """

    def __init__(self, init_customers: int) -> None:
        """
        Args:
            init_customers: INIT_CUSTOMERS from config/basic.py - anchor for RATIOS.
        """
        self._init_customers = init_customers

    # Public API

    def get_n(self, table_name: str, *, is_seed: bool, noise: bool = True) -> int:
        """
        Return the number of records needed for `table_name` in this run.

        Args:
            table_name: table name (UPPER, matches key in RATIOS/DAILY_RATES).
            is_seed:    True -> use RATIOS * INIT_CUSTOMERS; False -> use DAILY_RATES.
            noise:      True -> add +/-5% noise (Normal); False -> return base value.

        Returns:
            int >= 0. Result is 0 when table is not in config (static dims, etc).

        Raises:
            KeyError: if table_name does not exist in RATIOS or DAILY_RATES.
        """
        base = self._base_count(table_name, is_seed=is_seed)
        if base == 0:
            return 0
        if not noise:
            return base
        return self._apply_noise(base)

    def get_seed_target(self, table_name: str, *, hist_rate: float | None = None) -> int:
        """
        For SCD2 dim seeding: calculate number of records needed to reach desired active count
        after having hist_rate % historical records.

        Formula: target = desired_active / (1 - hist_rate)

        Args:
            table_name: SCD2 table name.
            hist_rate:  override HIST_RATE if needed. None -> read from propensity.

        Returns:
            int - total records to generate (including historical).
        """
        desired_active = self.get_n(table_name, is_seed=True, noise=True)
        rate = hist_rate if hist_rate is not None else prop.HIST_RATE.get(table_name, 0.0)
        if rate >= 1.0:
            raise ValueError(f"HIST_RATE={rate} for {table_name} must be < 1.0")
        return math.ceil(desired_active / (1.0 - rate))

    def churn_count(self, table_name: str, active_pool_size: int) -> int:
        """
        Calculate number of records to churn (SCD2 close) for the day.

        Formula: floor(SCD2_RATIO[table] * active_pool_size), min 0.
        """
        ratio = prop.SCD2_RATIO.get(table_name, 0.0)
        base = int(ratio * active_pool_size)
        if base == 0:
            return 0
        return self._apply_noise(base)

    # Private helpers

    def _base_count(self, table_name: str, *, is_seed: bool) -> int:
        if is_seed:
            if table_name not in prop.RATIOS:
                raise KeyError(f"VolumetryManager: '{table_name}' not in RATIOS.")
            ratio = prop.RATIOS[table_name]
            return int(ratio * self._init_customers)
        else:
            if table_name not in prop.DAILY_RATES:
                raise KeyError(f"VolumetryManager: '{table_name}' not in DAILY_RATES.")
            return prop.DAILY_RATES[table_name]

    @staticmethod
    def _apply_noise(n: int) -> int:
        """
        Add noise +/-VOLUMETRY_NOISE_PCT (Normal distribution) to n.
        Return int >= 1 if n > 0.
        """
        noise_factor = rng.normal(loc=1.0, scale=VOLUMETRY_NOISE_PCT)
        # clip to ensure non-negative and not excessively high
        noise_factor = float(np.clip(noise_factor, 1.0 - VOLUMETRY_NOISE_PCT * 3, 1.0 + VOLUMETRY_NOISE_PCT * 3))
        result = int(round(n * noise_factor))
        return max(1, result)
