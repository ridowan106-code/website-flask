from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# =========================
# SECRET KEY
# =========================
app.secret_key = 'secret123'

# =========================
# KONFIGURASI UPLOAD FOTO
# =========================
UPLOAD_FOLDER = 'static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# =========================
# KONFIGURASI DATABASE
# =========================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# =========================
# MEMBUAT DATABASE
# =========================
db = SQLAlchemy(app)

# =========================
# TABEL USER
# =========================
class User(db.Model):

    # PRIMARY KEY
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # USERNAME
    username = db.Column(
        db.String(100),
        unique=True
    )

    # PASSWORD
    password = db.Column(
        db.String(100)
    )


# =========================
# TABEL MAHASISWA
# =========================
class Mahasiswa(db.Model):

    # PRIMARY KEY
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # NAMA MAHASISWA
    nama = db.Column(
        db.String(100)
    )

    # NIM
    nim = db.Column(
        db.String(100)
    )

    # JURUSAN
    jurusan = db.Column(
        db.String(100)
    )

    # FOTO
    foto = db.Column(
        db.String(200)
    )


# =========================
# HOME
# =========================
@app.route('/')
def home():

    return render_template('index.html')


# =========================
# REGISTER
# =========================
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        # CEK USER SUDAH ADA ATAU BELUM
        cek_user = User.query.filter_by(
            username=username
        ).first()

        # JIKA USER SUDAH ADA
        if cek_user:

            return "Username sudah digunakan"

        # SIMPAN USER BARU
        user_baru = User(
            username=username,
            password=password
        )

        db.session.add(user_baru)

        db.session.commit()

        return redirect('/login')

    return render_template('register.html')


# =========================
# LOGIN
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        # CEK USER
        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        # JIKA LOGIN BERHASIL
        if user:

            session['username'] = user.username

            return redirect('/dashboard')

        # JIKA LOGIN GAGAL
        else:

            return "Username atau Password Salah"

    return render_template('login.html')


# =========================
# DASHBOARD
# =========================
# =========================
# DASHBOARD
# =========================
@app.route('/dashboard')
def dashboard():

    # CEK LOGIN
    if 'username' not in session:

        return redirect('/login')

    # TOTAL MAHASISWA
    total_mahasiswa = Mahasiswa.query.count()

    # TOTAL USER
    total_user = User.query.count()

    return render_template(
        'dashboard.html',

        username=session['username'],

        total_mahasiswa=total_mahasiswa,

        total_user=total_user
    )

    # CEK LOGIN
    if 'username' not in session:

        return redirect('/login')

    # TOTAL MAHASISWA
    total_mahasiswa = Mahasiswa.query.count()

    # TOTAL USER
    total_user = User.query.count()

    return render_template(
        'dashboard.html',
        username=session['username'],
        total_mahasiswa=total_mahasiswa,
        total_user=total_user
    )


# =========================
# LOGOUT
# =========================
@app.route('/logout')
def logout():

    session.pop('username', None)

    return redirect('/login')


# =========================
# DATA MAHASISWA
# =========================
# =========================
# DATA MAHASISWA
# =========================
@app.route('/mahasiswa')
def mahasiswa():

    # Ambil nomor halaman
    page = request.args.get('page', 1, type=int)

    # Pagination
    data_mahasiswa = Mahasiswa.query.paginate(
        page=page,
        per_page=5
    )

    return render_template(
        'mahasiswa.html',
        mahasiswa=data_mahasiswa
    )

    # CEK LOGIN
    if 'username' not in session:

        return redirect('/login')

    # AMBIL SEMUA DATA
    data_mahasiswa = Mahasiswa.query.all()

    return render_template(
        'mahasiswa.html',
        data=data_mahasiswa
    )


# =========================
# TAMBAH DATA MAHASISWA
# =========================
@app.route('/tambah', methods=['GET', 'POST'])
def tambah():

    # CEK LOGIN
    if 'username' not in session:

        return redirect('/login')

    # JIKA FORM DISUBMIT
    if request.method == 'POST':

        # AMBIL DATA FORM
        nama = request.form['nama']

        nim = request.form['nim']

        jurusan = request.form['jurusan']

        # AMBIL FILE FOTO
        foto = request.files['foto']

        # AMANKAN NAMA FILE
        nama_file = secure_filename(
            foto.filename
        )

        # SIMPAN FOTO
        foto.save(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                nama_file
            )
        )

        # SIMPAN DATA KE DATABASE
        data_baru = Mahasiswa(
            nama=nama,
            nim=nim,
            jurusan=jurusan,
            foto=nama_file
        )

        db.session.add(data_baru)

        db.session.commit()

        return redirect('/mahasiswa')

    return render_template('tambah.html')


# =========================
# EDIT DATA MAHASISWA
# =========================
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    data = Mahasiswa.query.get(id)

    if request.method == 'POST':

        data.nama = request.form['nama']
        data.nim = request.form['nim']
        data.jurusan = request.form['jurusan']

        # FOTO
        foto = request.files['foto']

        # JIKA FOTO DIGANTI
        if foto.filename != '':

            nama_foto = foto.filename

            foto.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    nama_foto
                )
            )

            data.foto = nama_foto

        db.session.commit()

        return redirect('/mahasiswa')

    return render_template(
        'edit.html',
        data=data
    )

    # CEK LOGIN
    if 'username' not in session:

        return redirect('/login')

    # AMBIL DATA BERDASARKAN ID
    data = Mahasiswa.query.get(id)

    if request.method == 'POST':

        data.nama = request.form['nama']

        data.nim = request.form['nim']

        data.jurusan = request.form['jurusan']

        # CEK JIKA ADA FOTO BARU
        foto = request.files['foto']

        if foto.filename != "":

            nama_file = secure_filename(
                foto.filename
            )

            foto.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    nama_file
                )
            )

            data.foto = nama_file

        db.session.commit()

        return redirect('/mahasiswa')

    return render_template(
        'edit.html',
        data=data
    )


# =========================
# HAPUS DATA MAHASISWA
# =========================
@app.route('/hapus/<int:id>')
def hapus(id):

    # CEK LOGIN
    if 'username' not in session:

        return redirect('/login')

    # AMBIL DATA
    data = Mahasiswa.query.get(id)

    # HAPUS DATA
    db.session.delete(data)

    db.session.commit()

    return redirect('/mahasiswa')


# =========================
# MENJALANKAN FLASK
# =========================
if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', port=10000)