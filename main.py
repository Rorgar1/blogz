#importing all the stuff to make things run
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

#setting up sql 
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


#creates a Blog class with title and body
class Blog(db.Model):

    owner_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog_body = db.Column(db.Text)

    def __init__(self, title, blog_body):
        self.title = title
        self.blog_body = blog_body

#creates a User class with email and password 
class User(db.Model):

    owner_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
   

    def __init__(self, username, password):
        self.username = username
        self.password = password

#login handler
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.pasword == password:
            #To do: remember user has logged in
            return redirect('/')
        else:
            #add explanation why login failes
            return '<h1>Error!</h1>'

    return render_template('login.html')

#signup handler
@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #to do: validate user's data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            # TODO - "remember" the user
            return redirect('/')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"



    return render_template('signup.html')


#redirect to display all the blog posts
@app.route('/')
def index():
    return redirect('/blog')


#display all the blog posts
@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')

    if blog_id == None:
        posts = Blog.query.all()
        return render_template('blog.html', posts=posts, title='Build-a-blog')
    else:
        post = Blog.query.get(blog_id)
        return render_template('entry.html', post=post, title='Blog Entry')   
        
#route to add a new post
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
       
        title_error = ''
        body_error = ''
#error messages for blank fields
        if not blog_title:
            title_error = "Please enter a blog title"
        if not blog_body:
            body_error = "Cannot leave body blank"
#add entry when all fields are filled in
        if not body_error and not title_error:
            new_entry = Blog(blog_title, blog_body)           
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) 
        else:
            return render_template('newpost.html', title='New Entry', title_error=title_error, body_error=body_error, 
                blog_title=blog_title, blog_body=blog_body)
    
    return render_template('newpost.html', title='New Entry')
 

if __name__ == '__main__':
    app.run()