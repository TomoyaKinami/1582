from flask import Flask, render_template,url_for,request,session,redirect,jsonify,g
from datetime import timedelta,datetime
import sqlite3
import random


app=Flask(__name__)
app.secret_key=b'random_string'
app.permanent_session_lifetime = timedelta(days=5)

def get_db(x,y):
    conn = sqlite3.connect(x)
    cur = conn.cursor()
    cur.execute('SELECT * FROM '+y)
    list=cur.fetchall()
    cur.close()
    conn.close()
    return list

def create_display(x,y):
    s=x[1]
    t=x[3]
    u=x[4]
    z=str(x[0])
    return '<div class="col-lg-3 col-md-4 col-sm-6 mt-3"><div class="box" id="makeImg" style="width:fit-content; height:40px; background:#e2e2e2; border: 2px solid #000000; border-radius: 20px 20px 20px 20px; font-family:Meiryo UI;"><p style="margin-top:5px; margin-left:10px; margin-right: 10px; font-weight: bold;">'+s+'  <span class="badge bg-secondary text-light">'+t+'pt</span>  <a href="'+y+'/'+z+'"><button style="width:fit-content; height:19px; font-size:12px; font-weight:bold; color:white; border: 0px; margin:auto; background-color: #6c757d; border-radius: 5px 5px 5px 5px;">'+u+'回</button></a></p></div></div>'

def create_block(x,y):
    list3=[]
    for i in range(0,len(x)):
        list3.append(create_display(x[i],y))
    block1=''.join(list3)
    block2='<div class="row">'+block1+'</div>'
    return block2

def create_class(x):
    card_title=x[1]
    card_teacher=x[2]
    card_place=x[3]
    card_url=x[4]
    return '<div class="card" style="width:20rem;"><div class="card-body"><h5 class="card-title">'+card_title+'</h5><p class="card-text">担当教員:'+card_teacher+'</p><p class="card-text">教室:'+card_place+'</p><a href="class/'+card_url+'"><button class="btn btn-primary">参加</button></a></div></div>'

def create_html(x,y):
    list2=[]
    list4=[]
    for i in range(0,len(x)):
        if i%4==0:
            if i==0:
                newlist=[]
            else:
                list2.append(newlist)
                newlist=[]
            newlist.append(x[i])
            if i==len(x)-1:
                list2.append(newlist)
        else:
            newlist.append(x[i])
            if i==len(x)-1:
                list2.append(newlist)
    for i in range(0,len(list2)):
        list4.append(create_block(list2[i],y))
    html_block=''.join(list4)
    return html_block

def short_create(x,z):
    if len(x)==0:
        y="<p class='text-black font-weight-bold h6'>該当者なし</p>"
    else:
        y=create_html(x,z)
    return y

def random_create(list):
    random.shuffle(list)
    list2=sorted(list,key=lambda x:x[3])
    return list2

def short_random(x,z):
    if len(x)==0:
        y="<p class='text-black font-weight-bold h6'>該当者なし</p>"
    else:
        newlist=random_create(x)
        y=create_html(newlist,z)
    return y


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
    session['random1']=False
    session['random2']=False
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
    session.pop('random1')
    session.pop('random2')
    session.pop('license')
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
    if status_list[key2][2]=='0':
        conn = sqlite3.connect('number.sqlite3')
        cur = conn.cursor()
        cur.execute('UPDATE '+class_name+' SET status="1" WHERE name="'+session['id']+'"')
        conn.commit()
        cur.close()
        conn.close()
        status_list=get_db('number.sqlite3',class_name)
    if 'login' in session and session['login']:
        if session['license']:
            msg='こんにちは、'+session['id']+'さん。'
            msg2='あなたは今 '+class_list[key][1]+' の授業に参加しています。'
            msg3=status_list[key2][2]
            msg5='"'+class_list[key][4]+'"'
            list0=[]
            list1=[]
            list2=[]
            list3=[]
            list4=[]
            list5=[]
            for i in range(0,len(status_list)):
                if status_list[i][2]=='0':
                    list0.append(status_list[i])
                if status_list[i][2]=='1':
                    list1.append(status_list[i])
                if status_list[i][2]=='2':
                    list2.append(status_list[i])
                if status_list[i][2]=='3':
                    list3.append(status_list[i])
                if status_list[i][2]=='4':
                    list4.append(status_list[i])
                if status_list[i][2]=='5':
                    list5.append(status_list[i])
            if session['random1']==True:
                status1=short_random(list1,class_name)
                session['random1']=False
            else:
                status1=short_create(list1,class_name)
            if session['random2']==True:
                status2=short_random(list2,class_name)
                session['random2']=False
            else:
                status2=short_create(list2,class_name)
            status0=short_create(list0,class_name)
            status3=short_create(list3,class_name)
            status4=short_create(list4,class_name)
            status5=short_create(list5,class_name)
            return render_template('class_teacher.html',\
                title='class',\
                    message=msg,\
                        msg2=msg2,\
                            msg3=msg3,\
                                msg5=msg5,\
                                    status1=status1,\
                                        status2=status2,\
                                            status3=status3,\
                                                status4=status4,\
                                                    status5=status5,\
                                                        status0=status0)
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

