from flask import Flask, render_template,url_for,request,session,redirect,jsonify,g
from datetime import timedelta,datetime
import sqlite3
import random
import pickle
import os
import time
import werkzeug



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

def db_exists(x,y):
    conn = sqlite3.connect(x)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE TYPE='table' AND name='"+y+"'")
    list=cur.fetchall()
    cur.close()
    conn.close()
    return list[0][0]

def block(x):
    list2=[]
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
    return list2

def random_create(list):
    if len(list)==0:
        return list
    else:
        random.shuffle(list)
        list2=sorted(list,key=lambda x:x[3])
        return list2

@app.before_request
def func():
    session.modified=True

@app.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request(e):
    return redirect('/')

@app.errorhandler(404) # 404エラーが発生した場合の処理
def error_404(e):
    return redirect('/')

@app.errorhandler(500) # 500エラーが発生した場合の処理
def error_500(e):
    return redirect('/')

@app.route('/',methods=['GET'])
def index():
    if 'login' in session and session['login']:
        if 'license' in session and session['license']:
            msg=session['id']+'先生'
        else:
            msg=session['id']+'さん' 
        class_list=get_db('number.sqlite3','classes')
        msg2=[]
        for i in range(0,len(class_list)):
            msg2.append(list(class_list[i]))
        color_list=['rgb(0, 234, 255)','rgb(162, 255, 0)','rgb(111, 0, 255)','rgb(255, 0, 17)','rgb(255, 242, 0)']
        for i in range(0,len(msg2)):
            msg2[i][4]='class/'+class_list[i][4]
            msg2[i].append(color_list[random.randrange(len(color_list))])
        return render_template('home.html',\
                message=msg,\
                            msg4=msg2,\
                                msg2=msg2)
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

@app.route('/setting',methods=['GET'])
def setting():
    if 'login' in session and session['login']:
        if 'license' in session and session['license']:
            msg=session['id']+'先生'
        else:
            msg=session['id']+'さん' 
        class_list=get_db('number.sqlite3','classes')
        msg2=[]
        msg3='パスワードの変更'
        for i in range(0,len(class_list)):
            msg2.append(list(class_list[i]))
        for i in range(0,len(msg2)):
            msg2[i][4]='class/'+class_list[i][4]
        return render_template('setting.html',\
                message=msg,\
                    msg3=msg3,\
                        err='1',\
                            msg4=msg2)
    else:
        return redirect('/login')

@app.route('/setting',methods=['POST'])
def accountchange():
    if 'login' in session and session['login']:
        member=get_db('number.sqlite3','number')
        for i in range(0,len(member)):
            if member[i][1]==session['id']:
                key=i
                break
            else:
                key='None'
        if not key=='None':
            try:
                oldpswd=request.form.get('oldpass')
                newpswd=request.form.get('newpass')
                newpswdagain=request.form.get('newpassagain')
                if newpswd==newpswdagain:
                    if member[key][2]==oldpswd:
                        conn = sqlite3.connect('number.sqlite3')
                        cur = conn.cursor()
                        cur.execute('UPDATE number SET pswd="'+newpswd+'" WHERE number="'+session['id']+'"')
                        conn.commit()
                        cur.close()
                        conn.close()
                        msg3='パスワード変更しました。'
                        err='2'
                    else:
                        msg3='現在のパスワードが違います。'
                        err='0'
                else:
                    msg3='新しいパスワードと再入力パスワードが一致しません。' 
                    err='0'
            except:
                msg3='パスワードの変更'
                err='1'
                pass
            if 'license' in session and session['license']:
                msg=session['id']+'先生'
            else:
                msg=session['id']+'さん' 
            class_list=get_db('number.sqlite3','classes')
            msg2=[]
            for i in range(0,len(class_list)):
                msg2.append(list(class_list[i]))
            for i in range(0,len(msg2)):
                msg2[i][4]='class/'+class_list[i][4]
            return render_template('setting.html',\
                    message=msg,\
                        msg3=msg3,\
                            err=err,\
                                msg4=msg2)
        else:
            return ('/logout')
    else:
        return redirect('/login')

@app.route('/logout',methods=['GET'])
def logout():
    session.pop('id',None)
    session.pop('login')
    session.pop('random1')
    session.pop('random2')
    session.pop('license')
    session.pop('warning')
    return redirect('/login')

