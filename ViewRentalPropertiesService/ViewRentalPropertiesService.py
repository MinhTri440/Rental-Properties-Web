from flask import Flask, render_template, request, session, redirect, url_for,jsonify
import pyodbc,requests,os
from datetime import datetime
from flask_session import Session
import hashlib
import hmac
import urllib
import urllib.parse
import urllib.request
app = Flask(__name__)
app.secret_key = 'không đoán được đâu'
# Thiết lập kết nối đến SQL Server
server = 'MSI\SQLEXPRESS02'
database = 'RENTAL_PROPERTIES'
username = ''
password = ''
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
# Đăng kí tài khoản
@app.route('/', methods=['GET'])
def home():
    if 'username' in session:
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE status=? ORDER BY TimeCreate DESC", 'Còn')
        lists = cursor.fetchall()
        lists = sorted(lists, key=lambda x: (x.Type_Post == 'VIP', x.Type_Post == 'MEDIUM', x.TimeCreate), reverse=True)
        if 'money' in session:
            return render_template('home.html',lists=lists,username=session['showname'],money=session['money'])
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE status=? ORDER BY TimeCreate DESC", 'Còn')
    lists = cursor.fetchall()
    # Sắp xếp lists theo type
    lists = sorted(lists, key=lambda x: (x.Type_Post == 'VIP', x.Type_Post == 'MEDIUM', x.TimeCreate), reverse=True)
    return render_template('home.html',lists=lists)
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username',None)
    session.pop('showname',None)
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        confirm_password = request.form['confirm_password']
        nameshow = request.form['nameshow']
        number = request.form['number']
        url = "http://localhost:5001/ResultRegister"
        payload = {"username": username,
                "pass":password,
                "confirm":confirm_password,
                'nameshow':nameshow,
                'number':number,
                'email':email
                }
        response=requests.post(url, json=payload)
        if response.text=='Tên tài khoản đã tồn tại':
            return render_template('register.html', error=response.text)
        if response.text=='Mật khẩu xác nhận không giống với mật khẩu':
            return render_template('register.html', password_error=response.text)
        return render_template('register.html',success=response.text)
    return render_template('register.html');

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        url = "http://localhost:5001/ResultLogin"
        payload = {"username": username,
                "pass":password,
                }
        response=requests.post(url, json=payload)
        if response.text=='Success':
            session['username']=username
            cursor = cnxn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", username, password)
            user = cursor.fetchone()
            session['showname']=user.nameshow
            session['money']=user.money
            return redirect("/")
        else:
            error=response.text
            return render_template('login.html',error=error)
    return render_template('login.html');
@app.route('/detail/<Id>', methods=['GET'])
def detail(Id):
    if 'username' in session:
        checkfavourite='';
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE Id=?",Id)
        rental_property = cursor.fetchone()
        cursor.execute("SELECT * FROM Favorite WHERE UserName=? AND Id_RentalProperty=? ", ( session['username'],Id))
        favourite = cursor.fetchall()
        cursor.execute("SELECT * FROM Reviews WHERE Id_Rental=? ", (Id))
        reviews= cursor.fetchall()
        if favourite:
            checkfavourite='yes'
        else:
            checkfavourite='no'
        return render_template('detail.html',rental_property=rental_property,username=session['showname'],checkfavourite=checkfavourite,reviews=reviews,money=session['money'])
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE Id=?",Id)
    rental_property = cursor.fetchone()
    cursor.execute("SELECT * FROM Reviews WHERE Id_Rental=? ", (Id))
    reviews= cursor.fetchall()
    return render_template('detail.html',rental_property=rental_property,reviews=reviews)
@app.route('/UpdateFavourite/<Id>', methods=['GET'])
def UpdateFavourite(Id):
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM Favorite WHERE Id_RentalProperty=? AND UserName=?", (Id, session['username']))
        favourite = cursor.fetchone()
        if favourite:
            cursor = cnxn.cursor()
            cursor.execute("DELETE FROM Favorite WHERE Id = ?",favourite.Id)
            cnxn.commit() 
            return redirect(f"/detail/{Id}")
        else:
            cursor = cnxn.cursor()
            cursor.execute("INSERT INTO Favorite(UserName,Id_RentalProperty) VALUES (?, ?)",session['username'] ,Id)
            cnxn.commit()
            return redirect(f"/detail/{Id}")    
