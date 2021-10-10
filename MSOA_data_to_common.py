import pandas as pd
import os

srcFolder = './data/MsoaData'
destFolder = './data/MSOAProcessing/CommonStartForm'


def load(filename):
    return pd.read_csv(os.path.join(srcFolder, filename))


def save(filename,df):
    df[['Z','MSOA code']].to_csv(os.path.join(destFolder, filename))


# This file will always be a bit messy so the idea is to isolate it from the rest of the transformations. The pattern
# bellow should be relatively easy to copy and I dont think there is much to be gained from anything more complicated.

# filename = 'FY2018NetAnnualIncome.csv'
# df = load(filename)
# df['Z'] = pd.to_numeric(df['Net annual income (£)'].str.strip().str.replace(',',''))
# save(filename, df)
#
# filename = 'FY2018NetIncomeAfterHousing.csv'
# df = load(filename)
# df['Z'] = pd.to_numeric(df['Net annual income after housing costs (£)'].str.strip().str.replace(',',''))
# save(filename, df)
#
# filename = 'FY2018NetIncomeBeforeHousing.csv'
# df = load(filename)
# df['Z'] = pd.to_numeric(df['Net annual income before housing costs (£)'].str.strip().str.replace(',',''))
# save(filename, df)

# filename = 'FY2016NetAnnualIncome.csv'
# df = load(filename)
# df['Z'] = pd.to_numeric(df['Net annual income (�)'].str.strip().str.replace(',',''))
# df.drop(df.tail(1).index, inplace=True)
# save(filename, df)
#
# filename = 'FY2016NetIncomeAfterHousing.csv'
# df = load(filename)
# df['Z'] = pd.to_numeric(df['Net annual income after housing costs (�)'].str.strip().str.replace(',',''))
# df.drop(df.tail(1).index, inplace=True)
# save(filename, df)
#
# filename = 'FY2016NetIncomeBeforeHousing.csv'
# df = load(filename)
# df['Z'] = pd.to_numeric(df['Net annual income before housing costs (�)'].str.strip().str.replace(',',''))
# df.drop(df.tail(1).index, inplace=True)
# save(filename, df)
#
#
# filename = 'FY2016TotalIncome.csv'
# df = load(filename)
# df['Z'] = pd.to_numeric(df['Total annual income (�)'].str.strip().str.replace(',',''))
# df.drop(df.tail(1).index, inplace=True)
# save(filename, df)
#
# filename = 'FY2018TotalIncome.csv'
# df = load(filename)
# df['Z'] = pd.to_numeric(df['Total annual income (�)'].str.strip().str.replace(',',''))
# df.drop(df.tail(1).index, inplace=True)
# save(filename, df)

# filename = 'FY2012NetWeeklyIncome.csv'
# out_filename = filename.replace('Weekly','Annual')
# df = load(filename)
# df.drop(df.tail(1).index, inplace=True)
# df['Z'] = df['Net weekly income (�)'] * 52
# save(out_filename, df)

# filename = 'FY2012NetWeeklyIncomeAfterHousing.csv'
# out_filename = filename.replace('Weekly','Annual')
# df = load(filename)
# df.drop(df.tail(1).index, inplace=True)
# df['Z'] = df['Net income after housing costs (�)'] * 52
# save(out_filename, df)
#
# filename = 'FY2012NetWeeklyIncomeBeforeHousing.csv'
# out_filename = filename.replace('Weekly','Annual')
# df = load(filename)
# df.drop(df.tail(1).index, inplace=True)
# df['Z'] = df['Net income before housing costs (�)'] * 52
# save(out_filename, df)
#
# filename = 'FY2012TotalWeeklyIncome.csv'
# out_filename = filename.replace('Weekly','Annual')
# df = load(filename)
# df.drop(df.tail(1).index, inplace=True)
# df['Z'] = df['Total weekly income (�)'] * 52
# save(out_filename, df)


filename = 'FY2014NetWeeklyIncome.csv'
out_filename = filename.replace('Weekly','Annual')
df = load(filename)
df.drop(df.tail(1).index, inplace=True)
df['Z'] = df['Net weekly income (�)'] * 52
save(out_filename, df)

filename = 'FY2014NetWeeklyIncomeAfterHousing.csv'
out_filename = filename.replace('Weekly','Annual')
df = load(filename)
df.drop(df.tail(1).index, inplace=True)
df['Z'] = df['Net income after housing costs (�)'] * 52
save(out_filename, df)

filename = 'FY2014NetWeeklyIncomeBeforeHousing.csv'
out_filename = filename.replace('Weekly','Annual')
df = load(filename)
df.drop(df.tail(1).index, inplace=True)
df['Z'] = df['Net income before housing costs (�)'] * 52
save(out_filename, df)

filename = 'FY2014TotalWeeklyIncome.csv'
out_filename = filename.replace('Weekly','Annual')
df = load(filename)
df.drop(df.tail(1).index, inplace=True)
df['Z'] = df['Total weekly income (�)'] * 52
save(out_filename, df)
