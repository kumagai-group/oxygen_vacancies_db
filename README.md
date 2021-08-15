## Oxygen vacancy database  

This repository includes the database reported in the paper
"Insights Into Oxygen Vacancies from High-Throughput First-Principles Calculations
" written by Yu Kumagai, Naoki Tsunoda, Akira Takahashi, and Fumiyasu Oba.

## How to use  

1. Clone this repository.
2. Prepare a clean python environment using e.g., virtualenv.
3. Run `pip install -r requirements.txt` to install the relevant python files.
4. Go to the oxygen_vacancies_db_data in the cloned directory 
   and unpack the files with `for i in *.tar.gz; do echo $i; tar xvfz $i; done` 
   (about 2GB)
5. Export PYTHONPATH=$PYTHONPATH:(PATH TO oxygen_vacancies_db) to add the path
6. Run `python (PATH TO oxygen_vacancies_db)/programs/create_app.py --source_dir="(PATH TO oxygen_vacancies_db)/oxygen_vacancies_db_ data" --formulas="[ZnO]"` 
   to see if you can create a ZnO page.


###  site_info.tar.gz file
This is the compressed files containing the site infos in the supercells.
The cif files of the supercell structures are also included.
 
###  oxygen_vacancies_db directory

This directory contains the information related to the machine learning of the defect formation energies.
The df_charge{0,1,2}.pcl files are the pickled dataframe files.
These can be retrieved using the following command.

```python
import pandas as pd
charge = 0
df = pd.read_pickle(f"df_charge{charge}.pcl")
```

The csv files are also distributed.

#### machine_learning.py

This script was used for the machine learning of the defect formation energies.
The command line argument is the random state used in the scikit learn, and 
the script can be run as follows:
```
python ~/my_programs/oxygen_vacancies_db/vacancy_formation_energy_ml/machine_learning.py 1
```

## Description of the GUI
### Unusual Defects
This panel indicates a set of defects that show non-trivial defects.

- unusual defect type: Shown when the defect type is detected other than vacancy, its type is written.
  In this study, vacancy_spit or unknown are appeared, the latter of which indicates large atomic reconstruction.
- supergroup: Shown if the final structure shows supergroup relation with respect to the initial site symmetry.
- not same config from init: Shown if the atomic configuration is considered to 
  be different from the initial structure using the atom mapping technique with cutoff = 1Å.
- energy strange: Shown in the absolute formation energy is anomalously large.

### To defect page
This page shows the information on individual defect.
The name e.g., Va_O1_0 indicates oxygen vacancy at the O1 site with charge state q=0.

#### Potential 
It shows the atomic site potential. 
The values for elements are potentials caused by the defect, which is the potential difference of the defective supercells from the perfect supercells calculated by VASP.
The PC indicates the point-charge potential, while Diff means the element values minus PC values.

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


