import psycopg2
import random
import string
import records

#depreciated
class COPG():
    def conn(self):
        conn = psycopg2.connect(
            "host=192.168.5.172 dbname=billtrak user=dj password=Skyliner34")
        return conn


class BTBackend():
    try:
        db = records.Database(
            "postgresql://192.168.5.172/billtrak?user=dj&password=Skyliner34")
    except:
        print("error in db connection")

    def genintid(self):
        return random.getrandbits(30)
        

    def gencharid(self):
        userid = ''.join(random.choices(
            string.ascii_letters + string.digits, k=8))
        return userid

    # def debugprint(self):
    #     rows=self.db.query("select * from bills")
    #     print(rows.all().paymenturl)
    #     pass

    def createcompany(self, companyname, datecreated, userid, companyid, category=None):
        companyid=self.genintid()
        query = "INSERT INTO company(companyid,companyname,datecreated,,userid,category) VALUES(:companyid,:companyname,:datecreated,:userid,:category)"
        self.db.query(query, companyid=companyid, companyname=companyname,
                      datecreated=datecreated, category=category, userid=userid)
    def getbilldata(self,userid):
        query="select * from billdatabyuserid WHERE userid=:userid"
        rows = self.db.query(query,userid=userid)
        return rows.all()
    def getbillsbycompany(self, companyid):
        query = "select * from bills where companyid=:companyid"

        rows = self.db.query(query, companyid=companyid)
        return rows.all()

    def getamtbybillid(self, billid):
        query = "select * from bills where billid=:billid"

        rows = self.db.query(query, billid=billid).first()
        return rows.amt

    def getcompanyidsbyuserid(self, userid):
        query = "select companyid from company where userid = :userid"
        return self.db.query(query, userid=userid).all

    def getcompanynames(self,userid):
        query = "select companyname from company where userid = :userid"
        return self.db.query(query, userid=userid).all

    def getbillrecurringstatus(self, billid):
        query = "select recurring from bills where billid=:billid"

        return self.db.query(query, billid=billid).first()

    def validateuser(self, userid):
        pass

    def validatepw(self, pw):
        pass

    def updatebillrecurring(self, billid):
        pass

    def deletebill(self, billid):
        query = "DELETE FROM bills WHERE billid=:billid"
        self.db.query(query, billid=billid)

    def createbill(self,  billid, amt, datepaid, dateinvoiced, recurring,companyid, paymenturl=None, phonenum=None, category=None, confirmationnum=None):
        query = "INSERT INTO bills VALUES(:billid,:companyid,:amt,:dateinvoiced,:datepaid,:confirmationnum,:paymenturl,:category,:phonenum,:recurring)"
        companyid=self.genintid()
        self.db.query(query, companyid=companyid, billid=billid, amt=amt, datepaid=datepaid, dateinvoiced=dateinvoiced,
                      confirmationnum=confirmationnum, paymenturl=paymenturl, phonenum=phonenum, category=category, recurring=recurring)

        

    def createnotification(self, notificationid, userid, useremail, billid, amt, phonenum, paymenturl):
        pass

    def deletenotification(self, notificationid):
        pass

# data = BTBackend().getbilldata('dj')
# for bill in data:
#     print (bill.amt)

# BTBackend().debugprint()
# print(BTBackend().getbillsbycompany('1'))
# print(BTBackend().getamtbybillid('test0002'))
# print(BTBackend().getamtbybillid('test0001'))
# BTBackend().createbill('1','test0002','7762','1/17/2019','1/12/2019')
