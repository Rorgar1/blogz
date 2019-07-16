#importing all the stuff to make things run
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi 

#setting up sql 
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'abcde12345' #required for session


#creates a Blog class with title and body
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog_body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, blog_body, owner):
        self.title = title
        self.blog_body = blog_body
        self.owner = owner

    def __repr__(self):
        return '<User %r>' % self.title #defines the string representation


#creates a User class with email and password 
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

   

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username #defines the string representation

#requires user to log in
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        redirect('/login')


#login handler
@app.route('/login', methods=['POST','GET'])
def login():
   
    if request.method == 'POST':
        password = request.form['password']
        username = request.form['username']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:                      #conditional breaks if user == None
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        else:
            flash('User password is incorrect, or user does not exist', 'error')
    
        

    return render_template('login.html')




#signup handler
@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #validates user's data

        existing_user = User.query.filter_by(username=username).first()
        
        if password != verify:
            flash('Password does not match', "error")
        elif len(username) < 3 or len(password) < 3:
            flash('Username and password must be more than 3 characters', 'error')
        elif existing_user:
            flash('User already exists', 'error')
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html')


#logout route and function
@app.route('/logout')
def logout():
    if session:
        del session['username']
        return redirect('/blog')
    else:
        return redirect('/login')


#redirect to display all the blog posts
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users, header='Blog Users')





#display all the blog posts
@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
 

    if blog_id == None:
        posts = Blog.query.all()
        return render_template('blog.html', posts=posts, title='Blogz')
    else:
        post = Blog.query.get(blog_id)
        return render_template('entry.html', post=post, title='Blog Entry')   




#route to add a new post
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        owner = User.query.filter_by(username=session['username']).first()
        title_error = ''
        body_error = ''

#error messages for blank fields
        if not blog_title:
            title_error = "Please enter a blog title"
        if not blog_body:
            body_error = "Cannot leave body blank"

#add entry when all fields are filled in
        if not body_error and not title_error:
            new_entry = Blog(blog_title, blog_body, owner)           
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) 
        else:
            return render_template('newpost.html', title='New Entry', title_error=title_error, body_error=body_error, 
                blog_title=blog_title, blog_body=blog_body)
    
    return render_template('newpost.html', title='New Entry')
 

if __name__ == '__main__':
    app.run()