@app.route('/Review', methods=['POST'])
def review():
        username=session['username']
        id_rental = request.form['id_rental']
        rating = request.form['rating']
        comment = request.form['comment']
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM USERS WHERE UserName=?",username)
        user= cursor.fetchone()
        showname=user.nameshow
        cursor = cnxn.cursor()
        cursor.execute("INSERT INTO Reviews(UserName,Id_Rental,star,comment,TimeCreate,NameShow) VALUES (?, ?,?,?,?,?)",username,id_rental,rating,comment,datetime.now(),showname)
        cnxn.commit()
        return redirect(f"/detail/{id_rental}")   
@app.route('/Search', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        if 'username' in session:
            price1=0
            price2=0
            area1=0
            area2=0
            type = request.form['type']
            quan = request.form['location']
            price = request.form['price']
            area=request.form['area']
            if price=='0':
                price1=0
                price2=999999999999999
            if price=='1':
                price1=0
                price2=5000000
            if  price=='2':
                price1=5000000
                price2=10000000
            if price=='3':
                price1=10000000
                price2=20000000
            if price=='4':
                price1=20000000
                price2=99999999999
            
            if area=='0':
                area1=20
                area2=9999999999
            if area=='1':
                area1=20
                area2=30
            if area=='2':
                area1=30
                area2=40
            if area=='3':
                area1=40
                area2=60
            if area=='4':
                area1=60
                area2=80
            if area=='5':
                area1=80
                area2=99999999999
            
            if quan=="0":
                if type=="0":
                    cursor = cnxn.cursor()
                    cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE Status=? AND area>=? AND area<? AND price>=? AND price<? ORDER BY TimeCreate DESC", ("Còn",area1, area2, price1, price2))
                    rental_properties = cursor.fetchall()
                    rental_properties = sorted(rental_properties, key=lambda x: (x.Type_Post == 'VIP', x.Type_Post == 'MEDIUM', x.TimeCreate), reverse=True)
                    return render_template('Search.html',rental_properties=rental_properties,username=session['showname'],money=session['money'])
                else:
                    cursor = cnxn.cursor()
                    cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE Status=? AND area>=? AND area<? AND price>=? AND price<? AND type=? ORDER BY TimeCreate DESC","Còn",area1,area2,price1,price2,type)
                    rental_properties = cursor.fetchall()
                    rental_properties = sorted(rental_properties, key=lambda x: (x.Type_Post == 'VIP', x.Type_Post == 'MEDIUM', x.TimeCreate), reverse=True)
                    return render_template('Search.html',rental_properties=rental_properties,username=session['showname'],money=session['money'])
            else:
                if type=="0":
                    cursor = cnxn.cursor()
                    cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE Status=? AND area>=? AND area<? AND price>=? AND price<? AND district=? ORDER BY TimeCreate DESC","Còn",area1,area2,price1,price2,quan)
                    rental_properties = cursor.fetchall()
                    rental_properties = sorted(rental_properties, key=lambda x: (x.Type_Post == 'VIP', x.Type_Post == 'MEDIUM', x.TimeCreate), reverse=True)
                    return render_template('Search.html',rental_properties=rental_properties,username=session['showname'],money=session['money'])
                else:
                    cursor = cnxn.cursor()
                    cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE Status=? AND area>=? AND area<? AND price>=? AND price<? AND type=? AND district=? ORDER BY TimeCreate DESC","Còn",area1,area2,price1,price2,type,quan)
                    rental_properties = cursor.fetchall()
                    rental_properties = sorted(rental_properties, key=lambda x: (x.Type_Post == 'VIP', x.Type_Post == 'MEDIUM', x.TimeCreate), reverse=True)
                    return render_template('Search.html',rental_properties=rental_properties,username=session['showname'],money=session['money'])        
        else:
            price1=0
            price2=0
            area1=0
            area2=0
            type = request.form['type']
            quan = request.form['location']
            price = request.form['price']
            area=request.form['area']
            if price=='0':
                price1=0
                price2=999999999999999
            if price=='1':
                price1=0
                price2=5000000
            if  price=='2':
                price1=5000000
                price2=10000000
            if price=='3':
                price1=10000000
                price2=20000000
            if price=='4':
                price1=20000000
                price2=99999999999
            
            if area=='0':
                area1=20
                area2=9999999999
            if area=='1':
                area1=20
                area2=30
            if area=='2':
                area1=30
                area2=40
            if area=='3':
                area1=40
                area2=60
            if area=='4':
                area1=60
                area2=80
            if area=='5':
                area1=80
                area2=99999999999
            
            if quan=="0":
                if type=="0":
                    cursor = cnxn.cursor()
                    cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE Status=? AND area>=? AND area<? AND price>=? AND price<? ORDER BY TimeCreate DESC", ("Còn",area1, area2, price1, price2))
                    rental_properties = cursor.fetchall()
                    rental_properties = sorted(rental_properties, key=lambda x: (x.Type_Post == 'VIP', x.Type_Post == 'MEDIUM', x.TimeCreate), reverse=True)
                    return render_template('Search.html',rental_properties=rental_properties)
                else:
                    cursor = cnxn.cursor()
                    cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE Status=? AND area>=? AND area<? AND price>=? AND price<? AND type=? ORDER BY TimeCreate DESC","Còn",area1,area2,price1,price2,type)
                    rental_properties = cursor.fetchall()
                    rental_properties = sorted(rental_properties, key=lambda x: (x.Type_Post == 'VIP', x.Type_Post == 'MEDIUM', x.TimeCreate), reverse=True)
                    return render_template('Search.html',rental_properties=rental_properties)
            else:
                if type=="0":
                    cursor = cnxn.cursor()
                    cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE Status=? AND area>=? AND area<? AND price>=? AND price<? AND district=? ORDER BY TimeCreate DESC","Còn",area1,area2,price1,price2,quan)
                    rental_properties = cursor.fetchall()
                    rental_properties = sorted(rental_properties, key=lambda x: (x.Type_Post == 'VIP', x.Type_Post == 'MEDIUM', x.TimeCreate), reverse=True)
                    return render_template('Search.html',rental_properties=rental_properties)
                else:
                    cursor = cnxn.cursor()
                    cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE Status=? AND area>=? AND area<? AND price>=? AND price<? AND type=? AND district=? ORDER BY TimeCreate DESC","Còn",area1,area2,price1,price2,type,quan)
                    rental_properties = cursor.fetchall()
                    rental_properties = sorted(rental_properties, key=lambda x: (x.Type_Post == 'VIP', x.Type_Post == 'MEDIUM', x.TimeCreate), reverse=True)
                    return render_template('Search.html',rental_properties=rental_properties)        
    if 'username' in session:
        return render_template('Search.html',username=session['showname'],money=session['money'])
    else:
        return render_template('Search.html')
@app.route('/account', methods=['GET','POST'])
def ManageAccount():
    if request.method == 'POST':
        showname=request.form['name']
        number = request.form['number']
        url = "http://localhost:5001/UpdatebyUser"
        payload = {"username": session['username'],
                   "showname":showname,
                   "number":number
                }
        response=requests.post(url, json=payload)
        result=response.text
        if result=="Thành công":
            return render_template('manageAccount.html',username=session['showname'],nameshow=showname,number=number,success="Cập nhật thành công",money=session['money'])
    if 'username' in session:
        url = "http://localhost:5001/GetUserbyUserName"
        payload = {"username": session['username'],
                }
        response=requests.post(url, json=payload)
        data=response.json()
        nameshow=data['nameshow']
        number=data['number']
        return render_template('manageAccount.html',username=session['showname'],nameshow=nameshow,number=number,money=session['money'])
@app.route('/changePass', methods=['GET','POST'])
def changePass():
    if request.method == 'POST':
        if 'username' in session:
            old=request.form['old']
            new = request.form['new']
            confirm = request.form['confirm']
            url = "http://localhost:5001/UpdatePass"
            payload = {"username": session['username'],"old":old,"new":new,"confirm":confirm}
            response=requests.post(url, json=payload)
            data=response.text
            return render_template('password.html',username=session['showname'],data=data,money=session['money'])
    if 'username' in session:
        return render_template('password.html',username=session['showname'],money=session['money'])
@app.route('/favorite', methods=['GET'])
def favour():
    if 'username' in session:
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE UserName=? AND Status=? ORDER BY TimeCreate DESC", (session['username'],"Còn"))
        rentals=cursor.fetchall()
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM Favorite WHERE UserName=? ", (session['username']))
        favour=cursor.fetchall()
        
        # Lấy danh sách rentals có Id giống với Id_rental của favourite
        if len(favour) > 0:
            fav_ids = [f[2] for f in favour]  # lấy ra danh sách Id_rental từ bảng favourite
            fav_ids_str = ','.join('?'*len(fav_ids))  # tạo chuỗi phần tử cho câu lệnh IN
            cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE Id IN ({})".format(fav_ids_str), fav_ids)
            rentals = cursor.fetchall()
        return render_template('favorite.html',username=session['showname'],money=session['money'],lists=rentals)
    return redirect("/login")
@app.route('/post', methods=['GET','POST'])
def post():
    if request.method == 'POST':
        title = request.form['title']
        adress=request.form['address']
        district = request.form['location']
        price=request.form['price']
        description=request.form['description']
        type=request.form['type']
        type_post=request.form['type_post']
        area=request.form['area']
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM Users WHERE UserName=?",session['username'])
        user = cursor.fetchone()
        if type_post=='VIP':
            if int(user.money)<50000:
                return render_template('post.html',username=session['showname'],money=session['money'],message="Bạn không đủ tiền vui lòng nạp tiền vào hệ thống")
        elif type_post=='MEDIUM':
              if int(user.money)<30000:
                return render_template('post.html',username=session['showname'],money=session['money'],message="Bạn không đủ tiền vui lòng nạp tiền vào hệ thống")
        else:
              if int(user.money)<15000:
                return render_template('post.html',username=session['showname'],money=session['money'],message="Bạn không đủ tiền vui lòng nạp tiền vào hệ thống")
        
            # Lưu các file ảnh vào thư mục static
        images = []
        for i in range(1, 4):
            image = request.files.get(f'image{i}')
            if image:
                filename = f'{title}_image{i}.jpg'  # Tạo tên file mới
                image.save(os.path.join(app.root_path, 'static/images', filename))
                images.append(filename)
        image1=f'images/{title}_image1.jpg'
        image2=f'images/{title}_image2.jpg'
        image3=f'images/{title}_image3.jpg'
        url = "http://localhost:5001/GetNumber"
        payload = {"username": session['username']}
        response=requests.post(url, json=payload)
        number=response.text
        url = "http://localhost:5002/UpPost"
        payload = {"username": session['username'],
                   "title": title,
                   "address":adress,
                   "district":district,
                   "price":price,
                   "description":description,
                   "type":type,
                   "type_post":type_post,
                   "image1":image1,
                   "image2":image2,
                   "image3":image3,
                   "number":number,
                   "area":area
                   }
        response=requests.post(url, json=payload)
        price=response.text
        url = "http://localhost:5001/UpdateMoney"
        payload = {"username": session['username'],
                   "price":price}
        response=requests.post(url, json=payload)
        session['money']=response.text
        return redirect("/showtransaction")
        
        
    if 'username' in session:
        return render_template('post.html',username=session['showname'],money=session['money'])
    else:
        return redirect("/login")
    
@app.route('/recharge', methods=['GET','POST'])
def recharge():
    if request.method == 'POST':
        money = request.form['count']
        method=request.form['payment']
        url = "http://localhost:5003/payment"
        payload = {"username": session['username'],
                   "price":money,
                   "method":method
                }
        response=requests.post(url, json=payload)
        if method=="Thẻ":
            return render_template('the.html',username=session['showname'],money=session['money'],method=method)
        else:
            return render_template('the.html',username=session['showname'],money=session['money'],method=method)
    if 'username' in session:
        return render_template('recharge.html',username=session['showname'],money=session['money'])
@app.route('/showpayment', methods=['GET'])
def showpayment():
    if 'username' in session:
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM Payment WHERE username=? ",session['username'])
        payments= cursor.fetchall()
        return render_template('showpayment.html',username=session['showname'],money=session['money'],payments=payments)
@app.route('/listpost', methods=['GET'])
def listpost():
    if 'username' in session:
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE UserName=? AND Status=? OR Status=? ORDER BY TimeCreate DESC", (session['username'],"Còn","Hết"))
        rentals=cursor.fetchall()
        return render_template('MyRental.html',username=session['showname'],money=session['money'],rentals=rentals)
    else:
        return redirect("/login")
@app.route('/DeleteRental', methods=['POST'])
def deleteRental():
        id = request.form['rentalId']
        url = "http://localhost:5002/DeletePost"
        payload = {"id_rental": id,
                }
        response=requests.post(url, json=payload)
        cursor = cnxn.cursor()
        cursor.execute("DELETE FROM Favorite WHERE Id_RentalProperty = ?",int(id))
        cnxn.commit() 
        return redirect("/listpost")
@app.route('/showtransaction', methods=['GET'])
def showTran():
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM Transactions WHERE UserName=? ORDER BY TimeCreate DESC", (session['username']))
    tran=cursor.fetchall()
    return render_template('showtran.html',username=session['showname'],money=session['money'],trans=tran)
@app.route('/editRental/<Id>', methods=['GET','POST'])
def editTran(Id):
    if request.method=="POST":
        title=request.form['title']
        price=request.form['price']
        description=request.form['description']
        map=request.form['map']
        zalo=request.form['zalo']
        facebook=request.form['facebook']
        images = []
        if map=="None":
            map=''
        if zalo=="None":
           zalo=''
        if facebook=="None":
            facebook=''
        for i in range(1, 4):
            image = request.files.get(f'image{i}')
            if image:
                filename = f'{title}_image{i}.jpg'  # Tạo tên file mới
                image.save(os.path.join(app.root_path, 'static/images', filename))
                images.append(filename)
        image1=f'images/{title}_image1.jpg'
        image2=f'images/{title}_image2.jpg'
        image3=f'images/{title}_image3.jpg'
        url = "http://localhost:5002/UpdatePost"
        payload = {
                   "id": Id,
                   "price":price,
                   "description":description,
                   "map":map,
                   "zalo":zalo,
                   "image1":image1,
                   "image2":image2,
                   "image3":image3,
                   "facebook":facebook
                   }
        response=requests.post(url, json=payload)
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE Id=?" ,Id )
        property_rental=cursor.fetchone()
        return render_template('edittran.html',username=session['showname'],money=session['money'],rental_property=property_rental)
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE Id=?" ,Id )
    property_rental=cursor.fetchone()
    return render_template('edittran.html',username=session['showname'],money=session['money'],rental_property=property_rental)
@app.route('/UpdateStatusRental', methods=['POST'])
def updateStatus():
    Id=request.form['rentalId']
    status=request.form['status']
    url = "http://localhost:5002/UpdateStatus"
    status1=''
    if status=='Còn':
        status1='Hết'
    if status=='Hết':
        status1='Còn'
    payload = {
                   "Id": Id,
                   "status":status1,
                   }
    response=requests.post(url, json=payload)
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE UserName=? AND Status=? OR Status=? ORDER BY TimeCreate DESC", (session['username'],"Còn","Hết"))
    rentals=cursor.fetchall()
    return render_template('MyRental.html',username=session['showname'],money=session['money'],rentals=rentals)
@app.route('/Upgrade/<Id>', methods=['GET','POST'])
def upgrade(Id):
    if request.method=="POST":
        post=request.form['goi']
        url = "http://localhost:5002/Upgrade"
        payload = {
                   "Id": Id,
                   "Post":post,
                   }
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE Id=?", (Id))
        rental=cursor.fetchone()
        cursor = cnxn.cursor()
        cursor.execute("SELECT * FROM Users WHERE UserName=?",session['username'])
        user = cursor.fetchone()
        if post=='VIP' and rental.Type_Post=="MEDIUM":
                if int(user.money)<20000:
                    return render_template('upgrade.html',username=session['showname'],money=session['money'],post=rental.Type_Post,Id_rental=Id,message="Bạn không đủ tiền vui lòng nạp tiền vào hệ thống")
        elif post=='VIP' and rental.Type_Post=="NORMAL":
              if int(user.money)<35000:
                return render_template('upgrade.html',username=session['showname'],money=session['money'],post=rental.Type_Post,Id_rental=Id,message="Bạn không đủ tiền vui lòng nạp tiền vào hệ thống")
        else:
              if int(user.money)<15000:
                return render_template('upgrade.html',username=session['showname'],money=session['money'],post=rental.Type_Post,Id_rental=Id,message="Bạn không đủ tiền vui lòng nạp tiền vào hệ thống")
        response=requests.post(url, json=payload)
        price=response.text
        url = "http://localhost:5001/UpdateMoney"
        payload = {"username": session['username'],
                   "price":price}
        response=requests.post(url, json=payload)
        session['money']=response.text
        return redirect("/showtransaction")
        
        
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM RENTAL_PROPERTIES WHERE Id=?",Id)
    rental=cursor.fetchone()
    return render_template('upgrade.html',username=session['showname'],money=session['money'],post=rental.Type_Post,Id_rental=Id)
if __name__ == '__main__':
    app.run(port=5000, debug=True)
    