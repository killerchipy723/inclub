from flask import Flask, render_template, request, redirect, url_for, session
import uuid
from db import getConnection
from datetime import datetime
import pymysql

app = Flask(__name__)
app.secret_key = "inclub_secreto_2026"

#---------------------------------Login--------------------------------------------- 
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

#----------------------------------Admin------------------------------------------------

@app.route("/admin")
def admin():
    if "id" not in session or session["rol"] != "Administrador":
        return redirect(url_for("home"))

    return render_template("admin.html",
                           usuario=session["nombre"],
                           rol=session["rol"])

#------------------------------------Usuarios--------------------------------------------
#Ruta Principal de Usuarios
@app.route("/usuario")
def home_userReg():
    if "id" not in session or session["rol"] != "Administrador":
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM usuarios")
    data = cursor.fetchall()
    message = request.args.get('message')

    return render_template("usuarios.html",
                           usuarios=data,
                           message = message,
                           usuario=session["nombre"],
                           rol=session["rol"])

#Ruta Registro de usuarios
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

    return redirect(url_for("home_userReg",message='Usuario Registrado Correctamente!'))

#Ruta para Eliminar Usuarios
@app.route("/delete_Usuario/<int:id>")
def delete_usuario(id):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM usuarios WHERE idusuarios=%s", (id,))
    conexion.commit()

    return redirect(url_for("home_userReg",message = 'Registro Eliminado Correctamente!'))


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

#--------------------------------------Ventas-------------------------------------
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
    if "id" not in session['rol']!="Administrador":
        return redirect(url_for('home'))
    
    conexion = getConnection()
    query = 'select * from clientes'
    cursor = conexion.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query)
    data = cursor.fetchall()
    message = request.args.get('message')  # 👈 ACA SÍ
    return render_template("clientes.html",
                           clientes=data,
                           message = message,
                           usuario=session["nombre"],
                           rol=session["rol"])

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
    return redirect(url_for('home_clientes',message = 'Cliente Registrado Correctamente'))


#Ruta para modificar Clientes
@app.route("/Update_Clientes/<int:id>", methods=["POST"])
def update_Clientes(id):
    if "id" not in session:
        return redirect(url_for("home"))

    apenomb = request.form["apenomb"]
    dni = request.form["dni"]
    cuil = request.form["cuil"]   
    query = 'UPDATE clientes SET apenomb=%s, dni=%s, cuil=%s WHERE idclientes=%s'
    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute(query,(apenomb,dni,cuil,id))    
    conexion.commit()

    return redirect(url_for('home_clientes',message = 'Cliente Actualizado Correctamente'))


#Ruta para Eliminar Clientes
@app.route("/delete_Clientes/<int:id>")
def eliminar_Clientes(id):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM clientes WHERE idclientes=%s", (id,))
    conexion.commit()
    return redirect(url_for('home_clientes',message = 'Cliente Eliminado Correctamente'))
# ------------------------------Jornadas----------------------------------

# ruta jornadas
@app.route("/Jornadas", methods=['GET'])
def home_Jornadas():
    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute("select * from jornadas")
    data = cursor.fetchall()

    message = request.args.get('message')  # 👈 ACA SÍ

    return render_template(
        "jornadas.html",
        jornadas=data,
        message=message,
        usuario=session["nombre"],
        rol=session["rol"]
    )
@app.route("/guardar_Jornadas", methods=['POST'])
def save_Jornadas():
    conexion = getConnection()

    nombre = request.form['nombre'].upper()
    clave = request.form['clave']
    finicio = request.form['finicio']
    ffinal = request.form['ffin']

    sql = '''
        insert into jornadas(nombre, clave, finicio, ffinal)
        values (%s, %s, %s, %s)
    '''

    cursor = conexion.cursor()
    cursor.execute(sql, (nombre, clave, finicio, ffinal))
    conexion.commit()

    return redirect(
        url_for('home_Jornadas', message='Registro Exitoso')
    )

#Ruta para modificar Jornadas
@app.route("/Update_Jornadas/<int:id>", methods=["POST"])
def update_Jornada(id):
    if "id" not in session:
        return redirect(url_for("home"))

    nombre = request.form["nombre"]
    clave = request.form["clave"]
    finicio = request.form["finicio"]  
    ffinal = request.form["ffinal"]  
    
    query = 'UPDATE jornadas SET nombre=%s, clave=%s, finicio=%s,ffinal=%s WHERE idclientes=%s'
    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute(query,(nombre,clave,finicio,ffinal,id))    
    conexion.commit()

    return redirect(url_for("home_Jornadas",message='Registro Actualizado Correctamente'))

