# coding: utf-8
#  Copyright (c) 2020 Kumagai group.
import itertools
from typing import List

from crystal_toolkit.helpers.layouts import html, dcc


def create_home():
    return html.Div([dcc.Location(id='url', refresh=False),
                     html.Div(id='page-content'),
                     dcc.Link('Go back to home', href='/',
                              style={"font-size": 20})])


def create_blank_page():
    return html.Div("Data is broken.")


def create_structure_links(formulas: List[str]):
    link_and_br = [[dcc.Link(f"{formula}",
                             href=f"/{formula}", style={"font-size": 20}),
                    html.Br()] for formula in formulas]
    return list(itertools.chain.from_iterable(link_and_br))


def create_search_box():
    return html.Div([dcc.Input(id="search_box", value="", placeholder="search"),
                     html.Br()])


def create_status_check_list():
    return html.Div([dcc.Checklist(
        id='defect_status',
        options=[
            {"label": "completed", "value": "completed"},
            {"label": "partially completed", "value": "partially completed"},
            {"label": "no defect", "value": "failed"}],
        value=["completed", "partially completed", "failed"]),
        html.Br()])


