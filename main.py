# %%    Load Dependencies
import pandas as pd
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
aqi_df = pd.read_csv('./resources/AQI_by_County/county_annual_aqi.csv')
bea_df = pd.read_csv('./resources/BEA/BEA_annual.csv', index_col=['State', 'Year'])
ihme_df = pd.read_csv('./resources/IHME-GBD_2021_DATA-fd6afd4d-1/IHME-GBD_2021_DATA-fd6afd4d-1.csv')


# %%    BEA DATA ALREADY FILTERED
bea_df


# %%    AQI DATA FILTERING
aqi_df['Very Unhealthy Days'] = aqi_df['Very Unhealthy Days'] + aqi_df['Hazardous Days']
aqi_columns_to_drop = ['Days CO', 'Days NO2', 'Days Ozone', 'Days PM2.5', 'Days PM10', 'Unhealthy for Sensitive Groups Days', 'County', 'Hazardous Days']
aqi_df = aqi_df.drop(columns=aqi_columns_to_drop)
aqi_df = aqi_df[(aqi_df['Year'] >= 2015) & (aqi_df['Year'] <= 2020)]
aqi_df = aqi_df[(aqi_df['State'] == 'New York') | 
                (aqi_df['State'] == 'New Mexico') | 
                (aqi_df['State'] == 'Washington')]
aqi_df = aqi_df.groupby(['State', 'Year']).mean().reset_index()
aqi_df = aqi_df.set_index(['State', 'Year'])
aqi_df


# %%    HEALTH DATA FILTERING
ihme_columns_to_drop = ['measure_id', 'location_id', 'sex_id', 'age_id', 'cause_id', 'metric_id', 'metric_name', 'upper', 'lower', 'age_name']
ihme_df = ihme_df.drop(columns=ihme_columns_to_drop)
ihme_df = ihme_df.rename(columns={
    'location_name': 'State',
    'measure_name': 'Measure',
    'sex_name': 'Sex',
    'cause_name': 'Cause',
    'val': 'Chronic Respiratory  Related POD (%)',
    'year': 'Year'})
ihme_df['Chronic Respiratory  Related POD (%)'] = ihme_df['Chronic Respiratory  Related POD (%)'] * 100
ihme_df = ihme_df[(ihme_df['Year'] >= 2015) & (ihme_df['Year'] <= 2020)]
ihme_df = ihme_df.groupby(['State', 'Year'])['Chronic Respiratory  Related POD (%)'].mean().reset_index()
ihme_df = ihme_df.set_index(['State', 'Year'])
ihme_df


# %%    Merging tables into master df
master_df = bea_df.merge(aqi_df, left_index=True, right_index=True)
master_df = master_df.merge(ihme_df, left_index=True, right_index=True)
# Creating Master Data Set
master_df.to_csv('./resources/master.csv')
# Load the master dataset
master_df = pd.read_csv('./resources/master.csv', index_col=['State', 'Year'])
master_df


# %%    Analysis #1:
# Comparative State Analysis: Recent economic performance vs. air quality across the three states
    
# This establishes a baseline understanding of how the latest economic indicators relate to 
# air quality metrics in our chosen states. providing a snapshot of whether states with
# stronger economies maintain better or worse air quality.

