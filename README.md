# BikeNetKit - Data export

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

Auxiliary [scripts](scripts/) for exporting data about all BikeNetKit packages, and [exported data](dataexports/), which is only needed once as preparation for the interactive visualization platform.


## Repository structure

```
├── cities                  <- Information for which cities to export
├── dataexports             <- Exported data sets, by dated subfolders
├── scripts                 <- Export scripts
├── .gitignore              <- Files and folders ignored by git
├── .pre-commit-config.yaml <- Pre-commit hooks used
├── README.md
├── environment.yml         <- Environment file to set up the environment using conda/mamba/pixi
```

## Credits

<!--Please cite as: 
>AUTHOR1, AUTHOR2, and AUTHOR3, PROJECTNAME, JOURNAL (YYYY), DOIURL  
-->

Development of BikeNetKit was supported by the Danish Innovation Fund (Innovationsfonden).