@app.route('/class/<class_name>/random1',methods=['GET'])
def random1(class_name):
    session['random1']=True
    return redirect('/class/'+class_name)
    
@app.route('/class/<class_name>/random2',methods=['GET'])
def random2(class_name):
    session['random2']=True
    return redirect('/class/'+class_name)

@app.route('/class/<class_name>/startclass',methods=['GET'])
def startclass(class_name):
    url_list=[]
    if not session['login']==True:
        redirect('/login')
    if not session['license']==True:
        session.pop('id',None)
        session.pop('random1')
        session.pop('random2')
        session.pop('license')
        redirect('/login')
    class_list=get_db('number.sqlite3','classes')
    for i in range(0,len(class_list)):
        url_list.append(class_list[i][4])
    if not class_name in url_list:
        return redirect('/')
    status_list=get_db('number.sqlite3',class_name)
    id_list=[]
    for i in range(0,len(status_list)):
        id_list.append(str(status_list[i][0]))
    conn = sqlite3.connect('number.sqlite3')
    cur = conn.cursor()
    for i in range(0,len(id_list)):
        cur.execute('UPDATE '+class_name+' SET status="0" WHERE id='+id_list[i])
        cur.execute('UPDATE '+class_name+' SET point="0" WHERE id='+id_list[i])
        cur.execute('UPDATE '+class_name+' SET tell="0" WHERE id='+id_list[i])
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/class/'+class_name)

@app.route('/class/<class_name>/startvote',methods=['GET'])
def startvote(class_name):
    url_list=[]
    if not session['login']==True:
        redirect('/login')
    if not session['license']==True:
        session.pop('id',None)
        session.pop('random1')
        session.pop('random2')
        session.pop('license')
        redirect('/login')
    class_list=get_db('number.sqlite3','classes')
    for i in range(0,len(class_list)):
        url_list.append(class_list[i][4])
    if not class_name in url_list:
        return redirect('/')
    conn = sqlite3.connect('number.sqlite3')
    cur = conn.cursor()
    cur.execute('UPDATE '+class_name+' SET status=REPLACE(status,"1","5")')
    cur.execute('UPDATE '+class_name+' SET status=REPLACE(status,"2","5")')
    cur.execute('UPDATE '+class_name+' SET status=REPLACE(status,"3","5")')
    cur.execute('UPDATE '+class_name+' SET status=REPLACE(status,"4","5")')
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/class/'+class_name)

@app.route('/class/<class_name>/finishvote',methods=['GET'])
def finishvote(class_name):
    url_list=[]
    if not session['login']==True:
        redirect('/login')
    if not session['license']==True:
        session.pop('id',None)
        session.pop('random1')
        session.pop('random2')
        session.pop('license')
        redirect('/login')
    class_list=get_db('number.sqlite3','classes')
    for i in range(0,len(class_list)):
        url_list.append(class_list[i][4])
    if not class_name in url_list:
        return redirect('/')
    status_list=get_db('number.sqlite3',class_name)
    list0=[]
    for i in range(0,len(status_list)):
        list0.append(list(status_list[i]))
    list1=[]
    list2=[]
    for i in range(0,len(list0)):
        if list0[i][2]=='1':
            list1.append(list0[i])
        if list0[i][2]=='2':
            list2.append(list0[i])
    for i in range(0,len(list1)):
        original=float(list1[i][3])
        new=original+1.0
        list1[i][3]=str(new)
        original2=list1[i][0]
        list1[i][0]=str(original2)
    for i in range(0,len(list2)):
        original=float(list2[i][3])
        new=original+0.5
        list2[i][3]=str(new)
        original2=list2[i][0]
        list2[i][0]=str(original2)
    conn = sqlite3.connect('number.sqlite3')
    cur = conn.cursor()
    for i in range(0,len(list1)):
        cur.execute('UPDATE '+class_name+' SET point='+list1[i][3]+' WHERE id='+list1[i][0])
    for i in range(0,len(list2)):
        cur.execute('UPDATE '+class_name+' SET point='+list2[i][3]+' WHERE id='+list2[i][0])
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/class/'+class_name)

@app.route('/class/<class_name>/<number>',methods=['GET'])
def tell(class_name,number):
    url_list=[]
    if not session['login']==True:
        redirect('/login')
    if not session['license']==True:
        session.pop('id',None)
        session.pop('random1')
        session.pop('random2')
        session.pop('license')
        redirect('/login')
    class_list=get_db('number.sqlite3','classes')
    for i in range(0,len(class_list)):
        url_list.append(class_list[i][4])
    if not class_name in url_list:
        return redirect('/')
    status_list=get_db('number.sqlite3',class_name)
    list1=[]
    list1.append(number)
    for i in range(0,len(status_list)):
        if status_list[i][0]==int(number):
            original=int(status_list[i][4])
            new=original+1
            list1.append(str(new))
            break
    conn = sqlite3.connect('number.sqlite3')
    cur = conn.cursor()
    cur.execute('UPDATE '+class_name+' SET tell="'+list1[1]+'" WHERE id='+list1[0])
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/class/'+class_name)

if __name__=='__main__':
    app.debug=False
    app.run(host='localhost')