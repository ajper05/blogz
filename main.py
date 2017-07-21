from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'F*4&8P9vmwJbmdtw'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_requests
def require_login():
    allowed_routes = ['signup', 'login', 'logout', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template('login.html', pagetitle="Log In to Your Blog")
    username = request.form["username"]
    password = request.form["password"]
    existing_user = User.query.filter_by(username=username).first()
    user = User.query.all()
    error = False

    if not existing_user:
        flash("Username is not registered", "error")
        error = True

    if not error:
        if username and username.password == password:
            session['username'] = username
            flash("You Have Been Logged in")

    else:
        return render_template('login.html', pagetitle="Log In to Your Blog", password=password, username=username)


@app.route('/signup', methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template('signup.html', pagetitle="Create a Blog account")

    username = request.form["username"]
    password = request.form["password"]
    verify = request.form["verify"]
    users = User.query.all()
    existing_user = User.query.filter_by(username=username).first()
    error = False
    if len(username) < 3:
        flash("Username is too short or left blank", "error")
        error = True

    if not existing_user:
        flash("That user already exists", "error")
        error = True

    if len(password) < 3:
        flash("Password is too short or left blank", "error")
        error = True

    if verify != password:
        flash("Password does not match", "error")
        error = True

    if not error:
        if request.method == "POST":
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    else:
        return render_template('signup.html', pagetitle="Create a Blog account", username=username, password=password, verify=verify)


@app.route('/logout')
def logout():
    if session:
        del session['username']
        flash('You Have Been Logged out')
    return redirect('/blog')


@app.route('/blog', methods=["POST", "GET"])
def blog():
    posts = Blog.query.all()
    if "id" in request.args:
        id = request.args.get('id')
        post = Blog.query.get(id)
        return render_template('blogmain.html', pagetitle="Build A Blog", title=post.title, body=post.body, owner=post.owner)

    if "user" in request.args:
        owner_id = request.args.get('user')
        username = User.query.get(owner_id)
        userposts = Blog.query.filter_by(owner_id=owner_id)

        return render_template('singlepost.html', pagetitle="Posts by" + username, user=username, userposts=userposts)

    return render_template('posts.html', pagetitle="build a blog", posts=posts)


@app.route('/newpost', methods=["POST", "GET"])
def newpost():

    if request.method == "GET":
        return render_template('newpost.html', pagetitle="build a blog")
    title = request.form["title"]
    body = request.form["body"]
    error = False

    if len(title) <= 0:
        flash("Title cannot be left blank", "error")
        error = True
    if len(title) > 255:
        flash("Title cannot be greater than 255 characters long", "error")
        error = True
    if len(body) > 500:
        flash("Post body cannot be greater than 500 characters in length")
        error = True
    if len(body) <= 0:
        flash("Post body cannot be left blank")
        error = True

    if not error:
        if request.method == "POST":
            post_title = request.form["title"]
            post_body = request.form["body"]
            owner = User.query.filter_by(username=session['username']).first()
            new_entry = Blog(post_title, post_body, owner)
            db.session.add(new_entry)
            db.session.commit()

        return render_template('posts.html', pagetitle="build a blog", title=title, body=body, owner=owner)

    else:
        return render_template('newpost.html', pagetitle="build a blog", title=title,)


@app.route('/', methods=["POST", "GET"])
def index():
    users = User.query.all()
    return render_template('index.html', pagetitle="List of Blogs!", users=users)


if __name__ == '__main__':
    app.run()
