# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple

from monty.json import MontyDecoder, MSONable
from pydefect.analyzer.band_edge_states import BandEdgeOrbitalInfos
from pydefect.analyzer.defect_energy import DefectEnergySummary
from pydefect.chem_pot_diag.chem_pot_diag import ChemPotDiag
from pydefect.corrections.abstract_correction import Correction
from vise.util.enum import ExtendedEnum
from vise.util.mix_in import ToJsonFileMixIn

decoder = MontyDecoder()


class ColNameMixIn:
    @classmethod
    def col_name(cls):
        name_w_underscore = re.sub("(?<!^)(?=[A-Z])", "_", cls.__name__)
        return name_w_underscore.lower()


@dataclass
class DataclassRoundTrip(ColNameMixIn, MSONable, ToJsonFileMixIn):

    def as_dict(self) -> dict:
        result = {}
        for k, v in asdict(self).items():
            if v is not None:
                try:
                    result[k] = v.as_dict()
                except AttributeError:
                    result[k] = v
        return result

    @classmethod
    def from_dict(cls, d):
        dd = {}
        for k, v in d.items():
            if "@" == k[0]:
                continue
            if isinstance(v, dict) and "@module" in v:
                dd[k] = decoder.process_decoded(v)
            else:
                dd[k] = v
        return cls(**dd)


@dataclass
class ChemPotDiagData(DataclassRoundTrip):
    formula: str
    retrieved_date: str
    chem_pot_diag: ChemPotDiag


@dataclass
class DefectState(ExtendedEnum):
    completed = "completed"
    failed = "failed"
    calc_failed = "calc_failed"
    not_calculated = "not_calculated"
    parse_failed = "parse_failed"


@dataclass
class DefectVisualData(DataclassRoundTrip):
    formula: str
    defect_energy_summary: DefectEnergySummary
    shallows: List[str]
    unusual_defects: Dict[str, List[str]]
    defect_states: Dict[str, DefectState]
    defect_details: Dict[str, Tuple[Correction, BandEdgeOrbitalInfos]]
    vbm: float
    cbm: float

