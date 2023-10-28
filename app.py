from flask import Flask,render_template,request,redirect,session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import math
import random
from werkzeug.utils import secure_filename
import json
import os
from datetime import datetime
import pymysql
current_time = datetime.now().strftime("%H:%M:%S %p")
app = Flask("__name__")
with open('templates/config.json','r') as c:
    params = json.load(c)['params']
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']


)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
mail = Mail(app)
app.config["SQLALCHEMY_DATABASE_URI"] = params["local_uri"]
db = SQLAlchemy(app)
random_generated_value = random.randint(00000,99999)

class Contactus(db.Model):
    Fname = db.Column(db.String(255),nullable=False)
    Lname = db.Column(db.String(255),nullable=False)
    Email = db.Column(db.String(30),primary_key=True)
    Password = db.Column(db.String(40),nullable=False)
    City = db.Column(db.String(100),nullable=False)
    State = db.Column(db.String(100),nullable=False)
    Zip = db.Column(db.Integer,nullable=False)
    
class Post(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    writer = db.Column(db.String(255),nullable=False)
    content = db.Column(db.String(200),nullable=False)
    img_url = db.Column(db.String(255),nullable = True)
    date = current_time
    

@app.route("/",methods=['GET','POST'])
def index():
    #return "This is my first Flask App"
    if ('user' in session and session['user'] == True):
        if (request.method == 'POST'):
            
            writer = request.form.get('writer')
            content = request.form.get('content')
            img_url = request.files['img_url']
            img_url.save(os.path.join(params['upload_location'],secure_filename(img_url.filename)))
            post = Post(writer=writer,content=content,img_url= img_url.filename)
            db.session.add(post)
            db.session.commit()
            return redirect('/post.html')


    return redirect('/login.html')
@app.route('/post.html')
def post():
    if ('user' in session and session['user'] == True):
    #Pagination Logic
        poster = Post.query.all()
        last = math.ceil(len(poster)/params['no_of_posts'])
        page = request.args.get('page')
        if (not str(page).isnumeric()):
            page = 1
        #First page
        page = int(page)
        poster = poster[(page-1)*params['no_of_posts']:(page-1)*params['no_of_posts']+params['no_of_posts']]
        if (page == 1):
            prev = 1
            nxt = str(page+1)
        elif (page == last):
        
            prev = str(page-1)
            nxt = last
        else:
            prev = str(page-1)
            nxt = str(page+1)
    #  poster = Post.query.all()[0:params['no_of_posts']]
        return render_template("/post.html",params=params,poster=poster,previous = prev,nxt = nxt)
    return redirect('/login.html')
@app.route("/signup.html",methods=['GET','POST'])

def signup():
    if (request.method == 'POST'):
        Fname =  request.form.get('Fname')
        Lname = request.form.get('Lname')
        Uname = request.form.get('Uname')
        Password = request.form.get('myPass')
        city = request.form.get('city')
        state = request.form.get('state')
        zipCode = request.form.get('zipCode')
        entry = Contactus(Fname = Fname,Lname = Lname,Email = Uname,Password=Password,City = city,State = state,Zip = zipCode)
        db.session.add(entry)
        db.session.commit()
        mail.send_message("New message from NotesApp",
                          sender = params['gmail-user'],
                          recipients = [Uname],
                          body = "Your OTP verification code is " + str(random_generated_value)
                          )
        session['random_value'] = str(random_generated_value)
        session['email'] = Uname
        return render_template('/modals.html')
       
    return render_template('/signup.html',params=params)
@app.route('/modals.html',methods=['GET','POST'])
def modals():
    if (request.method == 'POST'):
        password = request.form.get('confirm')
        if (session['random_value'] != str(password)):
            value = Contactus.query.filter_by(Email = session['email']).first()
            db.session.delete(value)
            db.session.commit()
          
            return redirect('/signup.html')
       
 
    return redirect('/login.html')

#@app.route("/dashboard.html")
#def dashboard():
 #   return render_template("/dashboard.html")
#@app.route("/uploader",methods=['GET','POST'])

#def uploader():
 #   if (request.method == 'POST'):
 #       f = request.files['myfile']
 #       f.save(os.path.join(params['upload_location'],secure_filename(f.filename)))
 #       return "updated successfully"
  #  return render_template("/dashboard.html")

@app.route('/login.html',methods=['GET','POST'])
def login():
    email = request.form.get('myEmail')
    password = request.form.get('myPass')
    query = Contactus.query.filter_by(Email=email).first()
    
    
    if (query and password == query.Password):
        session['user'] = True
        return render_template('/index.html',params=params)  
    else:
        return render_template('/login.html')
@app.route('/logout')
def logout():
     session.pop('user', None)    
     return redirect('/login.html')
#@app.route('/signup.html')
#def signup():
#    return render_template('/signup.html',params=params)
if __name__ == "__main__":
    app.run(debug=True)