@app.route('/class/<class_name>',methods=['GET'])
def hello_world(class_name):
    if session['login']==True:
        url_list=[]
        class_list=get_db('number.sqlite3','classes')
        for i in range(0,len(class_list)):
            url_list.append(class_list[i][4])
        if class_name in url_list:
            for i in range(0,len(class_list)):
                if class_list[i][4]==class_name:
                    key=i
                    break
            status_list=get_db('number.sqlite3',class_name)
            for i in range(0,len(status_list)):
                if status_list[i][1]==session['id']:
                    key2=i
                    break
                else:
                    key2=0
            current=time.time()
            conn = sqlite3.connect('number.sqlite3')
            cur = conn.cursor()
            cur.execute('UPDATE '+class_name+' SET time="'+str(current)+'" WHERE name="'+session['id']+'"')
            conn.commit()
            cur.close()
            conn.close()
            for i in range(0,len(class_list)):
                if class_list[i][4]==class_name:
                    if not class_list[i][6]=='0':
                        if status_list[key2][2]=='0':
                            conn = sqlite3.connect('number.sqlite3')
                            cur = conn.cursor()
                            cur.execute('UPDATE '+class_name+' SET status="1" WHERE name="'+session['id']+'"')
                            cur.execute('UPDATE '+class_name+' SET time="'+str(current)+'" WHERE name="'+session['id']+'"')
                            conn.commit()
                            cur.close()
                            conn.close()
            status_list=get_db('number.sqlite3',class_name)
            form_list=get_db('number.sqlite3',class_name+'_form')
            color_list=['rgb(0, 234, 255)','rgb(162, 255, 0)','rgb(111, 0, 255)','rgb(255, 0, 17)','rgb(255, 242, 0)']
            if 'login' in session and session['login']:
                if session['license']:
                    for i in range(0,len(class_list)):
                        if class_list[i][4]==class_name:
                            if not class_list[i][6]=='0':
                                timelist=[]
                                syncro=True
                                for i in range(0,len(status_list)):
                                    if status_list[i][5]==None:
                                        continue
                                    elif float(status_list[i][5])<=float(current-1800):
                                        timelist.append(status_list[i][0])
                                conn = sqlite3.connect('number.sqlite3')
                                cur = conn.cursor()
                                cur.execute('UPDATE classes SET time="'+str(current)+'" WHERE url="'+class_name+'"')
                                for i in range(0,len(timelist)):
                                    cur.execute('UPDATE '+class_name+' SET status="0" WHERE id='+str(timelist[i]))
                                conn.commit()
                                cur.close()
                                conn.close()
                                break
                            else:
                                syncro=False
                                break    
                    msg=session['id']+'先生'
                    msg2=class_list[key][1]
                    msg5='"'+class_list[key][4]+'"'
                    class_list.remove(class_list[key])
                    msg4=class_list
                    list0=[]
                    list1=[]
                    list2=[]
                    list3=[]
                    list4=[]
                    list5=[]
                    newstatus_list=[]
                    for i in range(0,len(status_list)):
                        newstatus_list.append(list(status_list[i]))
                    for i in range(0,len(newstatus_list)):
                        url=class_name+'/'+str(newstatus_list[i][0])
                        newstatus_list[i].append(url)
                    for i in range(0,len(newstatus_list)):
                        if newstatus_list[i][2]=='0':
                            list0.append(newstatus_list[i])
                        if newstatus_list[i][2]=='1':
                            list1.append(newstatus_list[i])
                        if newstatus_list[i][2]=='2':
                            list2.append(newstatus_list[i])
                        if newstatus_list[i][2]=='3':
                            list3.append(newstatus_list[i])
                        if newstatus_list[i][2]=='4':
                            list4.append(newstatus_list[i])
                        if newstatus_list[i][2]=='5':
                            list5.append(newstatus_list[i])
                    if session['random1']==True:
                        file1='cache/'+class_name+'_random1.dat'
                        try:
                            with open(file1,'rb') as f:
                                oldlist1=pickle.load(f)
                            partial_list1=[]
                            for i in range(0,len(list1)):
                                partial_list1.append(list1[i][0])
                            list1_update1=set(oldlist1)-set(partial_list1)
                            list1_update2=set(partial_list1)-set(oldlist1)
                            for i in range(0,len(list1_update1)):
                                for t in range(0,len(oldlist1)):
                                    if oldlist1[t]==list1_update1[i]:
                                        oldlist1.remove(oldlist1[t])
                            oldlist1.extend(list1_update2)
                            newlist1=[]
                            for t in range(0,len(oldlist1)):
                                for i in range(0,len(list1)):
                                    if list1[i][0]==oldlist1[t]:
                                        newlist1.append(list1[i])
                            status1=block(newlist1)
                        except:
                            newlist1=random_create(list1)
                            newnewlist1=[]
                            status1=block(newlist1)
                            for i in range(0,len(newlist1)):
                                newnewlist1.append(newlist1[i][0])
                            try:
                                with open(file1,'wb') as f:
                                    pickle.dump(newnewlist1,f)
                            except:
                                pass
                    else:
                        status1=block(list1)
                    if session['random2']==True:
                        file2='cache/'+class_name+'_random2.dat'
                        try:
                            with open(file2,'rb') as f:
                                oldlist2=pickle.load(f)
                            partial_list2=[]
                            for i in range(0,len(list2)):
                                partial_list2.append(list2[i][0])
                            list2_update1=set(oldlist2)-set(partial_list2)
                            list2_update2=set(partial_list2)-set(oldlist2)
                            for i in range(0,len(list2_update1)):
                                for t in range(0,len(oldlist2)):
                                    if oldlist2[t]==list2_update1[i]:
                                        oldlist2.remove(oldlist2[t])
                            oldlist2.extend(list2_update2)
                            newlist2=[]
                            for t in range(0,len(oldlist2)):
                                for i in range(0,len(list2)):
                                    if list2[i][0]==oldlist2[t]:
                                        newlist2.append(list2[i])
                            status2=block(newlist2)
                        except:
                            newlist2=random_create(list2)
                            newnewlist2=[]
                            status2=block(newlist2)
                            for i in range(0,len(newlist2)):
                                newnewlist2.append(newlist2[i][0])
                            try:
                                with open(file2,'wb') as f:
                                    pickle.dump(newnewlist2,f)
                            except:
                                pass
                    else:
                        status2=block(list2)
                    class_list=get_db('number.sqlite3','classes')
                    for i in range(0,len(class_list)):
                        if class_list[i][4]==class_name:
                            choice=class_list[i][6]
                    status0=block(list0)
                    status3=block(list3)
                    status4=block(list4)
                    status5=block(list5)
                    url1=class_name
                    warning=False
                    form=True
                    if 'warning' in session and session['warning']:
                        warning=True
                        session.pop('warning')
                    if len(form_list)==0:
                        form=False
                        return render_template('class_teacher.html',\
                            title='class',\
                                message=msg,\
                                    msg2=msg2,\
                                        warning=warning,\
                                            syncro=syncro,\
                                                status1=status1,\
                                                    status2=status2,\
                                                        status3=status3,\
                                                            status4=status4,\
                                                                status5=status5,\
                                                                    status0=status0,\
                                                                        choice=choice,\
                                                                            msg4=msg4,\
                                                                                url1=url1,\
                                                                                    form=form)
                    else:
                        newform_list=[]
                        for i in range(0,len(form_list)):
                            newform_list.append(list(form_list[i]))
                            newform_list[i].append(color_list[random.randrange(len(color_list))])
                            if newform_list[i][3]=='1':
                                newform_list[i][3]='ラジオボタン'
                            if newform_list[i][3]=='2':
                                newform_list[i][3]='チェックボックス'
                            if newform_list[i][3]=='3':
                                newform_list[i][3]='自由回答'
                        return render_template('class_teacher.html',\
                            title='class',\
                                message=msg,\
                                    msg2=msg2,\
                                        warning=warning,\
                                            syncro=syncro,\
                                                status1=status1,\
                                                    status2=status2,\
                                                        status3=status3,\
                                                            status4=status4,\
                                                                status5=status5,\
                                                                    status0=status0,\
                                                                        choice=choice,\
                                                                            msg4=msg4,\
                                                                                url1=url1,\
                                                                                    form=form,\
                                                                                        newform_list=newform_list)
                else:
                    url1=class_name
                    msg=session['id']+'さん'
                    msg2=class_list[key][1]
                    class_list.remove(class_list[key])
                    msg4=class_list
                    class_list=get_db('number.sqlite3','classes')
                    for i in range(0,len(class_list)):
                        if class_list[i][4]==class_name:
                            if not class_list[i][6]=='0':
                                msg3=status_list[key2][2]
                            else:
                                db_name=class_name+'2'
                                if db_exists('number.sqlite3',db_name):
                                    status_list=get_db('number.sqlite3',db_name)
                                    if status_list[key2][2]=='0':
                                        conn = sqlite3.connect('number.sqlite3')
                                        cur = conn.cursor()
                                        cur.execute('UPDATE '+db_name+' SET status="1" WHERE name="'+session['id']+'"')
                                        conn.commit()
                                        cur.close()
                                        conn.close()
                                    status_list=get_db('number.sqlite3',db_name)
                                    msg3=status_list[key2][2]
                    msg5=class_name
                    form=True
                    if len(form_list)==0:
                        form=False
                        return render_template('class.html',\
                            title='class',\
                                message=msg,\
                                    msg2=msg2,\
                                        msg3=msg3,\
                                            msg5=msg5,\
                                                msg4=msg4,\
                                                    form=form,\
                                                        url1=url1,\
                                                            afterclass=False)
                    else:
                        newform_list=[]
                        formform=[]
                        for i in range(0,len(form_list)):
                            newform_list.append(list(form_list[i]))
                            newform_list[i].append(color_list[random.randrange(len(color_list))])
                            if newform_list[i][3]=='1':
                                newform_list[i][3]='ラジオボタン'
                                file1='cache/'+class_name+'_form'+str(i+1)+'.dat'
                                try:
                                    with open(file1,'rb') as f:
                                        branch=pickle.load(f)
                                except:
                                    pass
                                newform_list[i].append(branch)
                            if newform_list[i][3]=='2':
                                newform_list[i][3]='チェックボックス'
                                file1='cache/'+class_name+'_form'+str(i+1)+'.dat'
                                try:
                                    with open(file1,'rb') as f:
                                        branch=pickle.load(f)
                                except:
                                    pass
                                newform_list[i].append(branch)
                            if newform_list[i][3]=='3':
                                newform_list[i][3]='自由回答'
                                newform_list[i].append('7')
                            formform.append(class_name+'_form'+str(i+1))
                        for i in range(0,len(formform)):
                            formal=get_db('number.sqlite3',formform[i])
                            for x in range(0,len(formal)):
                                if formal[x][1]==session['id']:
                                    if formal[x][2]=='0':
                                        newform_list[i].append('0')
                                    if formal[x][2]=='1':
                                        newform_list[i].append('1')
                                    break
                        for i in range(0,len(class_list)):
                            if class_list[i][4]==class_name:
                                if class_list[i][6]=='0':
                                    return render_template('class.html',\
                                        title='class',\
                                            message=msg,\
                                                msg2=msg2,\
                                                    msg3=msg3,\
                                                        msg5=msg5,\
                                                            msg4=msg4,\
                                                                form=False,\
                                                                    newform_list=newform_list,\
                                                                        url1=url1,\
                                                                            afterclass=True)
                                else:
                                    return render_template('class.html',\
                                                    title='class',\
                                                        message=msg,\
                                                            msg2=msg2,\
                                                                msg3=msg3,\
                                                                    msg5=msg5,\
                                                                        msg4=msg4,\
                                                                            form=form,\
                                                                                newform_list=newform_list,\
                                                                                    url1=url1,\
                                                                                        afterclass=False)
        else:
            return redirect('/')
    else:
        return redirect('/login')

