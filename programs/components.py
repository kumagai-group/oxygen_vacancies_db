# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
from fractions import Fraction
from itertools import groupby
from pathlib import Path
from typing import List, Optional, Union

import dash_core_components as dcc
import dash_html_components as html
from crystal_toolkit.core.mpcomponent import MPComponent
from crystal_toolkit.helpers.layouts import Columns, \
    Column, H3, get_data_list, H4, H5, Reveal, get_table
from dash_html_components import Br

from pydefect.analyzer.band_edge_states import BandEdgeOrbitalInfos
from pydefect.analyzer.eigenvalue_plotter import EigenvaluePlotlyPlotter
from pydefect.corrections.efnv_correction import ExtendedFnvCorrection
from pydefect.corrections.site_potential_plotter import \
    SitePotentialPlotlyPlotter
from pymatgen.core import Molecule
from pymatgen.analysis.graphs import MoleculeGraph
from pymatgen.analysis.local_env import CrystalNN
# from vise.analyzer.dielectric_function import DieleFuncData
from vise.analyzer.dos_data import DosPlotData
# from vise.analyzer.plot_absorption_coeff import AbsorptionCoeffPlotlyPlotter
from vise.analyzer.plot_band import BandPlotInfo
from vise.analyzer.plot_band_dos import BandDosPlotlyPlotter
from vise.analyzer.plot_brillouin_zone import BZPlotInfo, BZPlotlyPlotter
from vise.util.structure_symmetrizer import Site
import numpy as np

from programs.bulk_dataclass import BulkVisualData
from programs.defect_dataclass import DefectVisualData
from programs.structure_component import MoleculeComponent


def pretty_frac_format(x):
    x = x % 1
    fraction = Fraction(x).limit_denominator(8)
    if np.allclose(x, 1):
        x_str = "0"
    elif not np.allclose(x, float(fraction)):
        x = np.around(x, decimals=3)
        x_str = f"{x:.3g}"
    else:
        x_str = str(fraction)
    return x_str


# class AbsorptionComponent(MPComponent):
#     def __init__(self, diele_func_data: DieleFuncData = None, *args, **kwargs):
#         if diele_func_data:
#             plotter = AbsorptionCoeffPlotlyPlotter(diele_func_data)
#             fig = dcc.Graph(figure=plotter.create_figure())
#             self.column = Column([H3("Absorption coefficient"), fig])
#         else:
#             self.column = H3("Absorption coefficient not available")
#         super().__init__(*args, **kwargs)

    # @property
    # def layout(self):
    #     return html.Div(Columns([self.column]))

    # def generate_callbacks(self, app, cache):
    #     pass


