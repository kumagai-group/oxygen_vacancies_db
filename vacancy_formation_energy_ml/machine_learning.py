# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Yu Kumagai.
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import seaborn as sns
from matminer import PlotlyFig
from matplotlib import pyplot as plt
from monty.json import MSONable
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split, GridSearchCV, ShuffleSplit
from vise.util.mix_in import ToJsonFileMixIn
import pandas as pd


@dataclass
class RegressionStatics(MSONable, ToJsonFileMixIn):
    regressor: str
    train_size: int
    test_size: int
    random_state: int
    rmse_train: float
    mae_train: float
    r2_train: float
    rmse_test: float
    mae_test: float
    r2_test: float
    errors: Dict[str, float]
    predictions: Dict[str, Tuple[float, float]]
    importances: Dict[str, float]


class Regression:
    def __init__(self, df, train_size, random_state, name,
                 regressor="random_forest",
                 test_size=50, min_=20, max_=45,
                 descriptors=None,
                 **regressor_kwargs):
        formulas = df.formula.unique()
        train_formulas, test_formulas = train_test_split(
            formulas, train_size=train_size, test_size=test_size,
            random_state=random_state)

        self.name = name
        self.regressor = str(regressor)
        self.train_size = train_size
        self.test_size = test_size
        self.random_state = random_state

        self.X_train = df.query("formula in @train_formulas")
        self.train_names = list(self.X_train["full_name"])
        self.y_train = self.X_train["vacancy_formation_energy"]

        self.X_test = df.query("formula in @test_formulas")
        self.test_names = list(self.X_test["full_name"])
        self.y_test = self.X_test["vacancy_formation_energy"]

        if descriptors:
            self.X_train = self.X_train[descriptors]
            self.X_test = self.X_test[descriptors]
        else:
            dropped = ["formula", "full_name", "vacancy_formation_energy"]
            self.X_train.drop(dropped, axis=1, inplace=True)
            self.X_test.drop(dropped, axis=1, inplace=True)

        if regressor == "random_forest":
            regressor_kwargs["n_jobs"] = -1
            if "n_estimators" not in regressor_kwargs:
                regressor_kwargs["n_estimators"] = 400

            self.model = GridSearchCV(
                RandomForestRegressor(**regressor_kwargs),
                param_grid=dict(max_features=range(min_, max_)),
                scoring='neg_mean_squared_error',
                cv=ShuffleSplit(n_splits=4, test_size=0.1))
            self.model.fit(self.X_train, self.y_train)

        elif regressor == "linear":
            self.model = LinearRegression().fit(self.X_train, self.y_train)
        else:
            raise ValueError

        self.y_train_predict = self.model.predict(self.X_train)
        self.y_test_predict = self.model.predict(self.X_test)

        self.min_ = min(
            [min(self.y_train), min(self.y_test),
             min(self.y_train_predict), min(self.y_test_predict)]) - 0.5
        self.max_ = max(
            [max(self.y_train), max(self.y_test),
             max(self.y_train_predict), max(self.y_test_predict)]) + 0.5
        self.lims = [self.min_, self.max_]

    def show_grid_search_cv(self):
        ax = plt.gca()
        # Plot the score as a function of alpha
        ax.scatter(self.model.cv_results_['param_max_features'].data,
                   np.sqrt(-1 * self.model.cv_results_['mean_test_score']))
        ax.scatter([self.model.best_params_['max_features']],
                   np.sqrt([-1 * self.model.best_score_]),
                   marker='o', color='r', s=40)
        ax.set_xlabel('Max. Features')
        ax.set_ylabel('RMSE (eV/atom)')
        plt.savefig(f"grid_search_{self.name}.pdf")
        plt.show()
        plt.cla()

    def plotly_fig(self, mode="offline"):
        pf_rf = PlotlyFig(x_title='Calculated energy (eV)',
                          y_title='Predicted energy (eV)',
                          mode=mode,
                          width=800, height=800,
                          show_offline_plot=False,
                          filename=f"parity_{self.name}.html")

        pf_rf.xy([[self.y_test, self.y_test_predict], [self.lims, self.lims]],
                 limits={"x": self.lims, "y": self.lims},
                 modes=['markers', 'lines'],
                 sizes=15,
                 labels=[self.test_names],
                 lines=[{}, {'color': 'black', 'dash': 'dash'}],
                 showlegends=False)

    def seaborn_fig(self):
        train = self.y_train.to_frame()
        train["pred"] = self.y_train_predict
        test = self.y_test.to_frame()
        test["pred"] = self.y_test_predict

        plt.xlim(self.min_, self.max_)
        plt.ylim(self.min_, self.max_)
        ax = plt.gca()
        ax.set(aspect='equal')
        ax.plot(self.lims, self.lims, '-r', linestyle=":")
        ax.set(xlabel='Calculated formation energy (eV) ',
               ylabel='Predicted formation energy (eV)')
        sns.scatterplot("vacancy_formation_energy", "pred", data=train)
        sns.scatterplot("vacancy_formation_energy", "pred", data=test)
        plt.savefig(f"parity_{self.name}.pdf")
        plt.show()
        plt.clf()

    def make_statics(self):
        rmse_t = np.sqrt(mean_squared_error(self.y_train, self.y_train_predict))
        mae_t = mean_absolute_error(self.y_train, self.y_train_predict)
        r2_t = r2_score(self.y_train, self.y_train_predict)

        rmse_p = np.sqrt(mean_squared_error(self.y_test, self.y_test_predict))
        mae_p = mean_absolute_error(self.y_test, self.y_test_predict)
        r2_p = r2_score(self.y_test, self.y_test_predict)

        errors = {}
        predictions = {}
        for name, actual, predicted in \
                zip(self.test_names, self.y_test, self.y_test_predict):
            errors[name] = predicted - actual
            predictions[name] = (predicted, actual)

        try:
             importances = dict(
                 sorted(zip(self.X_train.columns,
                            self.model.best_estimator_.feature_importances_),
                        key=lambda x: x[1], reverse=True))
        except AttributeError:
            importances = None

        return RegressionStatics(self.regressor,
                                 self.train_size, self.test_size,
                                 self.random_state,
                                 rmse_t, mae_t, r2_t, rmse_p, mae_p, r2_p,
                                 errors, predictions, importances)


if __name__ == "__main__":
    filepath = Path(__file__).parent
    random_state = int(sys.argv[1])
    for charge in [0, 1, 2]:
        df = pd.read_pickle(filepath / f"df_charge{charge}.pcl")
#        # fill zero for weights that do not exist.
        df.fillna(0, inplace=True)
        for train_size in [22, 70, 220, 700]:
            name = f"charge{charge}_rand{random_state}_size{train_size}"
            reg = Regression(df,
                             train_size=train_size,
                             test_size=50,
                             random_state=random_state,
                             name=name)
            reg.show_grid_search_cv()
            reg.plotly_fig()
            reg.seaborn_fig()
            statics = reg.make_statics()
            statics.to_json_file(f"{name}.json")
            if charge == 0:
                name = f"charge{charge}_rand{random_state}_size{train_size}_deml"
                reg = Regression(df,
                                 train_size=train_size,
                                 test_size=50,
                                 random_state=random_state,
                                 regressor="linear",
                                 descriptors=["o2p_center_from_vbm",
                                              "formation_energy",
                                              "band_gap",
                                              "nn_ave_eleneg"],
                                 name=name)
                reg.seaborn_fig()
                statics = reg.make_statics()
                statics.to_json_file(f"{name}.json")