@app.route('/class/<class_name>/post1',methods=['GET'])
def receive_status1(class_name):
    newid2=str(session['id'])
    class_list=get_db('number.sqlite3','classes')
    for i in range(0,len(class_list)):
        if class_list[i][4]==class_name:
            if not class_list[i][6]=='0':
                conn = sqlite3.connect('number.sqlite3')
                cur = conn.cursor()
                cur.execute('UPDATE '+class_name+' SET status=1 WHERE name="'+newid2+'"')
                conn.commit()
                cur.close()
                conn.close()
                return redirect('/class/'+class_name)
            else:
                db_name=class_name+'2'
                if db_exists('number.sqlite3',db_name):
                    conn = sqlite3.connect('number.sqlite3')
                    cur = conn.cursor()
                    cur.execute('UPDATE '+db_name+' SET status=1 WHERE name="'+newid2+'"')
                    conn.commit()
                    cur.close()
                    conn.close()
                return  redirect('/class/'+class_name)

@app.route('/class/<class_name>/post2',methods=['GET'])
def receive_status2(class_name):
    newid2=str(session['id'])
    class_list=get_db('number.sqlite3','classes')
    for i in range(0,len(class_list)):
        if class_list[i][4]==class_name:
            if not class_list[i][6]=='0':
                conn = sqlite3.connect('number.sqlite3')
                cur = conn.cursor()
                cur.execute('UPDATE '+class_name+' SET status=2 WHERE name="'+newid2+'"')
                conn.commit()
                cur.close()
                conn.close()
                return redirect('/class/'+class_name)
            else:
                db_name=class_name+'2'
                if db_exists('number.sqlite3',db_name):
                    conn = sqlite3.connect('number.sqlite3')
                    cur = conn.cursor()
                    cur.execute('UPDATE '+db_name+' SET status=2 WHERE name="'+newid2+'"')
                    conn.commit()
                    cur.close()
                    conn.close()
                return  redirect('/class/'+class_name)  

