# BMI706: Data Visualization Project Mortality Data
---
Authors: Benedikt Geiger, Mirja Mittermaier, Fiona Song, Lantian Xu <br>
April 2022
---

The goal of our project is to gain insights from state- (and county-level) visualizations of US mortality data.
The data ranges from 1968 to 2016 and is stratified by state, (county), year, race, gender, age group and ICD group.

We used Altair and Streamlit to solve the following tasks:
* Identify differences in US state (and county) mortality rates
* Reveal mortality rate trends for different ICD groups
* Detect gender, race and age group mortality differences
* Display population growth per state, race and age group

<strong>Note</strong>: Our full project visualizes county-level data and is available on [this repository](https://github.com/BeGeiger/BMI706_mortality_project).
It requires the generation of data files by executing a shell script. This is our condensed repository, which restricts our visualizations to the state
level. All required data is already in the repository and no data generation scripts has to be executed.

Please read the `README_data_generation.md` file in the `data_generation` folder for further details on the raw data and our data processing steps.

Run the visualization app `project_app.py` via

```bash
streamlit run project_app.py
```
