from flask import Flask, render_template, request, session, redirect, url_for,jsonify
import pyodbc,requests
from flask_session import Session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Thiết lập kết nối đến SQL Server
server = 'MSI\SQLEXPRESS02'
database = 'RENTAL_PROPERTIES'
username = ''
password = ''
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

# Đăng kí tài khoản
@app.route('/payment', methods=['POST'])
def payment ():
        data = request.json
        username = data['username']
        price = data['price']
        method = data['method']
        cursor = cnxn.cursor()
        cursor.execute("INSERT INTO Payment (username, price,type,status,TimeCreate) VALUES (?,?,?,?,?)", username, int(price),method,"Đang xử lí",datetime.now())              
        cnxn.commit()
        success="OK"
        return "OK"

if __name__ == '__main__':
    app.run(port=5003, debug=True)