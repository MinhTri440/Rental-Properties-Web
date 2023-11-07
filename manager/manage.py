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

@app.route('/RentalManager', methods=['GET'])
def home ():
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM Transactions ORDER BY TimeCreate DESC")
    transactions = cursor.fetchall()
    return render_template("RentalManager.html",transactions=transactions)
@app.route('/YesPost', methods=['POST'])
def yesp ():
    id_rental = request.form['rental_id']
    url = "http://localhost:5002/UpdateStatus"
    payload = {"Id": id_rental,
               "status":"Còn"}    
    response=requests.post(url, json=payload)
    cursor = cnxn.cursor()
    cursor.execute("UPDATE Transactions SET status=? WHERE id_rental=?","Đã đăng",id_rental)
    cursor.commit()
    
    return redirect("/RentalManager")
@app.route('/NoPost', methods=['POST'])
def nop ():
    id_rental = request.form['id_rental']
    name = request.form['name']
    price = request.form['price']
    url = "http://localhost:5002/DeletePost"
    payload = {"id_rental": id_rental}    
    response=requests.post(url, json=payload)
    url = "http://localhost:5001/UpdateMoneyPlus"
    payload = {"username": name,
               "price": price}    
    response=requests.post(url, json=payload)
    cursor = cnxn.cursor()
    cursor.execute("UPDATE Transactions SET status=? WHERE id_rental=?","Không được duyệt",id_rental)
    cursor.commit()
    return redirect("/RentalManager")

@app.route('/YesUpgrade', methods=['POST'])
def yesUpgrade ():
    id_rental = request.form['rental_id']
    post = request.form['type_post']
    url = "http://localhost:5002/UpgradePost"
    payload = {"Id": id_rental,
               "Post":post}    
    response=requests.post(url, json=payload)
    cursor = cnxn.cursor()
    cursor.execute("UPDATE Transactions SET status=? WHERE id_rental=?","Đã nâng cấp",id_rental)
    cursor.commit()
    return redirect("/RentalManager")
@app.route('/NoUpgrade', methods=['POST'])
def noUpgrade ():
    Id = request.form['id_rental']
    name = request.form['name']
    price = request.form['price']

    url = "http://localhost:5001/UpdateMoneyPlus"
    payload = {"username": name ,
               "price": price}    
    response=requests.post(url, json=payload)
    cursor = cnxn.cursor()
    cursor.execute("UPDATE Transactions SET status=? WHERE id_rental=?","Không được duyệt",Id)
    cursor.commit()
    return redirect("/RentalManager")
@app.route('/incomeManager', methods=['GET'])
def imcome ():
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM Payment ORDER BY TimeCreate DESC")
    transactions = cursor.fetchall()
    return render_template("income.html",transactions=transactions)
@app.route('/YesNap', methods=['POST'])
def yesNap ():
    Id = request.form['id_pay']
    name = request.form['name']
    price = request.form['price']
    url = "http://localhost:5001/UpdateMoneyPlus"
    payload = {"username": name ,
               "price": price}    
    response=requests.post(url, json=payload)
    cursor = cnxn.cursor()
    cursor.execute("UPDATE Payment SET status=? WHERE Id=?","Nạp thành công",int(Id))
    cursor.commit()
    return redirect("/incomeManager")
@app.route('/NoNap', methods=['POST'])
def NoNap ():
    Id = request.form['id_pay']
    cursor = cnxn.cursor()
    cursor.execute("UPDATE Payment SET status=? WHERE Id=?","Nạp thất bại (hệ thống chưa nhận được tiền)",int(Id))
    cursor.commit()
    return redirect("/incomeManager")
@app.route('/statistic_bill', methods=['GET'])
def statistic():
    if request.method == 'GET':
        date = request.args.get('date')
        month = request.args.get('month')
        year = request.args.get('year')
        cursor = cnxn.cursor()
        if date:
            cursor.execute("SELECT * FROM payment WHERE CAST(TimeCreate AS DATE) = ? AND status=?", date,"Nạp thành công")
        elif month:
            month_list = month.split('-') # phân tách chuỗi theo ký tự '-'
            cursor.execute("SELECT * FROM payment WHERE YEAR(TimeCreate) = ? AND MONTH(TimeCreate) = ? AND status=?", month_list[0], month_list[1],"Nạp thành công")
        elif year:
            cursor.execute("SELECT * FROM payment WHERE YEAR(TimeCreate) = ? AND status=?", year,"Nạp thành công")
        else:
            cursor.execute("SELECT * FROM payment  WHERE status=? ","Nạp thành công")
        list_bill = cursor.fetchall()
        return render_template('statistic.html', list_bill=list_bill)
    
if __name__ == '__main__':
    app.run(port=5004, debug=True)