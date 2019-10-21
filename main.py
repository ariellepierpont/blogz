from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'f8wv3w2f>v9j4sEuhcNYydAGMzzZJgkGgyHE9gUqaJcCk^f*^o7fQyBT%XtTvcYM'


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180))
    body = db.Column(db.String(1000))
    created = db.Column(db.DateTime)

    def __init__(self, title, body ):
        self.title = title
        self.body = body
        self.created = datetime.utcnow()

    def is_valid(self):
        if self.title and self.body and self.created:
            return True
        else:
            return False

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.realtionship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return str(self.username)

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'signup', 'individual', 'index', 'home', 'OneBlog', 'user_page', 'UserPosts']
    if 'user' not in session and request.endpoint not in allowed_routes:
        return redirect('/login')

@app.route("/")
def index():
    return redirect("/blog")

@app.route("/blog")
def display_blog_entries():
    entry_id = request.args.get('id')
    if (entry_id):
        entry = Entry.query.get(entry_id)
        return render_template('single_entry.html', title="Blog Entry", entry=entry)

    sort = request.args.get('sort')
    if (sort=="newest"):
        all_entries = Entry.query.order_by(Entry.created.desc()).all()
    else:
        all_entries = Entry.query.all()   
    return render_template('all_entries.html', title="All Entries", all_entries=all_entries)

@app.route('/new_entry', methods=['GET', 'POST'])
def new_entry():
    if request.method == 'POST':
        new_entry_title = request.form['title']
        new_entry_body = request.form['body']
        new_entry = Entry(new_entry_title, new_entry_body)

        if new_entry.is_valid():
            db.session.add(new_entry)
            db.session.commit()
            url = "/blog?id=" + str(new_entry.id)
            return redirect(url)
        else:
            flash("Please check your entry for errors. Both a title and a body are required.")
            return render_template('new_entry_form.html',
                title="Create new blog entry",
                new_entry_title=new_entry_title,
                new_entry_body=new_entry_body)

    else:
        return render_template('new_entry_form.html', title="Create new blog entry")

@app.route("/individual")
def OneBlog():
    welcome = "Not logged in"
    if 'user' in session:
        welcome = "Logged in as:" + session['user']

    title = request.args.get('blog_title')
    if title:
        existing_blog = Blog.query.filter_by(title=title).first()
        author = User.query.filter_by(id=existing_blog.owner_id).first()
        return render_template("individual.html", title=existing_blog.title, body=existing_blog.body, author=author.username, welcome=welcome)

@app.route("/signup", methods=['POST', 'GET'])
def register():
    error = {"name_error": "", "pass_error": "", "verify_error": ""}
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == "":
            error["name_error"] = "Username cannot be blank"
        if password == "":
            error["pass_error"] = "Password cannot be blank"
        elif len(password) < 2:
            error["pass_error"] = "Password must be more than two characters long"
        else:
            if password != verify:
                error["verify_error"] = "Pasword and Verify must match"

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error["name_error"] = "There is already somebody with that username"

        if error["name_error"] == "" and error["pass_error"] == "" and error["verify_error"] == "":
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['user'] = new_user.username
            return redirect("/blog")

    return render_template("signup.html", title= "Register for this Blog",
        name_error= error["name_error"], pass_error= error["pass_error"],
        verify_error= error["verify_error"])


@app.route("/login", methods=['POST', 'GET'])
def login():
    error = {"name_error": "", "pass_error": ""}
    username = ""
    #if 'user' in session:
        #del session['user']
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            if password == "":
                error["pass_error"] = "Password cannot be blank."

            elif existing_user.password == password:
                session['user'] = existing_user.username
                return redirect("/blog")
            else:
                error["pass_error"] = "Invalid password"
        else:
            error["name_error"] = "Invalid username. Try again or Register."

    return render_template("login.html", title= "Login",
        name_error= error["name_error"], pass_error= error["pass_error"],
        username= username)


@app.route("/logout", methods= ['POST', 'GET'])
def logout():
        #current_user = session['user']
        #if request.method == 'POST':
        #yes = request.form['logout']
        #print(yes)
        #session['user'] = ""
        #return redirect("/blog")
        #return render_template("logout.html", title= "Logout", name= current_user)
    if 'user' in session:
        del session['user']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()