@app.route('/class/<class_name>/post3',methods=['GET'])
def receive_status3(class_name):
    newid2=str(session['id'])
    class_list=get_db('number.sqlite3','classes')
    for i in range(0,len(class_list)):
        if class_list[i][4]==class_name:
            if not class_list[i][6]=='0':
                conn = sqlite3.connect('number.sqlite3')
                cur = conn.cursor()
                cur.execute('UPDATE '+class_name+' SET status=3 WHERE name="'+newid2+'"')
                conn.commit()
                cur.close()
                conn.close()
                return redirect('/class/'+class_name)
            else:
                db_name=class_name+'2'
                if db_exists('number.sqlite3',db_name):
                    conn = sqlite3.connect('number.sqlite3')
                    cur = conn.cursor()
                    cur.execute('UPDATE '+db_name+' SET status=3 WHERE name="'+newid2+'"')
                    conn.commit()
                    cur.close()
                    conn.close()
                return  redirect('/class/'+class_name) 

@app.route('/class/<class_name>/post4',methods=['GET'])
def receive_status4(class_name):
    newid2=str(session['id'])
    class_list=get_db('number.sqlite3','classes')
    for i in range(0,len(class_list)):
        if class_list[i][4]==class_name:
            if not class_list[i][6]=='0':
                conn = sqlite3.connect('number.sqlite3')
                cur = conn.cursor()
                cur.execute('UPDATE '+class_name+' SET status=4 WHERE name="'+newid2+'"')
                conn.commit()
                cur.close()
                conn.close()
                return redirect('/class/'+class_name)
            else:
                db_name=class_name+'2'
                if db_exists('number.sqlite3',db_name):
                    conn = sqlite3.connect('number.sqlite3')
                    cur = conn.cursor()
                    cur.execute('UPDATE '+db_name+' SET status=4 WHERE name="'+newid2+'"')
                    conn.commit()
                    cur.close()
                    conn.close()
                return  redirect('/class/'+class_name)  

@app.route('/class/<class_name>/correct',methods=['GET'])
def correct(class_name):
                    file3='cache/'+class_name+'_correct.dat'
                    status_list=get_db('number.sqlite3',class_name)
                    list0=[]
                    list1=[]
                    list2=[]
                    list3=[]
                    list4=[]
                    list5=[]
                    newstatus_list=[]
                    for i in range(0,len(status_list)):
                        newstatus_list.append(list(status_list[i]))
                    for i in range(0,len(newstatus_list)):
                        url=class_name+'/'+str(newstatus_list[i][0])
                        newstatus_list[i].append(url)
                    for i in range(0,len(newstatus_list)):
                        if newstatus_list[i][2]=='0':
                            list0.append(newstatus_list[i])
                        if newstatus_list[i][2]=='1':
                            list1.append(newstatus_list[i])
                        if newstatus_list[i][2]=='2':
                            list2.append(newstatus_list[i])
                        if newstatus_list[i][2]=='3':
                            list3.append(newstatus_list[i])
                        if newstatus_list[i][2]=='4':
                            list4.append(newstatus_list[i])
                        if newstatus_list[i][2]=='5':
                            list5.append(newstatus_list[i])
                    if session['random1']==True:
                        file1='cache/'+class_name+'_random1.dat'
                        try:
                            with open(file1,'rb') as f:
                                oldlist1=pickle.load(f)
                            partial_list1=[]
                            for i in range(0,len(list1)):
                                partial_list1.append(list1[i][0])
                            list1_update1=set(oldlist1)-set(partial_list1)
                            list1_update2=set(partial_list1)-set(oldlist1)
                            for i in range(0,len(list1_update1)):
                                for t in range(0,len(oldlist1)):
                                    if oldlist1[t]==list1_update1[i]:
                                        oldlist1.remove(oldlist1[t])
                            oldlist1.extend(list1_update2)
                            newlist1=[]
                            for t in range(0,len(oldlist1)):
                                for i in range(0,len(list1)):
                                    if list1[i][0]==oldlist1[t]:
                                        newlist1.append(list1[i])
                            status1=block(newlist1)
                        except:
                            newlist1=random_create(list1)
                            newnewlist1=[]
                            status1=block(newlist1)
                            for i in range(0,len(newlist1)):
                                newnewlist1.append(newlist1[i][0])
                            try:
                                with open(file1,'wb') as f:
                                    pickle.dump(newnewlist1,f)
                            except:
                                pass
                    else:
                        status1=block(list1)
                    if session['random2']==True:
                        file2='cache/'+class_name+'_random2.dat'
                        try:
                            with open(file2,'rb') as f:
                                oldlist2=pickle.load(f)
                            partial_list2=[]
                            for i in range(0,len(list2)):
                                partial_list2.append(list2[i][0])
                            list2_update1=set(oldlist2)-set(partial_list2)
                            list2_update2=set(partial_list2)-set(oldlist2)
                            for i in range(0,len(list2_update1)):
                                for t in range(0,len(oldlist2)):
                                    if oldlist2[t]==list2_update1[i]:
                                        oldlist2.remove(oldlist2[t])
                            oldlist2.extend(list2_update2)
                            newlist2=[]
                            for t in range(0,len(oldlist2)):
                                for i in range(0,len(list2)):
                                    if list2[i][0]==oldlist2[t]:
                                        newlist2.append(list2[i])
                            status2=block(newlist2)
                        except:
                            newlist2=random_create(list2)
                            newnewlist2=[]
                            status2=block(newlist2)
                            for i in range(0,len(newlist2)):
                                newnewlist2.append(newlist2[i][0])
                            try:
                                with open(file2,'wb') as f:
                                    pickle.dump(newnewlist2,f)
                            except:
                                pass
                    else:
                        status2=block(list2)
                    status0=block(list0)
                    status3=block(list3)
                    status4=block(list4)
                    status5=block(list5)
                    url1=class_name
                    allstatus=[]
                    allstatus.append(status0)
                    allstatus.append(status1)
                    allstatus.append(status2)
                    allstatus.append(status3)
                    allstatus.append(status4)
                    allstatus.append(status5)
                    try:
                        with open(file3,'rb') as f:
                            judge=pickle.load(f)
                            if allstatus==judge:
                                return('True')
                    except:
                        pass
                    try:
                        with open(file3,'wb') as f:
                            pickle.dump(allstatus,f)
                    except:
                        pass
                    return render_template('block.html',\
                                            status1=status1,\
                                                status2=status2,\
                                                    status3=status3,\
                                                        status4=status4,\
                                                            status5=status5,\
                                                                status0=status0,\
                                                                            url1=url1)
    

