from flask import Flask,render_template,request,redirect,url_for,flash,session
import sqlite3 as sql
import hashlib
from functools import wraps
app=Flask(__name__)

@app.before_request
def check_authentication():
    # List of routes that don't require authentication
    allowed_routes = ['home', 'login', 'create_account']

    # Check if the user is not logged in and the route requires authentication
    if 'username' not in session and request.endpoint not in allowed_routes:
        flash('Not Allowed Without Login', 'error')
        return redirect(url_for('home'))

#home page routing
@app.route("/")
def home():
    return render_template("home.html")

# Login route
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        con = sql.connect("db_USERS.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashlib.md5(password.encode()).hexdigest()))
        user = cur.fetchone()
        con.close()
        
        if user:
            session['username'] = username
            flash('Logged in successfully', 'success')
            return redirect(url_for("index"))
        else:
            flash('Invalid Username Or Password', 'error')
    #if get request
    return render_template("login.html")

# Create account route
@app.route("/create_account", methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        con = sql.connect("db_USERS.db")
        cur = con.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashlib.md5(password.encode()).hexdigest()))
        con.commit()
        con.close()
        
        flash('Account Created Successfully', 'success')
        return redirect(url_for("login"))
    #if get request
    return render_template("create_account.html")

# Logout route
@app.route("/logout")
def logout():
    session.pop('username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

#route for index page that will render the testcases in database shared with all logedin users
@app.route("/index")
def index():
    con=sql.connect("db_TESTCASES.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from testcases")
    data=cur.fetchall()
    return render_template("index.html",datas=data)

#route for retreving testcase details based on id
@app.route("/testcase/<int:id>")
def get_testcase(id):
    con = sql.connect("db_TESTCASES.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM testcases WHERE ID = ?", (id,))
    testcase = cur.fetchone()
    con.close()

    if testcase:
        return render_template("testcase.html", testcase=testcase)
    else:
        flash('TestCase Not Found', 'error')
        return redirect(url_for("index"))

@app.route("/validate_testcase",methods=['POST','GET'])
def validate_testcase():
    if request.method == 'POST':
        num1 = request.form['num1']
        num2 = request.form['num2']
        operation = request.form['operation']
        result = request.form['result']
        if not num1 or not num2 or not operation or not result:
            flash('All Fields Are Required', 'error')
            return redirect(url_for("validate_testcase"))
        #chech that both numbers and result are numeric
        try:
            num1 = float(num1)
            num2 = float(num2)
            result = float(result)
        except ValueError:
            flash('NUM1,NUM2,Result Must Be Numeric Values', 'error')
            return redirect(url_for("validate_testcase"))
        #check that the operation is either add or sub or mul or div
        if operation not in ["MUL", "DIV", "ADD", "SUB"]:
            flash('Operation Must Be MUL or DIV or ADD or SUB', 'error')
            return redirect(url_for("validate_testcase"))
        con=sql.connect("db_TESTCASES.db")
        con.row_factory=sql.Row
        cur=con.cursor()
        cur.execute("SELECT * FROM testcases WHERE NUM1=? AND NUM2=? AND OPERATION=?", (num1, num2, operation))
        data=cur.fetchall()
        if data:
            con = sql.connect("db_TESTCASES.db")
            cur = con.cursor()
            for row in data:
                if result==int(row['RESULT']):
                    cur.execute("INSERT INTO execution_results (NUM1,NUM2,OPERATION,RESULT,EXPECTEDRESULT,STATUS) VALUES (?, ?, ?, ? , ? , ? )", (row['NUM1'],row['NUM2'],row['OPERATION'],result,row['RESULT'],'PASS'))
                else:
                    cur.execute("INSERT INTO execution_results (NUM1,NUM2,OPERATION,RESULT,EXPECTEDRESULT,STATUS) VALUES (?, ?, ?, ? , ? , ? )", (row['NUM1'],row['NUM2'],row['OPERATION'],result,row['RESULT'],'FAIL'))
            con.commit()
            flash("Validated And Added To Execution Results Table", 'success')
            return redirect(url_for("index"))
        else:
            flash("Test Case Not Exits", 'error')
            return redirect(url_for("validate_testcase"))
        
    return render_template("validate_testcase.html")
#route for retreving execusions results
@app.route("/execution_results")
def execution_results():
    con=sql.connect("db_TESTCASES.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from execution_results")
    data=cur.fetchall()
    return render_template("execution_results.html",datas=data)
#route for adding new testcase
@app.route("/add_testcase",methods=['POST','GET'])
def add_testcase():
    if request.method == 'POST':
        num1 = request.form['num1']
        num2 = request.form['num2']
        operation = request.form['operation']
        result = request.form['result']
        #check that all field having value
        if not num1 or not num2 or not operation or not result:
            flash('All Fields Are Required', 'error')
            return redirect(url_for("add_testcase"))
        #chech that both numbers and result are numeric
        try:
            num1 = float(num1)
            num2 = float(num2)
            result = float(result)
        except ValueError:
            flash('NUM1,NUM2,Result Must Be Numeric Values', 'error')
            return redirect(url_for("add_testcase"))
        #check that the operation is either add or sub or mul or div
        if operation not in ["MUL", "DIV", "ADD", "SUB"]:
            flash('Operation Must Be MUL or DIV or ADD or SUB', 'error')
            return redirect(url_for("add_testcase"))
    
        
        con = sql.connect("db_TESTCASES.db")
        cur = con.cursor()
        cur.execute("INSERT INTO testcases (NUM1,NUM2,OPERATION,RESULT) VALUES (?, ?, ?, ?)", (num1,num2,operation,result))
        con.commit()
        flash('TestCase Added', 'success')
        return redirect(url_for("index"))
    return render_template("add_testcase.html")

#route to edit one of the existing testcase
@app.route("/edit_testcase/<string:id>",methods=['POST','GET'])
def edit_testcase(id):
    if request.method=='POST':
        num1 = request.form['num1']
        num2 = request.form['num2']
        operation = request.form['operation']
        result = request.form['result']
        if not num1 or not num2 or not operation or not result:
            flash('All Fields Are Required', 'error')
            return redirect(url_for("edit_testcase",id=id,))
        try:
            num1 = float(num1)
            num2 = float(num2)
            result = float(result)
        except ValueError:
            flash('NUM1,NUM2,Result Must Be Numeric Values', 'error')
            return redirect(url_for("edit_testcase",id=id,))
        
        if operation not in ["MUL", "DIV", "ADD", "SUB"]:
            flash('Operation Must Be MUL or DIV or ADD or SUB', 'error')
            return redirect(url_for("edit_testcase",id=id,))
    
        
        
        con=sql.connect("db_TESTCASES.db")
        cur=con.cursor()
        cur.execute("update testcases set NUM1=?,NUM2=?,OPERATION=?,RESULT=? where ID=?",(num1,num2,operation,result,id))
        con.commit()
        flash('TestCase Updated','success')
        return redirect(url_for("index"))
    con=sql.connect("db_TESTCASES.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from testcases where ID=?",(id,))
    data=cur.fetchone()
    return render_template("edit_testcase.html",datas=data)

#route to delete one from the exixting database
@app.route("/delete_testcase/<string:id>",methods=['GET'])
def delete_testcase(id):
    con=sql.connect("db_TESTCASES.db")
    cur=con.cursor()
    cur.execute("delete from testcases where ID=?",(id,))
    con.commit()
    flash('TestCase Deleted','error')
    return redirect(url_for("index"))
    
if __name__=='__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)