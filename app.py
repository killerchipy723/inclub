from flask import Flask, render_template, request, redirect, url_for, session
from db import getConnection
from datetime import datetime
import pymysql

app = Flask(__name__)
app.secret_key = "inclub_secreto_2026"

# Login Loguot
@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    nombre = request.form["nombre"]
    clave = request.form["clave"]

    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    query = """
        SELECT idusuarios, nombre, rol, estado
        FROM usuarios
        WHERE nombre=%s AND clave=%s
    """
    cursor.execute(query, (nombre, clave))
    user = cursor.fetchone()

    if not user:
        return render_template("login.html", error="Usuario o contraseña incorrectos")

    if user["estado"] != "Activo":
        return render_template("login.html", error="Usuario inactivo")

    # 🔐 GUARDAR SESIÓN
    session["id"] = user["idusuarios"]
    session["nombre"] = user["nombre"]
    session["rol"] = user["rol"]

    if user["rol"] == "Administrador":
        return redirect(url_for("admin"))
    else:
        return redirect(url_for("ventas"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

#Admin seccion

@app.route("/admin")
def admin():
    if "id" not in session or session["rol"] != "Administrador":
        return redirect(url_for("home"))

    return render_template("admin.html",
                           usuario=session["nombre"],
                           rol=session["rol"])

#Usuarios

@app.route("/usuario")
def home_userReg():
    if "id" not in session or session["rol"] != "Administrador":
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM usuarios")
    data = cursor.fetchall()

    return render_template("usuarios.html",
                           usuarios=data,
                           user=session["nombre"],
                           rol=session["rol"])


@app.route("/reg_Usu", methods=["POST"])
def reg_usuario():
    if "id" not in session:
        return redirect(url_for("home"))

    nombre = request.form["nombre"]
    clave = request.form["clave"]
    rol = request.form["rol"]
    estado = request.form["estado"]

    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO usuarios(nombre,clave,rol,estado) VALUES (%s,%s,%s,%s)",
        (nombre, clave, rol, estado)
    )
    conexion.commit()

    return redirect(url_for("home_userReg"))


@app.route("/delete_Usuario/<int:id>")
def delete_usuario(id):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM usuarios WHERE idusuarios=%s", (id,))
    conexion.commit()

    return redirect(url_for("home_userReg"))


@app.route("/Update_Usuario/<int:id>", methods=["POST"])
def update_usuario(id):
    if "id" not in session:
        return redirect(url_for("home"))

    nombre = request.form["nombre"]
    clave = request.form["clave"]
    rol = request.form["rol"]
    estado = request.form["estado"]

    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE usuarios
        SET nombre=%s, clave=%s, rol=%s, estado=%s
        WHERE idusuarios=%s
    """, (nombre, clave, rol, estado, id))
    conexion.commit()

    return redirect(url_for("home_userReg"))

#Ventas
@app.route("/ventas")
def ventas():
    if "id" not in session:
        return redirect(url_for("home"))

    return render_template("ventas.html",
                           usuario=session["nombre"],
                           rol=session["rol"])


@app.route("/registrar_venta", methods=["POST"])
def registrar_venta():
    if "id" not in session:
        return redirect(url_for("home"))

    cliente = request.form["cliente"]
    total = request.form["total"]

    conexion = getConnection()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO ventas
        (cliente, total, vendedor_id, vendedor_nombre, fecha_hora)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        cliente,
        total,
        session["id"],
        session["nombre"],
        datetime.now()
    ))

    conexion.commit()

    return redirect(url_for("ventas"))

#-------------------------------Clientes----------------------------------
#ruta principal de clientes
@app.route("/clientes",methods=['GET'])
def home_clientes():
    conexion = getConnection()
    query = 'select * from clientes'
    cursor = conexion.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template("clientes.html",clientes=data)

#Ruta para guardar clientes
@app.route("/guardar_Clientes",methods=['POST'])
def guardar_Clientes():
    query = 'insert into clientes(apenomb,dni,cuil)VALUES(%s,%s,%s)'
    apenomb = request.form['apenomb']
    dni = request.form['dni']
    cuil = request.form['cuil']
    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute(query,(apenomb,dni,cuil))
    conexion.commit()
    msg = "Registro Exitoso de Cliente"
    return redirect(url_for('home_clientes',succes=msg))



#-------------------------------Arranque-----------------------------------
if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0')