@app.route('/class/<class_name>/random1',methods=['GET'])
def random1(class_name):
    if session['login']==True:
        if 'license' in session:
            if session['license']==True:
                url_list=[]
                class_list=get_db('number.sqlite3','classes')
                for i in range(0,len(class_list)):
                    url_list.append(class_list[i][4])
                if class_name in url_list:
                    file='cache/'+class_name+'_random1.dat'
                    if os.path.exists(file):
                        os.remove(file)
                    session['random1']=True
                    return redirect('/class/'+class_name)
                else:
                    return redirect('/')
            else:
                return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/')
    
@app.route('/class/<class_name>/random2',methods=['GET'])
def random2(class_name):
    if session['login']==True:
        if 'license' in session:
            if session['license']==True:
                url_list=[]
                class_list=get_db('number.sqlite3','classes')
                for i in range(0,len(class_list)):
                    url_list.append(class_list[i][4])
                if class_name in url_list:
                    file='cache/'+class_name+'_random2.dat'
                    if os.path.exists(file):
                        os.remove(file)
                    session['random2']=True
                    return redirect('/class/'+class_name)
                else:
                    return redirect('/')
            else:
                return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/class/<class_name>/startclass',methods=['GET'])
def startclass(class_name):
    if session['login']==True:
        if 'license' in session:
            if session['license']==True:
                url_list=[]
                class_list=get_db('number.sqlite3','classes')
                for i in range(0,len(class_list)):
                    url_list.append(class_list[i][4])
                if class_name in url_list:
                    status_list=get_db('number.sqlite3',class_name)
                    id_list=[]
                    for i in range(0,len(status_list)):
                        id_list.append(str(status_list[i][0]))
                    form_list=get_db('number.sqlite3',class_name+'_form')
                    conn = sqlite3.connect('number.sqlite3')
                    cur = conn.cursor()
                    for i in range(0,len(id_list)):
                        cur.execute('UPDATE '+class_name+' SET status="0" WHERE id='+id_list[i])
                        cur.execute('UPDATE '+class_name+' SET point="0" WHERE id='+id_list[i])
                        cur.execute('UPDATE '+class_name+' SET tell="0" WHERE id='+id_list[i])
                    cur.execute('UPDATE classes SET status="1" WHERE url="'+class_name+'"')
                    cur.execute('DROP TABLE '+class_name+'_form')
                    for i in range(0,len(form_list)):
                        cur.execute('DROP TABLE '+class_name+'_form'+str(i+1))
                    cur.execute('CREATE TABLE "'+class_name+'_form" ("id"	INTEGER NOT NULL UNIQUE,"url"	NUMERIC NOT NULL UNIQUE,"sentence"	TEXT NOT NULL,"style"	TEXT NOT NULL,PRIMARY KEY("id" AUTOINCREMENT))')
                    conn.commit()
                    cur.close()
                    conn.close()
                    file='cache/'+class_name+'_random1.dat'
                    file2='cache/'+class_name+'_random2.dat'
                    if os.path.exists(file):
                        os.remove(file)
                    if os.path.exists(file2):
                        os.remove(file2)
                    return redirect('/class/'+class_name)
            else:
                return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/class/<class_name>/startvote',methods=['GET'])
