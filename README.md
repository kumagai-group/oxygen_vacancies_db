# Oxygen vacancy database  
This repository includes the database reported in the paper
"Insights Into Oxygen Vacancies from High-Throughput First-Principles Calculations
" written by Yu Kumagai, Naoki Tsunoda, Akira Takahashi, and Fumiyasu Oba.

For the data generation, see also [vise](https://github.com/kumagai-group/vise) 
and [pydefect](https://github.com/kumagai-group/pydefect) codes.

## How to use  
1. Clone this repository.
2. Prepare a clean python environment using e.g., virtualenv.
3. Run `pip install -r requirements.txt` to install the relevant python files.
4. Go to the oxygen_vacancies_db_data directory  
   and unpack the files with `for i in *.tar.gz; do echo $i; tar xvfz $i; done` 
   (about 2GB)
5. Add the path to oxygen_vacancies_db directory, e.g., with `export PYTHONPATH=$PYTHONPATH:(PATH TO oxygen_vacancies_db)` command.
6. Run `python (PATH TO oxygen_vacancies_db)/programs/create_app.py --source_dir="(PATH TO oxygen_vacancies_db)/oxygen_vacancies_db_data" --formulas="[ZnO]"` 
   to see if you can create a ZnO page. You need single quotations, e.g., `"['Zn(GaO2)2']"` when the formula has parentheses.
   The (PATH TO oxygen_vacancies_db) would be absolute one beginning with `/`. 
   One can also specify the port number as `--port=8051` (default is 8050).
7. Open the web page, e.g., `http://127.0.0.1:8050/` using a browser. Since the safari does not support part of plotly's functions, 
   so we recommend using another browser such as Google Chrome.

All the data is licensed under a [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) license.

## site_info.tar.gz file
This compressed file contains the site information in the supercells.
The cif files describe the supercell structures adopted in the paper.
 
## vacancy_formation_energy_ml directory
This directory includes the information related to the machine learning of the defect formation energies.
The df_charge{0,1,2}.pcl files are the pickled dataframe files, 
with which DataFrame instances can be retrieved using the following command.

```python
import pandas as pd
charge = 0
df = pd.read_pickle(f"df_charge{charge}.pcl")
```

The CSV files generated from the dataframes are also distributed in the same directory.

In the columns, the full_name means the formula plus vacancy name (e.g., Va_O1), and vacancy_formation_energy means the 
vacancy formation energy aligned at the O site local potential, and the origin of the Fermi level is set to the VBM in ZnO.
See our paper that will appear soon for details.

### machine_learning.py
This script was used for the machine learning of the defect formation energies.
The command line argument receives the random state used in the scikit learn. 
The script can be run as follows:
```
python ~/my_programs/oxygen_vacancies_db/vacancy_formation_energy_ml/machine_learning.py 1
```

## Description for the graphical user interface 
The graphical user interface has been created using the [plotly](https://plotly.com) 
and [crystaltoolkit](https://github.com/materialsproject/crystaltoolkit).

### Band structure & density of states
The green lines in the **band** figure shows the band structure calculated using PBEsol, 
while the black lines using the non-self-consistent use of a dielectric-dependent (nsc-dd) hybrid functional.
See our paper for details of the calculation conditions.

#### Defects with PHS
This panel tabulates the vacancies with perturbed host states (PHS).
See our paper for details of the PHS.

#### Non-trivial Defects
This panel indicates the vacancies showing non-trivial behavior.

- defect type: Shown when the defect is not a simple vacancy.
  The shown type is *vacancy spit* or *unknown*, the latter of which usually accompanies large atomic reconstruction.
- supergroup: Shown when the final structure has supergroup relation with respect to the initial site symmetry.
- not same config from init: Shown when the atomic configuration is considered to 
  be different from the initial structure using the atom mapping technique with cutoff = 1Å.
- energy strange: Shown when the formation energy is anomalous.

#### Defect Formation Energy
The **Allow defects with perturbed host states** button allow one to control 
if the formation energies of the defects with the PHS are considered in the formation energy figure. 

One can also change the chemical potential condition 
by pushing the circle with an alphabet in the chemical potential diagram for binary or ternary compounds. 
Otherwise, **Equilibrium label** is used.

### To defect page
This web page shows the information on individual defect calculation result.
The name indicates vacancy site and charge state (*q*). 
For example, Va_O1_0 means the oxygen vacancy at the O1 site with charge state *q*=0.

#### Potential 
The values for elements are the atomic site potentials caused by the defect, 
which is the potential difference of the defective supercells from the perfect supercells calculated with VASP.
The **PC** indicates the point-charge potential that is calculated using the defect charge and sum of the ion-clamped and ionic dielectric constant. 
**Diff** is difference of the atomic site potentials from the **PC** values.
The region for averaging **Diff** and its averaged value are expressed in the width and height of the red horizontal dashed line , respectively.

#### Eigenvalues 
It indicates the electron eigenvalues at the converged structures.
The energy is in the absolute scale directly obtained from the VASP calculations.
The horizontal two purple lines indicate the valence band maximum and conduction band minimum in the supercell without a vacancy.
The occupation number and band index are appeared by moving their mouse cursor over the point.
The points are colored by red when the occupation is less than 0.2, 
while by blue when it is larger than 0.8, and those in between by green.
When the calculation result is spin polarized, eigenvalues in the both spin channel are shown.

#### Vesta file and PARCHG files 
The VESTA file shows the defective supercell structure in [VESTA](https://jp-minerals.org/vesta/en/) program format.
Local structures are shown with labels and arrows.
When the label has a single number, the distance from the defect is shown. 
Conversely, two numbers connected with an underscore means the distance from the defect and its displacement distance (>0.1Å).
Arrows indicate the displacement directions and its displacement distance magnified 10 times.

The PARCHG file is a compressed file, which includes the relaxed structure named CONTCAR-finish with POSCAR format,
and the parchg_($BAND_INDEX).vesta files show the structure with squared wavefunction at the $BAND_INDEX band index
When the number of k-points is more than 1, their averaged values by weight are stored.
To reduce the compressed file size, the values in PARCHG_($BAND_INDEX).vesta are categorized from their original values
according to the normalized values by the largest one as shown below. 
The VESTA show these isosurfaces by default.

- 0.0 ~ 0.1 --> 0
- 0.1 ~ 0.5 --> 1
- 0.5 ~ 0.8 --> 2
- 0.8 ~ 1.0 --> 3