class BandDosComponent(MPComponent):

    def __init__(self,
                 dos_plot_data: Union[DosPlotData, dict],
                 band_plot_info: Union[BandPlotInfo, dict],
                 band_plot_info_2: Union[BandPlotInfo, dict] = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(dos_plot_data, dict):
            dos_plot_data = DosPlotData.from_dict(dos_plot_data)
        if isinstance(band_plot_info, dict):
            print(band_plot_info["x_ticks"].keys())
            band_plot_info = BandPlotInfo.from_dict(band_plot_info)
        if isinstance(band_plot_info_2, dict):
            band_plot_info_2 = BandPlotInfo.from_dict(band_plot_info_2)

        band_dos = BandDosPlotlyPlotter(dos_plot_data,
                                        band_plot_info,
                                        band_plot_info_2)
        self.fig = dcc.Graph(figure=band_dos.fig)

    @property
    def layout(self):
        return html.Div(Columns(
            [Column([H3("Band structure & density of states"), self.fig])]))

    def generate_callbacks(self, app, cache):
        pass


class BZComponent(MPComponent):
    def __init__(self, bz_plot_info: BZPlotInfo = None, *args, **kwargs):
        if bz_plot_info:
            bz_plotter = BZPlotlyPlotter(bz_plot_info)
            self.fig = dcc.Graph(figure=bz_plotter.create_figure())
        else:
            self.fig = H3("Not Available")

        super().__init__(*args, **kwargs)

    @property
    def layout(self):
        return html.Div(Columns([Column(self.fig)]))

    def generate_callbacks(self, app, cache):
        pass


class ScalarComponent(MPComponent):
    def __init__(self, data: BulkVisualData, *args, **kwargs):
        self.data = data
        super().__init__(*args, **kwargs)

    @property
    def layout(self):
        data = {"Band gap": self.data.pretty_band_gap,
                # "Optical gap": self.data.pretty_optical_gap,
                "Ave ion-clamped dielectrics": self.data.pretty_ave_ele_dielectric,
                "Ave ionic dielectrics": self.data.pretty_ave_ion_dielectric,
                # "Ave hole effective mass": self.data.pretty_ave_p_mass,
                # "Ave electron effective mass": self.data.pretty_ave_n_mass,
                }
        return Columns([Column([H4("Material properties"), get_data_list(data)])])

    def generate_callbacks(self, app, cache):
        pass


class TensorComponent(MPComponent):
    def __init__(self, data: BulkVisualData, *args, **kwargs):
        self.data = data
        super().__init__(*args, **kwargs)

    @property
    def layout(self):
        data = {"Ion-clamped dielectrics": self.data.pretty_ele_dielectric,
                "Ionic dielectrics": self.data.pretty_ion_dielectric,
                # "Hole effective mass": self.data.pretty_p_mass_tensor,
                # "Electron effective mass": self.data.pretty_n_mass_tensor,
                }
        return Columns([Column([H4("Tensor properties"), get_data_list(data)])])

    def generate_callbacks(self, app, cache):
        pass


class SiteComponent(MPComponent):
    def __init__(self, data: BulkVisualData, *args, **kwargs):
        self.data = data
        self.structure = data.structure_graph.structure
        super().__init__(*args, **kwargs)

    @property
    def layout(self):
        cation_columns = []
        anion_columns = []
        cnn = CrystalNN()

        for symbol, site in self.data.sites.items():
            wyckoff_contents = []
            data = dict()
            site = Site.from_dict(site)
            idx = site.equivalent_atoms[0]
            data["Wyckoff"] = site.wyckoff_letter
            data["Site Symmetry"] = site.site_symmetry
            data["Bader Net Charge (e⁻)"] = self.data.pretty_bader_charges[idx]
            nn_info = cnn.get_nn_info(structure=self.structure, n=idx)
            data["Local Structure"] = self._make_local_env(site, nn_info)
            datalist = get_data_list(data)
            wyckoff_contents.append(H5(f"{symbol}", className="mpc-label"))
            site_data = []
            for idx in site.equivalent_atoms:
                site_data += [(pretty_frac_format(self.structure[idx].frac_coords[0]),
                               pretty_frac_format(self.structure[idx].frac_coords[1]),
                               pretty_frac_format(self.structure[idx].frac_coords[2]))]
            wyckoff_contents.append(datalist)
            wyckoff_contents.append(Reveal(get_table(site_data),
                                           title=f"Frac coords ({len(site_data)})",
                                           id=f"{self.data.formula}_{symbol}_sites"))
            if symbol[0] == "O":
                anion_columns.append(Column(html.Div(wyckoff_contents)))
            else:
                cation_columns.append(Column(html.Div(wyckoff_contents)))

        return Column([H3("Site Info"),
                       Columns(cation_columns),
                       Columns(anion_columns)])

    def _make_local_env(self, site: Site, nn_info: list):
        repr_idx = site.equivalent_atoms[0]
        mol = Molecule.from_sites(
            [self.structure[repr_idx]] + [i["site"] for i in nn_info])
        mol = mol.get_centered_molecule()
        mg = MoleculeGraph.with_empty_graph(molecule=mol)
        for i in range(1, len(mol)):
            mg.add_edge(0, i)

        result = html.Div([MoleculeComponent(
            molecule_graph=mg,
            disable_callbacks=True,
            id=f"{self.data.formula}_site_{repr_idx}").layout()])

        return result

    def generate_callbacks(self, app, cache):
        pass


class SymmetryComponent(MPComponent):
    def __init__(self, data: BulkVisualData, *args, **kwargs):
        self.data = data
        super().__init__(*args, **kwargs)

    @property
    def layout(self):
        sg = f"{self.data.space_group} ({self.data.space_group_num})"
        data = {"Space Group": sg,
                "a, b, c": self.data.pretty_a_b_c,
                "α, β, γ": self.data.pretty_lattice_angles}
        return Columns([Column([H4("Unit cell"), get_data_list(data)])])

    def generate_callbacks(self, app, cache):
        pass


class DefectStatusTableComponent(MPComponent):
    def __init__(self, data: DefectVisualData, *args, **kwargs):
        self.data = data
        super().__init__(*args, **kwargs)

    @property
    def defect_state_table(self):
        _lambda = lambda x: "_".join(x.split("_")[:2])
        states = []
        for defect_type, group in groupby(
                sorted(self.data.defect_states, key=_lambda), _lambda):
            in_data = {v.split("_")[2]: self.data.defect_states[v] for v
                       in sorted(group, key=lambda x: x.split("_")[2])}
            states.append(get_data_list({defect_type: get_data_list(in_data)}))
        return Columns(states)

    @property
    def shallow_defects(self):
        _lambda = lambda x: "_".join(x.split("_")[:2])
        states = []
        for defect_type, group in groupby(
                sorted(self.data.shallows, key=_lambda), _lambda):
            in_data = [html.Td(v.split("_")[2]) for v
                       in sorted(group, key=lambda x: x.split("_")[2])]
            states.append(get_data_list({defect_type: html.Tr(in_data)}))
        return Columns(states)

    @property
    def unusual_defects(self):
        _lambda = lambda x: "_".join(x.split("_")[:2])
        states = []
        for defect_type, group in groupby(
                sorted(self.data.unusual_defects, key=_lambda), _lambda):
            in_data = {v.split("_")[2]: self.data.unusual_defects[v][0] for v
                       in sorted(group, key=lambda x: x.split("_")[2])}
            states.append(get_data_list({defect_type: get_data_list(in_data)}))
        return Columns(states)

    @property
    def layout(self):
        return Columns([Column([H4("Defect Status"),
                                self.defect_state_table,
                                H4("Defects with PHS"),
                                self.shallow_defects,
                                H4("Non-trivial Defects"),
                                self.unusual_defects])])

    def generate_callbacks(self, app, cache):
        pass


class SingleDefectComponent(MPComponent):
    def __init__(self,
                 source_dir: Path,
                 correction: ExtendedFnvCorrection,
                 band_edge_orbital_infos: BandEdgeOrbitalInfos,
                 formula: str,
                 defect_name: str,
                 supercell_vbm, supercell_cbm,
                 id_,
                 *args, **kwargs):
        self.source_dir = source_dir
        self.correction = correction
        self.band_edge_orbital_infos = band_edge_orbital_infos
        self.formula = formula
        self.defect_name = defect_name
        self.supercell_vbm = supercell_vbm
        self.supercell_cbm = supercell_cbm
        super().__init__(id=id_, *args, **kwargs)

    @property
    def layout(self):
        pot = SitePotentialPlotlyPlotter.from_efnv_corr(
            title=self.defect_name, efnv_correction=self.correction)
        eig = EigenvaluePlotlyPlotter(
            title=self.defect_name,
            band_edge_orb_infos=self.band_edge_orbital_infos,
            supercell_vbm=self.supercell_vbm,
            supercell_cbm=self.supercell_cbm)

        pot_graph = dcc.Graph(figure=pot.create_figure())
        eig_graph = dcc.Graph(figure=eig.create_figure())

        return html.Div([html.Br(),
                         H3(self.defect_name),
                         Columns([html.Div(pot_graph),
                                  html.Div(eig_graph)]),
                         self.vesta_download_button, Br(),
                         self.tar_download_button,
                         ])

    @property
    def tar_download_button(self):
        full_name = f"{self.formula}_{self.defect_name}"
        return html.A("PARCHG files",
                      href=f"/downloads/defects/{full_name}.tar.gz",
                      download=f"{full_name}.tar.gz",
                      id=f"{self.id()}-download-link",
                      style={"font_size": 30})

    @property
    def vesta_download_button(self):
        full_name = f"{self.formula}_{self.defect_name}"
        return html.A("VESTA file",
                      href=f"/downloads/defects/{full_name}.vesta",
                      download=f"{full_name}.vesta",
                      id=f"{self.id()}-download-link",
                      style={"font_size": 30})

    def generate_callbacks(self, app, cache):
        pass

