from flask import Flask, render_template,url_for,request,session,redirect
from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalch

engine=create_engine('sqlite://sample.sqlite3')

Base=declarative_base()

class Mydata(Base):
    __tablename__='mydata'

    id=Column(Integer,primary_key=True)
    name=Column(String(255))
    mail=Column(String(255))
    age=Column(Integer)

    def toDict(self):
        return {
            'id':int(self.id),
            'name':str(self.name),
            'mail':str(self.mail),
            'age':int(self.age)
        }
    
def getByList(arr):
    res=[]
    for item in arr:
        res.append(item.toDict())
    return res

def getAll():
    Session=sessionmaker(bind=engine)
    ses=Session()
    res=ses.query(Mydata).all()
    ses.close()
    return res

@app.route('/',methods=['GET'])
def index():
    return render_template('index2.html',\
        title='Index',\
            message='SQLite3 Database',\
                alert='This is SQLite3 Database Sample!')

@app.route('/ajax',methods=['GET'])
def ajax():
    mydata=getAll()
    return jsonify(getByList(mydata));

if __name__=='__main__':
    app.debug=False
    app.run(host='localhost')