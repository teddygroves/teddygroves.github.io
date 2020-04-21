"""Functions for doing Legendre transforms"""
import numpy as np
from equilibrator_cache.models import Compound, CompoundMicrospecies
from equilibrator_cache.reaction import Reaction
from scipy.special import logsumexp


R = 8.31e-3                                       # kJ / mol / K
standard_dg_formation_mg = -455.3                 # kJ/mol (Mg2+ formation energy)


def dh(ionic_strength: float, temperature: float) -> float:
    """Debeye-Hueckel factor for finding an ionic strength/temperature effect."""
    _a1 = 1.108
    _a2 = 1.546e-3
    _a3 = 5.959e-6
    B = 1.6
    alpha = _a1 - _a2 * temperature + _a3 * temperature ** 2
    return 0.0 if ionic_strength <= 0.0 else (
        alpha * ionic_strength ** 0.5 / (1.0 + B * ionic_strength ** 0.5)
    )


def legendre_transform(
    p_h: float,
    ionic_strength: float,
    temperature: float,
    p_mg: float,
    num_protons: float,
    charge: float,
    num_magnesiums: float,
):
    log10 = np.log(10)
    RT = R * temperature
    ph_part = num_protons * log10 * p_h
    dh_part = (num_protons - charge ** 2) * dh(ionic_strength, temperature)
    mg_part = 0 if num_magnesiums <= 0 else num_magnesiums * (
        p_mg * log10 - standard_dg_formation_mg / RT
    )
    return ph_part + dh_part + mg_part


def get_ddg_over_rt_for_microspecies(
    ms: CompoundMicrospecies,
    p_h: float,
    ionic_strength: float,
    temperature: float,
    p_mg: float
):
    conditions = p_h, ionic_strength, temperature, p_mg
    ms_facts = ms.number_protons, ms.charge, ms.number_magnesiums
    return ms.ddg_over_rt + legendre_transform(*conditions, *ms_facts)


def get_ddg_over_rt_for_compound(
    cpd: Compound,
    p_h: float,
    ionic_strength: float,
    temperature: float,
    p_mg: float
):
    conditions = p_h, ionic_strength, temperature, p_mg
    return -logsumexp([
        -1 * get_ddg_over_rt_for_microspecies(ms, *conditions)
        for ms in cpd.microspecies
    ])


def get_ddg_over_rt_for_reaction(
        rxn: Reaction,
        p_h: float,
        ionic_strength: float,
        temperature: float,
        p_mg: float
):
    conditions = p_h, ionic_strength, temperature, p_mg
    return sum([
        stoichiometric_coef * get_ddg_over_rt_for_compound(cpd, *conditions)
        for cpd, stoichiometric_coef in rxn.items(protons=False)
    ])
