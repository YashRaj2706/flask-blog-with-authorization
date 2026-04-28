from flask import Flask, render_template, redirect, session, request,url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "supersecret"


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True, )
    email= db.Column(db.String(50), unique=True, )
    password = db.Column(db.String(40), nullable=False)

    posts = db.relationship('Post', backref='author', lazy=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    content = db.Column(db.String(200))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



@app.route('/')
def home():
    return redirect('/login')


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

       
        new_user = User(user_name=user_name,email=email, password=password)
        if  confirm_password!= password :
            return "Password doesn't match"

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")
        except:
            return "User already exists"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")

        print("Login attempt:", user_name)

        user = User.query.filter_by(user_name=user_name).first()

        if user and user.password == password:
            session["user_id"] = user.id
            session["user_name"] = user.user_name

            print("Login successful")
            return redirect(url_for("dashboard"))

        else:
            return "Invalid username or password"

    return render_template("login.html")


@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    posts = Post.query.filter_by(user_id=session["user_id"]).all()

    return render_template("dashboard.html",
                           posts=posts,
                           user_name=session["user_name"])


@app.route("/create_post", methods=["GET", "POST"])
def create_post():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        new_post = Post(
            title=title,
            content=content,
            user_id=session["user_id"]
        )

        db.session.add(new_post)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("createpost.html")


@app.route("/delete_post/<int:post_id>")
def delete_post(post_id):
    if "user_id" not in session:
        return redirect("/login")
    
    post=Post.query.get_or_404(post_id)

    if post.user_id!=session["user_id"]:
        return "unauthorized access"
    
    db.session.delete(post)
    db.session.commit()

    return redirect("/dashboard")

@app.route('/logout')
def logout():
    session.pop("user_id",None)
    session.pop("user_name",None)

    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():  
        
        db.create_all()
        app.run(debug=True)