# Filter the data for 2020
df_2020 = master_df.loc[pd.IndexSlice[:, 2020], :].copy()
# Reset index to make State a column
df_2020 = df_2020.reset_index()
# Prepare economic indicators
economic_data = df_2020[['State', 'personal_income', 'GDP (in $)', 'people_employed']]
economic_data_melted = economic_data.melt(id_vars=['State'], var_name='Indicator', value_name='Value')
# Prepare air quality indicators
air_quality_data = df_2020[['State', 'Good Days', 'Moderate Days', 'Unhealthy Days', 'Very Unhealthy Days']]
air_quality_data_melted = air_quality_data.melt(id_vars=['State'], var_name='Indicator', value_name='Value')
# Set up the plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 16))
fig.suptitle('Comparative State Analysis: Economic Performance and Air Quality (2020)', fontsize=16)
# Plot economic indicators
sns.barplot(x='State', y='Value', hue='Indicator', data=economic_data_melted, ax=ax1)
ax1.set_title('Economic Indicators')
ax1.set_ylabel('Value')
ax1.tick_params(axis='x', rotation=45)
ax1.legend(title='Indicator', bbox_to_anchor=(1.05, 1), loc='upper left')
# Plot air quality indicators
sns.barplot(x='State', y='Value', hue='Indicator', data=air_quality_data_melted, ax=ax2)
ax2.set_title('Air Quality Indicators')
ax2.set_ylabel('Number of Days')
ax2.tick_params(axis='x', rotation=45)
ax2.legend(title='Indicator', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# Conclusion:
    # These findings imply that effective environmental policies,
    # geographical factors, and the nature of economic activities
    # play crucial roles in determining air quality alongside economic 
    # performance. Further research into specific industries, population 
    # density, and environmental regulations would provide more 
    # comprehensive insights into these relationships.

    # The analysis challenges the common assumption that higher economic 
    # activity leads to poorer air quality, as demonstrated by New York's 
    # superior performance in both economic metrics and good air quality 
    # days (306 days) compared to the smaller economies of 
    # Washington (280 days) and New Mexico (213 days).


# %%       Analysis #2:
# Time Series Analysis: GDP vs. AQI for New York State & Washington
# This analysis examines the relationship between economic growth (measured by GDP) 
# and air quality (measured by Max AQI) in New York State and Washington from 2015 to 2020. 

# It aims to reveal potential correlations or divergences between economic performance and
# environmental quality over time in both states given that Washington had the 
# most 'Very Unhealthy Days'.

# Function to create plot for a given state
master_df = master_df.reset_index()
def create_gdp_aqi_plot(state_data, state_name):
    fig, ax1 = plt.subplots(figsize=(14, 7))
    # Plot GDP on the first y-axis
    ax1.set_xlabel('Year')
    ax1.set_ylabel('GDP (in $)', color='tab:blue')
    ax1.plot(state_data['Year'], state_data['GDP (in $)'], color='tab:blue', marker='o', label='GDP')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    # Create a second y-axis for Max AQI
    ax2 = ax1.twinx()
    ax2.set_ylabel('Max AQI', color='tab:red')
    ax2.plot(state_data['Year'], state_data['Max AQI'], color='tab:red', marker='x', label='Max AQI')
    ax2.tick_params(axis='y', labelcolor='tab:red')
    # Add legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    plt.title(f'GDP vs Max AQI Over Time for {state_name}')
    fig.tight_layout()
    plt.show()
# Create plot for New York
ny_data = master_df[master_df['State'] == 'New York']
create_gdp_aqi_plot(ny_data, 'New York')
# Create plot for Washington
wa_data = master_df[master_df['State'] == 'Washington']
create_gdp_aqi_plot(wa_data, 'Washington')
# Conclusion:
    # From 2015 to 2020, New York's GDP grew from approximately $1.5 trillion to $1.77 trillion,
    # reflecting consistent economic expansion despite a slight dip in 2020 due to the pandemic, 
    # while Washington's GDP increased steadily from $467 billion in 2015 to $620 billion in 2020, 
    # showcasing robust economic growth.
    
    # Unlike New York, Washington's GDP and Max AQI trends diverged more noticeably, indicating 
    # that economic growth may have coincided with periods of poorer air quality. The differing
    # trends between New York and Washington highlight the importance of tailored environmental 
    # policies and management strategies to balance economic growth with air quality maintenance.

    # These findings underscore the critical need for integrated public health strategies that a
    # ddress the environmental impacts of economic activities, ensuring that economic prosperity
    # does not come at the cost of public health.