#Ruta para Eliminar Jornadas
@app.route("/delete_Jornadas/<int:id>")
def delete_jornada(id):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM jornadas WHERE idjornada=%s", (id,))
    conexion.commit()

    return redirect(url_for("home_Jornadas",message ='Jornada eliminada correctamente'))

#-----------------------------Productos----------------------------------
#Ruta Principal de productos
@app.route("/Productos")
def home_Productos():
    conexion = getConnection()
    query = 'select * from productos'
    message = request.args.get('message')
    cursor = conexion.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template('productos.html',
                           message = message,
                           productos=data,
                           rol=session['rol'],
                           usuario=session['nombre'])

#Ruta para guardar Productos

@app.route("/guardar_Productos",methods=['POST'])
def save_Productos():
    conexion = getConnection()
    nombre = request.form['nombre'].upper()
    importe = request.form['importe']
    estado = request.form['estado']
    query = 'insert into productos(nombre,importe,estado)VALUES(%s,%s,%s)'
    cursor = conexion.cursor()
    cursor.execute(query,(nombre,importe,estado))
    conexion.commit()
    return redirect(url_for('home_Productos',message='Producto Agregado Correctamente'))

#Ruta para modificar productos
@app.route("/Update_Productos/<int:id>",methods=['POST'])
def update_Productos(id):
    conexion = getConnection()
    nombre = request.form['nombre'].upper()
    importe = request.form['importe']
    estado = request.form['estado']
    query = 'update productos set nombre=%s,importe=%s,estado=%s where idproductos=%s'
    cursor = conexion.cursor()
    cursor.execute(query,(nombre,importe,estado,id))
    conexion.commit()
    return redirect(url_for('home_Productos',message='Producto Modificado Correctamente'))

#Ruta para eliminar productos
@app.route("/delete_Productos/<int:id>")
def delete_producto(id):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE idproductos=%s", (id,))
    conexion.commit()

    return redirect(url_for("home_Jornadas",message ='Producto eliminado correctamente'))

#------------------------------Punto de venta-----------------------------
#ruta para obtener mac
def obtener_mac():
    mac = uuid.getnode()
    return ':'.join(f'{(mac >> ele) & 0xff:02x}' for ele in range(40, -1, -8))


#Ruta Principal Puntos de Venta
@app.route("/puntos_venta",methods=['GET'])
def punto_venta():
    mac = obtener_mac()
    message = request.args.get('message')
    conexion = getConnection()
    sql = 'select * from puntos_venta'
    cursor = conexion.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    return render_template('punto_venta.html',mac = mac,message=message,
                           puntos_venta=data,
                           rol=session['rol'],
                           usuario=session['nombre'])

#Ruta para asignar puntos de venta
@app.route("/guardar_Puntos_venta",methods=['POST'])
def save_punto():
    conexion = getConnection()
    sql = 'INSERT INTO puntos_venta(nombre,idequipo,estado)VALUES(%s,%s,%s)'
    nombre = request.form['nombre'].upper()
    idequipo = request.form['idequipo']
    estado = request.form['estado']
    cursor = conexion.cursor()
    cursor.execute(sql,(nombre,idequipo,estado))
    conexion.commit()
    return redirect(url_for('punto_venta',message='Punto de Eventa asignado correctamente!'))

#Ruta para modificar productos
@app.route("/Update_Puntos_venta/<int:id>",methods=['POST'])
def update_Puntos(id):
    conexion = getConnection()
    nombre = request.form['nombre'].upper()
    idequipo = request.form['idequipo']
    estado = request.form['estado']
    query = 'update puntos_venta set nombre=%s,idequipo=%s,estado=%s where idpunto=%s'
    cursor = conexion.cursor()
    cursor.execute(query,(nombre,idequipo,estado,id))
    conexion.commit()
    return redirect(url_for('punto_venta',message='Punto de Venta Modificado Correctamente'))

#Ruta para eliminar productos
@app.route("/delete_Puntos_venta/<int:id>")
def delete_puntos(id):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM puntos_venta WHERE idpunto=%s", (id,))
    conexion.commit()

    return redirect(url_for("home_Jornadas",message ='Punto de venta eliminado correctamente'))






#-------------------------------Arranque-----------------------------------
if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0')