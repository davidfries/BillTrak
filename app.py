from flask import Flask, request, render_template, redirect, flash, session, abort,jsonify
from flask_mail import Mail,Message
from flask_session import Session
from redis import Redis
from werkzeug.middleware.proxy_fix import ProxyFix
from backend import BTBackend as BTBackend
import datetime
import os
from secrets import secrets as secrets
from scheduler import EmailScheduler
import requests
app = Flask(__name__)
# app.secret_key = os.urandom(12)
app.config['MAIL_SERVER']='smtp.sendgrid.net'
app.config['MAIL_PORT']='465'
app.config['MAIL_USE_SSL']='True'
app.config['MAIL_USERNAME']='apikey'
app.config['PASSWORD']='{}'.format(secrets.emailapikey)
app.config['MAIL_DEFAULT_SENDER']='notification@billtrak.io'
app.config['SESSION_TYPE']='redis'
app.config['SESSION_REDIS']=Redis('192.168.5.75')
app.config['SECRET_KEY'] = secrets.sessionkey
mail=Mail(app)
Session().init_app(app)
app.wsgi_app=ProxyFix(app.wsgi_app,x_host=1,x_proto=1)
# @app.before_request
# def before_request():
#     if not request.is_secure:
#         url = request.url.replace("http://", "https://", 1)
#         # code = 301
#         return redirect(url)


@app.route('/')
def default():
    return render_template('index.html')

@app.route('/paybill/<billid>')
def paybill(billid):
    return redirect('/bills/'+session['username'])

@app.route('/bills/<username>', methods=['GET', 'POST'])
def billapp(username):
    
    
    
    try:
        if session['logged_in'] and session['username']==username: #checks if the user is marked as logged in and if the username requested in url matches that token
            billdata = BTBackend().getbilldata(str(username))
            compdata=BTBackend().getcompanynames(str(username))
            companycount= BTBackend().getcompanycount(username)
            # print(companycount)
            return render_template('bills.html', billdata=billdata,userid=username,data=compdata, companycount=companycount)
        else:
            return redirect('/')
    except Exception as err:
        print(err)
        return redirect('/')

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
        bill=BTBackend().getbillinfo(billid)
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
    
    if request.args.get('auth_token')==str(f'{secrets.emailkey}' and request.method == 'POST'): #checks if auth token equals what is set here
        print('notif method works as intended')
        users=BTBackend().getnotifications()
        with mail.connect() as conn:
            for user in users:
                message = """
                Hello,

                The bill for {companyname} is due on {duedate}. The total amount due is: {amt}
                To pay your bill visit the following user-defined link: {paymenturl}
                Alternatively, you can pay by phone at: {phonenum}

                Sincerely,
                BillTrak Notification Service

                
                
                """.format(companyname=user.companyname,duedate=user.duedate,paymenturl=user.paymenturl,phonenum=user.phonenum)
                subject = "BillDue Notification"
                msg = Message(recipients=[BTBackend().getemailbyuserid(user.userid)],
                            body=message,
                            subject=subject)

                conn.send(msg)
        return '<h1>Notifications sent!</h1>'
    else:
        print('didn"t work with toekn')
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
    if(request.args.get('auth_token')==secrets.emailkey):
        schedule=EmailScheduler()
        cron=schedule.getcron()
        schedule.getscheduler().add_job(sendemail,cron.from_crontab('0 12 * * *'))
        schedule.getscheduler().start()
        print("Started email job! ADMIN OUTPUT")

@app.route('/getemailjobs',methods=['GET'])
def getemailjobs():
    if(request.args.get('auth_token')==secrets.emailkey and request.method=='GET'):
        schedule=EmailScheduler()
        
        schedule.getscheduler().start()
        print(schedule.getscheduler().get_jobs())
        return str(schedule.getscheduler().get_jobs())
    else:
        return "Stop doing that."
def sendemail():
    requests.post('localhost/sendmail?auth_token={}'.format(secrets.emailkey))
if __name__ == '__main__':
       
    app.run(port='5002', host="0.0.0.0")

