
import random
import string
import records




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
    def createuser(self,userid,password,email):
        query='''
        INSERT INTO users (userid, password,email) VALUES (
        :userid,
     crypt(:password, gen_salt('bf')),:email
            );
        '''
        try:
            
            self.db.query(query,userid=userid,password=password,email=email)
        except:
            print("creaqte user error")
    def createcompany(self, companyname, datecreated, userid,  category=None):
        companyid=self.genintid()
        query = "INSERT INTO company(companyid,companyname,datecreated,userid,category) VALUES(:companyid,:companyname,:datecreated,:userid,:category)"
        self.db.query(query, companyid=companyid, companyname=companyname,
                      datecreated=datecreated, category=category, userid=userid)
    def getbilldata(self,userid):
        query="select * from billdatabyuserid WHERE userid=:userid AND date_trunc('month', duedate) = date_trunc('month', current_date)"
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
        return self.db.query(query, userid=userid).all()

    def getcompanynames(self,userid):
        query = "select companyname from company where userid = :userid"
        return self.db.query(query, userid=userid).export('json')#exports rows to JSON for request from JS

    def getbillrecurringstatus(self, billid):
        query = "select recurring from bills where billid=:billid"

        return self.db.query(query, billid=billid).first()
    def getemailbyuserid(self,userid):
        query="SELECT email from users where userid=:userid"
        return self.db.query(query, userid=userid).all()

    def validateuser(self, userid):
        pass

    def validatepw(self, password,userid):
        query="""
        SELECT *
        FROM users
        WHERE userid = :userid
        AND password = crypt(:password, password);
        """
        rows=self.db.query(query,password=password,userid=userid).all()
        print(len(rows)>0)
        return len(rows)>0
        

    def updatebillrecurring(self, billid):
        pass

    def deletebill(self, billid):
        query = "DELETE FROM bills WHERE billid=:billid"
        self.db.query(query, billid=billid)

    def getcompanyidbyname(self,companyname):
        return "None"

    def createbill(self,  billid, amt,  duedate, recurring,userid,companyname,companyid=None,datepaid=None, paymenturl=None, phonenum=None, category=None, confirmationnum=None):
        query = "INSERT INTO bills(billid,companyid,amt,datepaid,confirmationnum,paymenturl,category,phonenum,recurring,duedate) VALUES(:billid,:companyid,:amt,:datepaid,:confirmationnum,:paymenturl,:category,:phonenum,:recurring,:duedate)"
        
        companyid=self.getcompanyidbyname(companyname)
        self.db.query(query,  billid=billid, companyid=companyid, amt=amt, datepaid=datepaid, 
                      confirmationnum=confirmationnum, paymenturl=paymenturl,category=category, phonenum=phonenum,  recurring=recurring,duedate=duedate)

        
    def getnotifications(self):
        query=""" 
        select * from billdatabyuserid WHERE duedate = current_date + interval '3 day'
        
        """
        rows=self.db.query(query).all()

        return rows

    

