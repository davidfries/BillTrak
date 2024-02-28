from flask import Flask, request, render_template, redirect, flash, session, abort,jsonify
from flask_mail import Mail,Message
from flask_session import Session
from redis import Redis
from werkzeug.middleware.proxy_fix import ProxyFix
from backend import BTBackend as BTBackend
import datetime
import os
# from secrets import secrets as secrets
from scheduler import EmailScheduler
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from logging import Logger
import logging
from handlers import LogHandler
import requests
app = Flask(__name__)
# app.secret_key = os.urandom(12)
app.config['MAIL_SERVER']='smtp.sendgrid.net'
app.config['MAIL_PORT']='465'
app.config['MAIL_USE_SSL']='True'
app.config['MAIL_USERNAME']='apikey'
app.config['PASSWORD']='{}'.format(os.getenv('emailapikey'))
app.config['MAIL_DEFAULT_SENDER']='notification@billtrak.io'
app.config['SESSION_TYPE']='redis'
app.config['SESSION_REDIS']=Redis(os.getenv('redisurl'))
app.config['SECRET_KEY'] = os.getenv('sessionkey')
logger=Logger("BillTrakCore")
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
    level=logging.INFO)

hdlr=LogHandler()
logger.addHandler(hdlr)

mail=Mail(app)
Session().init_app(app)
app.wsgi_app=ProxyFix(app.wsgi_app,x_host=1,x_proto=1)
# @app.before_request
# def before_request():
#     if not request.is_secure:
#         url = request.url.replace("http://", "https://", 1)
#         # code = 301
#         return redirect(url)

@app.context_processor
def inject_user():
    try:
        userid=session['username']
    except:
        userid=""
    return dict(username=userid)
@app.route('/')
def default():
    return render_template('index.html')

@app.route('/paybill/<billid>')
def paybill(billid):
    BTBackend().paybill(billid)
    return redirect('/bills/'+session['username'])
def aggregatebillamts(bills):
    total=0
    try:
        for bill in bills:
            total+=int(bill.sum)
    except Exception as e:
        print(e)
    return total
@app.route('/bills/managecashflow/',methods=['GET','POST'])
def managecashflow():
    if(request.method=='GET'):
        try:
            userid=session['username']
        except:
            return redirect('login.html')
        try:
            data=BTBackend().getcompanyamts(userid)
            if(data[0].monthlyincome):
                try:
                    total=aggregatebillamts(data)
                    percentage = int((total/data[0].monthlyincome)*100)
                except:
                    logger.info("error in percentage calculation for cashflow")
            else:
                percentage=0

        except Exception as e:
            print(e)
            return redirect('/bills/'+session['username'])
        return render_template('cashflow.html',data=data,percentage=percentage)
    if(request.method=='POST'):
        # try:
        BTBackend().addmonthlyincome(session['username'],request.form['monthlyincome'])
        
        # data=BTBackend().getcompanyamts(session['username'])
        
            
        return redirect("/bills/managecashflow")
        # except:
        #     print("error when adding monthly incomeflask")
        #     return re

@app.route('/bills/<username>', methods=['GET', 'POST'])
def billapp(username):
    
    
    if(request.method =='GET'):
        try:
            if session['logged_in'] and session['username']==username: #checks if the user is marked as logged in and if the username requested in url matches that token
                billdata = BTBackend().getbilldata(str(session['username']))
                compdata=BTBackend().getcompanynames(str(session['username']))
                companycount= BTBackend().getcompanycount(session['username'])
                billcount=len(billdata)
                logger.info("{}'s billcount is: {}".format(username,billcount))
                # print(billdata[0].paid)
                # print(companycount)
                return render_template('bills.html', billdata=billdata,userid=username,data=compdata, companycount=companycount,billcount=billcount)
            else:
                return redirect('/')
        except Exception as err:
            print(err)
            return redirect('/')
    else:
        return redirect('/')
@app.route('/resetpassword', methods=['POST'])
def resetpw():
    if(request.method=='POST'):
        try:
            userid=session['username']
        except:
            logger.error("Error on password reset: MISSING LOG-IN")
        newpassword=request.form['newpassword']
        reset=BTBackend().resetpw(userid,newpassword)
        if(reset=='SUCCESS'):
            return redirect('/settings')
        elif(reset=='FAILURE'):
            return redirect('/bills')
    else:
        return "FORBIDDEN"
    
@app.route('/login', methods=['GET','POST'])
def userlogin():
    

    if request.method == 'POST':
        username = request.form['userid']
        if(BTBackend().validatepw(request.form['password'],username)): #checks if password is valid
            session['logged_in']= True #this is important for displaying elements on main app page
            session['username']=username #sets the session username token
            url="/bills/"+username
            return redirect(url) 
        else:
            return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session['logged_in']=False
    session.pop('username',None)
    return redirect('/')

