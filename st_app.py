import streamlit as st
import pandas as pd
import altair as alt
import webbrowser


# todo: add chime model with auto populate

st.title('California SARS-CoV2 tracking')


# https://data.ca.gov/group/covid-19
cdph_data_url = 'https://data.chhs.ca.gov/dataset/f333528b-4d38-4814-bebb-12db1f10f535/resource/046cdd2b-31e5-4d34-9ed3-b48cdbc4be7a/download/covid19cases_test.csv'
hospital_data_url = 'https://data.chhs.ca.gov/dataset/2df3e19e-9ee4-42a6-a087-9761f82033f6/resource/47af979d-8685-4981-bced-96a6b79d3ed5/download/covid19hospitalbycounty.csv'


def gather_data():
    return pd.read_csv(cdph_data_url)


data = gather_data()
county = sorted(data.area.unique())
county_select = st.selectbox('Select County', list(county))


population_data = data[['area', 'population']].drop_duplicates(keep='last')
county_pop = int(population_data.loc[population_data.area == county_select].population)
running_days = st.slider('Select running days average range', 1, 30, 14)


# data functions
@st.cache
def cases(data_cases):
    data_cases['new_confirmed_cases_rolling_average'] = (data_cases.cases.rolling(running_days).mean()).round(0)
    data_cases['new_deaths_rolling_average'] = (data_cases.reported_deaths.rolling(running_days).mean()).round(0)
    data_cases['cfr'] = ((data_cases.loc[:, 'cumulative_deaths']/data_cases.loc[:, 'cumulative_cases'])*100).round(2)
    county_cases = (data_cases.area == county_select)
    return data_cases.loc[county_cases]


@st.cache
def hospital_data():
    data_hospital = pd.read_csv(hospital_data_url)
    county_hospital = (data_hospital['county'] == county_select)
    return data_hospital.loc[county_hospital]


cases_data = cases(data)
hospital_data = hospital_data()


# Altair charts
def cases_chart():
    chart = (alt.Chart(cases_data)
             .encode(
                 x=alt.X("date:T", title=None), 
                 tooltip=['date:T', 
                          'new_confirmed_cases_rolling_average:Q', 
                          'cases:Q', 
                          "cumulative_deaths:Q"])
            )
    cases_bars = chart.mark_bar().encode(y=alt.Y("cases:Q", title="New confirmed cases"))
    cases_line_14 = chart.mark_line(color='blue').encode(y=alt.Y("new_confirmed_cases_rolling_average:Q",
                                                                 title="14-day average"))
    deaths_line = chart.mark_line(color='black').encode(y=alt.Y("cumulative_deaths:Q",title="Total deaths"))
    return (
        alt.layer(cases_bars, cases_line_14, deaths_line)
        .properties(title=f"{county_select} County cases by day", width=1000, height=400)
        .interactive()
    )


def hospital_chart():
    chart = alt.Chart(hospital_data).encode(x = alt.X('todays_date:T', title = None))
    icu_pos = chart.mark_line(color='blue', size=3).encode(y = alt.Y('icu_covid_confirmed_patients:Q', title='ICU'))
    pos_pts = chart.mark_bar(color='steelblue', size=5).encode(y = alt.Y('hospitalized_covid_confirmed_patients:Q', title='Positive hospitalized'))
    return (
        alt.layer(pos_pts, icu_pos)
        .encode(tooltip=['todays_date:T', 'icu_covid_confirmed_patients:Q', 'hospitalized_covid_confirmed_patients:Q'])
        .properties(title = 'Currrent Hospitilazations & ICU', width=1000, height=400)
        .interactive()
    )


def cfr_chart():
    cfr_chart = alt.Chart(cases_data).encode(x = alt.X('date:T'))
    cfr = cfr_chart.mark_line(color='blue', size=3).encode(y = alt.Y('cfr:Q',title = 'CFR'))
    return (cfr.encode(tooltip=[alt.Tooltip('date:T', title='Date'), alt.Tooltip('cfr:Q', title='CFR')])).properties(title = 'CFR', width=1000,height=400).interactive()


def icu():
    icu_chart = alt.Chart(hospital_data).encode(x=alt.X('todays_date:T', title=None))
    icu_line = icu_chart.mark_line(color='blue', size=3).encode(y=alt.Y('icu_available_beds:Q', title=None))
    return (icu_line.encode(tooltip=['todays_date:T', 'icu_available_beds:Q'])
        .properties(title='ICU beds available', width=1000,height=400)
        .interactive()
    )


# sidebar items
show_cases_data = st.sidebar.checkbox('Show cases data')
if show_cases_data:
    st.write(cdph_data_url)
    st.subheader('Raw cases data')
    st.write(cases_data)

show_hosptial_data = st.sidebar.checkbox('Show hospital data')
if show_hosptial_data:
    st.write(hospital_data_url)
    st.subheader('Raw hospital data')
    st.write(hospital_data)

show_population_data = st.sidebar.checkbox('Show population data')
if show_population_data:
    st.write(f'{county_select} County has a population of {county_pop:,}')


# sidebar buttons for external sites
divoc = 'https://91-divoc.com/pages/covid-visualization/?chart=countries&highlight=United%20States&show=highlight-only&y=both&scale=linear&data=cases-daily-7&data-source=jhu&xaxis=left&extraData=deaths-daily-7&extraDataScale=separately#countries'
chime = 'https://penn-chime.phl.io/'

if st.sidebar.button('91-DIVOC'):
    webbrowser.open_new_tab(divoc)

if st.sidebar.button('CHIME'):
    webbrowser.open_new_tab(chime)

# display charts
new_per_x_days = int(cases_data.reported_cases[-running_days:].sum())
pop_x = county_pop/100000
running_per_pop = round(new_per_x_days/pop_x)
st.write(f'There have been **{new_per_x_days:,}** new confirmed cases in **{county_select} County** over the last **{running_days}** days with **{running_per_pop}** new cases per 100,000 county residents.')
cases_chart = cases_chart()
hospital_chart = hospital_chart()
cfr_chart = cfr_chart()
icu = icu()

st.altair_chart(cases_chart, use_container_width=False)
st.altair_chart(hospital_chart, use_container_width=False)
st.altair_chart(cfr_chart, use_container_width=False)
st.altair_chart(icu, use_container_width=False)




