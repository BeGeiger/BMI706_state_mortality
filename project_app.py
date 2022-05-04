import altair as alt
import pandas as pd
import streamlit as st
import numpy as np
from array import *
from numpy import NAN
from streamlit_vega_lite import vega_lite_component, altair_component
from vega_datasets import data


path_mort_state = 'data_generation/mortality/state_level/'

## read in data ##
@st.cache
def load_state6878():
	return pd.read_csv(path_mort_state + 'Mort6878.tsv', sep='\t')

@st.cache
def load_state7998():
	return pd.read_csv(path_mort_state + 'Mort7998.tsv', sep='\t')

@st.cache
def load_state9916():
	return pd.read_csv(path_mort_state + 'Mort9916.tsv', sep='\t')

@st.cache
def load_state6816():
	return pd.read_csv(path_mort_state + 'Mort6816.tsv', sep='\t', low_memory=False)

@st.cache
def load_pop6816():
	return pd.read_csv('data_generation/population/state_level/Pop6816.tsv', sep='\t')



def prep_data3(dat, year, race, gender, age, ICD):
	dat = dat[dat['Year'] == year]
	dat = dat[dat['Race'] == race]
	dat = dat[dat['Gender'] == gender]
	dat = dat[dat['Age Group'] == age]
	dat = dat[dat['ICD Group'] == ICD]
	return dat

def prep_data4(dat, state, race, gender, age):
	dat = dat[dat['State'] == state]
	dat = dat[dat['Race'] == race]
	dat = dat[dat['Gender'] == gender]
	dat = dat[dat['Age Group'] == age]
	return dat


state6878 = load_state6878()
state7998 = load_state7998()
state9916 = load_state9916()
state6816 = load_state6816()
state_pop = load_pop6816()

year_min = 1968
year_max = 2016

age_order = [
	'< 1 year','1-4 years', '5-9 years', '10-14 years','15-19 years','20-24 years',
	'25-34 years','35-44 years','45-54 years','55-64 years','65-74 years', '75-84 years',
	'85+ years'
]



## US STATE MORTALITY RATES ##
st.header("US State Mortality Rates")

year3 = st.slider('Year', min_value=year_min, max_value=year_max, step=1, key="year3")

# year selection determines data
if year3 <= 1978:
	dat_state = state6878
elif year3 > 1978 and year3 <= 1988:
	dat_state = state7998
elif year3 > 1988 and year3 <= 1998:
	dat_state = state7998
else:
	dat_state = state9916

#selections
gender3 = st.radio("Sex", tuple(dat_state["Gender"].unique()), key="gender3")
race3 = st.radio("Race", tuple(dat_state["Race"].unique()), key="race3")
ICD3 = st.selectbox('ICD Group', dat_state["ICD Group"].unique(), key="ICD3")
age3 = st.selectbox(
	'Age Group', 
	[ao for ao in age_order if ao in dat_state["Age Group"].unique()],
	key="age3"
)

selected = alt.selection_single()

state_subset = prep_data3(dat_state, year3, race3, gender3, age3, ICD3)


# STATE MORTALITY RATES
source_us = alt.topo_feature(data.us_10m.url, 'states')
rate_scale3_state = alt.Scale(
	domain=[state_subset['Mortality Rate'].min(), state_subset['Mortality Rate'].max()], 
	scheme="bluegreen"
)
rate_color3_state = alt.Color(
	field="Mortality Rate", 
	type="quantitative", 
	scale=rate_scale3_state
)

background_us = alt.Chart(source_us).mark_geoshape(
	fill='lightgray',
	stroke='white'
).properties(
	width=700,
	height=420
).project(
	'albersUsa'
)

state_rate = alt.Chart(source_us).mark_geoshape().encode(
	color= rate_color3_state,
	tooltip=["Mortality Rate:Q", "State:N"]
).properties(
	title=f'Mortality Rate of {ICD3} for {gender3} {age3} old in {year3} in U.S.',
	width=700,
	height=420
).transform_lookup(
	lookup="id",
	from_=alt.LookupData(state_subset, "State Code", ["Mortality Rate", 'State']),
).project(
	'albersUsa'
).add_selection(
	selected
).transform_filter(
	selected
)

if len(state_subset):
	st.altair_chart(background_us+state_rate, use_container_width=True)
else:
	st.info("No state-level data avaiable for the given subset.")	


## MORTALITY TRENDS OF DIFFERENT ICD CODES ##
st.header("Mortality Rate Trends for Different ICD Groups")

