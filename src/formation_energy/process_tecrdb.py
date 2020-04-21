from equilibrator_cache import create_compound_cache_from_quilt
from equilibrator_cache.reaction import Reaction
from equilibrator_cache.compound_cache import CompoundCache
from math import isnan
import numpy as np
import pandas as pd
from reaction_balancing import balance_reaction
from legendre import get_ddg_over_rt_for_reaction, R

RAW_MEASUREMENTS_FILEPATH = 'data/tecrdb_measurements.csv'
OUTPUT_FILEPATH = 'data/tecrdb_measurements_processed.csv'
NON_NULL = ['reaction_balanced', 'K_prime', 'p_h', 'temperature']
DEFAULT_IONIC_STRENGTH = 0.25
DEFAULT_P_MG = 14  # i.e. a negligible concentration of Mg2+

def main():
    ccache = create_compound_cache_from_quilt(version="0.2.9")
    m = pd.read_csv(RAW_MEASUREMENTS_FILEPATH, index_col=0)
    m['reaction_balanced'] = m['reaction'].apply(
        lambda s: balance_reaction(
            Reaction.parse_formula(ccache.get_compound, s), ccache
        )
    )
    m = m.dropna(subset=NON_NULL).copy()
    m['ionic_strength'] = m['ionic_strength'].fillna(DEFAULT_IONIC_STRENGTH)
    m['p_mg'] = m['p_mg'].fillna(DEFAULT_P_MG)
    m['standard_dg_prime'] = -R * m['temperature'] * np.log(m['K_prime'])
    m['ddg_over_rt'] = m.apply(
        lambda row: get_ddg_over_rt_for_reaction(
            row['reaction_balanced'],
            row['p_h'],
            row['ionic_strength'],
            row['temperature'],
            row['p_mg']
        ), axis=1
    )
    m['ddg_over_rt_default_mg'] = m.apply(
        lambda row: get_ddg_over_rt_for_reaction(
            row['reaction_balanced'],
            row['p_h'],
            row['ionic_strength'],
            row['temperature'],
            DEFAULT_P_MG
        ), axis=1
    )
    m['standard_dg'] = m['standard_dg_prime'] - m['ddg_over_rt'] * R * m['temperature']
    m['standard_dg_default_mg'] = (
        m['standard_dg_prime'] - m['ddg_over_rt_default_mg'] * R * m['temperature']
    )
    m.to_csv(OUTPUT_FILEPATH)
    return m


if __name__ == "__main__":
    main()
