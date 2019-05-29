import pymysql.cursors
import pandas as pd
import numpy as np
import nltk
import math 
import os
import re
# =========================================================================
# functions 
# =========================================================================
def execute_file_sql(con, file_name):
    sql_file = open(file_name, 'r').readlines()
    query = ""
    i = 0
    for sql_line in sql_file:
        i += 1
        sql_line = sql_line.strip()
        query += sql_line
        if len(query) > 0:
            if query[len(query) - 1] == ';':
                query = query[:len(query) - 1]
                #print('[DEBUG ] ', query)
                with con.cursor() as cursor:
                    cursor.execute(query)
                query = ""

def execute_sql(con, SQL):
    with con.cursor() as cursor:
        cursor.execute(SQL)
#         result = cursor.fetchall()
#         print(result)
        con.commit()

def read_file(Path):
    with open(Path, 'r') as f:
        while True:
            line = f.readline()
            if not line: break
#             print(line)

def parse_schedules(Path):
    queries = []
    schedules = []
    with open(Path, 'r') as f:
        while True:
            line = f.readline()
            if not line: break
    #         print(line)
            queries.append(line)
            if(line[0] == "<"):
        #         print(query.split("> ")[1])
                schedules.append(line.split("> ")[1])
            else:
        #         print(query)
                schedules.append(line)
    return schedules, queries 

def write_search_log(num_of_search, search_query, search_result):
    search_path = dirpath + "/search.txt"
    with open(search_path,'a') as f:
        f.write("search {0}\n".format(num_of_search))
        f.write("query {0}".format(search_query))
        f.write(search_result+"\n")

#design write search log function  <T*> operation
def write_transaction_log(con, tran, dirpath, SQL, active_transactions, log_line_number):
    # parse SQL
    executable_line = re.split("> ", SQL.split("<")[1])[1]   
    log = ""
    if "commit" in SQL:
        log = "<{0}> commit\n".format(re.split("> ",SQL.split("<")[1])[0])
        active_transactions.remove(tran)
        
    elif "rollback" in SQL:
        log = "<{0}> abort\n".format(re.split(">",SQL.split("<")[1])[0])
        active_transactions.remove(tran)
        execute_tran_rollback(con, tran, dirpath)
        
    elif "DELETE" in SQL:
        [tran, command, table, key_value] = re.split("> |FROM | WHERE ",SQL.split("<")[1]) 
        [key, key_v, _] = re.split(" = |;",key_value)
        key_value = "{0} = {1}".format(key, key_v)
        with con.cursor() as cursor:
            # write log
            cursor.execute("select COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME= '{0}'".format(table))
            cols = cursor.fetchall()
            cursor.execute("select * from {0} where {1} = {2}".format(table, key, key_v))
            old_values = cursor.fetchall()
            log_old_values = ""
            for info in old_values:
#                 log_old_values += ""
                for i, col in enumerate(cols):
                    log_old_values  += "{0} = {1}#".format(col[0], info[i])
                log_old_values += "//"
                
            # log 에 먼저 쓰고 delete operation
            cursor.execute(executable_line)
        log = "<{0}> <{1}> <{2}> <{3}>\n".format(tran,table,key_value, log_old_values)
    elif "UPDATE" in SQL:
        [tran, command_table, col_value, key_value] = re.split("> |SET | WHERE ",SQL.split("<")[1])
        [command, table, _] = command_table.split(" ")
        [col, new_v] = re.split(" = ",col_value)
        [key, key_v, _] = re.split(" = |;",key_value)
        new_value = "{0} = {1}".format(col, new_v)
        key_value = "{0} = {1}".format(key, key_v)
        old_value = ""
        with con.cursor() as cursor:
            # write log
            cursor.execute("select {0} from {1} where {2} = {3}".format(col, table, key, key_v))
            result = cursor.fetchall()
            old_v = ""
            if(len(result) != 0):
                old_v = result[0][0]
            old_value = "{0} = {1}".format(col, old_v)
            
            # log 에 먼저 쓰고 update operation
            cursor.execute(executable_line)
        log = "<{0}> <{1}> <{2}> <{3}> <{4}>\n".format(tran,table,key_value, old_value, new_value)


    log_path = dirpath + "/prj2.log"
    with open(log_path,'a') as f:
        f.write(log)
#         print(log_line_number,": ", log)

