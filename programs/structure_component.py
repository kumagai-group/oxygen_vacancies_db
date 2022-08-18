# coding: utf-8
#  Copyright (c) 2020 Kumagai group.
import re
from collections import OrderedDict
from ctypes import Structure
from typing import Tuple, Optional, Union, Dict

from crystal_toolkit.core.legend import Legend
from crystal_toolkit.core.mpcomponent import MPComponent
from crystal_toolkit.core.scene import Scene
from crystal_toolkit.helpers.layouts import *
from crystal_toolkit.renderables.structuregraph import get_structure_graph_scene
from crystal_toolkit.renderables.moleculegraph import get_molecule_graph_scene

from dash.dependencies import Input, Output, State
from dash_mp_components import CrystalToolkitScene
from pymatgen.core import Composition
from pymatgen.analysis.graphs import MoleculeGraph, StructureGraph
from pymatgen.analysis.local_env import NearNeighbors
from pymatgen.core.periodic_table import DummySpecie


class StructureComponent(MPComponent):

    available_bonding_strategies = {
        subclass.__name__: subclass for subclass in
        NearNeighbors.__subclasses__()
    }

    default_scene_settings = {
        "extractAxis": True,
        "renderer": "webgl",
    }

    default_title = ""

    def __init__(
            self,
            structure_graph: StructureGraph = None,
            formula: str = None,
            id: str = None,
            scene_additions: Optional[Scene] = None,
            **kwargs):

        super().__init__(id=id, default_data=structure_graph, **kwargs)

        self.formula = formula
        self.initial_scene_settings = self.default_scene_settings.copy()

        if scene_additions:
            self.initial_scene_additions = Scene(name="scene_additions",
                                                 contents=scene_additions
                                                 ).to_json()
        else:
            self.initial_scene_additions = None

        self.graph = structure_graph
        scene = self.create_stores()

        self._initial_data["scene"] = scene
        self.scene_kwargs = {}

    def create_stores(self):
        self.create_store("scene_settings",
                          initial_data=self.initial_scene_settings)
        self.create_store("graph_generation_options",
                          initial_data={"unit_cell_choice": "input"})
        self.create_store(
            "display_options",
            initial_data={
                "color_scheme": "VESTA",
                "radius_strategy": "uniform",
                "draw_image_atoms": True,
                "bonded_sites_outside_unit_cell": True,
                "hide_incomplete_bonds": True,
                "show_compass": True,
            },
        )
        self.create_store("scene_additions",
                          initial_data=self.initial_scene_additions)
        scene, legend = self.get_scene_and_legend(
            self.graph,
            scene_additions=self.initial_data["scene_additions"],
            **self.initial_data["display_options"])
        self.create_store("legend_data", initial_data=legend)
        self.create_store("graph", initial_data=self.graph)

        return scene

    def generate_callbacks(self, app, cache):

        app.clientside_callback(
            """
            function (values, options) {
                const visibility = {}
                options.forEach(function (opt) {
                    visibility[opt.value] = Boolean(values.includes(opt.value))
                })
                return visibility
            }
            """,
            Output(self.id("scene"), "toggleVisibility"),
            [Input(self.id("hide-show"), "value")],
            [State(self.id("hide-show"), "options")],
        )

    def _make_legend(self, legend):

        if not legend:
            return html.Div(id=self.id("legend"))

        def get_font_color(hex_code):
            # ensures contrasting font color for background color
            c = tuple(int(hex_code[1:][i: i + 2], 16) for i in (0, 2, 4))
            if 1 - (c[0] * 0.299 + c[1] * 0.587 + c[2] * 0.114) / 255 < 0.5:
                font_color = "#000000"
            else:
                font_color = "#ffffff"
            return font_color

        try:
            formula = Composition.from_dict(
                legend["composition"]).reduced_formula
        except:
            # TODO: fix legend for Dummy Specie compositions
            formula = "Unknown"

        legend_colors = OrderedDict(
            sorted(list(legend["colors"].items()),
                   key=lambda x: formula.find(x[1]))
        )

        legend_elements = [
            Button(
                html.Span(
                    name, className="icon",
                    style={"color": get_font_color(color)}
                ),
                kind="static",
                style={"backgroundColor": color},
            )
            for color, name in legend_colors.items()
        ]

        return Field(
            [Control(el, style={"marginRight": "0.2rem"}) for el in
             legend_elements],
            id=self.id("legend"),
            grouped=True)

    def _make_title(self, legend):

        if not legend or (not legend.get("composition", None)):
            return H1(self.default_title, id=self.id("title"))

        composition = legend["composition"]
        if isinstance(composition, dict):

            try:
                composition = Composition.from_dict(composition)

                composition = Composition(
                    {
                        el: amt
                        for el, amt in composition.items()
                        if not isinstance(el, DummySpecie)
                    }
                )
                composition = composition.get_reduced_composition_and_factor()[
                    0]
                formula = composition.reduced_formula
                formula_parts = re.findall(r"[^\d_]+|\d+", formula)
                formula_components = [
                    html.Sub(part.strip())
                    if part.isnumeric()
                    else html.Span(part.strip())
                    for part in formula_parts
                ]
            except:
                formula_components = list(map(str, composition.keys()))

        return H1(formula_components, id=self.id("title"),
                  style={"display": "inline-block"}
        )

    @property
    def _sub_layouts(self):

        struct_layout = html.Div(
            CrystalToolkitScene(
                id=self.id("scene"),
                data=self.initial_data["scene"],
                settings=self.initial_scene_settings,
                sceneSize="100%",
                **self.scene_kwargs,
            ),
            style={
                "width": "100%",
                "height": "100%",
                "overflow": "hidden",
                "margin": "0 auto",
            },
        )

        poscar_download = html.A("POSCAR",
                                 href=f"/downloads/unitcell/{self.formula}-POSCAR",
                                 download=f"POSCAR",
                                 id=f"{self.id()}-poscar-download-link")

        title_layout = html.Div(
            self._make_title(self._initial_data["legend_data"]),
            id=self.id("title_container"),
        )

        legend_layout = html.Div(
            self._make_legend(self._initial_data["legend_data"]),
            id=self.id("legend_container"),
        )

        options_layout = Field(
            [
                html.Div(
                    [
                        dcc.Checklist(
                            options=[
                                {"label": "Bonds", "value": "bonds"},
                                {"label": "Unit cell", "value": "unit_cell"},
                                {"label": "Polyhedra", "value": "polyhedra"},
                            ],
                            value=["bonds", "unit_cell", "polyhedra"],
                            labelStyle={"display": "block"},
                            inputClassName="mpc-radio",
                            id=self.id("hide-show"),
                            persistence=True,
                            persistence_type="local",
                        )
                    ],
                    className="mpc-control",
                ),
            ]
        )

        return {"struct": struct_layout,
                "poscar": poscar_download,
                "options": options_layout,
                "title": title_layout,
                "legend": legend_layout}

    def layout(self, size: str = "600px") -> html.Div:
        """
        :param size: a CSS string specifying width/height of Div
        :return: A html.Div containing the 3D structure or molecule
        """
        return html.Div(
            self._sub_layouts["struct"], style={"width": size, "height": size}
        )

    @staticmethod
    def _get_structure(graph: Union[StructureGraph, Structure]) -> Structure:
        if isinstance(graph, StructureGraph):
            return graph.structure
        elif isinstance(graph, Structure):
            return graph
        else:
            raise ValueError

    @staticmethod
    def get_scene_and_legend(
            graph: Optional[StructureGraph],
            color_scheme="VESTA",
            radius_strategy="uniform",
            draw_image_atoms=True,
            bonded_sites_outside_unit_cell=True,
            hide_incomplete_bonds=True,
            explicitly_calculate_polyhedra_hull=False,
            scene_additions=None,
            show_compass=True,
    ) -> Tuple[Scene, Dict[str, str]]:

        scene = Scene(name="StructureComponentScene")

        if graph is None:
            return scene, {}

        structure = StructureComponent._get_structure(graph)

        # TODO: add radius_scale
        legend = Legend(
            structure,
            color_scheme=color_scheme,
            radius_scheme=radius_strategy,
        )

        if isinstance(graph, StructureGraph):
            scene = get_structure_graph_scene(
                graph,
                draw_image_atoms=draw_image_atoms,
                bonded_sites_outside_unit_cell=bonded_sites_outside_unit_cell,
                hide_incomplete_edges=hide_incomplete_bonds,
                explicitly_calculate_polyhedra_hull=explicitly_calculate_polyhedra_hull,
                legend=legend)

        scene.name = "StructureComponentScene"

        axes = structure.lattice._axes_from_lattice()
        axes.visible = show_compass
        scene.contents.append(axes)

        scene = scene.to_json()
        if scene_additions:
            scene["contents"].append(scene_additions)

        return scene, legend.get_legend()

    @property
    def options_layout(self):
        """
        :return: A layout including options to change the appearance, bonding, etc.
        """
        return self._sub_layouts["options"]

    @property
    def title_layout(self):
        """
        :return: A layout including the composition of the structure/molecule as a title.
        """
        return self._sub_layouts["title"]

    @property
    def legend_layout(self):
        """
        :return: A layout including a legend for the structure/molecule.
        """
        return self._sub_layouts["legend"]

    @property
    def poscar_layout(self):
        return self._sub_layouts["poscar"]

    @property
    def cif_layout(self):
        return self._sub_layouts["cif"]


