# -*- coding: utf-8 -*-
"""
Created on August 5th, 2019
Created by: Chris Nosowsky

This is a script for reading in a CSV File of column names and creating a SQL
select statement out of the columns.

Purpose: generate all the column names without having to manually enter it
"""

#Next Steps: create sql part that selects from database and 

import csv
#import cx_Oracle



def open_it(filename):
    lines = []
    f = open(filename, 'r')
    csv_reader = csv.reader(f, delimiter = '\t')
    for line in csv_reader:
        for l in line:
            lines.append(l)
    f.close()
    return lines

def create_columns_sql(lines):
    ll = []
    cols = []
    conv_names = []
    cols_text = ""
    cols_text_2 = ""
    schema = "a"
    prefix = "dim_"
    final = ""
    final2 = ""
    final3 = ""
    
    for l in lines:
        ll.append(l.split(','))
    for sec in ll:
        cols.append(sec[3])
    #maybe seperate function
    if ll[0][2].find("_D") > 0:
        schema = "ad"
        prefix = "dim_"
    elif ll[0][2].find("_V") > 0:
        schema = "ap"
        prefix = "sem_"        
    
    part1 = "SELECT "
    for col in cols:
        if col == cols[-1]:
            if prefix == "sem_":
                cols_text_2 += "a." + col
            cols_text += schema + "." + col + " AS " + prefix + col.lower()
            conv_name = prefix + col.lower()
            conv_names.append(conv_name)
        else:
            if prefix == "sem_":
                cols_text_2 += "a." + col + ",\n"
            cols_text += schema + "." + col + " AS " + prefix + col.lower() + ",\n"
            conv_name = prefix + col.lower() + ",\n"
            conv_names.append(conv_name)
           
    if prefix == "sem_":
        final2 = part1 + cols_text_2 + "\nFROM dates d" + "\n\n\n"     
    final =  part1 + cols_text + "\nFROM " + ll[0][1] + "." + ll[0][2] + " " + schema
    
    for conv in conv_names:
        final3 += conv
    
    
    return final2 + final + "\n\n" + final3


def nvl_compare(combined, dimensional, semantic):
    ll = []
    ii = 0
    x = 0
    last = 0
    output = ""
    for i in range(len(combined)):
        if combined[i] == '\n':
            ll.append(combined[last:i-1])
            last = i+1
    
    for line in ll:
        if line[:3] == "dim":
            x = dimensional[ii].rfind(',')
            output += "nvl(" + line + ","
            if ("CHAR" or "VARCHAR2" or "VARCHAR") in dimensional[ii][x+1:]:
                output += "'---') <> nvl(sem_vw" + line[3:] + ",'---') or"
            if ("TIMESTAMP(6)" or "TIMESTAMP") in dimensional[ii][x+1:]:
                output += "to_timestamp('11/30/2199', 'mm/dd/yyyy')) <> nvl(sem_vw" + line[3:] + ",to_timestamp('11/30/2199', 'mm/dd/yyyy')) or"
            if ("NUMBER") in dimensional[ii][x+1:]:
                output += "0) <> nvl(sem_vw" + line[3:] + ",0) or" 
            ii+=1
            output += "\n"
    return output[:-4]        

def write(final_string, compare = ""):
    ofile = open('sql_generated.txt', 'w')
    ofile.write(final_string)
    ofile.close()

def main(): #only manual entry is copy and pasting in column names in csv and updating file names. That is it.
    file = "Column_Names_Agency_D.csv" #Your filename of your columns here
    file2 = "Column_Names_Agency_V.csv"
    lines_dim = open_it(file)
    lines_sem = open_it(file2)
    final = create_columns_sql(lines_dim)
    final2 = create_columns_sql(lines_sem)
    
    combined = final + "\n\n\n" + final2
    
    output = nvl_compare(combined, lines_dim, lines_sem)
    
    im_done = combined + "\n\n\n" + output
    
    write(im_done)
    
    


if __name__ == '__main__':
     main()
