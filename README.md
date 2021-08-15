# Oxygen vacancy database  
This repository includes the database reported in the paper
"Insights Into Oxygen Vacancies from High-Throughput First-Principles Calculations
" written by Yu Kumagai, Naoki Tsunoda, Akira Takahashi, and Fumiyasu Oba.

The data are generated mainly using the [vise](https://github.com/kumagai-group/vise) 
and [pydefect](https://github.com/kumagai-group/pydefect) codes:

## How to use  
1. Clone this repository.
2. Prepare a clean python environment using e.g., virtualenv.
3. Run `pip install -r requirements.txt` to install the relevant python files.
4. Go to the oxygen_vacancies_db_data in the cloned directory 
   and unpack the files with `for i in *.tar.gz; do echo $i; tar xvfz $i; done` 
   (about 2GB)
5. Export PYTHONPATH=$PYTHONPATH:(PATH TO oxygen_vacancies_db) to add the path
6. Run `python (PATH TO oxygen_vacancies_db)/programs/create_app.py --source_dir="(PATH TO oxygen_vacancies_db)/oxygen_vacancies_db_ data" --formulas="[ZnO]"` 
   to see if you can create a ZnO page. You need to write, e.g., `"['Zn(GaO2)2']"` when the formula has parentheses.
7. Open the web page, e.g., `http://127.0.0.1:8050/` using a browser. We recommend to use Google Chrome.

All the data is licensed under a [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) license.

## site_info.tar.gz file
This compressed file contains the site information in the supercells.
The cif files describe the supercell structures adopted in the paper.
 
## oxygen_vacancies_db directory
This directory includes the information related to the machine learning of the defect formation energies.
The df_charge{0,1,2}.pcl files are the pickled dataframe files and DataFrame instances can be retrieved using the following command.

```python
import pandas as pd
charge = 0
df = pd.read_pickle(f"df_charge{charge}.pcl")
```

The csv files generated from the dataframes are also distributed.

### machine_learning.py
This script was used for the machine learning of the defect formation energies.
The command line argument receives the random state used in the scikit learn. 
The script can be run as follows:
```
python ~/my_programs/oxygen_vacancies_db/vacancy_formation_energy_ml/machine_learning.py 1
```

## Description for the graphical user interface 
### Band structure & density of states
The green lines in the *band* figure shows the PBE band structure, while
the black lines the calculated one by the non-self-consistent use of a dielectric-dependent (nsc-dd) hybrid functional.
See our paper for details of the calculation conditions.

#### Defects with PHS
This panel tabulates the defects with perturbed host states (PHS).
See our paper for details of the PHS.

#### Non-trivial Defects
This panel indicates a set of defects that show non-trivial defects.

- defect type: Shown when the defect type is detected other than vacancy.
  The shown type is vacancy_spit or unknown, the latter of which indicates the defect accompany large atomic reconstruction.
- supergroup: Shown when the final structure shows supergroup relation with respect to the initial site symmetry.
- not same config from init: Shown when the atomic configuration is considered to 
  be different from the initial structure using the atom mapping technique with cutoff = 1Å.
- energy strange: Shown when the absolute formation energy is anomalously large.

#### Defect Formation Energy
Using the **Allow defects with perturbed host states** button, 
one can control if the formation energies of the defects with the PHS are considered in the formation energy figure. 

One can also change the chemical potential condition by pushing the circle with an alphabet in the chemical potential diagram
for binary or ternary compounds. 
Otherwise, **Equilibrium label** can be used for the chemical potential.

### To defect page
This web page shows the information on individual defect calculation.
The name indicates vacancy site and charge state (*q*). 
For example, Va_O1_0 means the oxygen vacancy at the O1 site with charge state *q*=0.

#### Potential 
This panel shows the atomic site potential. 
The values for elements are potentials caused by the defect, 
which is the potential difference of the defective supercells from the perfect supercells calculated with VASP.
The **PC** indicates the point-charge potential, 
while **Diff** means difference of the element values from the **PC** values.

#### Eigenvalues 
The Eigenvalues mean the electron eigenvalues at the converged structures.
The energy is in the absolute scale directly obtained from the VASP calculations.
The occupation number and band index are shown by moving their mouse cursor over the point and having a hover label appear.
The points are colored by blue when the occupation is less than 0.2, 
while by red when it is larger than 0.8, and those in between by green.

#### Vesta file and PARCHG files 
The vesta file shows the defective supercell structure in [VESTA](https://jp-minerals.org/vesta/en/) program format.
In the VESTA program, local structures are shown with labels and arrows.
When the label is a single number, the distance from the defect is shown, 
while two numbers are connected with an underscore, the distance and the displacement (>0.1Å) are shown.
The arrow indicates the direction of the displacement and the length is 10 times the displacement.

The PARCHG file is a compressed file, which includes the converged structure named CONTCAR-finish with POSCAR format,
and the parchg_($BAND_INDEX).vesta files show the structure with squared wavefunction at the $BAND_INDEX band index
When the number of k-points is more than 1, their averaged value by weight is shown.
To reduce the compressed file size, the values in PARCHG_($BAND_INDEX).vesta are categorized from their original values
according to the normalized values by the largest value as shown below. And, the VESTA show theses isosurfaces by default.

- 0.0 ~ 0.1 --> 0
- 0.1 ~ 0.5 --> 1
- 0.5 ~ 0.8 --> 2
- 0.8 ~ 1.0 --> 3