def write_checkpoint(dirpath, active_transactions):
    log_path = dirpath + "/prj2.log"    
    log = "checkpoint "
    i = 0
    for tran in sorted(active_transactions):
        if( i != len(active_transactions) - 1):
            log +=  "<{0}>, ".format(tran)
        else:
            log +=  "<"+tran+">\n"
        i += 1
    if(len(active_transactions) == 0):
        log += "\n"
    
    with open(log_path,'a') as f:
        f.write(log)    
#     print(log)

def log_based_recovery(dirpath, line_number, active_transactions, line_last_checkpoint, line_last_log_checkpoint, last_log_checkpoint_active_transactions):
#     print("=============================================  log based recovery start ===================================================")
    recovery_log_path = dirpath + "/recovery.txt"
    schedule_path = dirpath + "/prj2.sched"
    trans_log_path = dirpath + "/prj2.log"
    header = "recover {0}\n".format(line_number)
#     print("recovery.txt ... ")
#     print(header)
#     print("last check point line: ",line_last_checkpoint)
#     print("last_log_checkpoint line: ",  line_last_log_checkpoint)
#     print("active_trans: ", active_transactions)
#     print("last_log_checkpoint_active_transactions: ", last_log_checkpoint_active_transactions)
        
    Undo = last_log_checkpoint_active_transactions.copy()
    Redo = set()
    
    with open(recovery_log_path,'a') as f:
        f.write(header)
    
#     print("Undo: ",Undo)
#     print("Redo: ",Redo)
    
    count = 1
    with open(schedule_path,'r') as f:
        while True:
            line = f.readline()
            if count in range(line_last_checkpoint + 1, line_number):
                if line[0] == "<":
                    tran = re.split(">",line.split("<")[1])[0]
                    if tran not in Undo:
                        Undo.add(tran)
                    elif "commit" in line:
                        Undo.remove(tran)
                        Redo.add(tran)
                    elif "rollback" in line:
                        Undo.remove(tran)
            if count == line_number:
                break
            count += 1
            
#     print("updated Undo: ",Undo)
#     print("updated Redo: ",Redo)
#     print("============== redo start ======================")
    for e in Redo:
        redo_execute(con, e, dirpath, line_last_log_checkpoint)
#     print("============== redo end ======================")
    
#     print("============== undo start ======================")
    for e in Undo:
        execute_tran_rollback(con, e, dirpath)
#     print("============== undo end ======================")
    
    redo_log = "redo "
    undo_log = "undo "
    i = 0
    for tran in sorted(Redo):
        if( i != len(Redo) - 1):
            redo_log +=  "<{0}>, ".format(tran)
        else:
            redo_log +=  "<"+tran+">\n"
        i += 1
    if(len(Redo) == 0):
        redo_log += "\n"
        
    j = 0
    for tran in sorted(Undo):
        if( j != len(Undo) - 1):
            undo_log +=  "<{0}>, ".format(tran)
        else:
            undo_log +=  "<"+tran+">\n"
        j += 1
    if(len(Undo) == 0):
        undo_log += "\n"
        
    with open(recovery_log_path,'a') as f:
        f.write(redo_log)
        f.write(undo_log)
        
#     print("Undo log: ", undo_log)
#     print("Redo log: ", redo_log)

#     print("=============================================  log based recovery end ===================================================")
    
def redo_execute(con, tran, dirpath, line_last_log_checkpoint):
    log_path = dirpath + "/prj2.log"
    with con.cursor() as curosr:       
#         print("=======================", tran ," redo start ==========================")
#         print("line_last_log_checkpoint: ", line_last_log_checkpoint)
        count = 1
        with open(log_path,'r') as f:
            while True:
                line = f.readline()
                if count > line_last_log_checkpoint:
#                     print("log line ", count," : ", end = "") 
#                     print(line)
                    if line[0] == "<":
                        tran_line = re.split(">",line.split("<")[1])[0]
                        if tran_line == tran:

                            parse_list = re.split("<|> <|>",line)
                            if len(parse_list) == 6: # DELETE
                                [_, tran, table, key_value, deleted_list, _] = parse_list
                                [key, key_v] = re.split(" = ", key_value)
                                sql = "DELETE FROM {0} WHERE {1} = {2}".format(table, key, key_v)
