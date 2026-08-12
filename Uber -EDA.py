import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns


df = pd.read_csv("uber.csv")
print(df.head(),"\n") # frist 5 rows     


#----------------- removing [ un-named & Key ]  colums -----------------
df = df.drop(df.columns[0], axis=1)


# removing the Key colum
df = df.drop('key', axis=1)
print(df.head(),"\n") 
print(df.info(),"\n") 


# info ab   out data

print(df.describe(),"\n") # Statistics
print(df.isnull().sum(),"\n")  # counting the NaN  data
print(df.duplicated().sum()) # counting the duplicated data


# -------------------- deleting the emty row & cleaning data -------
#---------------------- fare_amount & passenger_count ---------------

df.dropna(inplace=True)
print(df.isnull().sum(),"\n")  
print(df.describe(),"\n")

df = df[(df['fare_amount'] > 0) & (df['fare_amount'] <= 150)]
df = df[(df['passenger_count'] > 0) & (df['passenger_count'] <= 6)]
print(df.describe(),"\n")

# -----------------Data Visualization-----------------

# Distribution of Fare Amount
plt.figure(figsize=(10, 5))
sns.histplot(df['fare_amount'], bins=100, kde=True, color='blue')
plt.title('Distribution of Fare Amount')
plt.xlabel('Fare (USD)')
plt.ylabel('Count')
plt.show()


# Passenger Count Distribution
plt.figure(figsize=(6, 4))
sns.countplot(x='passenger_count', data=df, palette='Set2')
plt.title('Passenger Count Distribution')
plt.show()