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

The data licensed under a [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) license.

## Precautions  

1. 
