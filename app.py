from flask import Flask, render_template, request, redirect, url_for, session
import uuid
from db import getConnection
from datetime import datetime
import pymysql



app = Flask(__name__)
app.secret_key = "inclub_secreto_2026"

#---------------------------------Login--------------------------------------------- 
@app.route("/", methods=["GET"])
def home():
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    nombre = request.form["nombre"]
    clave = request.form["clave"]
    equipo = obtener_mac()

    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    # 1️⃣ VALIDAR USUARIO
    cursor.execute("""
        SELECT idusuarios, nombre, rol, estado
        FROM usuarios
        WHERE nombre=%s AND clave=%s
    """, (nombre, clave))
    user = cursor.fetchone()

    if not user:
        conexion.close()
        return render_template("login.html", error="Usuario o contraseña incorrectos")

    if user["estado"] != "Activo":
        conexion.close()
        return render_template("login.html", error="Usuario inactivo")

    # 🟢 BYPASS ADMINISTRADOR
    if user["rol"] == "Administrador":
        session["id"] = user["idusuarios"]
        session["nombre"] = user["nombre"]
        session["rol"] = user["rol"]
        session["equipo"] = equipo  # IP actual
        conexion.close()
        return redirect(url_for("admin"))

    # 2️⃣ VALIDAR PUNTO (NO ADMIN)
    cursor.execute("""
        SELECT idpunto, nombre
        FROM puntos_venta
        WHERE idequipo=%s AND estado='Activo'
    """, (equipo,))
    punto = cursor.fetchone()

    if not punto:
        conexion.close()
        return render_template(
            "login.html",
            error="Este equipo no está habilitado como punto de venta"
        )

    # 3️⃣ VALIDAR USUARIO ↔ PUNTO
    cursor.execute("""
        SELECT 1
        FROM usuarios_puntos
        WHERE idusuario=%s AND idpunto=%s
        LIMIT 1
    """, (user["idusuarios"], punto["idpunto"]))

    if not cursor.fetchone():
        conexion.close()
        return render_template(
            "login.html",
            error="Usuario no autorizado para este punto de venta"
        )

    # 4️⃣ GUARDAR SESIÓN
    session["id"] = user["idusuarios"]
    session["nombre"] = user["nombre"]
    session["rol"] = user["rol"]
    session["idpunto"] = punto["idpunto"]
    session["punto"] = punto["nombre"]

    conexion.close()
    return redirect(url_for("ventas"))



# =======================
# LOGOUT
# =======================

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
    conexion.close()

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
    conexion.close()

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
    conexion.close()

    return redirect(url_for("home_userReg"))
#--------------------------------------Usuarios Puntos---------------------------

# ==============================
# RUTA PRINCIPAL ASIGNACIONES
# ==============================

@app.route("/usuarios_puntos")
def usuarios_puntos():
    if "id" not in session or session["rol"] != "Administrador":
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    # Usuarios
    cursor.execute("SELECT idusuarios, nombre FROM usuarios WHERE estado='Activo'")
    usuarios = cursor.fetchall()

    # Puntos de venta
    cursor.execute("SELECT idpunto, nombre, idequipo FROM puntos_venta WHERE estado='Activo'")
    puntos = cursor.fetchall()

    # Asignaciones
    cursor.execute("""
        SELECT up.id,
               u.nombre AS usuario,
               p.nombre AS punto,
               p.idequipo
        FROM usuarios_puntos up
        JOIN usuarios u ON u.idusuarios = up.idusuario
        JOIN puntos_venta p ON p.idpunto = up.idpunto
    """)
    asignaciones = cursor.fetchall()

    conexion.close()

    message = request.args.get("message")

    return render_template(
        "usuarios_puntos.html",
        usuarios=usuarios,
        puntos=puntos,
        asignaciones=asignaciones,
        message=message,
        usuario=session["nombre"],
        rol=session["rol"]
    )


# ==============================
# REGISTRAR ASIGNACIÓN
# ==============================

