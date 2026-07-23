# Bike Net Kit / Data export

Auxiliary [scripts](scripts/) for exporting data about all BikeNetKit packages, and [exported data](dataexports/), which is only needed once as preparation for the interactive visualization platform.


## Setup
Installation with [`Pixi`](https://pixi.prefix.dev/latest/) is fastest and most stable:

```
pixi init --import environment.yml
```

At this point, run the pixi shell to run scripts in the environment:

```
pixi shell
```

## Update
To use latest BikeNetKit package releases, don't forget to upgrade them (example growbikenet):

```
pixi upgrade growbikenet
```

## Repository structure

```
├── cities           <- Exported and meta city data
├── dataexports      <- Exported data sets
├── scripts          <- Export scripts
├── environment.yml  <- Environment file
```

## Supported by
Development of BikeNetKit was supported by the [Innovation Fund Denmark](https://innovationsfonden.dk/en), the EU HORIZON project [JUST STREETS](https://www.just-streets.eu), and the [Data Science Section](https://en.itu.dk/Research/Sections-and-research-groups/Data-Science) of IT University of Copenhagen.


[![Innovation Fund Denmark](https://raw.githubusercontent.com/BikeNetKit/.github/refs/heads/main/profile/_static/logo_innovationfund.png)](https://innovationsfonden.dk/en) &emsp;&emsp; [![European Union](https://raw.githubusercontent.com/BikeNetKit/.github/refs/heads/main/profile/_static/logo_eu.png)](https://commission.europa.eu/index_en) &ensp; [![JUST STREETS](https://raw.githubusercontent.com/BikeNetKit/.github/refs/heads/main/profile/_static/logo_juststreets.png)](https://www.just-streets.eu/) 


