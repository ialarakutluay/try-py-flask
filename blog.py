from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.handlers.sha2_crypt import sha256_crypt

#kullanıcı kayıt formu
class RegisterForm(Form):
    name = StringField("İsim Soyisim",validators=[validators.length(min = 4, max = 100)])
    username  = StringField('Kullacı Adı', validators=[validators.length(min = 5, max = 20)])
    email  = StringField('Email', validators=[validators.Email(message="Lütfen geçerli bir email adresi giriniz")])
    password  = PasswordField("Parola:" ,validators=[
        validators.DataRequired(message = "Lütfen bir paralo belirleyiniz..."),
        validators.EqualTo(fieldname= "confirm" , message="Parolanız uyuşmuyor")
    ])
    confirm = PasswordField("Paralonazı doğrulayınız")

class LoginForm(Form):
    username  = StringField('Kullacı Adı')
    password  = PasswordField("Parola:")



app = Flask(__name__)

app.secret_key="blog"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "ROOT"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "blog"
app.config["MYSQL_CURSORCLASS"] ="DictCursor"  #dic yapısında veri sağlar

mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/article")
def article():
    return render_template("article.html")

@app.route("/article/<string:id>")
def detail(id):
    return "Article Id:" + id

#Kayıt olma
@app.route("/register", methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        #print(form.name.raw_data)
        name = form.name.raw_data[0]
        username= form.username.raw_data[0]
        email = form.email.raw_data[0]
        password = sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()

        sorgu = "Insert into user(name,email,username,password) VALUES(%s,%s,%s,%s)"
        
        cursor.execute(sorgu,(name,email,username,password))

        mysql.connection.commit() #veri tabanına güncelleme varsa zorundayız.

        cursor.close()

        flash("Basariyla kayıt oldunuz..","success")
       
        return redirect(url_for("login"))
    else:
        return render_template("register.html", form = form)


#giriş yapma
@app.route("/login", methods = ["GET","POST"])
def login():
    form = LoginForm(request.form)

    if request.method == "POST":
        username=form.username.raw_data[0]
        password_entered=form.password.raw_data[0]
        
        cursor = mysql.connection.cursor()
        sorgu = "Select * From User where username = %s"

        result = cursor.execute(sorgu,(username,))

        if result > 0:
            data = cursor.fetchone()
            real_password = data ["password"]
            #print(form.password.raw_data[0])
            if sha256_crypt.verify(password_entered , real_password):
                flash("başarıyla giriş yaptınız","success")
                return redirect(url_for("index"))
            else:
                flash("uyumsuz","danger")
        else:
            flash("kullanıcı uyumsuz","danger")
            return redirect(url_for("login"))
 

    return render_template("login.html",form= form)
    
   

if __name__ == "__main__":
    app.run(debug=True)