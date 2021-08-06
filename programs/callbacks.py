# coding: utf-8
#  Copyright (c) 2020 Kumagai group.
from typing import List

import dash
from dash.dependencies import Input, Output
from crystal_toolkit.helpers.layouts import html

from programs.create_homepage import create_structure_links

cs = ["cubic", "tetragonal", "hexagonal", "trigonal", "orthorhombic",
      "monoclinic", "triclinic"]


def make_html(app: dash.Dash, formulas: List[str], layouts, defect_layouts):

    @app.callback(Output('page-content', 'children'),
                  [Input('url', 'pathname')])
    def display_page(pathname: str):
        # TODO: avoid empty return that trigger callback exception but not crash
        if pathname is None:
            return
        if pathname == "/":
            a = html.Div(create_structure_links(formulas=formulas))
            return html.Div([a])
        elif "defect" in pathname:
            formula = pathname.strip("/").split("_")[1]
            return defect_layouts[formula]
        else:
            formula = pathname.strip("/")
            return layouts[formula]


