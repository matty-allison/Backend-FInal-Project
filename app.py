#imported modules used for this app
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
import cloudinary
import cloudinary.uploader


# Function for creating the users database and creating the tables
def createDataBase():
    conn = sqlite3.connect('sneakeromatic.db')
    print("database opened")

    conn.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "name TEXT NOT NULL,"
                 "email TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("table opened")
    conn.close()


# function for creating the products table
def createProductTable():
    with sqlite3.connect('sneakeromatic.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS sneakers(sneaker_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "sneaker_name TEXT NOT NULL,"
                     "sneaker_brand TEXT NOT NULL,"
                     "sneaker_description TEXT NOT NULL,"
                     "sneaker_price TEXT NOT NULL,"
                     "sneaker_image TEXT NOT NULL)")
    print("table opened")

def createReviewTable():
    with sqlite3.connect('sneakeromatic.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "review_name TEXT NOT NULL,"
                     "review TEXT NOT NULL)")
        print("table opened")


# Calling the functions to create the table
createDataBase()
createProductTable()
createReviewTable()

# function to take image uploads and convert them into urls
def image_convert():
    app.logger.info('in upload route')
    cloudinary.config(cloud_name="dbhj6nbj9",
                      api_key="533486918376564",
                      api_secret="NMOQ39T4DW4lJnNmlhf12oNopnw"
                      )
    upload_result = None
    if request.method == 'POST' or request.method == 'PUT':
        sneaker_image = request.json['sneaker_image']
        app.logger.info('%s file_to_upload', sneaker_image)
        if sneaker_image:
            upload_result = cloudinary.uploader.upload(sneaker_image)
            app.logger.info(upload_result)
            return upload_result['url']


