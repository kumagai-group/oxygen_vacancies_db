# coding: utf-8
#  Copyright (c) 2020 Kumagai group.
from pathlib import Path

from crystal_toolkit.helpers.layouts import (html, Container, Section,
                                             Columns, Column, Box, Reveal, H4, dcc)
from monty.serialization import loadfn
import json
from pydefect.analyzer.dash_components.cpd_energy_dash import CpdEnergyComponent
from pydefect.chem_pot_diag.chem_pot_diag import ChemPotDiag

from programs.bulk_dataclass import BulkVisualData
from programs.components import SymmetryComponent, ScalarComponent, \
    TensorComponent, SiteComponent, BandDosComponent, BZComponent, \
    AbsorptionComponent, DefectStatusTableComponent
from programs.defect_dataclass import DefectVisualData
from programs.structure_component import StructureComponent

box_size = 500


class CreateLayout:
    def __init__(self, source_dir: Path, formula: str):
        self.formula = formula
        dir_ = source_dir / formula
        json_open = open(dir_ / "bulk_visual_data.json", 'r')
        d = json.load(json_open)
        self.bulk_data = BulkVisualData.from_dict(d)

        json_open = open(dir_ / "chem_pot_diag.json", 'r')
        d = json.load(json_open)
        self.cpd = ChemPotDiag.from_dict(d)

        json_open = open(dir_ / "defect_visual_data.json", 'r')
        d = json.load(json_open)
        self.defect_data = DefectVisualData.from_dict(d)

        self._structure = StructureComponent(
            structure_graph=self.bulk_data.structure_graph,
            id=f"str_mol_{self.formula}")

    @property
    def _mp_links(self):
        mp_link_root = "https://materialsproject.org/materials"
        return html.A(f'{self.bulk_data.mp_id}',
                      href=f'{mp_link_root}/{self.bulk_data.mp_id}/',
                      style={'font-weight': 'bold', "font-size": "20px"},
                      target="_blank")

    # property is okay if it is called only once as id is not duplicated.
    @property
    def _symmetry(self):
        return SymmetryComponent(data=self.bulk_data, id=f"symmetry_{self.formula}")

    @property
    def _scalar(self):
        return ScalarComponent(data=self.bulk_data, id=f"scalar_{self.formula}")

    @property
    def _tensor(self):
        return TensorComponent(data=self.bulk_data, id=f"tensor_{self.formula}")

    @property
    def _sites(self):
        return SiteComponent(data=self.bulk_data, id=f"sites_{self.formula}" )

    @property
    def _band_dos(self):
        return BandDosComponent(
            dos_plot_data=self.bulk_data.dos_plot_data,
            band_plot_info=self.bulk_data.band_dd_hybrid_plot_info,
            band_plot_info_2=self.bulk_data.band_pbesol_plot_info,
            id=f"band_dos_{self.formula}")

    @property
    def _bz(self):
        return BZComponent(self.bulk_data.bz_plot_info, id=f"bz_{self.formula}")

    @property
    def _absorption(self):
        return AbsorptionComponent(self.bulk_data.shifted_diele_func,
                                   id=f"absorption_{self.formula}")

    @property
    def _defect_status(self):
        return DefectStatusTableComponent(
            self.defect_data, id=f"defect_status_{self.formula}")

    @property
    def _cpd_defect(self):
        return CpdEnergyComponent(
            self.cpd,
            self.defect_data.defect_energy_summary,
            id=f"cpd_defect_{self.formula}")

    @property
    def _defect_link(self):
        return dcc.Link(f"To defect page",
                        href=f"/defect_{self.formula}",
                        style={"font-size": 20})

    def make_body(self):
        return Container(
            [
                Section(
                    [
                        Columns(
                            [
                                Column(
                                    [self._structure.title_layout]
                                )
                            ]
                        ),
                        Columns(
                            [
                                Column(
                                    [
                                        Box(
                                            self._structure.layout(size="100%"),
                                            style={
                                                "width": box_size,
                                                "height": box_size,
                                                "minWidth": "400px",
                                                "minHeight": "400px",
                                                "maxWidth": "700px",
                                                "maxHeight": "600px",
                                                "overflow": "hidden",
                                                "padding": "0.25rem",
                                                "marginBottom": "0.5rem",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    self._structure.legend_layout,
                                                    style={"float": "left"},
                                                ),
                                                html.Div(self._mp_links)],
                                            style={
                                                "width": "300px",
                                                "minWidth": "300px",
                                                "marginBottom": "40px",
                                            },
                                        ),
                                        self._structure.options_layout,
                                    ],
                                    narrow=True,
                                ),
                                Column(
                                    [
                                        self._symmetry.layout,
                                        self._scalar.layout,
                                    ],
                                    style={"width": box_size,
                                           "max-width": box_size},
                                ),
                                Column(
                                    self._tensor.layout
                                )
                            ],
                            desktop_only=False,
                            centered=False,
                        ),
                        Columns(Column([self._sites.layout,
                                        self._band_dos.layout,
                                        Reveal([self._bz.layout],
                                               title="Brillouin zone",
                                               id="bz-show-options"),
                                        self._absorption.layout
                                        ],
                                       )),
                        Column(self._defect_status.layout),
                        H4("Defect Formation Energy"),
                        Column(self._cpd_defect.layout),
                        self._defect_link
                    ]
                ),
            ], id=f"all_{self.formula}")

