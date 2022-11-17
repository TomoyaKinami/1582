from flask import Flask, render_template,url_for,request,session,redirect,jsonify,g
import sqlite3

app=Flask(__name__)
app.secret_key=b'random_string'

def get_db(x,y):
    conn = sqlite3.connect(x)
    cur = conn.cursor()
    cur.execute('SELECT * FROM '+y)
    list=cur.fetchall()
    cur.close()
    conn.close()
    return list

def create_class(x):
    card_title=x[1]
    card_teacher=x[2]
    card_place=x[3]
    card_url=x[4]
    return '<div class="card" style="width:20rem;"><div class="card-body"><h5 class="card-title">'+card_title+'</h5><p class="card-text">担当教員:'+card_teacher+'</p><p class="card-text">教室:'+card_place+'</p><a href="class/'+card_url+'"><button class="btn btn-primary">参加</button></a></div></div>'

@app.route('/',methods=['GET'])
def index():
    if 'login' in session and session['login']:
        if session['license']:
            license_exist='Y'
        else:
            license_exist='N'
        msg='Login id:'+session['id']
        class_list=get_db('number.sqlite3','classes')
        class_list2=[]
        for i in range(0,len(class_list)):
            class_list2.append(create_class(class_list[i]))
        class_list3=''.join(class_list2)
        return render_template('home.html',\
            title='Home',\
                message=msg,\
                        class_list3=class_list3)
    else:
        return redirect('/login')

@app.route('/login',methods=['GET'])
def login(): 
    return render_template('login.html',\
    title='Login',\
    err='False',\
    message='IDとパスワードを入力:',\
    id='')

@app.route('/login',methods=['POST'])
def login_post():
    member=get_db('number.sqlite3','number')
    id=request.form.get('id')
    pswd=request.form.get('pass')
    for i in range(0,len(member)):
        if member[i][1]==id:
            key=i
            break
        else:
            session['login']=False
            key='None'
    if not key=='None':
        if member[key][2]==pswd:
            session['login']=True
            if member[key][3]=='Y':
                session['license']=True
            else:
                session['license']=False
        else:
            session['login']=False
    session['id']=id
    if session['login']:
        return redirect('/')
    else:
        return render_template('login.html',\
            title='Login',\
                err=False,\
                    message='idまたはpasswordが違います。',\
                        id=id)

@app.route('/logout',methods=['GET'])
def logout():
    session.pop('id',None)
    session.pop('login')
    return redirect('/login')

@app.route('/class/<class_name>',methods=['GET'])
def hello_world(class_name):
    license=session['license']
    url_list=[]
    class_list=get_db('number.sqlite3','classes')
    for i in range(0,len(class_list)):
        url_list.append(class_list[i][4])
    if not class_name in url_list:
        return redirect('/')
    for i in range(0,len(class_list)):
        if class_list[i][4]==class_name:
            key=i
            break
    status_list=get_db('number.sqlite3',class_name)
    for i in range(0,len(status_list)):
        if status_list[i][1]==session['id']:
            key2=i
            break
    if 'login' in session and session['login']:
        if session['license']:
            msg='こんにちは、'+session['id']+'さん。'
            msg2='あなたは今 '+class_list[key][1]+' の授業に参加しています。'
            msg3=status_list[key2][2]
            msg5='"'+class_list[key][4]+'"'
            return render_template('class_teacher.html',\
                title='class',\
                    message=msg,\
                        msg2=msg2,\
                            msg3=msg3,\
                                msg5=msg5)
        else:
            msg='こんにちは、'+session['id']+'さん。'
            msg2='あなたは今 '+class_list[key][1]+' の授業に参加しています。'
            msg3=status_list[key2][2]
            msg5='"'+class_list[key][4]+'"'
            return render_template('class.html',\
                title='class',\
                    message=msg,\
                        msg2=msg2,\
                            msg3=msg3,\
                                msg5=msg5)
    else:
        return redirect('/')

@app.route('/class/post',methods=['POST'])
def receive_status():
    newid2=str(session['id'])
    class_name=request.form.get("url")
    newstatus=request.form.get("status")
    conn = sqlite3.connect('number.sqlite3')
    cur = conn.cursor()
    cur.execute('UPDATE '+class_name+' SET status='+newstatus+' WHERE name="'+newid2+'"')
    conn.commit()
    cur.close()
    conn.close()
    return newstatus

if __name__=='__main__':
    app.debug=False
    app.run(host='localhost')