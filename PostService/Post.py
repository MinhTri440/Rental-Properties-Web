from flask import Flask, render_template, request, session, redirect, url_for,jsonify
import pyodbc,requests
from datetime import datetime
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
@app.route('/UpPost', methods=['POST'])
def Post():
        data = request.json
        title = data['title']
        description = data['description']
        address = data['address']
        district = data['district']
        image1 = data['image1']
        image2=data['image2']
        image3=data['image3']
        price=data['price']
        type=data['type']
        area=data['area']
        number=data['number']
        username=data['username']
        type_post=data['type_post']
        cursor = cnxn.cursor()
        cursor.execute("INSERT INTO Rental_Properties (title, description, address, district, image1, image2, image3, price, type, area, number, UserName, Status, TimeCreate, Type_Post) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (title, description, address, district, image1, image2, image3, int(price), type, int(area), number, username, "Đang xử lí", datetime.now(), type_post))
        cursor.commit()
        price_post=0
        if type_post=='VIP':
            price_post=50000
        elif type_post=='MEDIUM':
            price_post=30000
        else:
            price_post=15000
        cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE UserName=? AND title=? AND address=?",username,title,address)
        rental = cursor.fetchone()
        cursor.execute("INSERT INTO Transactions (username,id_rental,type,price,status,TimeCreate) VALUES (?,?,?,?,?,?)",username,int(rental.Id),"Đăng bài",int(price_post),"Đang xử lí",datetime.now())
        cursor.commit()
        return str(price_post)
@app.route('/DeletePost', methods=['POST'])
def deletepost():
        data = request.json
        id = data['id_rental']
        cursor = cnxn.cursor()
        cursor.execute("DELETE FROM Rental_Properties WHERE Id = ?",int(id))
        cursor.commit()
        return "Đã xóa"
@app.route('/UpdatePost', methods=['POST'])
def Updatepost():
        data = request.json
        id = data['id']
        description = data['description']
        image1 = data['image1']
        image2=data['image2']
        image3=data['image3']
        price=data['price']
        map=data['map']
        zalo=data['zalo']
        facebook=data['facebook']
        cursor = cnxn.cursor()
        cursor.execute("UPDATE RENTAL_PROPERTIES SET description = ?, image1=?, image2=?, image3=?, price=?, linkmap=?, number_zalo=? , link_facebook=?  WHERE Id = ?",description,image1,image2,image3,int(price),map,zalo,facebook,int(id))
        cursor.commit()
        return "Đã cập nhật"
@app.route('/UpdateStatus', methods=['POST'])
def UpdateStatus():
        data = request.json
        id = data['Id']
        status = data['status']
        cursor = cnxn.cursor()
        cursor.execute("UPDATE RENTAL_PROPERTIES SET Status = ?  WHERE Id = ?",status,int(id))
        cursor.commit()
        return "Đã cập nhật Status"
@app.route('/Upgrade', methods=['POST'])
def upgrade():
        data = request.json
        id = data['Id']
        post = data['Post']
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE Id=?",id)
        rental = cursor.fetchone()
        money=''
        if rental.Type_Post=="MEDIUM" and post=="VIP":
           money='20000'
        if rental.Type_Post=="NORMAL" and post=="MEDIUM":
           money='15000'
        if rental.Type_Post=="NORMAL" and post=="VIP":
           money='35000'
        cursor.execute("INSERT INTO Transactions (username,id_rental,type,price,status,TimeCreate) VALUES (?,?,?,?,?,?)",rental.UserName,int(rental.Id),"Nâng cấp bài",int(money),"Đang xử lí",datetime.now())
        cursor.commit()
        return  money
@app.route('/UpgradePost', methods=['POST'])
def upgradePost():
        data = request.json
        id_rental = data['Id']
        post = data['Post']
        cursor = cnxn.cursor()
        cursor.execute("UPDATE RENTAL_PROPERTIES SET Type_Post = ? , TimeCreate=? WHERE Id = ?",post,datetime.now(),int(id_rental))
        cursor.commit()
        return  "Đã cập nhật loại tin"
if __name__ == '__main__':
        app.run(port=5002, debug=True)