def startvote(class_name):
    if session['login']==True:
        if 'license' in session:
            if session['license']==True:
                url_list=[]
                class_list=get_db('number.sqlite3','classes')
                for i in range(0,len(class_list)):
                    url_list.append(class_list[i][4])
                if class_name in url_list:
                    for i in range(0,len(class_list)):
                        if class_list[i][4]==class_name:
                            if not class_list[i][6]=='0':
                                conn = sqlite3.connect('number.sqlite3')
                                cur = conn.cursor()
                                cur.execute('UPDATE '+class_name+' SET status=REPLACE(status,"1","5")')
                                cur.execute('UPDATE '+class_name+' SET status=REPLACE(status,"2","5")')
                                cur.execute('UPDATE '+class_name+' SET status=REPLACE(status,"3","5")')
                                cur.execute('UPDATE '+class_name+' SET status=REPLACE(status,"4","5")')
                                cur.execute('UPDATE classes SET status="2" WHERE url="'+class_name+'"')
                                conn.commit()
                                cur.close()
                                conn.close()
                                file='cache/'+class_name+'_random1.dat'
                                file2='cache/'+class_name+'_random2.dat'
                                if os.path.exists(file):
                                    os.remove(file)
                                if os.path.exists(file2):
                                    os.remove(file2)
                                return redirect('/class/'+class_name)
                            else:
                                return redirect('/class/'+class_name)
                else:
                    return redirect('/')
            else:
                return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/')
    

@app.route('/class/<class_name>/finishvote',methods=['GET'])
def finishvote(class_name):
    url_list=[]
    if session['login']==True:
        if 'license' in session:
            if session['license']==True:
                class_list=get_db('number.sqlite3','classes')
                for i in range(0,len(class_list)):
                    url_list.append(class_list[i][4])
                if class_name in url_list:
                    for i in range(0,len(class_list)):
                        if class_list[i][4]==class_name:
                            if not class_list[i][6]=='0':
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
                                    original=int(list1[i][3])
                                    new=original+2
                                    list1[i][3]=str(new)
                                    original2=list1[i][0]
                                    list1[i][0]=str(original2)
                                for i in range(0,len(list2)):
                                    original=int(list2[i][3])
                                    new=original+1
                                    list2[i][3]=str(new)
                                    original2=list2[i][0]
                                    list2[i][0]=str(original2)
                                conn = sqlite3.connect('number.sqlite3')
                                cur = conn.cursor()
                                cur.execute('UPDATE classes SET status="1" WHERE url="'+class_name+'"')
                                for i in range(0,len(list1)):
                                    cur.execute('UPDATE '+class_name+' SET point='+list1[i][3]+' WHERE id='+list1[i][0])
                                for i in range(0,len(list2)):
                                    cur.execute('UPDATE '+class_name+' SET point='+list2[i][3]+' WHERE id='+list2[i][0])
                                conn.commit()
                                cur.close()
                                conn.close()
                                if len(list1)==0 and len(list2)==0:
                                    session['warning']=True
                                return redirect('/class/'+class_name)
                            else:
                                return redirect('/class/'+class_name)
                else:
                    return redirect('/')             
            else:
                return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/')
    
@app.route('/class/<class_name>/finishclass',methods=['GET'])
def finishclass(class_name):
    url_list=[]
    if session['login']==True:
        if 'license' in session:
            if session['license']==True:
                class_list=get_db('number.sqlite3','classes')
                for i in range(0,len(class_list)):
                    url_list.append(class_list[i][4])
                if class_name in url_list:
                    db_name=class_name+'2'
                    if db_exists('number.sqlite3',db_name)==0:
                        conn = sqlite3.connect('number.sqlite3')
                        cur = conn.cursor()
                        cur.execute('UPDATE classes SET status="0" WHERE url="'+class_name+'"')
                        cur.execute('CREATE TABLE "'+class_name+'2" AS SELECT * FROM "'+class_name+'"')
                        conn.commit()
                        cur.close()
                        conn.close()
                    else:
                        conn = sqlite3.connect('number.sqlite3')
                        cur = conn.cursor()
                        cur.execute('UPDATE classes SET status="0" WHERE url="'+class_name+'"')
                        cur.execute('drop table '+db_name)
                        cur.execute('CREATE TABLE "'+class_name+'2" AS SELECT * FROM "'+class_name+'"')
                        conn.commit()
                        cur.close()
                        conn.close() 
                    return redirect('/class/'+class_name)
                else:
                    return redirect('/')             
            else:
                return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/class/<class_name>/register',methods=['POST'])
def register(class_name):
    url_list=[]
    if session['login']==True:
        if 'license' in session:
            if session['license']==True:
                class_list=get_db('number.sqlite3','classes')
                for i in range(0,len(class_list)):
                    url_list.append(class_list[i][4])
                if class_name in url_list:
                    id=request.form.get('id')
                    point=request.form.get('point')
                    tell=request.form.get('tell')
                    status_list=get_db('number.sqlite3',class_name)
                    list1=[]
                    list1.append(id)
                    for i in range(0,len(status_list)):
                        if status_list[i][1]==id:
                            list1.append(point)
                            list1.append(tell)
                            break
                    conn = sqlite3.connect('number.sqlite3')
                    cur = conn.cursor()
                    cur.execute('UPDATE '+class_name+' SET tell="'+list1[2]+'" WHERE name='+list1[0])
                    cur.execute('UPDATE '+class_name+' SET point="'+list1[1]+'" WHERE name='+list1[0])
                    conn.commit()
                    cur.close()
                    conn.close()
                    return '/class/'+class_name
                else:
                    return '/'             
            else:
                return '/'
        else:
            return '/'
    else:
        return '/'

