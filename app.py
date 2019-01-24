from flask import Flask, request, render_template,redirect,flash,session,abort
from backend import BTBackend as BTBackend
import os
app=Flask(__name__)
app.secret_key=os.urandom(12)

@app.route('/')
def default():
    return render_template('index.html')

@app.route('/bills/<username>',methods=['GET','POST'])
def billapp(username):
    if request.method=='POST':
        try:
            BTBackend().createbill(BTBackend().gencharid(),request.form['billamt'],userid=username,companyname=request.form['companyname'],duedate=request.form['duedate'],paymenturl=request.form['billurl'],phonenum=request.form['billtel'],recurring=request.form['recurring'])
            url="/bills/"+username
            return redirect(url)
        except Exception as err:
            print(err)
    else:
        billdata=BTBackend().getbilldata(str(username))
        print(billdata)
        for bill in billdata:
            print(bill.amt)
        return render_template('bills.html',billdata=billdata)
        
    

if __name__ == '__main__':
    
    app.run(port='5002',host="0.0.0.0")