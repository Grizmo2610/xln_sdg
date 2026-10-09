from __future__ import annotations

import numpy as np
from numpy.random import Generator
from unidecode import unidecode
from faker.providers.person.vi_VN import Provider as VnPersonProvider

from engine.config.constant import FAKER_FEMALE_POOL_SIZE, FAKER_MALE_POOL_SIZE
from engine.config.listchoice import CITY_DISTRICT_MAP, CITY_NAMES

_LAST_NAMES: tuple[str, ...] = VnPersonProvider.last_names
_MIDDLE_NAMES: tuple[str, ...] = VnPersonProvider.middle_names
_FIRST_MALE: tuple[str, ...] = VnPersonProvider.first_names_male
_FIRST_FEMALE: tuple[str, ...] = VnPersonProvider.first_names_female
_FIRST_UNISEX: tuple[str, ...] = VnPersonProvider.first_names_unisex

_FIRST_FEMALE_FULL: tuple[str, ...] = _FIRST_FEMALE + _FIRST_UNISEX

_MIDDLE_NAMES_SINGLE: tuple[str, ...] = tuple(
    w for w in _MIDDLE_NAMES if " " not in unidecode(w).upper()
)

# CITY_LIST uses numeric city codes; the phone/street/CCCD tables below are
# keyed by legacy region keys. Translate numeric -> legacy (unknown -> OTHER).
_CODE_TO_REGION: dict[str, str] = {
    "4": "HN", "8": "HCM", "31": "HP", "511": "DN", "71": "CT",
    "650": "BD", "61": "BH", "72": "LA", "66": "TN", "64": "VT",
}


def _regions(codes) -> np.ndarray:
    """Map array of numeric city codes to legacy region keys."""
    return np.array([_CODE_TO_REGION.get(str(c), "OTHER") for c in codes], dtype=object)


_CITY_TO_PROVINCE_CODE: dict[str, str] = {
    "HN":    "001",
    "HCM":   "079",
    "HP":    "031",
    "DN":    "048",
    "CT":    "092",
    "BD":    "074",
    "BH":    "075",
    "LA":    "080",
    "TN":    "072",
    "VT":    "077",
    "OTHER": "082",
}

_PHONE_PREFIXES: dict[str, list[str]] = {
    "HN":    ["024", "096", "097", "098", "032", "033", "034", "035", "036", "037"],
    "HCM":   ["028", "090", "093", "070", "079", "077", "076", "078", "089"],
    "HP":    ["0225", "091", "094"],
    "DN":    ["0236", "090", "093"],
    "OTHER": ["056", "058", "059", "086", "096", "097", "098"],
}

_STREET_NAMES: dict[str, list[str]] = {
    "HN": [
        "HOAN KIEM", "CAU GIAY", "DONG DA", "HAI BA TRUNG", "BA DINH",
        "TAY HO", "LONG BIEN", "HOANG MAI", "THANH XUAN", "NAM TU LIEM",
    ],
    "HCM": [
        "NGUYEN HUE", "LE LOI", "DINH TIEN HOANG", "VO VAN TAN", "NAM KY KHOI NGHIA",
        "CACH MANG THANG 8", "LY THUONG KIET", "TRAN HUNG DAO", "BUI THI XUAN", "PASTEUR",
    ],
    "HP": [
        "LACH TRAY", "TO HIEU", "TRAN PHU", "NGUYEN TRI PHUONG", "CAU DAT",
    ],
    "DN": [
        "NGUYEN VAN LINH", "LE DUAN", "TRAN PHU", "NUI THANH", "DIEN BIEN PHU",
    ],
    "OTHER": [
        "TRAN HUNG DAO", "NGUYEN HUE", "LE LOI", "PHAN BOI CHAU", "NGUYEN THAI HOC",
    ],
}

_PHONE_PREFIXES_NP: dict[str, np.ndarray] = {k: np.array(v) for k, v in _PHONE_PREFIXES.items()}
_STREET_NAMES_NP: dict[str, np.ndarray]   = {k: np.array(v) for k, v in _STREET_NAMES.items()}
_PHONE_KNOWN: list[str] = [k for k in _PHONE_PREFIXES if k != "OTHER"]
_STREET_KNOWN: list[str] = [k for k in _STREET_NAMES if k != "OTHER"]

