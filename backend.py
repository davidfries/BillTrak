import random
import string
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from envs import envs
import datetime
from datetime import timedelta
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    userid = Column(String, primary_key=True)
    password = Column(String)
    email = Column(String)

class Company(Base):
    __tablename__ = 'company'
    companyid = Column(Integer, primary_key=True)
    companyname = Column(String)
    datecreated = Column(Date)
    userid = Column(String)
    category = Column(String)

class Bill(Base):
    __tablename__ = 'bills'
    billid = Column(Integer, primary_key=True)
    companyid = Column(Integer)
    amt = Column(Integer)
    datepaid = Column(Date)
    confirmationnum = Column(String)
    paymenturl = Column(String)
    category = Column(String)
    phonenum = Column(String)
    recurring = Column(Boolean)
    duedate = Column(Date)

class Notification(Base):
    __tablename__ = 'notificationall'
    id = Column(Integer, primary_key=True)
    duedate = Column(Date)

class BTBackend():
    def __init__(self):
        engine = create_engine(f"postgresql://{envs['dburl']}/billtrak?user=dj&password={envs['dbpw']}")

        Session = sessionmaker(bind=engine)
        self.session = Session()

    def genintid(self):
        return random.getrandbits(30)

    def gencharid(self):
        userid = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        return userid

    def createuser(self, userid, password, email):
        user = User(userid=userid, password=password, email=email)
        self.session.add(user)
        self.session.commit()

    def createcompany(self, companyname, datecreated, userid, category=None):
        companyid = self.genintid()
        company = Company(companyid=companyid, companyname=companyname, datecreated=datecreated, userid=userid, category=category)
        self.session.add(company)
        self.session.commit()

    def getbilldata(self, userid):
        rows = self.session.query(Bill).filter(Bill.userid == userid).order_by(Bill.duedate.desc()).all()
        return rows

    def getbillsbycompany(self, companyid, companyname):
        rows = self.session.query(Bill).filter(Bill.companyid == self.getcompanyidbyname(companyname)).all()
        return rows

    def getbillinfo(self, billid, userid):
        row = self.session.query(Bill).filter(Bill.billid == billid, Bill.userid == userid).first()
        return row

    def getcompanyidsbyuserid(self, userid):
        rows = self.session.query(Company.companyid).filter(Company.userid == userid).all()
        return rows

    def getcompanycount(self, userid):
        rows = self.session.query(Company.companyname).filter(Company.userid == userid).all()
        return len(rows)

    def getcompanynames(self, userid):
        rows = self.session.query(Company.companyname).filter(Company.userid == userid).all()
        data = [{"name": row.companyname} for row in rows]
        return data

    def getbillrecurringstatus(self, billid):
        row = self.session.query(Bill.recurring).filter(Bill.billid == billid).first()
        return row

    def getemailbyuserid(self, userid):
        rows = self.session.query(User.email).filter(User.userid == userid).all()
        return rows

    def validatepw(self, password, userid):
        rows = self.session.query(User).filter(User.userid == userid, User.password == password).all()
        return len(rows) > 0

    def addmonthlyincome(self, userid, amt):
        user = self.session.query(User).filter(User.userid == userid).first()
        user.monthlyincome = amt
        self.session.commit()

    def getcompanyamts(self, userid):
        rows = self.session.query(Company).filter(Company.userid == userid).all()
        return rows

    def editbills(self, billid, amt, duedate, phonenum, paymenturl, confirmationnum):
        bill = self.session.query(Bill).filter(Bill.billid == billid).first()
        bill.amt = amt
        bill.duedate = duedate
        bill.phonenum = phonenum
        bill.paymenturl = paymenturl
        bill.confirmationnum = confirmationnum
        self.session.commit()

    def updatebillamt(self, billid, amt):
        bill = self.session.query(Bill).filter(Bill.billid == billid).first()
        bill.amt = amt
        self.session.commit()

    def updatebillrecurring(self, billid, recurring):
        bill = self.session.query(Bill).filter(Bill.billid == billid).first()
        bill.recurring = not recurring
        self.session.commit()

    def deletebill(self, billid):
        self.session.query(Bill).filter(Bill.billid == billid).delete()
        self.session.commit()

    def getcompanyidbyname(self, companyname):
        row = self.session.query(Company.companyid).filter(Company.companyname == companyname).first()
        return row.companyid

    def createbill(self, billid, amt, duedate, recurring, userid, companyname, confirmationnum, companyid=None, datepaid=None, paymenturl=None, phonenum=None, category=None):
        companyid = self.getcompanyidbyname(companyname)
        bill = Bill(billid=billid, companyid=companyid, amt=amt, datepaid=datepaid, confirmationnum=confirmationnum, paymenturl=paymenturl, category=category, phonenum=phonenum, recurring=recurring, duedate=duedate)
        self.session.add(bill)
        self.session.commit()

    def getnotifications(self):
        rows = self.session.query(Notification).filter(Notification.duedate > datetime.datetime.now() - timedelta(days=3)).all()
        return rows

    def paybill(self, billid):
        bill = self.session.query(Bill).filter(Bill.billid == billid).first()
        bill.paid = not bill.paid
        self.session.commit()
    def resetpw(self, userid, password):
        user = self.session.query(User).filter(User.userid == userid).first()
        user.password = password
        try:
            self.session.commit()
            return 'SUCCESS'
        except:
            return 'FAILURE'