#                                 print(sql)
                                execute_sql(con, sql)
                            elif len(parse_list) == 7: # UPDATE
                                [_, tran, table, key_value, old_value, new_value,_] = parse_list
                                [key, key_v] = re.split(" = ", key_value)
                                [col, new_v] = re.split(" = ", new_value)
                                sql = "UPDATE {0} SET {1} = {2} WHERE {3} = {4}".format(table, col, new_v, key, key_v)
#                                 print(sql)
                                execute_sql(con,sql) 
                            if "commit" in line:
                                break

                count += 1
                
        con.commit()
#         print("=======================", tran ," redo end ==========================")
    
def execute_tran_rollback(con, tran, dirpath):
    log_path = dirpath + "/prj2.log"
    with con.cursor() as curosr:       
#         print("=======================", tran ," rollback start ==========================")
        for line in reversed(open("prj2.log").readlines()):
            log_line = line.rstrip()
#             print(log_line)
            if log_line[0] == "<":
                tran_line = re.split(">",log_line.split("<")[1])[0]
                if tran_line == tran:
                    parse_list = re.split("<|> <|>",log_line)
                    if len(parse_list) == 6: # DELETE
                        [_, tran, table, key_value, deleted_list, _] = parse_list
                        [key, key_v] = re.split(" = ", key_value)
                        old_records = re.split("//", deleted_list)
                        for i in range(len(old_records) - 1): # insert 해야할 recored 수 
                            insert_values = re.split("#", old_records[i])
                            cols = []
                            vals = []
                            for i, value in enumerate(insert_values):
                                if (i < len(insert_values) - 1):
                                    [c, v] = re.split(" = ", value)
                                    cols.append(c)
                                    vals.append(v)
                            cols = tuple(cols)
                            vals = tuple(vals)
    #                         print(cols, vals)
                            sql = "insert into {0} values {1}".format(table, vals)
#                             print(sql)
                            with con.cursor() as cursor:
                                cursor.execute(sql)

                    elif len(parse_list) == 7: # UPDATE
                        [_, tran, table, key_value, old_value, new_value,_] = parse_list
                        [key, key_v] = re.split(" = ", key_value)
                        [col, new_v] = re.split(" = ", new_value)
                        [col, old_v] = re.split(" = ", old_value)
                        old_v = "{}".format(old_v)
                        sql = "UPDATE {0} SET {1} = %s WHERE {2} = {3}".format(table, col, key, key_v)
#                         print(sql % old_v)
                        with con.cursor() as cursor:
                            cursor.execute(sql, old_v)
                    if "start" in log_line:
                        break
        con.commit()
#         print("=======================", tran ," rollback end ==========================")
        
def TFIDFscore(Nd, Ndt, Nt):
        return math.log1p(Ndt/Nd)*(1/Nt)
    
def SortCriteria(item):
        return item[2]*item[3]
       
