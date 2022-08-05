# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 15:50:03 2022
@author: Admin
"""
from markupsafe import Markup
from flask import Flask , request , render_template

import mysql.connector as mysql

conn = mysql.connect(host = "localhost", username = "root" , passwd = "Pettaashu2003")
cur = conn.cursor()

app = Flask(__name__)

def use_database():
    query = "use slambook;"
    cur.execute(query)
    conn.commit()
    
def create_database_tables():
    
    try:
        query = "create database slambook;"
        cur.execute(query)
        conn.commit()
        use_database();
        query = "create table chat_data(login_user varchar(15) , other_user varchar(15) , question varchar(255) , answer varchar(255) );"
        cur.execute(query)
        conn.commit()
        
        query = "create table user_details(username varchar(15) primary key, password varchar(15) , name varchar(15) , dob date , year varchar(10) , degree varchar(10) , hostelname varchar(10) , roomnumber int );"
        cur.execute(query)
        conn.commit()
        
        print("queries executed successfully , all set !")
    except:
        print("error")
        
create_database_tables()
use_database()
class Person:
    username = ''
    password = ''
    name = ''
    dob = ''
    year = ''
    degree = ''
    hostelname = ''
    roomnumber = 0

def trim(i , n):
    return i + " "*(n - len(i))

def login_database(user,pas):
    
    query = "select password from user_details where username like '"+user+"';"
    cur.execute(query)
    l =  cur.fetchall()
    print(l)
    try:
        passwd = l[0][0]
        print(passwd , pas , passwd == pas)
        if passwd == pas:
            return "logged in"
        else:
            return "wrong pwd"
    except:
        return "no user"

def search_database(person):
    
    
    name = person.name
    hostelname = person.hostelname
    degree = person.degree
    
    
    query = "select username from user_details where name like '%"+name+"%' and hostelname like '%"+hostelname+"%' and degree like '%"+degree+"%';"
    cur.execute(query)
    
    l =  cur.fetchall()
    print(l)
    return l

def create_record(new_user , table_name):
    
    username = new_user.username
    password = new_user.password
    name = new_user.name
    dob = new_user.dob
    year = new_user.year
    degree = new_user.degree
    hostelname = new_user.hostelname
    roomnumber = new_user.roomnumber
    
    query = "insert into "+table_name+" values('{}' , '{}' , '{}' , '{}' , '{}' ,'{}' , '{}' , {});".format(username , password , name , dob , year , degree , hostelname , roomnumber)
    print(query)
    
    try:
        cur.execute(query)
        conn.commit()
        return "insertion done"
    except:
        return "error"
    
@app.route("/login.html" , methods = ["GET" , "POST"])
def login_page():
    
    global login_user
    
    msg = ""
    
    if request.method == "POST":
        
        username = request.form.get("username")
        password = request.form.get("password")
        print(username , password)
        
        response = login_database(username , password)
    
        if response == "no user":
            msg = "No user exists with the given credentials !"
        elif response == "logged in":
            msg = "You have been logged In Successfully !"
            login_user = username
        elif response == "wrong pwd":
            msg = "Wrong Password , Please Try Again !"
        else:
            msg = "Error while connecting with database"
        print(msg)
        
    return render_template("login.html" , msg = msg)

@app.route("/search.html" , methods = ["GET" , "POST"])
def search_page():
    msg = ''
    if login_user == '':
        msg = "<script>alert('You Must Login to proceed !');</script>"
        msg = Markup(msg)
        return render_template("search.html" , msg = msg)
    if request.method == "POST":
        
        search_person = Person()
        search_person.name = request.form.get("name")
        search_person.degree = request.form.get("degree")
        search_person.hostelname = request.form.get("hostelname")        
        response = search_database(search_person)
        print("RESPONSE:" , response)
        if response == [] or len(response[0]) == 0:
            msg = "<script>alert('No record found');</script>"
        else:
            msg = '<center>'
            count = 0
            for i in response:
                i = i[0]
                msg += '<form method = "POST" action = "/ask_questions.html" style = "padding:10px;width: 40%;border: 2px solid black;">'
                msg += '<button class = "submit_button" style = "background-color:lightgreen;"type = "submit" name = "p_name" value = "'+i+'"> ASK QUESTION TO '+i+'</button> </form>'
                count += 1
            msg += '</center>'
            
        msg = Markup(msg)
        return render_template("search.html" , msg = msg)
    else:
        return render_template("search.html")

questions = ''
question_list = []
count = 0
login_user = ''
other_user = ''

@app.route("/ask_questions.html" , methods = ["GET" , "POST"])
def ask_question():
    
    msg = ''
    if login_user == '':
        msg = "<script>alert('You Must Login to proceed !');</script>"
        msg = Markup(msg)
        return render_template("search.html" , msg = msg)
    global questions , count , other_user,question_list
    
    if request.method == "POST":
        _name = request.form.get("p_name")
        _question = request.form.get("question")
        
        if _name:
            other_user = _name
            print("ANSWER PERSON : " , _name)
            count = 0
            questions = ''
            question_list = []
        elif _question:
            print(_question)
            # add question to page
            count += 1
            questions += '<p><input type="text" name = "quest'+str(count)+'" style="width:70em;" value = "'+_question+'"></p>'
            question_list.append(_question)
        else:
            print("Submit all questions : " , question_list)
            query = "";
            for j in question_list:
                query="insert into chat_data values('{}' , '{}' , '{}' , '{}');".format(login_user , other_user , j , ' ')
                cur.execute(query)
                conn.commit()
                
            question_list = []
            questions = ''
            count = 0
            return render_template("ask_questions.html" , msg = Markup("<script>alert('Submitted successfully');</script>"))
        
    return render_template("ask_questions.html" , msg = Markup(questions))
    


@app.route("/home.html" , methods = ["GET" , "POST"])
def home_page():
    
    msg = ''
    if login_user == '':
        msg = "<script>alert('You Must Login to proceed !');</script>"
    else:
        
        msg = '<center>'
        response  = search_response(login_user)
        for i in response:
            msg += '<form method = "POST" action = "/view_response.html" style = "padding:10px;width: 40%;border: 2px solid black;">'
            msg += '<button class = "submit_button" style = "background-color:lightgreen;"type = "submit" name = "p_name" value = "'+i+'"> VIEW RESPONSE OF '+i+'</button> </form>'
        response  = search_reply(login_user)
        for i in response:
            msg += '<form method = "POST" action = "/edit_reply.html" style = "padding:10px;width: 40%;border: 2px solid black;">'
            msg += '<button class = "submit_button" style = "background-color:lightgreen;"type = "submit" name = "p_name" value = "'+i+'"> REPLY TO '+i+'</button> </form>'

        msg += '</center>'
        
    
    return render_template("home.html" , msg = Markup(msg))

@app.route("/view_response.html" , methods = ["GET" , "POST"])
def view_response():
    
    msg = ''
    if login_user == '':
        msg = "<script>alert('You Must Login to proceed !');</script>"
        msg = Markup(msg)
        return render_template("view_response.html" , msg = msg)
    msg = ''
    global other_user
    if request.method == "POST":
        other_user = request.form.get("p_name")
        response = search_messages(login_user , other_user)
        for (a,b,c,d) in response:
            msg += "<form><p>Q) {}</p><br><p>{}</p></form>".format(c,d)
        return render_template("view_response.html" , msg = Markup(msg))
    else:
        return render_template("view_response.html" , msg = '')
    
@app.route("/edit_reply.html" , methods = ["GET" , "POST"])
def edit_reply():
    
    msg = ''
    if login_user == '':
        msg = "<script>alert('You Must Login to proceed !');</script>"
        msg = Markup(msg)
        return render_template("edit_reply.html" , msg = msg)
    
    msg = ''
    global other_user , count
    if request.method == "POST":
        _name = request.form.get("p_name")
        if _name:
            other_user = _name
            response = search_messages( other_user , login_user)
            print(response)
            count = len(response)
            
            for (a,b,c,d) in response:
                msg += "<form method='POST' action = '/edit_reply.html'><p>Q) {}</p><br><input type = 'text' value = '{}' name='answer' style = 'width:60em;'></input><button type='submit' value = '{}' name = 'question'>submit</button></form>".format(c,d,c)
            return render_template("view_response.html" , msg = Markup(msg))
        else:
            que = request.form.get("question")
            ans = request.form.get("answer")
            update_chat(other_user,login_user , que,ans)
            response = search_messages( other_user , login_user)
            count = len(response)
            msg = "<script>alert('Reply saved successfully !')</script>"
            for (a,b,c,d) in response:
                msg += "<form method='POST' action = '/edit_reply.html'><p>Q) {}</p><br><input type = 'text' value = '{}' name='answer' style = 'width:60em;'></input><button type='submit' value = '{}' name = 'question'>submit</button></form>".format(c,d,c)
            return render_template("view_response.html" , msg = Markup(msg))
        
    else:
        return render_template("view_response.html" , msg = '')

def update_chat(a,b,c,d):
    
    query = "Update chat_data set answer = '{}' where login_user = '{}' and other_user = '{}' and question = '{}' ;".format(d,a,b,c)
    
    cur.execute(query)
    conn.commit()
    
    
def search_messages(login_user , other_user):

    query = "select * from chat_data where login_user like '{}' and other_user like '{}'".format(login_user , other_user); 
    cur.execute(query)
    return cur.fetchall()

    
def search_response(user):
    
    query = "Select distinct(other_user) from chat_data where login_user like '{}' ; ".format(user)
    cur.execute(query)
    l = []
    for i in cur.fetchall():
        l.append(i[0])
    print(l)
    return l

def search_reply(user):
    
    query = "Select distinct(login_user) from chat_data where other_user like '{}%' ; ".format(user)
    print(query)
    cur.execute(query)
    l = []
    for i in cur.fetchall():
        l.append(i[0])
    print(l)
    return l
    
@app.route("/signup.html" , methods = ["GET" , "POST"])
def signup():
    print("SIGNUP PHASE")
    msg = ''
    if request.method == "POST":
        
        new_user = Person()
        
        new_user.username = request.form.get('username')
        new_user.password = request.form.get('password')
        new_user.name = request.form.get('name')
        new_user.dob = request.form.get('dob')
        new_user.year = request.form.get('year')
        new_user.degree = request.form.get('degree')
        new_user.hostelname = request.form.get('hostelname')
        new_user.roomnumber = request.form.get('roomnumber')
        
        response = create_record(new_user , "user_details")
        if response == "insertion done":
            msg = "Great , Your account is created , you can now login"
            return render_template("signup.html" , msg = msg)
        else:
            msg = "Error , please check your input data , no duplicates are allowed !"
            return render_template("signup.html" , msg = msg)
    else:
        return render_template("signup.html" , msg = msg)

app.run()