# selection
state4 = st.selectbox('State', state6816["State"].unique(), key="state4")
gender4 = st.radio("Sex", tuple(state6816["Gender"].unique()), key="gender4")
race4 = st.radio("Race", tuple(state6816["Race"].unique()), key="race4")
age4 = st.selectbox('Age Group', age_order, key="age4")


all_subset = prep_data4(state6816, state4, race4, gender4, age4)
all_subset['Year'] = pd.to_datetime(all_subset['Year'], format='%Y')


icd_selection = alt.selection_single(
    fields=['ICD Group'],
    bind='legend',
    init={'ICD Group': "no_disease"}
)



base = alt.Chart(all_subset).mark_area().encode(
	x=alt.X('year(Year):T', scale=alt.Scale(domain=[all_subset['Year'].min(), all_subset['Year'].max()]), title=None)
)

time_brush = alt.selection_interval(encodings=['x'])


upper = base.encode(
	alt.X('year(Year):T', scale=alt.Scale(domain=time_brush), title=None),
	y=alt.Y("Mortality Rate:Q", title=None),
	row=alt.Row('ICD Group:N', header=alt.Header(labels=False), title="Mortality Rate"),
	color = alt.Color('ICD Group:N', legend=alt.Legend())
).add_selection(
	icd_selection
).properties(
	width=700,	
	height=50,
	title=f'Mortality Rates for {gender4} {age4} old across years'
)

lower = alt.Chart(all_subset).mark_line().encode(
	alt.X('year(Year):T', title='Year'),
	y=alt.Y("Mortality Rate:Q", title=None),
	color = alt.value("black")
).transform_filter(
	icd_selection
).add_selection(
	time_brush
).properties(
	width=700,
	height=50,
	title='Mortality Rate of the ICD Group selected in the Legend'
)


chart4 = alt.vconcat(
	upper, lower
).resolve_scale(
	color='independent'
)


if len(all_subset):
	st.write("Note: Area chart is empty when there is only data for one year")
	st.altair_chart(chart4, use_container_width=True)
else:
	st.info("No data avaiable for given subset.")



## COMPARE SEX AND RACE GROUPS ##
ICD_default = ['Pneumonia']

st.header("Gender and Race Mortality Differences")

year5 = st.slider('Year', min_value=year_min, max_value=year_max, step=1, key="year5")

if year5 <= 1978:
	dat_task5 = state6878
elif year5 <= 1998:
	dat_task5 = state7998
else:
	dat_task5 = state9916

state5 = st.selectbox('State', dat_task5["State"].unique(), key="state5")
age5 = st.selectbox('Age Group', age_order, key="age5")
ICD5 = st.multiselect('ICD Group', dat_task5["ICD Group"].unique(), ICD_default, key="ICD5")

dat_task5 = dat_task5[(dat_task5["State"] == state5) & (dat_task5["Year"] == year5) & (dat_task5["Age Group"] == age5) & (dat_task5["ICD Group"].isin(ICD5))]


# Bar Chart: Gender Differences
st.subheader("Gender Mortality Differences")

race5 = st.radio("Race", dat_task5["Race"].unique(), key="race5")
gender_subset = dat_task5[dat_task5["Race"] == race5]

gender_task5 = alt.Chart(gender_subset).mark_bar().encode(
	x=alt.X('Gender:N', title=None, axis=alt.Axis(labels=False)),
	y='Mortality Rate:Q',
	color=alt.Color("Gender"),
	column=alt.Column('ICD Group:N', header=alt.Header(labelAngle=-90, labelAlign='right', titleOrient='bottom')),
	tooltip=["Mortality Rate:Q","Gender:N", "ICD Group:N"]
).properties(
	width=50
).configure_range(
	category={'scheme': 'viridis'}
)

if len(gender_subset):
	st.altair_chart(gender_task5, use_container_width=False)
else:
	st.info("No data avaiable for the given subset.")

	
# Bar Chart: Race Differences
st.subheader("Race Mortality Differences")

gender5 = st.radio("Sex", dat_task5["Gender"].unique(), key = "gender5")
race_subset = dat_task5[dat_task5["Gender"] == gender5]

race_task5 = alt.Chart(race_subset).mark_bar().encode(
	x=alt.X('Race:N', title = None, axis = alt.Axis(labels = False)),
	y='Mortality Rate:Q',
	color=alt.Color("Race"),
	column=alt.Column('ICD Group:N', header=alt.Header(labelAngle=-90, labelAlign='right', titleOrient='bottom')),
	tooltip=["Mortality Rate:Q", "Race:N", "ICD Group:N"]
).properties(
	width=50
).configure_range(
	category={'scheme': 'magma'}
)

