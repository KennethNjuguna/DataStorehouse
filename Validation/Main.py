"""
-------------------------------- UNDER DEVELOPMENT -----------------------------------------
                    
"""

import re
import os
import pandas as pd
import numpy as np
import json

def file_type(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    size = os.path.getsize(file_path)
    with open(report_file, 'a') as file:
             file.write('\t\t\t\t************ VALIDATION REPORT OF UPLOADED FILE ************ \n\n')

    if file_extension == '.csv':
        with open(report_file, 'a') as file:
             file.write('FILE TYPE : CSV \n')
             file.write(f'FILE SIZE : {size/1000} KB\n')
        classify_csv(file_path)
        count_null_blank(file_path)

    elif file_extension == '.json':
        with open(report_file, 'a') as file:
             file.write('FILE TYPE : JSON \n')
             file.write(f'FILE SIZE : {size/1000} KB\n')
        classify_json(file_path)

    elif file_extension == '.txt':
        with open(report_file, 'a') as file:
             file.write('FILE TYPE : TXT \n')
             file.write(f'FILE SIZE : {size/1000} KB\n')
        classify_text(file_path)

    else:
       with open(report_file, 'a') as file:
             file.write('FILE TYPE : UNKNOWN \n')
             file.write(f'FILE SIZE : {size/1000} KB\n')
    
def classify_text(file_path):
    numeric_count = 0
    text_count = 0

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()  
            numeric_pattern = r'^[0-9]+$'
            if re.match(numeric_pattern, line):
                numeric_count += 1
            else:
                text_count += 1

    # if numeric_count > text_count:
    #     return 'Numeric'
    # else:
    #     return 'Text'
    with open(report_file, 'a') as file:
             file.write(f'Ratio for Text Token to Numeric Token is : {text_count} : {numeric_count}\n\n')


def classify_csv(file_path):
    df = pd.read_csv(file_path)

    numeric_columns = 0
    text_columns = 0

    for column in df.columns:
        if pd.to_numeric(df[column], errors='coerce').notnull().all():
            numeric_columns += 1
        else:
            text_columns += 1

    with open(report_file, 'a') as file:
             file.write(f'Ratio for Text column to Numeric column is : {text_columns} : {numeric_columns}\n\n')

def classify_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    numeric_count = 0
    text_count = 0

    def check_type(value):
        if isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit()):
            return 'Numeric'
        else:
            return 'Text'

    def iterate_json(obj):
        nonlocal numeric_count, text_count
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    iterate_json(value)
                else:
                    type_result = check_type(value)
                    if type_result == 'Numeric':
                        numeric_count += 1
                    else:
                        text_count += 1
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    iterate_json(item)
                else:
                    type_result = check_type(item)
                    if type_result == 'Numeric':
                        numeric_count += 1
                    else:
                        text_count += 1

    iterate_json(data)
    with open(report_file, 'a') as file:
             file.write(f'Ratio for Text Object to Numeric Object is : {text_count} : {numeric_count}\n\n')


def count_null_blank(csv_file):
    df = pd.read_csv(csv_file)
    column_stats = []

    for column in df.columns:
        null_count = df[column].isnull().sum()
        blank_count = df[column].map(lambda x: str(x).strip() == '').sum()
        data_type = df[column].dtype
        q1=median=q3=iqr=bias=skewness=skew=0
        if data_type=='int64'or data_type=='float64':
            values = df[column].dropna()
            sorted_values = np.sort(values)
            no_of_values = len(sorted_values)
            q1_index = int(0.25 * (no_of_values + 1))
            q3_index = int(0.75 * (no_of_values + 1))
            if(q1_index!=0 or q3_index!=0):
                q1 = sorted_values[q1_index - 1]
                q3 = sorted_values[q3_index - 1]
                iqr = q3 - q1
                bias = (q3 - q1) / (q3 + q1)
                median = np.median(values)   #q2
                skewness = 3 * (median - np.mean(values)) / np.std(values)
                if((q3-median)<(median-q1)):
                    skew="Negative Skew"
                else:
                    skew="Positive Skew"
        column_stats.append((column, null_count, blank_count, data_type,q1,median,q3,iqr,bias,skewness,skew))
    
    
    with open(report_file, 'a') as file:
        file.write('\t\t\t\t\t\t\t------ COLUMN WISE ANALYSIS ------\n\n')
        for column, null_count, blank_count, data_type,q1,median,q3,iqr,bias,skewness,skew in column_stats:
            file.write(f'Column Name : {column}\n')
            file.write(f'Number of Null Values : {null_count}\n')
            file.write(f'Number of Blank Values : {blank_count}\n')
            file.write(f'Data type of column : {data_type}\n')
            file.write(f'Quartile 1 Value : {q1}\n')
            file.write(f'Quartile 2 Value : {median}\n')
            file.write(f'Quartile 3 Value : {q3}\n')
            file.write(f'InterQuartile Range : {iqr}\n')
            file.write(f'Bias : {bias}\n')
            file.write(f'Skewness Value: {skewness}\n')
            file.write(f'Skew Result : {skew}\n')
            file.write('---\n\n')


file_path = 'BSE_Companies.csv'
report_file = 'Report.txt'
with open(report_file, 'w') as file:
    file.write('')
classification = file_type(file_path)      
with open(report_file, 'a') as file:
             file.write('\n\n\nREMARKS : \n')
             file.write('\t\tThe Quartile, Bias and Skewness are only calculated for Numeric Columns and No Null and No Blank Columns.\n')
             file.write('\nNOTE : *This is an AutoGenerated Analysis Report the Values Maybe Differ by the method of calculation and file neatness \n')
             file.write("\t\t\t\t\t\t\t\t\t@ DATA STOREHOUSE")
print("The Report is updated in 'Report.txt' file...")