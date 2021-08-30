import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
import re
import cloudinary
import cloudinary.uploader
from werkzeug.utils import redirect


# class for tables
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


# def get_users():
#     with sqlite3.connect('Mobile.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM users")
#         users = cursor.fetchall()
#
#         new_data = []
#
#         for data in users:
#             new_data.append(User(data[0], data[4], data[5]))
#     return new_data
#
#
# users = get_users()


class Tables:
    def __init__(self):
        self.conn = sqlite3.connect('Mobile.db')
        self.conn = self.conn.cursor()

        self.conn.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                          "full_name TEXT NOT NULL,"
                          "last_name TEXT NOT NULL,"
                          "identity TEXT NOT NULL,"
                          "phone_number TEXT NOT NULL,"
                          "email TEXT NOT NULL,"
                          "username TEXT NOT NULL,"
                          "password TEXT NOT NULL)")
        print("user table created successfully")

        self.conn.execute("CREATE TABLE IF NOT EXISTS hardware(product_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                          "image TEXT NOT NULL,"
                          "product_name TEXT NOT NULL,"
                          "description TEXT NOT NULL,"
                          "features TEXT NOT NULL,"
                          "price TEXT NOT NULL)")
        print("hardware table created")

        self.conn.execute("CREATE TABlE IF NOT EXISTS admin(admin_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                          "full_name TEXT NOT NULL,"
                          "last_name TEXT NOT NULL,"
                          "identity TEXT NOT NULL,"
                          "phone_number TEXT NOT NULL,"
                          "email TEXT NOT NULL,"
                          "username TEXT NOT NULL,"
                          "password TEXT NOT NULL)")
        print("admin created")
        self.conn.close()


Tables()

app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'


# email code
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'gafrica851@gmail.com'
app.config['MAIL_PASSWORD'] = 'xifyoxanvrvewvxl'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# register a user


