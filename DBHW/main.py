
#######################################################################
# # Connect to mysql
# # Output: con obj, cursor obj
#######################################################################
IP = "s.snu.ac.kr"
ID = "ADB2018_26190"
PW = "ADB2018_26190"
DBase = "ADB2018_26190"
import pymysql.cursors
import pandas as pd
import nltk
import math 

con = pymysql.connect(host = IP, 
                            user = ID,
                            password = PW,
                            db = DBase,
                            charset = 'utf8mb4')
# con = pymysql.connect(host = 'localhost', 
#                             user = 'root',
#                             password = 'root',
#                             db = dbname,
#                             charset = 'utf8mb4')
cursor = con.cursor()

print("building tables...")
# # Before executing this file, create wiki, link table in DBase using mysql-workbench  
#######################################################################
# # Make inverted index table 
# # Input: wiki table 
# # Output: InvertedIndex table(term, id, title, freq)
#######################################################################
sql = "select * from wiki"
cursor.execute(sql)
result_wiki = cursor.fetchall()

sql = "select count(*) from information_schema.tables where (table_schema = %s) and (table_name = %s)"
cursor.execute(sql, (DBase, "InvertedIndex"))

if cursor.fetchall()[0][0] == 0: 
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
    
#cursor.execute("drop table InvertedIndex")

print("ready to search...")
#######################################################################
# # PageRank Score Calculation
# # Input: link table 
# # Output: PageRank list R(id, PageRank score)
#######################################################################
# print("calculating pagerank score ...")
import numpy as np
# Get Ni for each
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

#######################################################################
# # TF-IDF Score calculation
# # Input: InvertedIndex table, wiki table, query(string)
# # Output: TF-IDF list TFIDF(id, title, TF-IDF score) 
#######################################################################
def TFIDFscore(Nd, Ndt, Nt):
        return math.log1p(Ndt/Nd)*(1/Nt)
while True:
    
    # Get input from console
    print("2018-26190>",end = '')
    query = input()
    if query == "exit()":
        break
    querys = query.lower().split()
    
    TFIDFs_idx = {}
    TFIDFs_idx_inverse = {}
    TFIDFs = []
    iteration = 0
    for query in querys:
        #######################################################################
        # # TF-IDF Score calculation for each word 
        #######################################################################
        sql = "select sum(freq),id from InvertedIndex where id in (select id from InvertedIndex where term = %s) group by id order by id"
        cursor.execute(sql,query)
        NdInfo = cursor.fetchall()

        sql = "select freq, id, term from InvertedIndex where term = %s order by id"
        cursor.execute(sql,query)
        NdtInfo = cursor.fetchall()

        sql = "select count(*) from InvertedIndex where term = %s"
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
        PrankScore = R[N_idx[Id]][0]
        QAList.append((Id, Uniontitle, UnionTFIDFScore, PrankScore))

    def SortCriteria(item):
        return item[2]*item[3]
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

con.close()
