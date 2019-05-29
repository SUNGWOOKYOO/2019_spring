import pymysql
import math
import operator
from nltk.tokenize import word_tokenize

conn = pymysql.connect(host = 's.snu.ac.kr',
                        port = 3306,
                        user = '',
                        password='',
                        db = '')

def execute_sql(file_name):
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
                cursor.execute(query)
                query = ""

cursor = conn.cursor()

#============================================================
#                 Creating LINK, SQL Table
#============================================================
execute_sql("link.sql")
execute_sql("wiki.sql")
#============================================================


#============================================================
#              Creating Inverted Index Table
#============================================================
query = '''
        SELECT * FROM wiki
        '''
cursor.execute(query)
results = cursor.fetchall()

query = '''
        DROP TABLE IF EXISTS `InvIdx`
        '''
cursor.execute(query)
        
query = '''
        CREATE TABLE `InvIdx` (
        `term` varchar(1000) NOT NULL,
        `id` int(11) NOT NULL
        ) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
        '''
cursor.execute(query)

#================Inserting Inverted Index====================
query = "LOCK TABLES InvIdx WRITE"
cursor.execute(query)
InvIdxTable = {}
query = "INSERT INTO InvIdx(term, id) VALUES (%s, %s)"
query_tuples = []
n_d = {}
n_d_t = {}
id_title = {}

for result in results:
    id_title.update({result[0]: result[1]})
    id = result[0]
    terms = word_tokenize(result[1]) + word_tokenize(result[2])            
    total_terms = 0
    n_d_elem = {}

    for term in terms:
        if True:
            #if not term in stop_words:
            #if ((len(term)>1) or (term >= 'a' and term <= 'z') or (term >= 'A' and term <= 'Z')):
            total_terms += 1
            if not term in n_d_elem:
                n_d_elem.update({term : 1})
            else:
                num = n_d_elem[term]
                num += 1
                n_d_elem.update({term : num})

            if not term in InvIdxTable:
                InvIdxTable.update({term: [id]})
                query_tuples.append([term, id])
            else:
                InvElem = InvIdxTable[term]
                if not id in InvElem:
                    InvElem.append(id)
                    InvIdxTable.update({term:InvElem})
                    query_tuples.append([term, id])

    n_d_t.update({id : n_d_elem})
    n_d.update({id : total_terms})

cursor.executemany(query, query_tuples)
query = "UNLOCK TABLES"
cursor.execute(query)
        
#============================================================
#                      TFIDF Calculating
#============================================================

TFIDF = {}
for title in n_d_t:
    TFIDF_ELEM = {}
    elem = n_d_t[title]
    for term in elem:
        tf_idf_value = math.log(1 + n_d_t[title][term]/n_d[title]) / len(InvIdxTable[term])
        TFIDF_ELEM.update({term : tf_idf_value})
    TFIDF.update({title : TFIDF_ELEM})
#============================================================

       
query = '''
        SELECT * FROM link
        '''
cursor.execute(query)
results = cursor.fetchall()
        
#Data structure [Dictionary]
#PageRank['id'] = Page Rank Value
#PageLink['id'] = [] List of linked page to id
PageRank = {}
PageLink = {}
PageLink_inv = {}
        
      

for result in results:
    if result[0] in PageLink:
        elem = PageLink[result[0]]
        elem.append(result[1])
        PageLink.update({result[0] : elem})
    else:
        elem = [result[1]]
        PageLink.update({result[0] : elem})


    if not result[0] in PageRank:
        PageRank.update({result[0] : 0})

    if not result[1] in PageRank:
        PageRank.update({result[1] : 0})


    if result[1] in PageLink_inv:
        elem = PageLink_inv[result[1]]
        elem.append(result[0])
        PageLink_inv.update({result[1] : elem})
    else:
        elem = [result[0]]
        PageLink_inv.update({result[1] : elem})
        


#============================================================
#                      PageRank Calculating
#============================================================

epsilon = 10.0
total_page = len(PageRank)
for page in PageRank:
    PageRank.update({page : 1/total_page})

num_iter = 0
while epsilon > 10e-8:
    num_iter += 1
    epsilon = 0
    for id in PageRank:
        if id in PageLink_inv:
            prev_value = PageRank[id]
            term1 = 0.15/total_page
            term2 = 0
            for linked_id in PageLink_inv[id]:
                term2+=1/len(PageLink[linked_id]) * PageRank[linked_id]
            post_value = (term1 + (1-0.15) * term2)
            epsilon += abs(post_value - prev_value)
            PageRank.update({id : post_value})
        

#print('Number of Iteration ', num_iter)
#print('page size  : ', len(PageRank))
#print('pagelink size : ', len(PageLink))
#print('Invpagelink size : ', len(PageLink_inv))
conn.commit()
conn.close()
print('building tables...')
print('ready to search')    
        
        
while True:
    terms  = input("1234-12345>").split()
    terms2 = []
    for term in terms:
        for word in InvIdxTable:
            if term != word and term.lower() == word.lower():
                terms2.append(word)
    terms = terms + terms2
    terms = list(set(terms))

    result_tfidf = {}
    for term in terms:
        if term in InvIdxTable:
            for page_id in InvIdxTable[term]:
                if not int(page_id) in result_tfidf:
                    result_tfidf.update({int(page_id) : TFIDF[page_id][term]})
                else:
                    sum_v = result_tfidf[int(page_id)] + TFIDF[page_id][term]
                    result_tfidf.update({int(page_id): sum_v})

    result = {}
    for id in result_tfidf:
        result.update({id : -result_tfidf[id] * PageRank[id]})

    result = sorted(result.items(), key = operator.itemgetter(1,0))
    for i in range(10):
        if i > len(result) - 1:
            break
        print(result[i][0],',',id_title[result[i][0]],',',result_tfidf[result[i][0]],',',PageRank[result[i][0]])


