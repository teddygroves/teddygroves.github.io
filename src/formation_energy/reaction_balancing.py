from equilibrator_cache.reaction import Reaction
from equilibrator_cache.compound_cache import CompoundCache
from typing import Union
import warnings


def balance_reaction(rxn: Reaction, ccache: CompoundCache) -> Union[Reaction, None]:
        """Try balancing the reaction with H2O and H+.
        
        Copied from here with minor changes:
        https://gitlab.com/equilibrator/equilibrator-cache/-/blob/develop/src/equilibrator_cache/reaction.py

        """

        proton, water = ccache.proton, ccache.water

        if rxn.is_balanced(ignore_atoms=[]):
            # the reaction is already balanced, nothing to do
            return rxn

        elif rxn.is_balanced(ignore_atoms=["H"]):
            # the reaction just needs to be balanced by protons
            return rxn.balance_with_compound(proton, ignore_atoms=[])

        elif rxn.is_balanced(ignore_atoms=["H", "O", "e-"]):
            # we need to first balance the O atoms using water, and then
            # balance the H atoms using protons
            return (
                rxn
                .balance_with_compound(water, ignore_atoms=["H"])
                .balance_with_compound(proton, ignore_atoms=[])
            )

        else:
            # this reaction cannot be balanced only by H2O and H+, because
            # elements other than e-, O, and H are not balanced
            warnings.warn("This reaction cannot be balanced: " f"{rxn}")
            return None

