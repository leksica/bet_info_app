import csv
from collections import defaultdict
from difflib import SequenceMatcher

def read_csv(filename):
    data = []
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def combine_data(files):
    combined_data = defaultdict(list)
    for file in files:
        data = read_csv(file)
        for row in data:
            key = row['datum'], row['vreme'], row['domacin'],row['gost']
            name_file = file.removesuffix(".csv")
            combined_data[key].append((row, name_file)) 
    return combined_data

def find_maximums1(combined_data):
    max_values = {}
    for key, rows in combined_data.items():
        max_values[key] = {}
        for column in ['ki_1', 'ki_x', 'ki_2']:
            max_value = max(rows, key=lambda x: float(x[0][column]))  
            max_values[key][column] = {'value': max_value[0][column], 'file': max_value[1]} 
    return max_values
def find_maximums2(combined_data):
    max_values = {}
    for key, rows in combined_data.items():
        max_values[key] = {}
        for column in ['ki_1', 'ki_x', 'ki_2','gg','ng','0-2','3+']:
            max_value = max(rows,key=lambda x: float(x[0][column]))
            max_values[key][column] = {'value': max_value[0][column], 'file': max_value[1]}
    return max_values
def find_maximums3(combined_data):
    max_values = {}
    for key, rows in combined_data.items():
        max_values[key] = {}
        for column in ['0-2','3+']:
            max_value = max(rows,key=lambda x: float(x[0][column]))
            max_values[key][column] = {'value': max_value[0][column], 'file': max_value[1]}
    return max_values

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

if __name__ == "__main__":
    files = ['merkur.csv','balkanbet.csv','maxbet.csv','mozzart.csv','soccer.csv', 'pinnbet.csv','meridian.csv','admiralbet.csv','superbet.csv']  # List of CSV files
    combined_data = combine_data(files)

    cnt=0
    for key1,values1 in combined_data.items():
        cnt+=1
        for key2,values2 in combined_data.items():
            if(key1[0]==key2[0] and key1[1]==key2[1]):
                if(similarity(key1[2],key2[2])>0.7 and similarity(key1[3],key2[3])>0.7 and (similarity(key1[2],key2[2])!=1 or similarity(key1[3],key2[3])!=1) ):
                    key1_t = list(key1)
                    key2_t = list(key2)
                    key1_t[2]=key2_t[2]
                    key1_t[3]=key2_t[3]
                    key1 = tuple(key1_t)
                    key2 = tuple(key2_t)
    max_values = find_maximums2(combined_data)
    sFile = open ("demo.txt","w")
    for key, values in max_values.items():
        print(f"{key}",file = sFile)
        for column, info in values.items():
                max_value = info['value']
                file_name = info['file']
                print(f"{column} {file_name} {max_value}",file = sFile)
    for key, values in max_values.items():
        c=0
        if(float(values['gg']['value'])!=0 and float(values['ng']['value'])!=0):
            c=float(1/float(values['gg']['value']))+float(1/float(values['ng']['value']))
        if(1-c>0.01 and c<1 and c!=0):
            print(f"Combination: {key}")
            for column, info in values.items():
                max_value = info['value']
                file_name = info['file']
                print(f"Max {column} ({file_name}): {max_value}")
            print(1-c)

    max_values = find_maximums1(combined_data)
    for key, values in max_values.items():
        c=0
        if(float(values['ki_1']['value'])!=0 and float(values['ki_x']['value']!=0)and float(values['ki_2']['value'])!=0):
            c=float(1/float(values['ki_1']['value'])) + float(1/float(values['ki_x']['value'])) + float(1/float(values['ki_2']['value']))
        if(1-c>0.01 and c<1 and c!=0):
            print(f"Combination: {key}")
            for column, info in values.items():
                max_value = info['value']
                file_name = info['file']
                print(f"Max {column} ({file_name}): {max_value}")
            print(1-c)
    max_values = find_maximums3(combined_data)
    for key, values in max_values.items():
        c=0
        if(float(values['0-2']['value'])!=0 and float(values['3+']['value'])!=0):
            c=float(1/float(values['0-2']['value']))+float(1/float(values['3+']['value']))
        if(1-c>0.01 and c<1 and c!=0):
            print(f"Combination: {key}")
            for column, info in values.items():
                max_value = info['value']
                file_name = info['file']
                print(f"Max {column} ({file_name}): {max_value}")
            print(1-c)
    