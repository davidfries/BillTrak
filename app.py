from flask import Flask, request, render_template, redirect, flash, session, abort
from backend import BTBackend as BTBackend
import os
app = Flask(__name__)
app.secret_key = os.urandom(12)


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
        if session['logged_in']:
            return render_template('bills.html', billdata=billdata)

    except:
        return redirect('/')

@app.route('/login', methods=['GET','POST'])
def userlogin():
    

    if request.method == 'POST':
        username = request.form['userid']
        if(BTBackend().validatepw(request.form['password'],username)):
            session['logged_in']= True #this is important for displaying elements on main app page
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

if __name__ == '__main__':
    
    app.run(port='5002', host="0.0.0.0")
