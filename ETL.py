import pandas as pd

confirmed = pd.read_csv('time_series_covid19_confirmed_global.csv')
deaths = pd.read_csv('time_series_covid19_deaths_global.csv')
recovered = pd.read_csv('time_series_covid19_recovered_global.csv')

# Transformation des données

# Suppression des colonnes Lat et Long
confirmed = confirmed.drop(['Lat', 'Long', 'Province/State'], axis=1)
deaths = deaths.drop(['Lat', 'Long', 'Province/State'], axis=1)
recovered = recovered.drop(['Lat', 'Long', 'Province/State'], axis=1)

# Utilisation de la fonction melt pour regrouper les dates dans une seule colonne
df_confirmed = confirmed.melt(id_vars=['Country/Region'], var_name='Date', value_name='Nbr_cas')
df_deaths = deaths.melt(id_vars=['Country/Region'], var_name='Date', value_name='Nbr_cas')
df_recovered = recovered.melt(id_vars=['Country/Region'], var_name='Date', value_name='Nbr_cas')

# Conversion de la colonne date au format date
df_confirmed['Date'] = pd.to_datetime(df_confirmed['Date'], format='%m/%d/%y')
df_deaths['Date'] = pd.to_datetime(df_deaths['Date'], format='%m/%d/%y')
df_recovered['Date'] = pd.to_datetime(df_recovered['Date'], format='%m/%d/%y')

# Renommer colonne
df_confirmed = df_confirmed.rename(columns={'Country/Region': 'Country_region'})
df_deaths = df_deaths.rename(columns={'Country/Region': 'Country_region'})
df_recovered = df_recovered.rename(columns={'Country/Region': 'Country_region'})

# Evolution des cas par pays et date
df_agg_confirmed = df_confirmed.groupby(['Country_region', 'Date']).sum().reset_index()
df_agg_deaths = df_deaths.groupby(['Country_region', 'Date']).sum().reset_index()
df_agg_recovered = df_recovered.groupby(['Country_region', 'Date']).sum().reset_index()

# Convertir le data frame en format JSON
df_agg_confirmed.to_json('confirmed.json', orient='records')
df_agg_deaths.to_json('deaths.json', orient='records')
df_agg_recovered.to_json('recovered.json', orient='records')


