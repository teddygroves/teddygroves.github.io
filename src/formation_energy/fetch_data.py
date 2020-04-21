import pandas as pd
from equilibrator_cache import create_compound_cache_from_quilt
import component_contribution
import quilt


QUILT_PACKAGE_VERSION = '0.2.9'

def fetch_data(quilt_pkg):
    ccache = create_compound_cache_from_quilt(version=QUILT_PACKAGE_VERSION)
    con = ccache.engine
    return {
        'compounds': pd.read_sql_table('compounds', con=con),
        'compound_identifiers': pd.read_sql_table('compound_identifiers', con=con),
        'compound_microspecies': pd.read_sql_table('compound_microspecies', con=con),
        'registries': pd.read_sql_table('registries', con=con),
        'formation_measurements': quilt_pkg.train.formation_energies_transformed(),
        'redox_measurements': quilt_pkg.train.redox(),
        'tecrdb_measurements': quilt_pkg.train.TECRDB(),
    }


if __name__ == "__main__":
    try:
        quilt_pkg = quilt.load('equilibrator/component_contribution')
    except:
        quilt.install(
            package=component_contribution.DEFAULT_QUILT_PKG,
            version=QUILT_PACKAGE_VERSION,
            force=True
        )
        quilt_pkg = quilt.load('equilibrator/component_contribution')

    dfs = fetch_data(quilt_pkg)

    for df_name, df in dfs.items():
        df.to_csv(f'data/{df_name}.csv')
