import psycopg2
import random
import string
import records
class COPG():
    def conn(self):
        conn=psycopg2.connect("host=192.168.5.172 dbname=billtrak user=dj password=Skyliner34")
        return conn
class BTBackend():
    try:
        db=records.Database("postgresql://192.168.5.172/billtrak?user=dj&password=Skyliner34")
    except:
        print("error in db connection")

    def genintid(self):
        pass
    def gencharid(self):
        userid = ''.join(random.choices(
            string.ascii_letters + string.digits, k=8))
        return userid
        
    def debugprint(self):
        rows=self.db.query("select * from bills")
        print(rows.first().paymenturl)
        pass
    
    
    
    def getbillsbycompany(self,companyid):
        query="select * from bills where companyid=:companyid"
        
        rows=self.db.query(query,companyid=companyid)
        return rows.all()
        
    def getamtbybillid(self,billid):
        query="select * from bills where billid=:billid"
        
        rows=self.db.query(query,billid=billid).first()
        return rows.amt
    def getbillinfo(self):
        pass
    def validateuser(self,userid):
        pass
    def validatepw(self,pw):
        pass
    def updatebillrecurring(self,billid):
        pass
    def deletebill(self,billid):
        pass
    def createbill(self,companyid,amt,datepaid,dateinvoiced,paymenturl=None,phonenum=None):
        pass
    def createnotification(self,notificationid,userid,useremail,billid,amt,phonenum,paymenturl):
        pass
    def deletenotification(self,notificationid):
        pass
    
BTBackend().debugprint()
print(BTBackend().getbillsbycompany('1') )   
print(BTBackend().getamtbybillid('test0001'))