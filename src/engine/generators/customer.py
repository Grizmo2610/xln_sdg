from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import polars as pl

from engine.core.base import BaseGenerator
from engine.core.pool import PoolRegistry
from engine.core.vn_faker import VietnameseFaker
from engine.core.sampling import SamplingEngine
from engine.config import propensity as prop
from engine.config import listchoice as L
from engine.config.constant import CUST_OPEN_DATE_START_YEAR, EXP_DATE_SENTINEL
from engine.config.random import rng
from engine.schema.columns import (
    CUST_KEY, CUSTOMER, SHORT_NAME, CUSTOMER_CLASS,
    CONTACT_DATE, PORTFOLIO, DISTRICT_CODE, DISTRICT_NAME, CITY_CODE, CITY_NAME,
    STATUS_DATE, EMPLOYMENT, CUSTOMER_GROUP, SEAB_CU_SEGMENT,
    SECTOR, ACCOUNT_OFFICER, ACCOUNT_OFFICER_NAME, EFF_DATE, EXP_DATE,
    DATE_OF_BIRTH, GENDER, LEGAL_ID, LEGAL_DOC_NAME,
    LEGAL_ISS_DATE, PHONE_T24, EMAIL_T24, ADDRESS_T24, SB_ID,
    CONTRACT_ID, CONTRACT, DATASOURCE, CONTRACT_REF,
    CATEGORY, CURRENCY, COLLATERAL_DESC, VALUE_DATE, MATURITY_DATE,
    INT_LIQ_ACCT, MORTGAGE_ACCOUNT, CHRG_LIQ_ACCT, SECURED, CO_CODE, REMARKS,
    FREQUENCY, FREQUENCY_DAY, FREQUENCY_PR, TERM, LIMIT_REF, SEAB_LOS_ID,
    REF_CONTRACT_REF, SOURCE_TYPE, CAMPAIGN_ID,
    REF_VALUE_DATE, REF_MAT_DATE, REF_CONTRACT_AMT, REF_CONTRACT_CCY,
)

_faker = VietnameseFaker(seed=42)

# Email domains thực tế hơn
_EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]


def _rid(prefix: str = "", n: int = 8) -> str:
    return prefix + "".join(str(rng.integers(0, 10)) for _ in range(n))


def _rand_dates(start: date, end: date, n: int) -> list[date]:
    arr = SamplingEngine.random_dates(
        np.datetime64(start, "D"), np.datetime64(end, "D"), n
    )
    return [d.astype("datetime64[ms]").astype(object) for d in arr]


def _name_to_email(name: str, domain: str) -> str:
    """NGUYEN VAN AN → nguyenvanan@gmail.com"""
    parts = name.lower().split()
    return "".join(parts) + "@" + domain