def print_search_query(con, querys, R, N_idx):
    TFIDFs_idx = {}
    TFIDFs_idx_inverse = {}
    TFIDFs = []
    iteration = 0
    for query in querys:
        #######################################################################
        # # TF-IDF Score calculation for each word 
        #######################################################################
        sql = "select sum(freq),id from InvertedIndex where id in (select id from InvertedIndex where term = %s) group by id order by id"
        NdInfo = None
        with con.cursor() as cursor:
            cursor.execute(sql,query)
            NdInfo = cursor.fetchall()

        sql = "select freq, id, term from InvertedIndex where term = %s order by id"
        NdtInfo = None
        with con.cursor() as cursor:
            cursor.execute(sql,query)
            NdtInfo = cursor.fetchall()

        sql = "select count(*) from InvertedIndex where term = %s"
        Nt = None
        with con.cursor() as cursor:   
            cursor.execute(sql,query)
            Nt = cursor.fetchall()[0][0]

        TFIDF = []
        for i in range(len(NdtInfo)):
            if NdInfo[i][1] == NdtInfo[i][1]:
                Nd = NdInfo[i][0]
                Ndt = NdtInfo[i][0]
                id = NdInfo[i][1]
        #         print(id," ",math.log1p(Ndt/Nd)*(1/Nt))
        #         TFIDF.append((id, math.log1p(Ndt/Nd)*(1/Nt)))
                TFIDF.append((id, TFIDFscore(Nd, Ndt, Nt)))
        TFIDFs.append(TFIDF)
        TFIDFs_idx[query] = iteration
        TFIDFs_idx_inverse[iteration] = query
        iteration = iteration + 1

    # Get title dictionary     
    sql = "select id,title from wiki order by id"
    id_title = None
    with con.cursor() as cursor:
        cursor.execute(sql)
        id_title = cursor.fetchall()
    id_title_dictionary = {}
    for _, idtitle in enumerate(id_title):
        v_id = idtitle[0]
        v_title = idtitle[1]
        id_title_dictionary[v_id] = v_title

    # Union TFIDFs
    TFIDFsetlist = []      
    for query in querys:
        temp = np.array(TFIDFs[TFIDFs_idx[query]])
        if len(temp) == 0:
            idsForOneQuery = temp.astype(int)
        else:
            idsForOneQuery = temp[...,0].astype(int)
        TFIDFsetlist.append(set(idsForOneQuery))

    UnionId = []
    UnionId_idx = {}
    UnionId_idx_inverse = {}
    for TFIDFset in TFIDFsetlist:
        UnionId = list(set(UnionId)|set(TFIDFset))

    UnionId.sort()
    iteration = 0;
    for idvalue in UnionId:
        UnionId_idx[idvalue] = iteration
        UnionId_idx_inverse[iteration] = idvalue
        iteration = iteration + 1

    # Get TFIDF Score Matrix SM
    SM = np.zeros((len(querys), len(UnionId)))
    for row in range(len(querys)):
        LenOfcols = len(TFIDFs[row])
    #     print(LenOfcols)
        for j in range(LenOfcols): # j means each query's index of id
    #         print(TFIDFs[row][j][0], TFIDFs[0][j][1], TFIDFs[0][j][2])  # 
            col = UnionId_idx[TFIDFs[row][j][0]]
    #         title = TFIDFs[row][j][1]
            score = TFIDFs[row][j][1]
            SM[row][col] = score
    # SM
    #######################################################################
    # # Get Top K list
    # # Input: TFIDF Score Matrix SM, PageRank list R
    # # Output: QAList(sorted order by TFIDF score * PageRank score)
    #######################################################################
    QAList = []
    for it in UnionId_idx:
        Id = it
        UnionTFIDFScore = SM[...,UnionId_idx[it]].sum()
        Uniontitle = id_title_dictionary[it] 
        if Id in N_idx:
            PrankScore = R[N_idx[Id]][0]
        else:
            print("the link does not exist")
            PrankScore = 0
        QAList.append((Id, Uniontitle, UnionTFIDFScore, PrankScore))

    QAList.sort(key= SortCriteria, reverse= True)

    strFormat = '%-10s%-60s%-20s%-20s\n'
    strOut = strFormat % ('id', 'title', 'TF-IDF', 'PageRank')
    iteration = 0;
    for ans in QAList:
        if iteration < 10:
#             print(ans[0], ans[1], format(ans[2],"10.2e"), format(ans[3],"10.2e"))
            strOut += strFormat %(ans[0], ans[1], format(ans[2],"10.2e"), format(ans[3],"10.2e"))
        else:
            break
        iteration = iteration + 1
    print(strOut)
    
    return strOut

def create_invertedindex(con):
    with con.cursor() as cursor:
        cursor.execute("drop table if exists InvertedIndex")
        sql = "select * from wiki"
        cursor.execute(sql)
        result_wiki = cursor.fetchall()
         # Create inverted index table 
        sql = "create table InvertedIndex (term varchar(255) not null, id int(11) not null, freq int(11) not null)"
        cursor.execute(sql)
        # # Clean inverted index table
        # sql = "delete from InvertedIndex" 
        # cursor.execute(sql)

        # insertion from wiki table 
        sql = "insert into InvertedIndex (term,id,freq) values (%s,%s,%s)"
        for Doc in result_wiki:
        #     print(type(Doc)) #tuple (id, doc_name, doc_script)
            tokens = nltk.word_tokenize(Doc[2].lower())
            fdist = nltk.FreqDist(tokens) # dictionary {term:freq, ... }
            for term, freq in fdist.items():
                cursor.execute(sql,(term, Doc[0], freq))
        #     print(fdist)
        con.commit()

