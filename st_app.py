import streamlit as st
import pandas as pd
import altair as alt
import webbrowser



# import chime

st.title('California SARS-CoV2 tracking project')


# url's to CDPH data sources
# https://data.ca.gov/group/covid-19
cases_url = 'https://data.ca.gov/dataset/590188d5-8545-4c93-a9a0-e230f0db7290/resource/926fd08f-cc91-4828-af38-bd45de97f8c3/download/statewide_cases.csv'
hospital_url = 'https://data.ca.gov/dataset/529ac907-6ba1-4cb7-9aae-8966fc96aeef/resource/42d33765-20fd-44b8-a978-b083b7542225/download/hospitals_by_county.csv'
facility_beds = 'https://data.chhs.ca.gov/dataset/09b8ad0e-aca6-4147-b78d-bdaad872f30b/resource/0997fa8e-ef7c-43f2-8b9a-94672935fa60/download/healthcare_facility_beds.xlsx'


# county selection list
def county():
    data_hospital = pd.read_csv(hospital_url)
    data_hospital['todays_date'] = pd.to_datetime(data_hospital['todays_date'], format='%Y-%m-%d')
    county = sorted(data_hospital.county.unique())
    return county

# county selection dropdown
county_select = st.selectbox('Select County', list(county()))

# data functions
@st.cache
def cases():
    data_cases = pd.read_csv(cases_url)
    data_cases['date'] = pd.to_datetime(data_cases['date'], format='%Y-%m-%d')
    data_cases['new_confirmed_cases_rolling_average'] = (data_cases.newcountconfirmed.rolling(14).mean()).round(0)
    data_cases['new_deaths_rolling_average'] = (data_cases.newcountdeaths.rolling(14).mean()).round(0)
    data_cases['cfr'] = ((data_cases.loc[:, 'totalcountdeaths']/data_cases.loc[:, 'totalcountconfirmed'])*100).round(2)
    county_cases = (data_cases['county'] == county_select)
    county_cases_data = data_cases.loc[county_cases]
    return county_cases_data


@st.cache
def hospital():
    data_hospital = pd.read_csv(hospital_url)
    data_hospital['todays_date'] = pd.to_datetime(data_hospital['todays_date'], format='%Y-%m-%d')
    county_hospital = (data_hospital['county'] == county_select)
    county_hospital_data = data_hospital.loc[county_hospital]
    return county_hospital_data



# Altair charts
def cases_chart():
    chart = alt.Chart(cases()).encode(x=alt.X("date:T", title=None), tooltip=['date:T', 'new_confirmed_cases_rolling_average:Q', 'newcountconfirmed:Q', "totalcountdeaths:Q"])
    cases_bars = chart.mark_bar().encode(y=alt.Y("newcountconfirmed:Q", title="New confirmed cases"))
    cases_line_14 = chart.mark_line(color='blue').encode(y=alt.Y("new_confirmed_cases_rolling_average:Q",title="14-day average"))
    deaths_line = chart.mark_line(color='black').encode(y=alt.Y("totalcountdeaths:Q",title="Total deaths"))
    return (
        alt.layer(cases_bars, cases_line_14, deaths_line)
        .properties(title="County cases by day", width=1000, height=400)
        .interactive()
    )

def hospital_chart():
    chart = alt.Chart(hospital()).encode(x = alt.X('todays_date:T', title = None))
    icu_pos = chart.mark_line(color='blue', size=3).encode(y = alt.Y('icu_covid_confirmed_patients:Q', title='ICU'))
    pos_pts = chart.mark_bar(color='steelblue', size=5).encode(y = alt.Y('hospitalized_covid_confirmed_patients:Q', title='Positive hospitalized'))
    return (
        alt.layer(pos_pts, icu_pos)
        .encode(tooltip=['todays_date:T', 'icu_covid_confirmed_patients:Q', 'hospitalized_covid_confirmed_patients:Q'])
        .properties(title = 'Currrent Hospitilazations & ICU', width=1000, height=400)
        .interactive()
    )

def cfr_chart():
    cfr_chart = alt.Chart(cases()).encode(x = alt.X('date:T'))
    cfr = cfr_chart.mark_line(color='blue', size=3).encode(y = alt.Y('cfr:Q',title = 'CFR'))
    return (cfr.encode(tooltip=[alt.Tooltip('date:T', title='Date'), alt.Tooltip('cfr:Q', title='CFR')])).properties(title = 'CFR', width=1000,height=400).interactive()

def icu():
    icu_chart = alt.Chart(hospital()).encode(x=alt.X('todays_date:T', title=None))
    icu_line = icu_chart.mark_line(color='blue', size=3).encode(y=alt.Y('icu_available_beds:Q', title=None))
    return (icu_line.encode(tooltip=['todays_date:T', 'icu_available_beds:Q'])
        .properties(title='ICU beds available', width=1000,height=400)
        .interactive()
    )








# def icu_county():
#     data_beds = pd.read_excel(facility_beds)
#     icu_cap_county = sorted(data_beds.COUNTY_NAME.unique())
#     return icu_cap_county
# icu_select = st.selectbox('Select ICU', list(icu_county()))

# def icu_beds():
#     data_beds = pd.read_excel(facility_beds)
#     beds = data_beds.loc[:, ['FACNAME', 'FAC_FDR', 'BED_CAPACITY_TYPE', 'BED_CAPACITY']].where(data_beds['COUNTY_NAME'] == icu_county()).dropna()
#     icu_beds = beds.loc[:,:].where(beds['BED_CAPACITY_TYPE'] == 'INTENSIVE CARE').dropna()
#     icu_beds = icu_beds.BED_CAPACITY.sum()
#     return icu_beds



# sidebar items
cases_data = st.sidebar.checkbox('Show cases data')
if cases_data:
    st.write(cases_url)
    st.subheader('Raw data')
    st.write(cases())

hosptial_data = st.sidebar.checkbox('Show hospital data')
if hosptial_data:
    st.write(hospital_url)
    st.subheader('Raw data')
    st.write(hospital())


# sidebar buttons for external sites
divoc = 'https://91-divoc.com/pages/covid-visualization/?chart=countries&highlight=United%20States&show=highlight-only&y=both&scale=linear&data=cases-daily-7&data-source=jhu&xaxis=left&extraData=deaths-daily-7&extraDataScale=separately#countries'
chime = 'https://penn-chime.phl.io/'

if st.sidebar.button('91-DIVOC'):
    webbrowser.open_new_tab(divoc)

if st.sidebar.button('CHIME'):
    webbrowser.open_new_tab(divoc)

# display charts
st.write(cases_chart())
st.write(hospital_chart())
st.write(cfr_chart())
st.write(icu())



