import psycopg2
import records
class BTBackend():
    try:
        db=records.Database("postgresql://192.168.5.172/billtrak?user=dj&password=Skyliner34")
    except:
        print("error in db connection")
    def getdata(self):
        
        rows=self.db.query("select * from minthill where timestamp::timestamp::date >=now()-'36 hours'::interval")
        return rows.export('df')
    
    def getbillsbycompany(self,companyid):
        pass
    def getamtbybillid(self,billid):
        pass
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
    def createnotification(self,notificationid,)

    