if len(race_subset):
	st.altair_chart(race_task5, use_container_width=False)
else:
	st.info("No data avaiable for the given subset.")



## AGE GROUP DIFFERENCES ##
st.header("Age Group Mortality Differences")

year6 = st.slider('Year', min_value=year_min, max_value=year_max, step=1, key="year6")

if year6 <= 1978:
	dat_task6 = state6878
elif year6 <= 1998:
	dat_task6 = state7998
else:
	dat_task6 = state9916

state6 = st.selectbox('State', dat_task6["State"].unique(), key="state6")
gender6 = st.radio("Sex", tuple(dat_task6["Gender"].unique()), key="gender6")
race6 = st.radio("Race", tuple(dat_task6["Race"].unique()), key="race6")

ICD6 = st.multiselect('ICD Group', dat_task6["ICD Group"].unique(), ICD_default, key="ICD6")

task6_subset = dat_task6[(dat_task6["Year"] == year6) & (dat_task6["Gender"] == gender6) & (dat_task6["State"] == state6) & (dat_task6["ICD Group"].isin(ICD6))]

ICD_selected = alt.selection_single(fields=['ICD Group'], bind='legend')
ICD_task6 = alt.Chart(task6_subset).mark_bar().encode(
	x=alt.X('ICD Group:N', title=None, axis=alt.Axis(labels=False)),
	y='Mortality Rate:Q',
	color=alt.Color("ICD Group:N"),
	column=alt.Column('Age Group:O',sort=age_order, header=alt.Header(labelAngle=-90, labelAlign='right',titleOrient='bottom')),
	opacity=alt.condition(ICD_selected, alt.value(1), alt.value(0.1)),
	tooltip=["Mortality Rate:Q", "Age Group:O", "ICD Group:N"]
).add_selection(
	ICD_selected
).properties(
	width=50
).configure_range(
	category={'scheme': 'viridis'}
)

if len(task6_subset):
	st.altair_chart(ICD_task6, use_container_width=False)
else:
	st.info("No data avaiable for the given subset.")
	
	






## Population Growth ##
st.header("Population Growth per State")
alt.data_transformers.disable_max_rows()

state_pop_1 = state_pop.groupby(['State','Year','Gender', 'Race', 'Age Group']).sum().reset_index()

state7 = st.selectbox('State', state_pop_1["State"].unique(), key="state7")
state_pop_1 = state_pop_1[(state_pop_1["State"] == state7)]


race_selection = alt.selection_multi(fields=['Race'], bind='legend')

base = alt.Chart(state_pop_1).add_selection(
	race_selection
)

slider = alt.binding_range(name='Year:', min=year_min, max=year_max, step=1)
selector = alt.selection_single(
	name="YearSelector", fields=['Year'],
	bind=slider, init={"Year": 1968}
)

                            
upper = base.mark_bar().encode(
	x=alt.X('Race', axis=alt.Axis(labels=False,title=None)),
	y=alt.Y('sum(Population):Q', axis=alt.Axis(title='Population')),
	color=alt.Color('Race', scale=alt.Scale(scheme="magma"), legend=alt.Legend()),
	column=alt.Column('Year', title=None, header=alt.Header(labelAngle=90)),
	opacity=alt.condition(race_selection, alt.value(1), alt.value(0.2))
).properties(
	width=10
)


lower = base.mark_bar().encode(
	x=alt.X('Age Group', axis=alt.Axis(title=None), sort=age_order),
	y=alt.Y('sum(Population):Q', axis=alt.Axis(title='Population')),
	color=alt.Color('Age Group', sort=age_order, scale=alt.Scale(scheme="bluegreen")),
	tooltip = ['sum(Population)', 'Age Group']
).add_selection(
	race_selection
).transform_filter(
	race_selection
).add_selection(
	selector
).transform_filter(
	selector
).properties(
	width=780,
	height=250,
	title='Population Distribution per Year and Selected by Race via the above Legend'
)


chart3 = alt.vconcat(upper, lower).resolve_scale(
	color='independent'
).configure_view(
	stroke='transparent'
).configure_scale(
	bandPaddingInner=0,
	bandPaddingOuter=0.01,
).configure_facet(
	spacing=4
)

st.altair_chart(chart3, use_container_width=False)





