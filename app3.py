from flask import Flask, render_template,url_for,request,session,redirect,jsonify
import pickle

app=Flask(__name__)
app.secret_key=b'random_string'

member_data={}
message_data=[]
member_data_file='member_data.dat'
message_data_file='message_data.dat'

try:
    with open(member_data_file,"rb") as f:
        list=pickle.load(f)
        if list !=None:
            member_data=list
except:
    pass

try:
    with open(message_data_file,"rb") as f:
        list=pickle.load(f)
        if list !=None:
            message_data=list
except:
    pass

@app.route('/',methods=['GET'])
def index():
    global message_data
    return render_template('messages.html',\
        title='Message',\
            login=False,\
            message='not logined...',\
                data=message_data)

@app.route('/post',methods=['POST'])
def postMsg():
    global message_data
    id=request.form.get('id')
    msg=request.form.get('comment')
    message_data.append((id,msg))
    if len(message_data)>25:
        message_data.pop(0)
    try:
        with open(message_data_file,'wb') as f:
            pickle.dump(message_data,f)
    except:
        pass
    return 'True'

@app.route('/messages',methods=['POST'])
def getMsg():
    global message_data
    return jsonify(message_data)

@app.route('/login',methods=['POST'])
def login_post():
    global member_data,message_data
    id=request.form.get('id')
    pswd=request.form.get('pass')
    if id in member_data:
        if pswd==member_data[id]:
            flg='True'
            return flg
        else:
            flg='False'
            return flg
    else:
        member_data[id]=pswd
        flg='True'
        try:
            with open(member_data_file,'wb') as f:
                pickle.dump(member_data,f)
        except:
            pass
        return flg

if __name__=='__main__':
    app.debug=False
    app.run(host='localhost')