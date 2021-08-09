# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
from dataclasses import dataclass
from typing import List, Dict
import dash_html_components as html

from crystal_toolkit.helpers.layouts import get_table
from pymatgen.analysis.graphs import StructureGraph
from vise.analyzer.dielectric_function import DieleFuncData
from vise.analyzer.dos_data import DosPlotData
from vise.analyzer.plot_band import BandPlotInfo
from vise.analyzer.plot_brillouin_zone import BZPlotInfo

from vise.util.structure_symmetrizer import Site
import numpy as np

from programs.defect_dataclass import DataclassRoundTrip


class NoData(str):

    def __getitem__(self, item):
        return "N.A."


def suppress_exception(method):
    def safe_method(*args, **kwargs):
        try:
            result = method(*args, **kwargs)
        except (TypeError, AttributeError):
            result = NoData("NO DATA")
        return result
    return safe_method


@dataclass
class BulkVisualData(DataclassRoundTrip):
    formula: str
    mp_id: str
    sites: Dict[str, Site]
#    mp_ids: str
    structure_graph: StructureGraph
    space_group_num: int
    space_group: str
    # tight
    bader_charges: List[float] = None
    # dielectric
    ave_ele_diele: float = None
    ave_ion_diele: float = None
    ele_diele: List[List[float]] = None
    ion_diele: List[List[float]] = None
    # band_pbesol
    band_pbesol_plot_info: BandPlotInfo = None
    bz_plot_info: BZPlotInfo = None
    gga_band_gap: float = None
    # band_dd_hybrid_nsc
    band_gap: float = None
    band_dd_hybrid_plot_info: BandPlotInfo = None
    # absorption
    # optical_gap: float = None
    # diele_func: DieleFuncData = None
    # shifted_diele_func: DieleFuncData = None
    # effective_mass_pbesol
    # ave_p_mass: float = None
    # ave_n_mass: float = None
    # p_mass_tensor: List[List[float]] = None
    # n_mass_tensor: List[List[float]] = None
    # dos_pbesol
    dos_plot_data: DosPlotData = None

    @property
    @suppress_exception
    def pretty_band_gap(self):
        return f"{np.round(self.band_gap, 2)} eV"
    #
    # @property
    # @suppress_exception
    # def pretty_optical_gap(self):
    #     return f"{np.round(self.optical_gap, 2)} eV"

    @property
    @suppress_exception
    def pretty_ele_dielectric(self):
        return get_table(np.round(self.ele_diele, 2))

    @property
    @suppress_exception
    def pretty_ave_ele_dielectric(self):
        return str(np.round(self.ave_ele_diele, 2))

    @property
    @suppress_exception
    def pretty_ion_dielectric(self):
        return get_table(np.round(self.ion_diele, 2))

    @property
    @suppress_exception
    def pretty_ave_ion_dielectric(self):
        return str(np.round(self.ave_ion_diele, 2))

    @property
    @suppress_exception
    def pretty_bader_charges(self):
        return np.round(self.bader_charges, 2)
    #
    # @property
    # @suppress_exception
    # def pretty_p_mass_tensor(self):
    #     return get_table(np.round(self.p_mass_tensor, 2))
    #
    # @property
    # @suppress_exception
    # def pretty_n_mass_tensor(self):
    #     return get_table(np.round(self.n_mass_tensor, 2))
    #
    # @property
    # @suppress_exception
    # def pretty_ave_p_mass(self):
    #     return np.round(self.ave_p_mass, 1)
    #
    # @property
    # @suppress_exception
    # def pretty_ave_n_mass(self):
    #     return np.round(self.ave_n_mass, 1)

    @property
    def lattice(self):
        return self.structure_graph.structure.lattice

    @property
    def pretty_a_b_c(self):
        return get_row(np.round(self.lattice.lengths, 3))

    @property
    def pretty_lattice_angles(self):
        return get_row(np.round(self.lattice.angles, 3))


def get_row(row):
    return html.Tr([html.Td(item) for item in row])