@app.route("/reg_usuario_punto", methods=["POST"])
def reg_usuario_punto():
    if "id" not in session or session["rol"] != "Administrador":
        return redirect(url_for("home"))

    idusuario = request.form["idusuario"]
    idpunto = request.form["idpunto"]

    conexion = getConnection()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            INSERT INTO usuarios_puntos (idusuario, idpunto)
            VALUES (%s, %s)
        """, (idusuario, idpunto))
        conexion.commit()
        msg = "Usuario asignado correctamente!"
    except Exception:
        msg = "El usuario ya está asignado a ese punto"

    conexion.close()

    return redirect(url_for("usuarios_puntos", message=msg))


# ==============================
# ELIMINAR ASIGNACIÓN
# ==============================

@app.route("/delete_usuario_punto/<int:id>")
def delete_usuario_punto(id):
    if "id" not in session or session["rol"] != "Administrador":
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute(
        "DELETE FROM usuarios_puntos WHERE id=%s",
        (id,)
    )
    conexion.commit()
    conexion.close()

    return redirect(
        url_for(
            "usuarios_puntos",
            message="Asignación eliminada correctamente"
        )
    )


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
    conexion.close()
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
    conexion.close()

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
    conexion.close()
    return redirect(url_for('home_clientes',message = 'Cliente Eliminado Correctamente'))
# ------------------------------Jornadas----------------------------------

# ruta jornadas
@app.route("/Jornadas", methods=['GET'])
def home_Jornadas():
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    # Jornadas
    cursor.execute("SELECT * FROM jornadas")
    jornadas = cursor.fetchall()

    # 👉 Puntos de venta (equipos)
    cursor.execute("SELECT idpunto, nombre FROM puntos_venta WHERE estado='Activo'")
    puntos_venta = cursor.fetchall()

    # 👉 Productos
    cursor.execute("SELECT idproductos, nombre, importe FROM productos WHERE estado='Activo'")
    productos = cursor.fetchall()

    conexion.close()

    message = request.args.get('message')

    return render_template(
        "jornadas.html",
        jornadas=jornadas,
        puntos_venta=puntos_venta,   # 👈 ESTO FALTABA
        productos=productos,         # 👈 Y ESTO TAMBIÉN
        message=message,
        usuario=session["nombre"],
        rol=session["rol"]
    )


# Ruta para guardar Jornadas
@app.route("/guardar_Jornadas", methods=["POST"])
def save_Jornadas():
    # Seguridad: usuario logueado
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    try:
        # ================= DATOS JORNADA =================
        nombre = request.form["nombre"].upper()
        clave = request.form["clave"]
        finicio = request.form["finicio"]
        ffinal = request.form["ffin"]

        cursor.execute("""
            INSERT INTO jornadas (nombre, clave, finicio, ffinal, estado)
            VALUES (%s, %s, %s, %s, 'Activo')
        """, (nombre, clave, finicio, ffinal))

        # ID de la jornada recién creada
        idjornada = cursor.lastrowid

        # ================= EQUIPOS (PUNTOS DE VENTA) =================
        if request.form.get("equipos_todos"):
            cursor.execute("""
                SELECT idpunto
                FROM puntos_venta
                WHERE estado = 'Activo'
            """)
            puntos = cursor.fetchall()

            for p in puntos:
                cursor.execute("""
                    INSERT INTO jornadas_puntos (idjornada, idpunto)
                    VALUES (%s, %s)
                """, (idjornada, p["idpunto"]))
        else:
            equipos = request.form.getlist("equipos[]")
            for e in equipos:
                cursor.execute("""
                    INSERT INTO jornadas_puntos (idjornada, idpunto)
                    VALUES (%s, %s)
                """, (idjornada, e))

        # ================= PRODUCTOS =================
        if request.form.get("productos_todos"):
            cursor.execute("""
                SELECT idproductos
                FROM productos
                WHERE estado = 'Activo'
            """)
            productos = cursor.fetchall()

            for pr in productos:
                cursor.execute("""
                    INSERT INTO jornadas_productos (idjornada, idproducto)
                    VALUES (%s, %s)
                """, (idjornada, pr["idproductos"]))
        else:
            productos = request.form.getlist("productos[]")
            for pr in productos:
                cursor.execute("""
                    INSERT INTO jornadas_productos (idjornada, idproducto)
                    VALUES (%s, %s)
                """, (idjornada, pr))

        conexion.commit()

    except Exception as e:
        conexion.rollback()
        print("❌ Error al guardar jornada:", e)
        return redirect(
            url_for("home_Jornadas", message="Error al crear la jornada")
        )

    finally:
        conexion.close()

    return redirect(
        url_for("home_Jornadas", message="Jornada creada correctamente")
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
    conexion.close()

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
    conexion.close()

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
    conexion.close()
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
    conexion.close()
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
    conexion.close()

    return redirect(url_for("home_Jornadas",message ='Producto eliminado correctamente'))

#------------------------------Punto de venta-----------------------------
# Ruta para obtener "MAC" (ahora IP real del cliente)
def obtener_mac():
    """
    Devuelve la IP del equipo cliente.
    Se mantiene el nombre de la función para no romper el sistema.
    """
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr


def obtener_punto_por_mac(cursor):
    mac = obtener_mac()
    query = """
        SELECT idpunto, nombre
        FROM puntos_venta
        WHERE idequipo=%s AND estado='Activo'
    """
    cursor.execute(query, (mac,))
    return cursor.fetchone()


# ==============================
# RUTA PRINCIPAL PUNTOS DE VENTA
# ==============================

@app.route("/puntos_venta", methods=['GET'])
def punto_venta():
    mac = obtener_mac()
    message = request.args.get('message')

    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM puntos_venta')
    data = cursor.fetchall()
    conexion.close()

    return render_template(
        'punto_venta.html',
        mac=mac,
        message=message,
        puntos_venta=data,
        rol=session['rol'],
        usuario=session['nombre']
    )


# ============================
# RUTA PARA GUARDAR PUNTO VENTA
# ============================

@app.route("/guardar_Puntos_venta", methods=['POST'])
def save_punto():
    conexion = getConnection()
    cursor = conexion.cursor()

    nombre = request.form['nombre'].upper()
    idequipo = request.form.get('idequipo')

    # Si no se carga equipo, se asigna automáticamente el cliente actual
    if not idequipo:
        idequipo = obtener_mac()

    estado = request.form['estado']

    sql = """
        INSERT INTO puntos_venta (nombre, idequipo, estado)
        VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (nombre, idequipo, estado))
    conexion.commit()
    conexion.close()

    return redirect(
        url_for(
            'punto_venta',
            message='Punto de Venta asignado correctamente!'
        )
    )


# ===============================
# RUTA PARA MODIFICAR PUNTO VENTA
# ===============================

@app.route("/Update_Puntos_venta/<int:id>", methods=['POST'])
def update_Puntos(id):
    conexion = getConnection()
    cursor = conexion.cursor()

    nombre = request.form['nombre'].upper()
    idequipo = request.form['idequipo']
    estado = request.form['estado']

    query = """
        UPDATE puntos_venta
        SET nombre=%s, idequipo=%s, estado=%s
        WHERE idpunto=%s
    """
    cursor.execute(query, (nombre, idequipo, estado, id))
    conexion.commit()
    conexion.close()

    return redirect(
        url_for(
            'punto_venta',
            message='Punto de Venta Modificado Correctamente'
        )
    )


# =============================
# RUTA PARA ELIMINAR PUNTO VENTA
# =============================

@app.route("/delete_Puntos_venta/<int:id>")
def delete_puntos(id):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute(
        "DELETE FROM puntos_venta WHERE idpunto=%s",
        (id,)
    )
    conexion.commit()
    conexion.close()

    return redirect(
        url_for(
            "punto_venta",
            message='Punto de venta eliminado correctamente'
        )
    )






#-------------------------------Arranque-----------------------------------
if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0')