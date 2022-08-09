#imports
from tabulate import tabulate
import pandas as pd
import pandas.io.common
import numpy as np
import os
import csv
from pandas.io.parsers import ParserError
'''
converts a dataframe to all lowercase
'''
def dfToLowerCase(df):
    df = df.apply(lambda x: x.astype(str).str.lower())
    return df

'''
Removes characters that cause issues when filtering the dataframe
'''
def removeUnwantedCharacter(df,characters):
    for c in characters:
            for column in df:
                if df[column].dtype == object:
                    df[column] = df[column].replace({c:''}, regex=True)
    return df


'''
Searches the first 2 rows of the dataframe to extract the date
takes the latest date found and returns it
'''
def searchForDate(df):
    #print('searching for date')
    foundDate=''
    dates18=['2018','FY18','18/19']
    dates19=['2019','FY19','19/20']
    dates20=['2020','FY20','20/21']
    dates21=['2021','FY21','21/22']
    datesList=[dates18,dates19,dates20,dates21]
    #print('collecting rows')
    try:
        rows=[df.loc[1].values.flatten().tolist(),
        df.loc[0].values.flatten().tolist()]
    except KeyError:#occurs when no second row for some columns
        rows=[df.loc[0].values.flatten().tolist()]
    #print(rows)
    for row in rows:
        #print('Searching for row: ',row)
        for item in row:
            #print('item: ',item)
            for dates in datesList:
                #print('searching for date',dates)
                if any(date in item for date in dates):
                    #print('found date: ',dates[0])
                    foundDate = dates[0]

    for dates in datesList:
        if any(date in df.columns for date in dates):
            foundDate = dates[0]
    return foundDate

'''
passed a dataframe filtered to a single row
converts it to a list
removes the first values since this is the label
iterates through the list from back to front, storing any numbers found
iterates back to front, so values are overwritten by values earlier in the list
returns value closest to label <-- this could be changed to column where latest date was found
'''
def getdatafromrow(df):
    df = df.reset_index(drop=True)
    values = df.loc[0].values.flatten().tolist()
    values.pop(0)
    data = ''
    while data == '':
        for item in reversed(values):#could use reversed(values)
            if item !='nan':
                numbers=[]
                numbers = [int(s) for s in item.split() if s.isdigit()]#extract integers from the string
                if numbers!=[]:
                    data = sorted(numbers, reverse=True)[0] #take the largest number found - to discount errors in the OCR process
                else:#if no integers are found, try and find floats
                    for token in item.split():
                        try:
                            numbers.append(float(token))
                        except ValueError:
                            pass
                    if numbers!=[]:
                        data = sorted(numbers, reverse=True)[0]
        break
    return data


'''
given dataframe, list of phrases to extract
also accepts list if unwanted phrases & whether to sum the values or not  
filters dataframe to rows based on above criteria
gets data for each row
handles it based on above criteria or default
'''

def extractDataByPhrase(df,wantedPhrases,**kwargs):
    unwantedPhrases = kwargs.get('unwantedPhrases', None)
    sumIfMultiple = kwargs.get('sumIfMultiple', True)
    returnData = ''
    '''
    Filters the Dataframe to df_f which only includes rows with the filter phrases defined & without unwanted phrases
    '''
    df_f=[]
    if len(wantedPhrases)==1:
        df_f = df[df[0].str.contains(wantedPhrases[0])]#filters to rows where the label contains the wanted phrase
    else:
        df_f = df[df[0].str.contains(wantedPhrases[0])]#search for first wanted phrase & create new dataframe
        for i in range(1, len(wantedPhrases)):#search for the rest of the phrases & concat the dataframe
            #print('Data faound from phrase '+str(i)+': '+wantedPhrases[i])
            #print(df[0].str.contains(wantedPhrases[i]))
            #print(tabulate(df[df[0].str.contains(wantedPhrases[i])], headers='keys', tablefmt='psql'))
            df_f=pd.concat([df_f,df[df[0].str.contains(wantedPhrases[i])]])
        df_f = df_f.drop_duplicates(keep='first')
        #print('Finished Searching for multiple phrases')
        #print(tabulate(df_f, headers='keys', tablefmt='psql'))
    if unwantedPhrases is not None:
        #print('dropping unwanted phrases')
        df_f = df_f.reset_index(drop=True)#resets the index
        for phrase in unwantedPhrases:
            df_f = df_f[~df_f[0].str.contains(phrase)]#'filters out the unwanted phrases       
    df_f = df_f.reset_index(drop=True)#resets the index
    
    '''
    extracting data from the dfiltered dataframe
    if only 1 line, extracts that
    if multiple rows, extracts them all, and sums depending on argument given
    '''
    if len(df_f)==1:#if there is only 1 line of scope 1 data
        returnData = getdatafromrow(df_f)#extract the value from that row

    elif len(df_f)>1 and sumIfMultiple:#if multiple scope 1 values found

        #if there's a total scope 1 value, take that
        temp_df = df_f[df_f[0].str.contains("total")]
        if not temp_df.empty:
            returnData = getdatafromrow(temp_df)
            temp_df=[]

        #otherwise add all scope 1 values together
        else:
            values=[]#holds each scope 1 value
            for i in range(len(df_f)):#for each row
                #print('getting data for row: '+str(i))
                #print('Scope 1 Value: '+scope1_df.filter(items = [i], axis=0))
                values.append(getdatafromrow(df_f.filter(items = [i], axis=0)))
            values = list(filter(None, values))
            #print(values)
            returnData = sum(values)

    elif len(df_f)>1 and sumIfMultiple==False:
        #print('multiple phrases detected. No Sum argument given. giving first value in values columns.')
        returnData = getdatafromrow(df_f.head(1))
    
    return returnData