app = Flask(__name__)
#email building
CORS(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'matthewatwork18@gmail.com'
app.config['MAIL_PASSWORD'] = 'Mallison17$'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# first route to register new users
@app.route('/sign-up/', methods=["POST"])
def signUp():
    confirmation = {}
    try:

        if request.method == "POST":

            name = request.json['name']
            email = request.json['email']
            password = request.json['password']

            with sqlite3.connect("sneakeromatic.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users("
                               "name,"
                               "email,"
                               "password) VALUES(?, ?, ?)", (name, email, password))
                conn.commit()
                confirmation["message"] = "User registered successfully"
                confirmation["status_code"] = 200
                msg = Message('Good day new user', sender='matthewatwork18@gmail.com', recipients=[email])
                msg.body = "WELCOME, Thank you for signing up to Sneakeromatic, we are happy to have and hope you buy from our store we have a wide range of sneakers, a pair for everyone is our moto. Leave a review on our website it helps us with customer satisfaction."
                msg.send(msg)
    except ValueError:
        if request.method != "POST":
            return
    finally:
        return confirmation

# route for adding new sneaker
@app.route('/add-sneaker/', methods=["POST"])
def add():
    confirmation = {}
    try:
        if request.method == "POST":

            sneaker_name = request.json['sneaker_name']
            sneaker_brand = request.json['sneaker_brand']
            sneaker_description = request.json['sneaker_description']
            sneaker_price = request.json['sneaker_price']
            sneaker_image = image_convert()


            with sqlite3.connect("sneakeromatic.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO sneakers("
                               "sneaker_name,"
                               "sneaker_brand,"
                               "sneaker_description,"
                               "sneaker_price,"
                               "sneaker_image) VALUES (?, ?, ?, ?, ?)", (sneaker_name, sneaker_brand, sneaker_description, sneaker_price, sneaker_image))
                conn.commit()
                confirmation["message"] = "sneaker add successfully"
                confirmation["status_code"] = 200
    except ValueError:
        if request.method != "POST":
            return
    finally:
        return confirmation


#route to add review
@app.route('/add-review/', methods=["POST"])
def add_review():
    confirmation = {}
    try:
        if request.method == "POST":

            review_name = request.json['review_name']
            review = request.json['review']

            with sqlite3.connect("sneakeromatic.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO reviews("
                               "review_name,"
                               "review) VALUES (?, ?)", (review_name, review))
                conn.commit()
                confirmation["message"] = "review add successfully"
                confirmation["status_code"] = 200
    except ValueError:
        if request.method != "POST":
            return
    finally:
        return confirmation

# route to view users
@app.route('/view-users/', methods=["GET"])
def view_users():
    confirmation = {}
    with sqlite3.connect('sneakeromatic.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')

        users = cursor.fetchall()

    confirmation["status_code"] = 200
    confirmation["data"] = users
    return confirmation


# route to display all products the database
@app.route('/show-sneakers/', methods=["GET"])
def show_sneakers():
    confirmation = {}
    with sqlite3.connect('sneakeromatic.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sneakers')

        sneakers = cursor.fetchall()

    confirmation["status_code"] = 200
    confirmation["data"] = sneakers
    return confirmation

#route to get all reviews
@app.route('/show-reviews/')
def show_reviews():
    confirmation = {}
    with sqlite3.connect('sneakeromatic.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reviews')

        reviews = cursor.fetchall()

    confirmation["status_code"] = 200
    confirmation["data"] = reviews
    return confirmation

# route to view one product (product id required)
@app.route('/view-sneaker/<int:sneaker_id>/', methods=["GET"])
def view_sneaker(sneaker_id):
    confirmation = {}

    with sqlite3.connect("sneakeromatic.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sneakers WHERE sneaker_id=" + str(sneaker_id))

        confirmation["status_code"] = 200
        confirmation["description"] = "sneaker retrieved successfully"
        confirmation["data"] = cursor.fetchone()

    return jsonify(confirmation)


# route to edit a product (product id required)
@app.route('/edit-sneaker/<int:sneaker_id>/', methods=["PUT"])
def edit_sneaker(sneaker_id):
    confirmation = {}
    try:
        if request.method == "PUT":
            with sqlite3.connect('sneakeromatic.db') as conn:
                sneaker_name = request.json['sneaker_name']
                sneaker_brand = request.json['sneaker_brand']
                sneaker_description = request.json['sneaker_description']
                sneaker_price = request.json['sneaker_price']
                sneaker_image = request.json['sneaker_image']
                put_data = {}

                if sneaker_name is not None:
                    put_data["sneaker_name"] = sneaker_name
                    cursor = conn.cursor()
                    cursor.execute("UPDATE sneakers SET sneaker_name=? WHERE sneaker_id=?", (put_data["sneaker_name"], sneaker_id))
                    conn.commit()

                    confirmation["message"] = "Sneaker name changed successfully"
                    confirmation["status_code"] = 200

                if sneaker_brand is not None:
                    put_data["sneaker_brand"] = sneaker_brand
                    cursor = conn.cursor()
                    cursor.execute("UPDATE sneakers SET sneaker_brand=? WHERE sneaker_id=?", (put_data["sneaker_brand"], sneaker_id))
                    conn.commit()

                    confirmation["message"] = "Sneaker brand changed successfully"
                    confirmation["status_code"] = 200

                if sneaker_description is not None:
                    put_data["sneaker_description"] = sneaker_description
                    cursor = conn.cursor()
                    cursor.execute("UPDATE sneakers SET sneaker_description=? WHERE sneaker_id=?", (put_data["sneaker_description"], sneaker_id))
                    conn.commit()

                    confirmation["message"] = "sneaker description changed successfully"
                    confirmation["status_code"] = 200

                if sneaker_price is not None:
                    put_data["sneaker_price"] = sneaker_price
                    cursor = conn.cursor()
                    cursor.execute("UPDATE sneakers SET sneaker_price=? WHERE sneaker_id=?", (put_data["sneaker_price"], sneaker_id))
                    conn.commit()

                    confirmation["message"] = "sneaker price updated successfully"
                    confirmation["status_code"] = 200

                if sneaker_image is not None:
                    put_data["sneaker_image"] = image_convert()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE sneakers SET sneaker_image=? WHERE sneaker_id=?", (put_data["sneaker_image"], sneaker_id))
                    conn.commit()

                    confirmation["message"] = "sneaker image changed successfully"
                    confirmation["status_code"] = 200
    except ValueError:
        if request.method != "PUT":
            return
    finally:
        return confirmation


# route to delete a product (product id required)
@app.route('/delete-sneaker/<int:sneaker_id>/')
def delete_sneaker(sneaker_id):
    confirmation = {}

    with sqlite3.connect('sneakeromatic.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sneakers WHERE sneaker_id=" + str(sneaker_id))
        conn.commit()
        confirmation["message"] = "sneaker successfully deleted"
        confirmation["status_code"] = 200
    return confirmation


# route to edit a user (id required)
@app.route('/edit-user/<int:id>/', methods=["PUT"])
def edit_user(id):
    confirmation = {}
    try:
        if request.method == "PUT":
            with sqlite3.connect('sneakeromatic.db') as conn:
                name = request.json['name']
                email = request.json['email']
                password = request.json['password']
                put_data = {}

                if name is not None:
                    put_data["name"] = name
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET name=? WHERE id=?", (put_data["name"], id))
                    conn.commit()

                    confirmation["message"] = "name changed successfully"
                    confirmation["status_code"] = 200

                if email is not None:
                    put_data["email"] = email
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET email=? WHERE id=?", (put_data["email"], id))
                    conn.commit()

                    confirmation["message"] = "email changed successfully"
                    confirmation["status_code"] = 200

                if password is not None:
                    put_data["password"] = password
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET password=? WHERE id=?", (put_data["password"], id))
                    conn.commit()

                    confirmation["message"] = "password changed successfully"
                    confirmation["status_code"] = 200
    except ValueError:
        if request.method != "PUT":
            return
    finally:
        return confirmation


# route to delete a user (id required)
@app.route('/delete-user/<int:id>/')
def delete_user(id):
    confirmation = {}

    with sqlite3.connect('sneakeromatic.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=" + str(id))
        conn.commit()
        confirmation["message"] = "user successfully deleted"
        confirmation["status_code"] = 200
    return confirmation


# route to edit a user (id required)
@app.route('/edit-review/<int:id>/', methods=["PUT"])
def edit_review(id):
    confirmation = {}
    try:
        if request.method == "PUT":
            with sqlite3.connect('sneakeromatic.db') as conn:
                review_name = request.json['review_name']
                review = request.json['review']
                put_data = {}

                if review_name is not None:
                    put_data["review_name"] = review_name
                    cursor = conn.cursor()
                    cursor.execute("UPDATE reviews SET review_name=? WHERE id=?", (put_data["review_name"], id))
                    conn.commit()

                    confirmation["message"] = "name changed successfully"
                    confirmation["status_code"] = 200

                if review is not None:
                    put_data["review"] = review
                    cursor = conn.cursor()
                    cursor.execute("UPDATE reviews SET review=? WHERE id=?", (put_data["review"], id))
                    conn.commit()

                    confirmation["message"] = "review changed successfully"
                    confirmation["status_code"] = 200
    except ValueError:
        if request.method != "PUT":
            return
    finally:
        return confirmation


# route to delete a user (id required)
@app.route('/delete-review/<int:id>/')
def delete_review(id):
    confirmation = {}

    with sqlite3.connect('sneakeromatic.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reviews WHERE id=" + str(id))
        conn.commit()
        confirmation["message"] = "review successfully deleted"
        confirmation["status_code"] = 200
    return confirmation


if __name__ == '__main__':
    app.run(debug=True)