@app.route('/edit/<billid>', methods=['GET','POST'])
def editbill(billid):
    
    if request.method=='POST':
        BTBackend().editbills(billid,request.form['billamt'],request.form['duedate'],request.form['billtel'],request.form['billurl'],request.form['confirmationnum'])
        return redirect('/bills/'+session['username'])
    else:
        
        try:
            bill=BTBackend().getbillinfo(billid,session['username'])
        except:
            
            return redirect('/')
        return render_template('edit.html',bill=bill)

@app.route('/delete/<billid>', methods=['POST'])
def deletebill(billid):
    if request.method=='POST':
        BTBackend().deletebill(billid)
        return redirect('/bills/'+session['username'])
    else:
        #if the delete bill method isn't post, redirect to bills page
        return redirect('/bills/'+session['username'])

@app.route('/register',methods=['GET','POST'])
def registeruser():
    if request.method=='POST':
        BTBackend().createuser(request.form['userid'],request.form['password'],request.form['email'])
        return redirect('/login')
        
    else:
        return render_template('register.html')

@app.route('/settings',methods=['GET','POST'])
def managesettings():
    return render_template('settings.html')
@app.route('/sendmail',methods=['POST'])
def sendnotifications():
    
    if request.args.get('auth_token')==os.getenv('emailkey') and request.method == 'POST': #checks if auth token equals what is set here
        logger.info('notif method works as intended')
        users=BTBackend().getnotifications()
        try:
            
            for user in users:
                message = """
                Hello,

                The bill for {companyname} is due on {duedate}. The total amount due is: {amt}
                To pay your bill visit the following user-defined link: {paymenturl}
                Alternatively, you can pay by phone at: {phonenum}

                Sincerely,
                BillTrak Notification Service

                
                
                """.format(companyname=user.companyname,duedate=user.duedate,paymenturl=user.paymenturl,phonenum=user.phonenum,amt=user.amt)
                subject = "BillDue Notification"
                msg = Mail(to_emails=user.email,
                            from_email='notification@billtrak.io',
                            html_content=message,
                            subject=subject)
                logger.info("sending message {}".format(user))
                sg = SendGridAPIClient(os.getenv('emailapikey'))
                response=sg.send(msg)
                logger.info("Status Code: {} Body: {} Headers: {}".format(response.status_code,response.body,response.headers))
                    
        except Exception as e:
            logger.info("Exception in email send: {}".format(e))
            return '<h1>error in email send</h1>'
        return '<h1>Notifications sent!</h1>'
    else:
        logger.info('didn"t work with token')
        return '<h1>Notifications failed!</h1>'
@app.route('/addbill',methods=['GET','POST'])
def addbill():
    try:
        userid=session['username']
    except:
        return redirect('/')
    if request.method == 'POST':
        try:
            BTBackend().createbill(BTBackend().gencharid(), request.form['billamt'], userid=userid, companyname=request.form['companyname'],
                                   duedate=request.form['duedate'], paymenturl=request.form['billurl'], phonenum=request.form['billtel'], recurring=request.form['recurring'],
                                   confirmationnum=request.form['confirmationnum'])
            url = "/bills/"+userid
            return redirect(url)
        except Exception as err:
            print(err)
            url = "/bills/"+userid
            return redirect(url)
    else:
       data=BTBackend().getcompanynames(session['username'])
       return render_template('newbill.html',data=data,userid=userid)
@app.route('/addcompany',methods=['GET','POST'])
def addcompany():
    try:
        userid=session['username']
    except:
        return redirect('/')
    if request.method == 'POST':
        try:
            current_time=datetime.datetime.now()
            BTBackend().createcompany(request.form['companyname'],current_time.strftime('%m/%d/%Y'),userid)
            url = "/bills/"+userid
            return redirect(url)
        except Exception as err:
            print(err)
    else:
       return render_template('newcompany.html')

@app.route('/emailjobtrigger',methods=['POST'])
def triggeremailjob():
    if(request.args.get('auth_token')==os.getenv('emailkey')):
        schedule=EmailScheduler()
        cron=schedule.getcron()
        schedule.getscheduler().add_job(sendemail,cron.from_crontab('0 12 * * *'))
        schedule.getscheduler().start()
        logger.info("Started email job! ADMIN OUTPUT")

@app.route('/getemailjobs',methods=['GET'])
def getemailjobs():
    if(request.args.get('auth_token')==os.getenv('emailkey') and request.method=='GET'):
        schedule=EmailScheduler()
        
        schedule.getscheduler().start()
        logger.info(schedule.getscheduler().get_jobs()[0])
        return str(schedule.getscheduler().get_jobs())
    else:
        return "Stop doing that."
def sendemail():
    requests.post('http://localhost:5002/sendmail?auth_token={}'.format(os.getenv('emailkey')))
if __name__ == '__main__':
    schedule=EmailScheduler()
    schedule.getscheduler().start()
    
    logger.info("Starting flask server")
    app.run(port='5002', host="0.0.0.0")