'''
Handles parse errors when loading csv into pandas dataframe
'''
def handleParseError(folder,file):
   with open(folder+'\\'+file, 'r') as read_obj:
      csv_reader = csv.reader(read_obj)
      list_of_csv = list(csv_reader)
      columnLen=len(list_of_csv[0])
      
      #print(columnLen)
      outputList=[]
      for row in list_of_csv:
         outputList.append(row[:columnLen])
      #print(outputList)
      df=pd.DataFrame(outputList)
      return df
'''
Drops rows from the dataframe which contains unwanted dataframe
'''
def dropUnwantedRows(df,filterPhrases):
    #print('Dropping Unwanted Rows')
    columnsToDelete=[]
    '''
    Can use to drop columns with phrases like KWH we dont want to accidently collect data for
    '''
   
    for phrase in filterPhrases:
        df[~df[0].str.contains(phrase)]
    
    return df

'''
Drops columns from the dataframe which contains unwanted dataframe
'''
def dropUnwantedColumns(df,columns_to_delete):
    #print('Dropping Unwanted Columns')
    '''
    Import error where NaN values are sometimes imported as strings 'nan'
    Can mostly be ignored, but needs handling if first column are all NaN
    '''
    if all(i == 'nan' for i in df[0].values):
        df=df.drop(df.columns[0], axis=1)
        df.columns=range(df.shape[1])


    df = df.dropna(how='all', axis=1)#remove empty columns
    toDelete=[]
    columns = df.loc[:, df.columns != df.columns[0]].columns
    #print(tabulate(df, headers='keys', tablefmt='psql'))
    for column in columns:
        #print(column)
        if df[column].dtype == object:
            #print(str(df[column].iloc[0]))
            if any(word in str(df[column].iloc[0]) for word in columns_to_delete):
                toDelete.append(column)
            #print(str(df[column].iloc[1]))
            if len(df[column])>1 and any(word in str(df[column].iloc[1]) for word in columns_to_delete):
                if column not in toDelete:
                    toDelete.append(column)
    for column in toDelete:
            df = df.drop(column, 1)
    return df

def csv_to_array(folder,file):
    output=[]
    try:
        if file.endswith(".csv"):
            #print('file: '+file)
            characters=['\'',',']
            columns_to_delete=['energy','kwh']
            rows_to_delete=['kwh','kWh']
            try:
                df = pd.read_csv(folder+'\\'+file,encoding='iso-8859-1',header=None)
            except ParserError:
                df = handleParseError(folder,file)
            #print('Original Dataframe ')
            #print(tabulate(df, headers='keys', tablefmt='psql'))
            if len(df.columns)>1:
                df = df.dropna(how='all')#remove empty rows
                df = df.reset_index(drop=True)
                df = dfToLowerCase(df) #making df lower case
                df = removeUnwantedCharacter(df,characters)#remove unwanted characters from the whole of the dataframe  
                df = dropUnwantedColumns(df,columns_to_delete)#drop columns if their header is unwanted e.g units
                
                
                df = dropUnwantedRows(df,rows_to_delete)
                #print('Altered Dataframe')
                #print(tabulate(df, headers='keys', tablefmt='psql'))
                if len(df.columns)>1:
                    foundDate = searchForDate(df)
                    
                    scope1 = extractDataByPhrase(df,['scope 1',
                                                    'direct combustion',
                                                    'emissions from burning of gas',
                                                    'emissions from burning of fuel',
                                                    'emissions from combustion of gas',
                                                    'emissions from combustion of fuel'],
                                                
                                                unwantedPhrases=['scope 1\+2',
                                                    'scope 1 \+ 2',
                                                    'scope 1 \+2',
                                                    'scope 1\+ 2',
                                                    'kwh'])
                    scope2 = extractDataByPhrase(df,['scope 2',
                                                    'indirect',
                                                    'emissions from electricity',
                                                    'emissions from purchased electricity'],
                                                    
                                                    unwantedPhrases=['scope 1','kwh'])
                 
                    scope3 = extractDataByPhrase(df,['scope 3','travel'],
                                                    unwantedPhrases=['kwh'])
                    intensity = extractDataByPhrase(df,['intensity'])
                    totalemissions= extractDataByPhrase(df,['total gross co2e',
                                                        'total gross emissions',
                                                        'total net emissions',
                                                        'total emissions',
                                                        'total co2e',
                                                        'total gross co?e',
                                                        'total co?e',
                                                        'total gross coze',
                                                        'total coze',
                                                        'all scopes'],
                                                        unwantedPhrases=['kwh'],
                                                        sumIfMultiple=False)

                    #print('Date: '+foundDate)
                    #print('scope 1 value: ',scope1)
                    #print('scope 2 value: ',scope2)
                    #print('scope 3 value: ',scope3)
                    #print('Intensity: ', intensity)
                    #print('total emissions: ',totalemissions)
                    output.append([file[:-4],foundDate,scope1,scope2,scope3,intensity,totalemissions])
                    return output
            else:
                #print('Not enough data found')
                return output
    except pandas.io.common.EmptyDataError:
        #print('Dataframe Empty.')
        return output

#output = csv_to_array(r'C:\Users\Clamfighter\Documents\GitHub\pdf-table-reader\Filtered\Filtered - Copy',r'00457936.csv')

#print(output)