_LAST_ARR:  np.ndarray = np.array([unidecode(w).upper() for w in _LAST_NAMES])
_MID_ARR:   np.ndarray = np.array([unidecode(w).upper() for w in _MIDDLE_NAMES_SINGLE])
_FIRST_M:   np.ndarray = np.array([unidecode(w).upper() for w in _FIRST_MALE])
_FIRST_F:   np.ndarray = np.array([unidecode(w).upper() for w in _FIRST_FEMALE_FULL])

KNOWN_PREFIXES: frozenset[str] = frozenset(
    unidecode(p).upper()
    for p in (*VnPersonProvider.prefixes_male, *VnPersonProvider.prefixes_female)
)


def _to_ascii_upper(s: str) -> str:
    return unidecode(s).upper()


class VietnameseFaker:
    """
    Generate fake PII data following Vietnamese standards.

    Uses word lists from Faker's vi_VN provider but composes names
    manually (last + middle + first) to guarantee no honorific prefix
    appears in output.

    Pre-generates name pools at init -> O(1) sampling per record.
    All output is ASCII UPPERCASE (unidecode).
    """

    def __init__(self, seed: int) -> None:
        self.rng: Generator       = np.random.default_rng(seed)
        self._male_pool: np.ndarray   = np.array([])
        self._female_pool: np.ndarray = np.array([])

    def gen_city_code(self, n: int, weights: list[float] | None = None) -> np.ndarray:
        """
        Generate n city codes sampled by weight.

        Args:
            n:       number of records.
            weights: sampling weights aligned to city order.
                     More values than cities -> clip. Fewer -> pad with 0.
                     Does not sum to 1 -> renormalized automatically.
                     None -> uniform.

        Returns:
            np.ndarray[str] shape (n,) of city codes.
        """
        cities = np.array(list(_CITY_TO_PROVINCE_CODE.keys()))
        k = len(cities)

        if weights is None:
            probs = np.full(k, 1.0 / k)
        else:
            w = np.array(weights, dtype=float)
            if len(w) > k:
                w = w[:k]
            elif len(w) < k:
                w = np.pad(w, (0, k - len(w)), constant_values=0.0)
            total = w.sum()
            if total == 0:
                raise ValueError("weights sum to 0 — cannot normalize.")
            probs = w / total

        return cities[self.rng.choice(k, size=n, p=probs)]

    def gen_full_name(self, gender: np.ndarray | list) -> np.ndarray:
        """
        Generate full names for an array of gender values ("M"/"F").
        Returns np.ndarray[str] shape (n,) - ASCII UPPERCASE, no prefix.
        """
        gender_arr = np.asarray(gender)
        n = len(gender_arr)

        if len(self._male_pool) < n:
            self._male_pool = self._build_name_pool("M", n)
        if len(self._female_pool) < n:
            self._female_pool = self._build_name_pool("F", n)

        result = np.empty(n, dtype=self._male_pool.dtype)
        m_mask = gender_arr == "M"
        f_mask = ~m_mask
        nm, nf = int(m_mask.sum()), int(f_mask.sum())

        if nm:
            result[m_mask] = self._male_pool[self.rng.integers(0, len(self._male_pool), size=nm)]
        if nf:
            result[f_mask] = self._female_pool[self.rng.integers(0, len(self._female_pool), size=nf)]

        return result

    def gen_cccd(
        self,
        city_code: str | np.ndarray,
        gender: str | np.ndarray,
        birth_year: int | np.ndarray,
        n: int | None = None,
    ) -> np.ndarray:
        """
        Generate CCCD numbers (12 digits): [province 3][gender 1][birth year 2][random 6].
        Pass array-like inputs to infer n automatically, or pass scalar inputs with explicit n.
        """
        if n is None:
            for x in (city_code, gender, birth_year):
                if isinstance(x, (np.ndarray, list, tuple)):
                    n = len(x)
                    break
            else:
                raise ValueError("Pass at least one array-like argument or provide n explicitly.")

        def _bcast(x, dtype=str):
            val = [x] if np.ndim(x) == 0 else x
            return np.broadcast_to(np.asarray(val, dtype=dtype), (n,))

        city_arr   = _regions(_bcast(city_code, dtype=str))
        gender_arr = _bcast(gender, dtype=str)
        year_arr   = _bcast(birth_year, dtype=int)

        province_codes = np.array([
            _CITY_TO_PROVINCE_CODE.get(c, _CITY_TO_PROVINCE_CODE["OTHER"])
            for c in city_arr
        ])
        gender_digits = np.where(gender_arr == "M", "0", "1")
        year_2digit   = np.char.zfill((year_arr % 100).astype(str), 2)
        random_6      = np.char.zfill(self.rng.integers(0, 1_000_000, size=n).astype(str), 6)

        return np.char.add(
            np.char.add(np.char.add(province_codes, gender_digits), year_2digit),
            random_6,
        )

    def gen_phone(self, city_code: np.ndarray | list) -> np.ndarray:
        """Generate phone numbers for an array of city codes."""
        codes  = np.asarray(city_code).astype(str)
        n      = len(codes)
        result = np.empty(n, dtype=object)

        for region, prefix_arr in _PHONE_PREFIXES_NP.items():
            mask  = (codes == region) if region != "OTHER" else ~np.isin(codes, _PHONE_KNOWN)
            count = int(mask.sum())
            if count == 0:
                continue
            chosen = prefix_arr[self.rng.integers(0, len(prefix_arr), size=count)]
            result[mask] = np.array([
                p + np.char.zfill(str(self.rng.integers(0, 10 ** (10 - len(p)))), 10 - len(p))
                for p in chosen
            ])

        return result.astype(str)

    def gen_address(self, city_code: np.ndarray | list) -> np.ndarray:
        """Generate addresses for an array of city codes. ASCII UPPERCASE, no real PII."""
        raw     = np.asarray(city_code).astype(str)
        codes   = _regions(raw)
        n       = len(codes)
        streets = np.empty(n, dtype=object)

        for region, street_arr in _STREET_NAMES_NP.items():
            mask  = (codes == region) if region != "OTHER" else ~np.isin(codes, _STREET_KNOWN)
            count = int(mask.sum())
            if count == 0:
                continue
            streets[mask] = street_arr[self.rng.integers(0, len(street_arr), size=count)]

        # real city name per row from the original numeric code
        cities = np.array([CITY_NAMES.get(c, CITY_NAMES["OTHER"]) for c in raw], dtype=object)

        house_numbers = self.rng.integers(1, 500, size=n).astype(str)
        return np.char.add(
            np.char.add(house_numbers, " "),
            np.char.add(streets.astype(str), np.char.add(", ", cities.astype(str)))
        )

    def get_district(self, city_code: str) -> tuple[str, str]:
        """Return (DISTRICT_CODE, DISTRICT_NAME) sampled from city_code."""
        districts = CITY_DISTRICT_MAP.get(city_code, CITY_DISTRICT_MAP["OTHER"])
        codes     = list(districts.keys())
        code      = codes[int(self.rng.integers(0, len(codes)))]
        return code, _to_ascii_upper(districts[code])

    def get_city_name(self, city_code: str) -> str:
        """Return ASCII UPPERCASE city name."""
        return CITY_NAMES.get(city_code, CITY_NAMES["OTHER"])

    def gen_dob(self, min_age: int = 22, max_age: int = 65, n: int = 1) -> np.ndarray:
        """Generate n birth date strings 'YYYY-MM-DD'."""
        from datetime import date, timedelta

        today      = date.today()
        earliest   = today - timedelta(days=max_age * 365)
        latest     = today - timedelta(days=min_age * 365)
        total_days = (latest - earliest).days
        offsets    = self.rng.integers(0, total_days + 1, size=n)
        return np.array([(earliest + timedelta(days=int(o))).isoformat() for o in offsets])

    def _build_name_pool(self, gender: str, size: int) -> np.ndarray:
        """Pre-generate name pool: LAST MIDDLE FIRST, no prefix."""
        first_arr = _FIRST_M if gender == "M" else _FIRST_F

        last_picked  = _LAST_ARR[self.rng.integers(0, len(_LAST_ARR),  size=size)]
        mid_picked   = _MID_ARR[self.rng.integers(0, len(_MID_ARR),    size=size)]
        first_picked = first_arr[self.rng.integers(0, len(first_arr),   size=size)]

        return np.char.add(
            np.char.add(last_picked, " "),
            np.char.add(mid_picked, np.char.add(" ", first_picked)),
        )