def get_pagerank_score(con):
    R = None
    N_idx = None
    with con.cursor() as cursor:
        sql = "select id_from, count(*) as outgoing from link group by id_from order by id_from"
        cursor.execute(sql)
        FromNiInfo = cursor.fetchall()

        Ni_dict = {}
        for idx, FromNi in enumerate(FromNiInfo):
        #     print(FromNi[0], FromNi[1])
            id_from = FromNi[0]
            Ni = FromNi[1]
            Ni_dict[id_from] = Ni

        # Get N and id_all(sorted order) 
        sql = "select distinct id_from from link order by id_from"
        cursor.execute(sql)
        SetOfFromInfo = cursor.fetchall()

        sql = "select distinct id_to from link order by id_to"
        cursor.execute(sql)
        SetOfToInfo = cursor.fetchall()

        SetOfFrom = set()
        SetOfTo = set()

        for idx, From in enumerate(SetOfFromInfo):
        #     print(type(From[0]))
            SetOfFrom.add(From[0])

        for idx, To in enumerate(SetOfToInfo):
        #     print(type(From[0]))
            SetOfTo.add(To[0])

        id_all = sorted(SetOfFrom.union(SetOfTo))
        N = len(id_all)

        # Get N_idx and N_idx_inverse; it means dictionary[Doc.id] = index of Transition Matrix or State Matrix    
        N_idx = {}
        N_idx_inverse = {}
        for idInfo, idx in enumerate(id_all):
        #     print(idx, idInfo)
            N_idx[idx] = idInfo
            N_idx_inverse[idInfo] = idx

        # Get SateMatrix S; check whether existing from j to i link  
        S = np.zeros((N,N)) # from j to i info : S[i][j]
        sql = "select * from link order by id_from"
        cursor.execute(sql)
        FromToInfo = np.array(cursor.fetchall())
        for fromto in FromToInfo:
            id_to = fromto[1]
            id_from = fromto[0]
            S[N_idx[id_to]][N_idx[id_from]] = 1

        # Get Transition Matrix M and Score Vector R 
        M = np.zeros((N,N)) # from j to i info : M[i][j]
        for _, id_from in enumerate(sorted(SetOfFrom)):
            for _, id_to in enumerate(id_all):
                # if link id_from to id_to exists
                if S[N_idx[id_to]][N_idx[id_from]] != 0:
                    M[N_idx[id_to]][N_idx[id_from]] = 1/Ni_dict[id_from]

        # PageRank Algorithm
        # Input: Station Matrix S, Transition Matrix T, RankVector R 
        # Output: updated RankVector R 
        delta = 0.15
        elipslion = 1e-8
        # R = np.ones((N,1))*(1/N)
        R = np.ones((N,1))
        K = np.ones((N,1))*(delta/N)
        # R = delta * np.matmul(M,prevR) + K
        iteration = 0
        distance = 100
        while distance > elipslion:
        #     print("iteration", iteration, "...")
            prevR = R
            R = delta * np.matmul(M,R) + K
            iteration = iteration + 1
            distance = np.linalg.norm(R-prevR)
        #     print("distance = ",np.linalg.norm(R-prevR))
    return R,N_idx 

# =========================================================================
# preprocessing
# =========================================================================
#######################################################################
# # Connect to mysql
# # Output: con obj, cursor obj
#######################################################################
# IP = "s.snu.ac.kr"
# ID = "ADB2018_26190"
# PW = "ADB2018_26190"
# DBASE = "ADB2018_26190"
# WIKI = "wiki"
# LINK = "link"
# con = pymysql.connect(host = IP, 
#                             user = ID,
#                             password = PW,
#                             db = DBASE,
#                             charset = 'utf8mb4')

PW = "1360"
DBASE = "test"
WIKI = "wiki"
LINK = "link"
con = pymysql.connect(host = 'localhost', 
                            user = 'root',
                            password = PW,
                            db = DBASE,
                            charset = 'utf8mb4')

cursor = con.cursor()
dirpath = os.getcwd()

print("building tables...")
# 올바른 wiki, link, invertedindex가 있어야 TFIDF와 pagerank를 올바르게 계산될 수 있다.
# 초기화 시켜주는 라인들 
execute_file_sql(con, dirpath + "/link.sql")
execute_file_sql(con, dirpath + "/wiki.sql")
create_invertedindex(con)

# # Before executing this file, create wiki, link table in DBase using mysql-workbench  
#######################################################################
# # Make inverted index table 
# # Input: wiki table 
# # Output: InvertedIndex table(term, id, title, freq)
#######################################################################
sql = "select count(*) from information_schema.tables where (table_schema = %s) and (table_name = %s)"
cursor.execute(sql, (DBASE, "InvertedIndex"))

