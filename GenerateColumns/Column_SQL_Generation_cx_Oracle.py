# -*- coding: utf-8 -*-
"""
Created by: Chris Nosowsky
Date: 08/13/2019

This is a column generation script for views and dimensional.
It's purpose is to allow for instant generation of columns
rather then having to manually type out each one.
"""
import cx_Oracle

def get_connection(user, password, dsn):
    """
    allows for connection to Oracle database based on login information.
    """
    return cx_Oracle.connect(user, password, dsn)

def master_function(views, dims):
    """
    Master function that formats the text file with the necessary columns
    """
    db_conn = get_connection('YOURUSERNAME', 'YOURPASSWORD', 'YOURDSN')
    db_conn_2 = get_connection('YOURUSERNAME', 'YOURPASSWORD', 'YOURDSN')
    c = db_conn.cursor()
    d = db_conn.cursor()
    dmn = db_conn_2.cursor()
    dmnn = db_conn_2.cursor()
    
    for v in range(len(views)):
        final = ""
        semantic_names = []
        dim_names = []
        compare_list = []
        semantic = ""
        final += "\n================================================\n================================================"
        final += "\n========ALL COLUMNS NEXT VIEW: " + views[v] + "========\n\n"
        sem_sql_stmt = "select atc.owner, " + \
                       "atc.table_name, "+ \
                       "atc.column_name, " + \
                       "atc.data_type " + \
                       "from all_tab_cols atc " + \
                       "where atc.owner = 'ODF_SEM_OWNER' " + \
                       "and atc.table_name = '" + views[v] + "'" + \
                       "order by atc.column_name"
                       
                       
        count_stmt =   "select count(atc.column_name) " + \
                       "from all_tab_cols atc " + \
                       "where atc.owner = 'ODF_SEM_OWNER' " + \
                       "and atc.table_name = '" + views[v] + "'"
        
        count_dim_stmt =  "select count(atc.column_name) " + \
                           "from all_tab_cols atc " + \
                           "where atc.owner = 'DM_OWNER' " + \
                           "and atc.table_name = '" + dims[v] + "'"
                       
        dim_sql_stmt = "select atc.owner, " + \
                       "atc.table_name, "+ \
                       "atc.column_name, " + \
                       "atc.data_type " + \
                       "from all_tab_cols atc " + \
                       "where atc.owner = 'DM_OWNER' " + \
                       "and atc.table_name = '" + dims[v] + "'" + \
                       "order by atc.column_name"
                       
        c.execute(sem_sql_stmt)
        d.execute(count_stmt) 
        ###SEMANTIC###
        result = 0
        for row in d:
            result = row[0]
        x = 1
        for row in c:
            if x == 1:
                final += "SELECT\n"
                semantic += "SELECT\n"
            if x == result:
                final += "a." + row[2]
                semantic += "a." + row[2]
            else:
                final += "a." + row[2] + ",\n"
                semantic += "a." + row[2] + ",\n"
            x+=1  
        ##COMPARISON DIM TO SEM##
        final += "\n\n\n========" + dims[v] + " COMPARISON DIM TO SEM========\n\n"
             
        #DIMENSIONAL#
        dmn.execute(dim_sql_stmt)
        dmnn.execute(count_dim_stmt)
        x = 1
        result = 0
        for row in dmnn:
            result = row[0]
        
        for row in dmn:
            dim_names.append(("dim_" + row[2].lower(), row[3]))
            if x == 1:
                final += "SELECT\n"
            if x == result:
                final += "ad." + row[2] + " AS dim_" + row[2].lower()
            else:
                final += "ad." + row[2] + " AS dim_" + row[2].lower() + ",\n"            
            x+=1
        
        #SEMANTIC COMPARE#
        final += "\n\n========SEMANTIC COMPARE========\n\n"
        lines = semantic.split('\n')
        for line in lines:
            if line.find('a.') != -1:
                semantic_names.append("sem_vw_" + line[2:].lower())
                final += "ap." + line[2:-1] + " AS sem_vw_" + line[2:].lower() + "\n"
        
        final += "\n\n========CONVENTIONS FOR: " + dims[v] + " AND " + views[v] + "========\n\n"
        len_sem = len(semantic_names)
        len_dim = len(dim_names)
        for t in range(len_dim):
            final += dim_names[t][0] + ",\n"
        for s in range(len_sem):
            final += semantic_names[s] + "\n"
                      
        ##NOW COMPARING IT ALL TOGETHER## 
        c2 = db_conn.cursor()
        d2 = db_conn.cursor()
        dmn2 = db_conn_2.cursor()
        dmnn2 = db_conn_2.cursor()
        c2.execute(sem_sql_stmt)
        d2.execute(count_stmt)
        dmn2.execute(dim_sql_stmt)
        dmnn2.execute(count_dim_stmt)
        
        all_so_far = []         
        for i in range(len(semantic_names)):
            for t in range(len(dim_names)):
                if dim_names[t][0].find(semantic_names[i][7:10]) != -1:
                        if dim_names[t][0] not in all_so_far and semantic_names[i] not in all_so_far:
                            compare_list.append((dim_names[t][0], semantic_names[i], dim_names[t][1]))
                            all_so_far.append(dim_names[t][0])
                            all_so_far.append(semantic_names[i])
                        break
        final += "\n\n\n========NVL COMPARE========\n\n\n"
          
        for field in compare_list:
            if ("CHAR" or "VARCHAR2" or "VARCHAR") in field[2]:
                final += "nvl(" + field[0] + ",'---') <> nvl(" + field[1] + "'---') or \n"
            if ("TIMESTAMP(6)" or "TIMESTAMP") in field[2]:
                final += "nvl(" + field[0] + ",to_timestamp('11/30/2199', 'mm/dd/yyyy')) <> nvl(" + field[1] + "'---') or \n" 
            if ("NUMBER") in field[2]:
                final += "nvl(" + field[0] + ",0) <> nvl(" + field[1] + "0) or \n" 
        write(final, views[v])
        
    db_conn.close()
    db_conn_2.close()
       
def write(final_string, view_name = "test"):
    """
    Write function that writes a text file based on the generated columns
    """
    file_name = view_name + "_columns.txt"
    ofile = open(file_name, 'w')
    ofile.write(final_string)
    ofile.close()


def main():
    views = ["AGENCY_V", "ADDRESS_V", "ADDRESS_RELATIONSHIP_V", "AGENCY_PRODUCER_RELATIONSHIP_V",
             "CORE_SERVICE_CENTER_V", "EMPLOYEE_V", "PRODUCER_V"]
    
    dims = ["AGENCY_D", "ADDRESS_D", "ADDRESS_REL_B", "AGENCY_PRODUCER_REL_B",
             "CORE_SERVICE_CENTER_D", "EMPLOYEE_D", "PRODUCER_D"]
  
    master_function(views, dims)       

if __name__ == '__main__':
     main()