@app.route('/class/<class_name>/formregister',methods=['POST'])
def formregister(class_name):
    url_list=[]
    if session['login']==True:
        if 'license' in session:
            if session['license']==True:
                class_list=get_db('number.sqlite3','classes')
                for i in range(0,len(class_list)):
                    url_list.append(class_list[i][4])
                if class_name in url_list:
                    sentence=request.form.get('sentence')
                    style=request.form.get('style')
                    formlist=get_db('number.sqlite3',class_name+'_form')
                    number=str(len(formlist)+1)
                    if style=='1' or style=='2':
                        branch=[]
                        for i in range(0,len(request.form)-2):
                            branch.append(request.form.get('branch'+str(i+1)))
                        file1='cache/'+class_name+'_form'+number+'.dat'
                        try:
                            with open(file1,'wb') as f:
                                pickle.dump(branch,f)
                        except:
                            return 'false'
                    conn = sqlite3.connect('number.sqlite3')
                    cur = conn.cursor()
                    cur.execute('INSERT INTO '+class_name+'_form VALUES('+number+',"form'+number+'","'+sentence+'","'+style+'")')
                    cur.execute('CREATE TABLE '+class_name+'_form'+number+' AS SELECT * FROM form_layout')
                    if style=='1' or style=='2':
                        for i in range(0,len(branch)-1):
                            cur.execute('ALTER TABLE '+class_name+'_form'+number+' ADD COLUMN answer'+str(i+2)+'[text]')
                    conn.commit()
                    cur.close()
                    conn.close()
                    return 'true'
                else:
                    return 'false'             
            else:
                return 'false'
        else:
            return 'false'
    else:
        return 'false'

@app.route('/class/<class_name>/<form>',methods=['POST'])
def form_receive(class_name,form):
    if session['login']==True:
        url_list=[]
        class_list=get_db('number.sqlite3','classes')
        for i in range(0,len(class_list)):
            url_list.append(class_list[i][4])
        if class_name in url_list:
            for i in range(0,len(class_list)):
                if class_list[i][4]==class_name:
                    break
            form_list=get_db('number.sqlite3',class_name+'_form')
            noerror=False
            for i in range(0,len(form_list)):
                if form_list[i][1]==form:
                    noerror=True
                    style=form_list[i][3]
                    key=i
                    break
            if noerror==True:
                if style=='1':
                    radio=request.form.get('radio')
                    file1='cache/'+class_name+'_form'+str(key+1)+'.dat'
                    try:
                        with open(file1,'rb') as f:
                            branch=pickle.load(f)
                    except:
                        pass
                    for i in range(0,len(branch)):
                        if branch[i]==radio:
                            key2=i
                            break
                    conn = sqlite3.connect('number.sqlite3')
                    cur = conn.cursor()
                    cur.execute('UPDATE '+class_name+'_form'+str(key+1)+' SET status="1" WHERE name="'+session['id']+'"')
                    cur.execute('UPDATE '+class_name+'_form'+str(key+1)+' SET answer'+str(key2+1)+'="1" WHERE name="'+session['id']+'"')
                    conn.commit()
                    cur.close()
                    conn.close()
                if style=='2':
                    number=[]
                    check=request.form.getlist('checkbox')
                    file1='cache/'+class_name+'_form'+str(key+1)+'.dat'
                    try:
                        with open(file1,'rb') as f:
                            branch=pickle.load(f)
                    except:
                        pass
                    for i in range(0,len(check)):
                        for x in range(0,len(branch)):
                            if branch[x]==check[i]:
                                number.append(str(x+1))
                                break
                    conn = sqlite3.connect('number.sqlite3')
                    cur = conn.cursor()
                    cur.execute('UPDATE '+class_name+'_form'+str(key+1)+' SET status="1" WHERE name="'+session['id']+'"')
                    for i in range(0,len(number)):
                        cur.execute('UPDATE '+class_name+'_form'+str(key+1)+' SET answer'+number[i]+'="1" WHERE name="'+session['id']+'"')
                    conn.commit()
                    cur.close()
                    conn.close()
                if style=='3':
                    freeform=request.form.get('freeform')
                    conn = sqlite3.connect('number.sqlite3')
                    cur = conn.cursor()
                    cur.execute('UPDATE '+class_name+'_form'+str(key+1)+' SET status="1" WHERE name="'+session['id']+'"')
                    cur.execute('UPDATE '+class_name+'_form'+str(key+1)+' SET answer1="'+freeform+'" WHERE name="'+session['id']+'"')
                    conn.commit()
                    cur.close()
                    conn.close()
                return redirect('/class/'+class_name)
            else:
                return redirect('/class/'+class_name)
        else:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/class/<class_name>/<form>',methods=['GET'])
