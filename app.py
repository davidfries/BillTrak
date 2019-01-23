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
        pass
    else:
        billdata=BTBackend().getbilldata(str(username))
        print(billdata)
        for bill in billdata:
            print(bill.amt)
        return render_template('bills.html',billdata=billdata)
        
    

if __name__ == '__main__':
    
    app.run(port='5002',host="0.0.0.0")