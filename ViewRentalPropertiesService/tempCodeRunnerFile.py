
                }
        response=requests.post(url, json=payload)
        if method=="Thẻ":
            return render_template('the.html',username=session['showname'],money=session['money'],method=method)
        else: