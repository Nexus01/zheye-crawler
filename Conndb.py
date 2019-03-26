# !/usr/bin/python3
import pymongo

def insertdomainid(client,dbname, colname, domain, id, fromwhere):
    #远程服务器的IP和端口
    mydb = client[dbname] #database
    mycol = mydb[colname] #collection
    mylist = {"domain": domain, "ppid": id, "fromwhere": fromwhere}
    result = mycol.find_one({'ppid': id})
    if result:
        mycol.update({'ppid': id},{'domain': domain, 'ppid': id, "fromwhere": fromwhere})#更新数据
    else:
        mycol.insert_one(mylist)
    return