# if inverted index table does not exist, create inverted index table 
if cursor.fetchall()[0][0] == 0: 
    # Create inverted index table 
    create_invertedindex(con)

print("ready to search...")
#######################################################################
# # PageRank Score Calculation
# # Input: link table 
# # Output: PageRank list R(id, PageRank score)
#######################################################################
# print("calculating pagerank score ...")
# Get Ni for each
[R, N_idx] = get_pagerank_score(con)

# =========================================================================
# Interface 
# =========================================================================
#######################################################################
# # TF-IDF Score calculation
# # Input: InvertedIndex table, wiki table, query(string)
# # Output: TF-IDF list TFIDF(id, title, TF-IDF score) 
#######################################################################
while True:
    # Get input from console
    print("2018-26190>",end = '')
    query = input()
    if query == "exit()":
        break
    elif query == "init()":
        execute_file_sql(con, dirpath + "/link.sql")
        execute_file_sql(con, dirpath + "/wiki.sql")
        create_invertedindex(con)
        [R, N_idx] = get_pagerank_score(con)
        continue
    elif query[0] == "-": # -run *.sched # -run prj2.sched
        schedules_path = dirpath + "/"+query.split("-run ")[1]
        if os.path.isfile(schedules_path):
            [schedules, queries] = parse_schedules(schedules_path)
            # initialize search.txt
            num_of_search = 0
            open(dirpath+'/search.txt', 'w').close()
            open(dirpath+'/prj2.log', 'w').close()
            open(dirpath+'/recovery.txt', 'w').close()
            active_transactions = set()
            last_log_checkpoint_active_transactions = set()
            line_number = 1
            line_last_checkpoint = 1
            line_last_log_checkpoint = 1
            log_line_number = 1
            # execute schedules =================== 6 functions should be implemented 
            for schedule in queries:
                print("execute  schedule ", line_number, " ... :" , schedule) ###############
                
                if schedule[:6] == "search":
                    search_query = schedule.split("search ")[1]
#                     print(search_query)
                    search_result = print_search_query(con, search_query.lower().split(), R, N_idx)
                    write_search_log(num_of_search, search_query, search_result)
                    num_of_search += 1   
                elif schedule[0] == "<":
                    tran = re.split(">",schedule.split("<")[1])[0]
                    # active_transaction update
                    if tran not in active_transactions:
                        active_transactions.add(tran)
#                         print(log_line_number, " : ", "<{0}> start\n".format(tran))
                        with open(dirpath+"/prj2.log",'a') as f:
                            f.write("<{0}> start\n".format(tran))
                            ## ++++++++++++++++++++++++ log_line_number ++++++++++++++++++++++++ ##
                            log_line_number += 1
                    # write log <Transaction ID> [SQL]  # delete, update, commit, rollback를 처리 
                    write_transaction_log(con, tran, dirpath, schedule, active_transactions, log_line_number)
                    ##  ++++++++++++++++++++++++ log_line_number ++++++++++++++++++++++++ ##
                    log_line_number += 1    

                # write checkpoint log  
                elif schedule[:10] == "checkpoint":
                    write_checkpoint(dirpath, sorted(active_transactions))
                    line_last_log_checkpoint = log_line_number
                    line_last_checkpoint = line_number
                    ##  ++++++++++++++++++++++++ log_line_number ++++++++++++++++++++++++ ##
                    log_line_number += 1 
                    last_log_checkpoint_active_transactions = active_transactions.copy()
                    
                # system failure -recover
                elif schedule[:6] == "system":
                    log_based_recovery(dirpath, line_number, active_transactions, line_last_checkpoint, line_last_log_checkpoint, last_log_checkpoint_active_transactions)
                    active_transactions = set()
                    write_checkpoint(dirpath, active_transactions)
                    line_last_log_checkpoint = log_line_number
                    line_last_checkpoint = line_number
                    ##  ++++++++++++++++++++++++ log_line_number ++++++++++++++++++++++++ ##
                    log_line_number += 1  
                    
#                     print("pagerank and invertedindex updated")
                    create_invertedindex(con)
                    [R, N_idx] = get_pagerank_score(con)
                    
                line_number += 1 ##################
        else:
            print("such file is not exist")
    else:
        querys = query.lower().split()
        print_search_query(con, querys, R, N_idx)
    
con.close()
