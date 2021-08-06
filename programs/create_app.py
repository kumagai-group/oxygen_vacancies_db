# coding: utf-8
#  Copyright (c) 2020 Kumagai group.
from pathlib import Path
from random import sample
from typing import List

import crystal_toolkit.components as ctc
import flask
from dash import Dash
from fire import Fire

from programs.callbacks import make_html
from programs.create_defect_layout import CreateDefectLayout
from programs.create_homepage import create_home
from programs.create_layout import CreateLayout


def create_app(source_dir: str = None, formulas: List[str] = None):

    source_dir = Path(source_dir)
    # if formulas is None:
    #     formulas = []
    #     for doc in db["defect_visual_data"].find({}, {"formula": 1}):
    #         formulas.append(doc["formula"])

        # if random_num:
        #     formulas = pick_randomly(formulas, random_num)

    layouts = {}
    defect_layouts = {}
    for formula in formulas:
        create_layout = CreateLayout(source_dir=source_dir, formula=formula)
        create_defect_layout = CreateDefectLayout(source_dir=source_dir, formula=formula)
        print(f'Layout of {formula} has been created.')
        layouts[formula] = create_layout.make_body()
        print(f'Defect layout of {formula} has been created.')
        defect_layouts[formula] = create_defect_layout.make_body()
        # except Exception as e:
        #     print(f'Creation of {formula} layout failed.', e)

    app = Dash(__name__, suppress_callback_exceptions=True)
    make_html(app, list(layouts.keys()), layouts, defect_layouts)
    app.layout = create_home()

    @app.server.route(f'/downloads/defects/<full_name>.tar.gz',
                      methods=['GET'])
    def serve_tar_file(full_name: str):
        formula, defect_type = full_name.split("_", 1)
        print(source_dir / formula, defect_type)
        print("serve tar file:", full_name)
        return flask.send_from_directory(source_dir / formula, f"{full_name}.tar.gz")

    @app.server.route(f'/downloads/defects/<full_name>.vesta',
                      methods=['GET'])
    def serve_vesta_file(full_name: str):
        formula, defect_type = full_name.split("_", 1)
        print(source_dir / formula, defect_type)
        print("serve vesta file:", full_name)
        return flask.send_from_directory(source_dir / formula, f"{full_name}.vesta")

    @app.server.route(f'/downloads/unitcell/<full_name>', methods=['GET'])
    def serve_poscar_file(full_name: str):
        print("serve POSCAR file:", full_name)
        return flask.send_from_directory(source_dir, f"POSCAR-{full_name}")

    return app


def pick_randomly(candidates: List[str], random_num):
    return sample(candidates, random_num)


def main(source_dir, formulas=None, port=8050):
    app = create_app(source_dir, formulas=formulas)
    ctc.register_crystal_toolkit(layout=app.layout, app=app, cache=None)
    app.run_server(port=port)


if __name__ == "__main__":
    Fire(main)
