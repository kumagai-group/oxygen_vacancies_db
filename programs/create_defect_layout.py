# coding: utf-8
#  Copyright (c) 2020 Kumagai group.
import json
from pathlib import Path

from crystal_toolkit.helpers.layouts import Container, Section, Column
from monty.serialization import loadfn

from pydefect.analyzer.band_edge_states import BandEdgeOrbitalInfos
from pydefect.corrections.efnv_correction import ExtendedFnvCorrection

from programs.components import SingleDefectComponent
from programs.defect_dataclass import DefectVisualData


class CreateDefectLayout:
    def __init__(self, source_dir: Path, formula):
        dir_ = source_dir / formula
        json_open = open(dir_ / "defect_visual_data.json", 'r')
        d = json.load(json_open)
        defect_data = DefectVisualData.from_dict(d)

        self.defect_details = defect_data.defect_details
        self.formula = defect_data.formula
        self.defect_layout = []
        for defect_name, v in self.defect_details.items():
            correction = ExtendedFnvCorrection.from_dict(v[0])
            band_edge_orbital_infos = BandEdgeOrbitalInfos.from_dict(v[1])
            id_ = f"defect_{self.formula}_{defect_name}"
            comp = SingleDefectComponent(source_dir,
                                         correction,
                                         band_edge_orbital_infos,
                                         self.formula,
                                         defect_name,
                                         defect_data.vbm, defect_data.cbm, id_)
            self.defect_layout.append(comp.layout)

    def make_body(self):
        return Container([Section([Column(self.defect_layout)])],
                         id=f"defect_{self.formula}")