@app.route('/register/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":
        try:
            full_name = request.json['full_name']
            last_name = request.json['last_name']
            identity = request.json['identity']
            phone_number = request.json['phone_number']
            email = request.json['email']
            username = request.json['username']
            password = request.json['password']

            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if re.search(regex, email):
                with sqlite3.connect("Mobile.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO users("
                                   "full_name,"
                                   "last_name,"
                                   "identity,"
                                   "phone_number,"
                                   "email,"
                                   "username,"
                                   "password) VALUES(?, ?, ?, ?, ?, ?, ?)",
                                   (full_name, last_name, identity, phone_number,
                                    email, username, password))
                    conn.commit()
                    response['message'] = "success"
                    response["status_code"] = 201

                    msg = Message('Hello Message', sender='gafrica851@gmail.com', recipients=[email])
                    msg.body = "Welcome " + full_name + " Registration completed.\n You are welcome to shop whatever. "
                    mail.send(msg)
                    return response
        except ValueError:
            response['message'] = "failed"
            response["status_code"] = 209
            return response


@app.route('/register-admin/', methods=["POST"])
def admin_registration():
    response = {}

    if request.method == "POST":

        full_name = request.json['full_name']
        last_name = request.json['last_name']
        identity = request.json['identity']
        phone_number = request.json['phone_number']
        email = request.json['email']
        username = request.json['username']
        password = request.json['password']

        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(regex, email):
            with sqlite3.connect("Mobile.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO admin("
                               "full_name,"
                               "last_name,"
                               "identity,"
                               "phone_number,"
                               "email,"
                               "username,"
                               "password) VALUES(?, ?, ?, ?, ?, ?, ?)", (full_name, last_name, identity, phone_number,
                                                                         email, username, password))
                conn.commit()
                response['message'] = "success"
                response["status_code"] = 201

                msg = Message('Hello Message', sender='gafrica851@gmail.com', recipients=[email])
                msg.body = "Welcome admin" + full_name + " Registration completed.\n to add what ever you want to. "
                mail.send(msg)
        return response


# adding a product in database


@app.route('/add-product/', methods=["POST"])
def hardware_place():
    response = {}

    if request.method == "POST":
        image = upload_file()
        product_name = request.form['product_name']
        description = request.form['description']
        features = request.form['features']
        price = request.form['price']

        with sqlite3.connect("Mobile.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO hardware("
                           "image,"
                           "product_name,"
                           "description,"
                           "features,"
                           "price) VALUES(?, ?, ?, ?, ?)", (image, product_name, description, features, str('R') +
                                                            price))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


# route for viewing user in database


@app.route('/view-users/', methods=["GET"])
def get_user():
    response = {}
    with sqlite3.connect("Mobile.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")

        posts = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = posts
    return response

# route for the admin users


@app.route('/view-admin/', methods=["GET"])
def get_admin():
    response = {}
    with sqlite3.connect("Mobile.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin")

        posts = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = posts
    return response


@app.route('/login/', methods=['PATCH'])
def login():
    response = {}

    if request.method == 'PATCH':
        username = request.json['username']
        password = request.json['password']

        with sqlite3.connect('Mobile.db') as conn:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            cursor.execute('SELECT * FROM users WHERE username=? and password=?', (username, password))
            user = cursor.fetchall()
            data = []

            for a in user:
                data.append({u: a[u] for u in a.keys()})

            response['message'] = 'success'
            response['status_code'] = 200
            response['data'] = data

        return response


# login a root
@app.route('/login-admin/', methods=['POST'])
def login_admin():
    response = {}

    if request.method == "POST":
        username = request.json["username"]
        password = request.json["password"]
        conn = sqlite3.connect("Mobile.db")
        c = conn.cursor()
        statement = (f"SELECT * FROM admin WHERE username='{username}' and password ="
                     f"'{password}'")
        c.execute(statement)
        if not c.fetchone():
            response['message'] = "failed"
            response["status_code"] = 401
            return response
        else:
            response['message'] = "Signed in"
            response["status_code"] = 201
            return response
    else:
        return "wrong method"


# view product route
@app.route('/view-products/', methods=["GET"])
def get_product():
    response = {}

    with sqlite3.connect("Mobile.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM hardware")
        hardware = cursor.fetchall()
        data = []

        for i in hardware:
            data.append({u: i[u] for u in i.keys()})

        response['status_code'] = 200
        response['description'] = 'Product showing'
        response['data'] = data

    return jsonify(response)


# deleting route
@app.route("/delete-product/<int:product_id>", methods=["GET"])
def delete_product(product_id):
    response = {}
    with sqlite3.connect("Mobile.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hardware WHERE product_id=" + str(product_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Product deleted successfully "
    return response


# editing the product database below
@app.route('/edit-product/<int:product_id>', methods=["PUT"])
def update_product(product_id):
    response = {}

    if request.method == "PUT":
        try:
            image = request.json['image']
            product_name = request.json['product_name']
            description = request.json['description']
            features = request.json['features']
            price = request.json['price']

            with sqlite3.connect("Mobile.db") as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE hardware SET image=? , product_name=? , description=? , features=? , price=? "
                               "WHERE product_id=?", (image, product_name, description, features, price, product_id))
                conn.commit()
                response["message"] = "Product was successfully updated"
                response["status_code"] = 201
            return response
        except ValueError:
            response["message"] = "Failed to update product"
            response["status_code"] = 209
        return response


# using cloudinary to change pictures to urls
def upload_file():
    app.logger.info('in upload route')
    cloudinary.config(
        cloud_name="lifechoices",
        api_key="546799713717544",
        api_secret="Y-Uaa_MWdwXy1BMLkinP4n2f6V4"
    )
    # upload_result = None
    if request.method == 'POST' or request.method == 'PUT':
        image = request.files['image']
        app.logger.info('%s file_to_upload', image)
        if image:
            upload_result = cloudinary.uploader.upload(image)
            app.logger.info(upload_result)
            return upload_result['url']


if __name__ == '__main__':
    app.run()