class CustomerGenerator(BaseGenerator):

    def required_pools(self) -> list[str]:
        return []

    def generate(
        self,
        run_date: date,
        pool: PoolRegistry,
        n: int,
        sk_offset_cust: int = 0,
        sk_offset_contract: int = 0,
    ) -> dict[str, pl.DataFrame]:

        if n <= 0:
            e = pl.DataFrame()
            return {"CUST": e, "CUST_PII": e, "CONTRACT": e, "_mapping": e}

        cfg = prop.get_monthly(run_date.month)

        # ---- vectorised demographics ----
        city_idx   = SamplingEngine.weighted_choice(list(range(len(L.CITY_LIST))), cfg["CITY_WEIGHTS"], n)
        cities     = [L.CITY_LIST[i] for i in city_idx]
        cc         = np.array([c[0] for c in cities])
        cn         = np.array([c[1] for c in cities])
        dc         = np.array([c[2] for c in cities])
        dn         = np.array([c[3] for c in cities])

        genders    = SamplingEngine.sample_gender(n, cfg["FEMALE_RATIO"])
        names      = _faker.gen_full_name(genders)          # ASCII UPPERCASE Vietnamese names
        dobs       = _faker.gen_dob(min_age=22, max_age=65, n=n)
        phones     = _faker.gen_phone(cc)
        addresses  = _faker.gen_address(cc)
        cccd       = _faker.gen_cccd(
            city_code=cc, gender=genders,
            birth_year=np.array([int(d[:4]) for d in dobs]),
        )
        open_dates = _rand_dates(date(CUST_OPEN_DATE_START_YEAR, 1, 1), run_date, n)
        cls_arr    = SamplingEngine.weighted_choice(L.CUSTOMER_CLASSES, L.CUSTOMER_CLASS_WEIGHTS, n)
        grp_arr    = SamplingEngine.weighted_choice(L.CUSTOMER_GROUPS,  L.CUSTOMER_GROUP_WEIGHTS, n)
        seg_arr    = SamplingEngine.uniform_choice(L.SEGMENTS, n)
        sec_arr    = SamplingEngine.uniform_choice(L.SECTORS,  n)
        emp_arr    = SamplingEngine.weighted_choice(L.EMPLOYMENTS, [0.9, 0.1], n)
        email_dom  = SamplingEngine.uniform_choice(_EMAIL_DOMAINS, n)

        ds_pool    = SamplingEngine.weighted_choice(L.DATASOURCES,  cfg["DATASOURCE_WEIGHTS"],  n * 3)
        stp_pool   = SamplingEngine.weighted_choice(L.SOURCE_TYPES, cfg["SOURCE_TYPE_WEIGHTS"], n * 3)
        ds_idx     = 0

        cust_rows : list[dict] = []
        pii_rows  : list[dict] = []
        con_rows  : list[dict] = []
        map_rows  : list[dict] = []
        con_sk = sk_offset_contract

        for i in range(n):
            sk        = sk_offset_cust + i + 1
            cust_id   = _rid("C")
            name      = str(names[i])          # e.g. "NGUYEN VAN AN"
            od        = open_dates[i]
            city_code = str(cc[i])
            email     = _name_to_email(name, str(email_dom[i]))

            cust_rows.append({
                CUST_KEY:             sk,
                CUSTOMER:             cust_id,
                SHORT_NAME:           name,
                CUSTOMER_CLASS:       str(cls_arr[i]),
                CONTACT_DATE:         od,
                PORTFOLIO:            _rid("PF", 4),
                DISTRICT_CODE:        str(dc[i]),
                DISTRICT_NAME:        str(dn[i]),
                CITY_CODE:            city_code,
                CITY_NAME:            str(cn[i]),
                STATUS_DATE:          od,
                EMPLOYMENT:           str(emp_arr[i]),
                CUSTOMER_GROUP:       (str(grp_arr[i]) or None),
                SEAB_CU_SEGMENT:      str(seg_arr[i]),
                SECTOR:               str(sec_arr[i]),
                ACCOUNT_OFFICER:      _rid("AO", 4),
                ACCOUNT_OFFICER_NAME: f"RM_{_rid('', 4)}",
                EFF_DATE:             od,
                EXP_DATE:             EXP_DATE_SENTINEL,
            })
            pii_rows.append({
                CUST_KEY:       sk,
                CUSTOMER:       cust_id,
                DATE_OF_BIRTH:  date.fromisoformat(str(dobs[i])),
                GENDER:         str(genders[i]),
                LEGAL_ID:       str(cccd[i]),
                LEGAL_DOC_NAME: "CCCD",
                LEGAL_ISS_DATE: od,
                PHONE_T24:      str(phones[i]),
                EMAIL_T24:      email,
                ADDRESS_T24:    str(addresses[i]),
                SB_ID:          None,
                EFF_DATE:       od,
                EXP_DATE:       EXP_DATE_SENTINEL,
            })

            n_con = int(rng.choice(cfg["CONTRACT_COUNT_POOL"]))
            for _ in range(n_con):
                con_sk += 1
                cid     = _rid("HD")
                ds      = str(ds_pool[ds_idx % len(ds_pool)])
                stp     = str(stp_pool[ds_idx % len(stp_pool)])
                ds_idx += 1
                months  = int(rng.choice([12, 24, 36, 60, 84]))
                vd      = od
                md      = vd + timedelta(days=months * 30)
                freq    = str(rng.choice(L.FREQ_CODES))

                con_rows.append({
                    CONTRACT_ID:      con_sk,
                    CONTRACT:         cid,
                    DATASOURCE:       ds,
                    CONTRACT_REF:     _rid("REF"),
                    CATEGORY:         str(rng.choice(L.CATEGORIES)),
                    CURRENCY:         "VND",
                    COLLATERAL_DESC:  None,
                    VALUE_DATE:       vd,
                    MATURITY_DATE:    md,
                    INT_LIQ_ACCT:     _rid("ACC"),
                    MORTGAGE_ACCOUNT: None,
                    CHRG_LIQ_ACCT:    _rid("ACC"),
                    SECURED:          str(rng.choice(L.SECURED_VALS)),
                    CO_CODE:          city_code,
                    REMARKS:          None,
                    FREQUENCY:        freq,
                    FREQUENCY_DAY:    str(int(rng.integers(1, 29))),
                    FREQUENCY_PR:     freq,
                    TERM:             f"{months}M",
                    LIMIT_REF:        None,
                    SEAB_LOS_ID:      _rid("LOS"),
                    REF_CONTRACT_REF: None,
                    SOURCE_TYPE:      stp,
                    EFF_DATE:         vd,
                    EXP_DATE:         EXP_DATE_SENTINEL,
                    CAMPAIGN_ID:      None,
                    REF_VALUE_DATE:   None,
                    REF_MAT_DATE:     None,
                    REF_CONTRACT_AMT: None,
                    REF_CONTRACT_CCY: None,
                })
                map_rows.append({CONTRACT: cid, CUSTOMER: cust_id})

        return {
            "CUST":     pl.DataFrame(cust_rows).with_columns(pl.col(CUST_KEY).cast(pl.Int64)),
            "CUST_PII": pl.DataFrame(pii_rows).with_columns(pl.col(CUST_KEY).cast(pl.Int64)),
            "CONTRACT": pl.DataFrame(con_rows).with_columns(pl.col(CONTRACT_ID).cast(pl.Int64)),
            "_mapping": pl.DataFrame(map_rows) if map_rows
                        else pl.DataFrame(schema={CONTRACT: pl.Utf8, CUSTOMER: pl.Utf8}),
        }