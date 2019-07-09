from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog_body = db.Column(db.Text)
    completed = db.Column(db.Boolean)

    def __init__(self, title, blog_body):
        self.title = title
        self.blog_body = blog_body
        self.completed = False



#must display all the blog posts
@app.route('/blog', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        title = request.form['blog']
        new_blog = Blog(title)
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.filter_by(completed=False).all()
    completed_blogs = Blog.query.filter_by(completed=True).all()
    return  render_template('blog.html', title="Build A Blog!",
        blogs=blogs, completed_blogs=completed_blogs)

 #submit a new post at /newpost route. After submitting new post, app displays the main blog page       
@app.route('/newpost', methods=['POST'])
def newpost():

    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    db.session.add(blog)
    db.session.commit()

    return redirect('/blog')


if __name__ == '__main__':
    app.run()