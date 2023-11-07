from flask import Flask, render_template, request, session, redirect, url_for,jsonify
import pyodbc,requests
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Thiết lập kết nối đến SQL Server
server = 'MSI\SQLEXPRESS02'
database = 'RENTAL_PROPERTIES'
username = ''
password = ''
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

# Đăng kí tài khoản
@app.route('/ResultRegister', methods=['POST'])
def ResultRegister ():
        data = request.json
        username = data['username']
        password = data['pass']
        nameshow = data['nameshow']
        number = data['number']
        email = data['email']
        confirm_password=data['confirm']
        # Kiểm tra xem tài khoản đã tồn tại chưa
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", username)
        if password != confirm_password:
            password_error = 'Password and confirm password do not match'
            return password_error       
        if cursor.fetchone():
            error = 'Username already exists'
            return error
        cursor.execute("INSERT INTO Users (username, password,money,nameshow,number) VALUES (?, ?,?,?,?)", username, password,0,nameshow,number)
        cnxn.commit()
        success="Tạo tài khoản thành công"
        return success
@app.route('/ResultLogin', methods=['POST'])
def ResultLogin():
        data = request.json
        username = data['username']
        password = data['pass']
        # Kiểm tra xem tài khoản có tồn tại không
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", username, password)
        user = cursor.fetchone()
        if user:

            return "Success"
            
        else:
            error = 'Invalid username or password'
            return error
@app.route('/GetUserbyUserName', methods=['POST'])
def GetUserbyUserName ():
        data = request.json
        username = data['username']
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? ", username)
        user = cursor.fetchone()
        payload = {"nameshow": user.nameshow,
                   "number": user.number
                }
        return payload

@app.route('/UpdatebyUser', methods=['POST'])
def UpdatebyUser():
        data = request.json
        username = data['username']
        showname=data['showname']
        number=data['number']
        cursor = cnxn.cursor()
        cursor.execute("UPDATE Users SET nameshow = ?,number=? WHERE username = ?", (showname, number, username))
        cursor.commit()
        return "Thành công"
@app.route('/UpdatePass', methods=['POST'])
def UpdatePass():
    data = request.json
    username = data['username']
    old=data['old']
    new=data['new']
    confirm=data['confirm']
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=? ", username,old)
    user=cursor.fetchone()
    if user:
        if new==confirm:
            cursor = cnxn.cursor()
            cursor.execute("UPDATE Users SET password = ? WHERE username = ?", (new,username))
            cursor.commit()
            return "Cập nhật thành công"
        else:
            return "Mật khẩu với và xác nhận không giống nhau vui lòng nhập lại"
    else :
        return "Mật khẩu cũ không đúng"
@app.route('/GetNumber', methods=['POST'])
def getnum():
    data = request.json
    username = data['username']
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", username)
    user=cursor.fetchone()
    return user.number
@app.route('/UpdateMoney', methods=['POST'])
def updateMoney():
    data = request.json
    username = data['username']
    price = data['price']
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", username)
    user=cursor.fetchone()
    newmoney=int(user.money)-int(price)
    cursor.execute("UPDATE Users SET money = ? WHERE username = ?", (newmoney,username))
    cursor.commit()
    return str(newmoney)

@app.route('/UpdateMoneyPlus', methods=['POST'])
def updateMoneyP():
    data = request.json
    username = data['username']
    price = data['price']
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", username)
    user=cursor.fetchone()
    newmoney=int(user.money)+int(price)
    cursor.execute("UPDATE Users SET money = ? WHERE username = ?", (newmoney,username))
    cursor.commit()
    return str(newmoney)
@app.route('/GetEmail', methods=['POST'])
def getemail():
    data = request.json
    username = data['username']
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", username)
    user=cursor.fetchone()
    return user.email
if __name__ == '__main__':
    app.run(port=5001, debug=True)