#all the imports required for the app
from flask import Flask,render_template,request,redirect,url_for,session
from datetime import datetime


#it will initialize the flask app and will create an instance of the flask class
app = Flask(__name__)
#this is used to encrypt the session data
app.secret_key = "mysecretkey"  


#temperary data storage 

post_time = datetime.now()
#to store user data in a list using dictionary
users = [
    {"user_id": 1, 
    "username": "Rahul", 
    "password": "rahul123",
    "created_at": post_time},

    {"user_id": 2, 
    "username": "A", 
    "password": "123", 
    "created_at": post_time}
]  

#this will store the posts made by users in a list using dictionary
posts = [
    {"user_id": 1,
     "username": "Rahul",
     "post_id": 1,
     "title": "First Post",
     "content": "Hello everyone!",
     "timestamp": post_time},

    {"user_id": 2,
     "username": "Amit",
     "post_id": 2,
     "title": "My First Post",
     "content": "My first post!", 
     "timestamp": post_time}
]
#this will store the comments made by users in a list using dictionary
comments = []
likes = []
#will show home page and will display the list of users who have logged in
@app.route("/show_users", methods=["GET"])
def show_users():
    return render_template("show_users.html", users=users)



#this route will show the registration page when the user clicks on the registration button
@app.route("/", methods=["POST", "GET"])
def register():
    
    if request.method == "POST":
        user_id = max(user["user_id"] for user in users) + 1 if users else 1
        username = request.form.get("username")
        password = request.form.get("password")
        post_time = datetime.now()
        users.append({"user_id": user_id, "username": username, "password": password, "created_at": post_time})

        message = "Registration successful!"
        return render_template("registration.html", message=message)
    return render_template("registration.html")



#this route will show the login page when the user clicks on the login button
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        for user in users:
            if user["username"] == username and user["password"] == password:
                message = "Login successful!"
                session["username"] = user["username"]
                session["user_id"] = user["user_id"]
                return redirect(url_for("show_posts"))
        message = "Invalid username or password!"
        return render_template("login.html", message=message)
    return render_template("login.html")


#this route will show all posts posted by users 
@app.route("/posts", methods=["GET"])
def show_posts():
    if "username" in session:   
        sorted_posts = sorted(posts, key=lambda x: x["timestamp"], reverse=True)
        return render_template("show_post.html", posts=sorted_posts,likes=likes,comments=comments)
    return redirect(url_for("login"))



#this route will show the page where user can create a new post
@app.route("/add_posts", methods=["POST", "GET"])
def add_post():
    if request.method == "POST":
        content = request.form.get("content")
        username = session.get("username", "Anonymous")
        user_id = session.get("user_id")
        post_time = datetime.now()
        post_id = max(post.get("post_id", 0) for post in posts) + 1 if posts else 1
        title = request.form.get("title")
        posts.append(
            {
                "user_id": user_id,
                "username": username,
                "post_id": post_id,
                "title": title,
                "content": content,
                "timestamp": post_time
            }
        )
        return redirect(url_for("show_posts"))
    return render_template("add_post.html")    



#this route will show the page where user can view comments of a particular post
@app.route("/posts/<int:post_id>/comments", methods=["GET"])
def show_comments(post_id):
    post = next((post for post in posts if post["post_id"] == post_id),None)
    if not post:
        return "Post not found", 404

    post_comments = [
        comment for comment in comments
        if comment["post_id"] == post_id
    ]

    return render_template(
        "comments.html",
        post=post,
        comments=post_comments
    )

#this route will allow user to add comments to a particular post
@app.route("/posts/<int:post_id>/comments", methods=["POST"])
def add_comment(post_id):

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    comment_text = request.form.get("comment")

    comment_id = max(
        (comment["id"] for comment in comments),
        default=0
    ) + 1

    comments.append({
        "id": comment_id,
        "post_id": post_id,
        "user_id": user_id,
        "comment": comment_text,
        "created_at": datetime.now()
    })

    return redirect(url_for("show_comments", post_id=post_id))





#this route will allow user to like or unlike a particular post
@app.route("/posts/<int:post_id>/like", methods=["POST"])
def like_post(post_id):

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    existing_like = next(
        (
            like for like in likes
            if like["post_id"] == post_id
            and like["user_id"] == user_id
        ),
        None
    )

    if existing_like:
        # Unlike
        likes.remove(existing_like)

    else:
        # Like
        like_id = max(
            (like["id"] for like in likes),
            default=0
        ) + 1

        likes.append({
            "id": like_id,
            "post_id": post_id,
            "user_id": user_id
        })

    return redirect(url_for("show_posts"))



#this route will log out the user and clear the session data
@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("login"))




#this is the main function which will run the app    
if __name__ == "__main__":
    app.run(debug=True)