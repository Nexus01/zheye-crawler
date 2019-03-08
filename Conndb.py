# !/usr/bin/python3
import pymongo

def connectdb(ip,port,dbname,colname,domain,id):
    myclient = pymongo.MongoClient(str(ip)+":"+str(port))#远程服务器的IP和端口
    mydb = myclient[dbname] #database
    mycol = mydb[colname] #collection
    domainid(mycol,domain,id)
    return
def domainid(mycol,yu,id):
    mylist = {"domain": yu, "id": id}
    mycol.insert_one(mylist)
    return