class MoleculeComponent(MPComponent):

    default_scene_settings = {
        "extractAxis": True,
        "renderer":  "webgl",
        "enableZoom": False,
        "defaultZoom": 0.6}

    default_title = "oxide database"

    def __init__(
            self,
            molecule_graph: MoleculeGraph = None,
            id: str = None,
            **kwargs):

        super().__init__(id=id, default_data=molecule_graph, **kwargs)

        self.initial_scene_settings = self.default_scene_settings.copy()
        self.graph = molecule_graph
        scene = self.get_scene(self.graph)
        self.create_store("graph", initial_data=self.graph)
        self.create_store("scene_settings",
                          initial_data=self.initial_scene_settings)

        self._initial_data["scene"] = scene
        self.scene_kwargs = {}

    def generate_callbacks(self, app, cache):
        pass

    def layout(self):

        mol_layout = html.Div(
            CrystalToolkitScene(
                id=self.id("scene"),
                data=self.initial_data["scene"],
                settings=self.initial_scene_settings,
                sceneSize="100%",
                **self.scene_kwargs,
            ),
            style={"width": "200px", "height": "200px"},
        )

        return mol_layout

    @staticmethod
    def get_scene(graph: Optional[MoleculeGraph]) -> Scene:

        scene = Scene(name="MoleculeComponentScene")

        if graph is None:
            return scene

        legend = Legend(
            graph.molecule, color_scheme="VESTA", radius_scheme="uniform")

        if isinstance(graph, MoleculeGraph):
            scene = get_molecule_graph_scene(graph, legend=legend)

        scene.name = "MoleculeComponentScene"

        return scene.to_json()
