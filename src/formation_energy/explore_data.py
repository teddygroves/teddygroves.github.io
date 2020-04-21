from matplotlib import pyplot as plt
from legendre import R
import numpy as np
import pandas as pd
from equilibrator_cache import FARADAY
plt.style.use('sparse.mplstyle')


def load_data():
    return {
        'tecrdb': (
            pd.read_csv('data/tecrdb_measurements.csv', index_col=0)
            .dropna(subset=['K_prime'])
        ),
        'tecrdb_processed': (
            pd.read_csv('data/tecrdb_measurements_processed.csv', index_col=0)
        ),
        'formation': (
            pd.read_csv('data/formation_measurements.csv', index_col=0)
            .dropna(subset=['standard_dg_prime'])
        ),
        'redox': (
            pd.read_csv('data/redox_measurements.csv', index_col=0)
        ),
    }


def plot_k_prime(measurements, colorcol, filename):
    f, ax = plt.subplots(figsize=[10, 5])
    f.suptitle("TECRDB raw K prime measurements")
    order = (
        measurements.groupby('reaction')['K_prime']
        .transform('mean')
        .rank(method='dense')
    )
    ax.semilogx()
    ax.yaxis.set_major_locator(plt.NullLocator())
    ax.set_xlabel("Raw measured K prime (kJ per mole)")
    s = ax.scatter(
        measurements['K_prime'], order, c=measurements[colorcol], cmap='viridis'
    )
    cbar = f.colorbar(s)
    cbar.set_label(colorcol)
    f.savefig(
        f'../../img/{filename}', facecolor=f.get_facecolor(), bbox_inches = "tight"
    )
    return ax



def plot_dg_prime(measurements, colorcol, filename):
    measurements['standard_dg_prime'] = (
        -R * measurements['temperature'] * np.log(measurements['K_prime'])
    )
    f, ax = plt.subplots(figsize=[10, 5])
    f.suptitle("TECRDB ΔGr' measurements")
    order = (
        measurements.groupby('reaction')['standard_dg_prime']
        .transform('mean')
        .rank(method='dense')
    )
    ax.yaxis.set_major_locator(plt.NullLocator())
    ax.set_xlabel("Measured ΔGr' (kJ per mole)")
    s = ax.scatter(
        measurements['standard_dg_prime'],
        order,
        c=measurements[colorcol], cmap='viridis'
    )
    cbar = f.colorbar(s)
    cbar.set_label(colorcol)
    f.savefig(
        f'../../img/{filename}', facecolor=f.get_facecolor(), bbox_inches = "tight"
    )
    return ax


def plot_dg_prime_formation(measurements, colorcol, filename):
    f, ax = plt.subplots(figsize=[10, 5])
    f.suptitle("ΔGf' measurements")
    order = (
        measurements.groupby('cid')['standard_dg_prime']
        .transform('mean')
        .rank(method='dense')
    )
    ax.yaxis.set_major_locator(plt.NullLocator())
    ax.set_xlabel("Measured ΔGf' (kJ per mole)")
    s = ax.scatter(
        measurements['standard_dg_prime'],
        order,
        c=measurements[colorcol], cmap='viridis'
    )
    cbar = f.colorbar(s)
    cbar.set_label(colorcol)
    f.savefig(
        f'../../img/{filename}', facecolor=f.get_facecolor(), bbox_inches = "tight"
    )
    return ax


def plot_standard_dg(measurements, colorcol, filename):
    f, ax = plt.subplots(figsize=[10, 5])
    f.suptitle(
        "TECRDB ΔGr measurements\n"
        "obtained from condition-specific K's using the inverse Legendre "
        "transform method", horizontalalignment='left', x=0.02
    )
    order = (
        measurements.groupby('reaction')['standard_dg']
        .transform('mean')
        .rank(method='dense')
    )
    ax.yaxis.set_major_locator(plt.NullLocator())
    ax.set_xlabel("ΔGr (kJ per mole)")
    s = ax.scatter(
        measurements['standard_dg'],
        order,
        c=measurements[colorcol], cmap='viridis'
    )
    cbar = f.colorbar(s)
    cbar.set_label(colorcol)
    f.savefig(
        f'../../img/{filename}', facecolor=f.get_facecolor(), bbox_inches = "tight"
    )
    return ax


def plot_dg_prime_redox(measurements, colorcol, filename):
    d_nh = measurements['nH_red'] - measurements['nH_ox']
    d_charge = measurements['charge_red'] - measurements['charge_ox']
    d_e = d_nh - d_charge 
    measurements['standard_dg_prime'] = (
        -FARADAY.m * measurements['standard_E_prime'] * d_e
    )
    f, ax = plt.subplots(figsize=[10, 5])
    f.suptitle("Redox reaction ΔGr' measurements")
    order = (
        measurements.groupby('name')['standard_dg_prime']
        .transform('mean')
        .rank(method='dense')
    )
    ax.yaxis.set_major_locator(plt.NullLocator())
    ax.set_xlabel("Measured ΔGr' (kJ per mole)")
    s = ax.scatter(
        measurements['standard_dg_prime'],
        order,
        c=measurements[colorcol], cmap='viridis'
    )
    for (i, row), o in zip(measurements.iterrows(), order):
        ax.text(row['standard_dg_prime'], o, row['name'])
    cbar = f.colorbar(s)
    cbar.set_label(colorcol)
    f.savefig(
        f'../../img/{filename}', facecolor=f.get_facecolor(), bbox_inches = "tight"
    )
    return ax


def main():
    data = load_data()
    tecrdb = data['tecrdb']
    processed = data['tecrdb_processed']
    formation = data['formation']
    redox = data['redox']
    plot_k_prime(tecrdb, 'p_h', filename='tecrdb_kprime.png')
    plot_dg_prime(tecrdb, 'p_h', filename='tecrdb_dgprime.png')
    plot_dg_prime_formation(formation, 'p_h', filename='formation_dgprime.png')
    plot_standard_dg(processed, 'ddg_over_rt', filename='tecrdb_standard_dg.png')
    plot_dg_prime_redox(redox, 'p_h', filename='redox_dgprime.png')
    plt.close('all')


if __name__ == "__main__":
    main()
