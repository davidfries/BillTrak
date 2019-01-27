from flask import Flask, request, render_template, redirect, flash, session, abort
from flask_mail import Mail,Message
from backend import BTBackend as BTBackend
import os
app = Flask(__name__)
app.secret_key = os.urandom(12)
app.config['MAIL_SERVER']='mail.billtrak.io'
app.config['MAIL_PORT']='587'
app.config['MAIL_USE_SSL']='True'
app.config['MAIL_USERNAME']='admin'
app.config['PASSWORD']=''
app.config['MAIL_DEFAULT_SENDER']='notification@billtrak.io'

mail=Mail(app)

@app.route('/')
def default():
    return render_template('index.html')


@app.route('/bills/<username>', methods=['GET', 'POST'])
def billapp(username):
    if request.method == 'POST':
        try:
            BTBackend().createbill(BTBackend().gencharid(), request.form['billamt'], userid=username, companyname=request.form['companyname'],
                                   duedate=request.form['duedate'], paymenturl=request.form['billurl'], phonenum=request.form['billtel'], recurring=request.form['recurring'])
            url = "/bills/"+username
            return redirect(url)
        except Exception as err:
            print(err)
    else:
        billdata = BTBackend().getbilldata(str(username))
    try:
        if session['logged_in'] and session['username']==username: #checks if the user is marked as logged in and if the username requested in url matches that token
            
            return render_template('bills.html', billdata=billdata)
        else:
            return redirect('/')
    except:
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
    return redirect('/')

@app.route('/register',methods=['GET','POST'])
def registeruser():
    if request.method=='POST':
        BTBackend().createuser(request.form['userid'],request.form['password'],request.form['email'])
        return redirect('/login')
        
    else:
        return render_template('register.html')

@app.route('/settings',methods=['GET','POST'])
def managesettings():
    pass
@app.route('/sendmail',methods=['POST'])
def sendnotifications():
    
    if request.args.get('auth_token')==str('LB2JWxfAP9dqrdqNYY2LP3U8wQ'): #checks if auth token equals what is set here
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

if __name__ == '__main__':
    
    app.run(port='5002', host="0.0.0.0")