def form_pass(class_name,form):
    if session['login']==True:
        url_list=[]
        class_list=get_db('number.sqlite3','classes')
        for i in range(0,len(class_list)):
            url_list.append(class_list[i][4])
        if class_name in url_list:
            for i in range(0,len(class_list)):
                if class_list[i][4]==class_name:
                    key2=i
                    break
            form_list=get_db('number.sqlite3',class_name+'_form')
            noerror=False
            for i in range(0,len(form_list)):
                if form_list[i][1]==form:
                    noerror=True
                    style=form_list[i][3]
                    key=i
                    break
            if noerror==True:
                if 'license' in session and session['license']:
                    msg=session['id']+'先生'
                else:
                    msg=session['id']+'さん'
                msg2=class_name
                class_list.remove(class_list[key2])
                msg4=class_list 
                sentence=form_list[key][2]
                url1=form
                detail_form_list=get_db('number.sqlite3',class_name+'_form'+str(key+1))
                color_list=['#0D6EFD','#198754','#DC3545']
                if style=='1':
                    supply2=[]
                    status_list=get_db('number.sqlite3',class_name)
                    file1='cache/'+class_name+'_form'+str(key+1)+'.dat'
                    try:
                        with open(file1,'rb') as f:
                            branch=pickle.load(f)
                    except:
                        pass
                    for i in range(0,len(branch)):
                        supply1=[]
                        for x in range(0,len(detail_form_list)):
                            if detail_form_list[x][i+3]=='1':
                                supply1.append(detail_form_list[x][1])
                        supply2.append(supply1)
                    supply1=[]
                    for i in range(0,len(detail_form_list)):
                        if detail_form_list[i][2]=='0':
                            supply1.append(detail_form_list[i][1])
                    supply2.append(supply1)
                    for i in range(0,len(supply2)):
                        for y in range(0,len(supply2[i])):
                            for x in range(0,len(status_list)):
                                if supply2[i][y]==status_list[x][1]:
                                    supply2[i][y]=status_list[x]
                                    break
                    finalform=[]
                    for i in range(0,len(branch)+1):
                        if i==len(branch):
                            supply3=[]
                            supply3.append('未投票')
                            supply3.append('#6C757D')
                            supply3.append(block(supply2[i]))
                            finalform.append(supply3)
                        else:
                            supply3=[]
                            supply3.append(branch[i])
                            supply3.append(color_list[random.randrange(len(color_list))])
                            supply3.append(block(supply2[i]))
                            finalform.append(supply3)
                    if 'license' in session and session['license']:
                        return render_template('form.html',\
                            title='class',\
                                message=msg,\
                                    msg2=msg2,\
                                        finalform=finalform,\
                                            msg4=msg4,\
                                                url1=url1,\
                                                    sentence=sentence)
                    else:
                        return render_template('form_student.html',\
                            title='class',\
                                message=msg,\
                                    msg2=msg2,\
                                        finalform=finalform,\
                                            msg4=msg4,\
                                                url1=url1,\
                                                    sentence=sentence)
                if style=='2':
                    supply2=[]
                    status_list=get_db('number.sqlite3',class_name)
                    file1='cache/'+class_name+'_form'+str(key+1)+'.dat'
                    try:
                        with open(file1,'rb') as f:
                            branch=pickle.load(f)
                    except:
                        pass
                    for i in range(0,len(branch)):
                        supply1=[]
                        for x in range(0,len(detail_form_list)):
                            if detail_form_list[x][i+3]=='1':
                                supply1.append(detail_form_list[x][1])
                        supply2.append(supply1)
                    supply1=[]
                    for i in range(0,len(detail_form_list)):
                        if detail_form_list[i][2]=='0':
                            supply1.append(detail_form_list[i][1])
                    supply2.append(supply1)
                    for i in range(0,len(supply2)):
                        for y in range(0,len(supply2[i])):
                            for x in range(0,len(status_list)):
                                if supply2[i][y]==status_list[x][1]:
                                    supply2[i][y]=status_list[x]
                                    break
                    finalform=[]
                    for i in range(0,len(branch)+1):
                        if i==len(branch):
                            supply3=[]
                            supply3.append('未投票')
                            supply3.append('#6C757D')
                            supply3.append(block(supply2[i]))
                            finalform.append(supply3)
                        else:
                            supply3=[]
                            supply3.append(branch[i])
                            supply3.append(color_list[random.randrange(len(color_list))])
                            supply3.append(block(supply2[i]))
                            finalform.append(supply3)
                    if 'license' in session and session['license']:
                        return render_template('form.html',\
                            title='class',\
                                message=msg,\
                                    msg2=msg2,\
                                        finalform=finalform,\
                                            msg4=msg4,\
                                                url1=url1,\
                                                    sentence=sentence)
                    else:
                        return render_template('form_student.html',\
                            title='class',\
                                message=msg,\
                                    msg2=msg2,\
                                        finalform=finalform,\
                                            msg4=msg4,\
                                                url1=url1,\
                                                    sentence=sentence)
                if style=='3':
                    status_list=get_db('number.sqlite3',class_name)
                    supply1=[]
                    supply3=[]
                    for i in range(0,len(detail_form_list)):
                        supply2=[]
                        if detail_form_list[i][2]=='1':
                            supply2.append(detail_form_list[i][1])
                            supply2.append(detail_form_list[i][3])
                            supply1.append(supply2)
                    for i in range(0,len(detail_form_list)):
                        if detail_form_list[i][2]=='0':
                            supply3.append(detail_form_list[i][1])
                    for i in range(0,len(supply1)):
                        for x in range(0,len(status_list)):
                            if supply1[i][0]==status_list[x][1]:
                                supply1[i].append(status_list[x][3])
                                supply1[i].append(status_list[x][4])
                                supply1[i].append(color_list[random.randrange(len(color_list))])
                                break
                    for i in range(0,len(supply3)):
                        for x in range(0,len(status_list)):
                            if supply3[i]==status_list[x][1]:
                                supply4=[]
                                supply4.append(supply3[i])
                                supply4.append(status_list[x][3])
                                supply4.append(status_list[x][4])
                                supply3[i]=supply4
                                break
                    supply2=block(supply3)
                    if 'license' in session and session['license']:
                        return render_template('freeform.html',\
                            title='class',\
                                message=msg,\
                                    msg2=msg2,\
                                        supply2=supply2,\
                                            msg4=msg4,\
                                                url1=url1,\
                                                    sentence=sentence,\
                                                        supply1=supply1)
                    else:
                        return render_template('freeform_student.html',\
                            title='class',\
                                message=msg,\
                                    msg2=msg2,\
                                        supply2=supply2,\
                                            msg4=msg4,\
                                                url1=url1,\
                                                    sentence=sentence,\
                                                        supply1=supply1)

if __name__=='__main__':
    app.debug=False
    app.run(host='0.0.0.0')