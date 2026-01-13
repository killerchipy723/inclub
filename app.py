from flask import Flask, render_template, request, redirect, url_for, session,jsonify
import uuid
from db import getConnection
from datetime import datetime
import pymysql
import qrcode
import base64
from io import BytesIO





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
    return redirect(url_for("ventas_home"))



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

@app.route("/ventas", methods=["GET"])
def ventas_home():
    if "id" not in session:
        return redirect(url_for("home"))

    message = request.args.get("message")

    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    # -------------------- JORNADA ACTIVA --------------------
    cursor.execute("""
        SELECT idjornada, nombre
        FROM jornadas
        WHERE estado = 'Activo'
        LIMIT 1
    """)
    jornada = cursor.fetchone()

    if not jornada:
        conexion.close()
        return "ERROR: No hay jornada activa"

    session["idjornada"] = jornada["idjornada"]
    idjornada = jornada["idjornada"]
    idpunto = session.get("idpunto")


    # -------------------- RECAUDACIÓN TOTAL --------------------
    cursor.execute("""
    SELECT IFNULL(SUM(total), 0) AS recaudacion
    FROM ventas
    WHERE idjornada = %s
      AND idpunto = %s
      AND estado = 'OK'
""", (idjornada, idpunto))
    recaudacion = cursor.fetchone()["recaudacion"]

    # -------------------- CLIENTES --------------------
    cursor.execute("""
        SELECT idclientes, apenomb
        FROM clientes
        ORDER BY apenomb
    """)
    clientes = cursor.fetchall()

    # -------------------- MODOS DE PAGO --------------------
    cursor.execute("""
        SELECT idmodopago, modo
        FROM modopago
        ORDER BY modo
    """)
    modopago = cursor.fetchall()

    # -------------------- PRODUCTOS --------------------
    cursor.execute("""
        SELECT p.idproductos, p.nombre, p.importe
        FROM productos p
        JOIN jornadas_productos jp ON p.idproductos = jp.idproducto
        JOIN jornadas j ON jp.idjornada = j.idjornada
        WHERE p.estado = 'Activo'
        AND j.estado = 'Activo'
        ORDER BY p.nombre
    """)
    productos = cursor.fetchall()

    # -------------------- CLIENTES PARA PUNTOS --------------------
    cursor.execute("""
        SELECT idclientes, apenomb
        FROM clientes
        ORDER BY apenomb
    """)
    clientes_puntos = cursor.fetchall()

    conexion.close()

    return render_template(
        "ventas.html",
        usuario=session["nombre"],
        rol=session["rol"],
        message=message,
        jornada=jornada,
        recaudacion=recaudacion,
        clientes=clientes,
        modopago=modopago,
        productos=productos,
        clientes_puntos=clientes_puntos
    )




@app.route("/registrar_venta", methods=["POST"])
def registrar_venta():
    if "id" not in session:
        return redirect(url_for("home"))

    # ---------------- DATOS GENERALES ----------------
    idusuario = session["id"]
    idpunto = session["idpunto"]
    idjornada = session["idjornada"]

    idcliente = request.form.get("cliente")
    idmodopago = request.form.get("modopago")
    total_str = request.form.get("total", "0")

# Quita separador de miles y cambia coma por punto
    total_str = total_str.replace(".", "").replace(",", ".")

    total = float(total_str)


    productos = request.form.getlist("productos[]")
    cantidades = request.form.getlist("cantidades[]")
    precios = request.form.getlist("precios[]")
    cortesias = request.form.getlist("cortesias[]")

    conexion = getConnection()
    cursor = conexion.cursor()

    try:
        qr_token = uuid.uuid4().hex

        # ---------------- INSERT VENTA ----------------
        cursor.execute("""
            INSERT INTO ventas
            (idjornada, idusuario, idpunto, idclientes, idmodopago,
             total, descuento_total, fecha_hora, estado, observaciones, puntos_ganados,qr_token)
            VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),'OK','',0,%s)
        """, (
            idjornada,
            idusuario,
            idpunto,
            idcliente if idcliente != "0" else None,
            idmodopago,
            total,
            0,
            qr_token
        ))

        idventa = cursor.lastrowid

        # ---------------- DETALLE DE VENTA ----------------
        total_puntos = 0

        for i in range(len(productos)):
            idproducto = productos[i]
            cantidad = int(cantidades[i])
            precio = float(precios[i])
            es_cortesia = cortesias[i] == "true"

            subtotal = 0 if es_cortesia else cantidad * precio

            cursor.execute("""
                INSERT INTO ventas_detalle
                (idventa, idproductos, cantidad, precio_unitario, subtotal, cortesia)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (
                idventa,
                idproducto,
                cantidad,
                precio,
                subtotal,
                es_cortesia
            ))

            # -------- PUNTOS (ejemplo: 1 punto cada $100) --------
            if not es_cortesia:
                total_puntos += int(subtotal // 100)

        # ---------------- ACTUALIZAR PUNTOS ----------------
        cursor.execute("""
            UPDATE ventas
            SET puntos_ganados = %s
            WHERE idventa = %s
        """, (total_puntos, idventa))

        conexion.commit()

    except Exception as e:
        conexion.rollback()
        print("ERROR REGISTRAR VENTA:", e)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        conexion.close()

    return jsonify({
    "success": True,
    "idventa": idventa
})




#finalizar jornada
@app.route("/finalizar_jornada", methods=["POST"])
def finalizar_jornada():
    if "id" not in session:
        return redirect(url_for("home"))

    idjornada = session.get("idjornada")

    if not idjornada:
        return redirect(url_for("ventas"))

    conexion = getConnection()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE jornadas
        SET estado = 'Cerrado'
        WHERE idjornada = %s
    """, (idjornada,))

    conexion.commit()
    conexion.close()

    session.pop("idjornada", None)

    return redirect(url_for("ventas", message="Jornada finalizada"))




#-------------------------------Clientes----------------------------------
#ruta principal de clientes


# Ruta principal clientes
@app.route("/clientes", methods=['GET'])
def home_clientes():
    # Solo Administrador
    if "id" not in session or session['rol'] != "Administrador":
        return redirect(url_for('home'))

    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM clientes")
    data = cursor.fetchall()
    message = request.args.get('message')  # 👈 mensaje de confirmación
    conexion.close()

    return render_template(
        "clientes.html",
        clientes=data,
        message=message,
        usuario=session["nombre"],
        rol=session["rol"]
    )


# Ruta para guardar clientes
@app.route("/guardar_Clientes", methods=['POST'])
def guardar_Clientes():
    if "id" not in session:
        return redirect(url_for('home'))

    apenomb = request.form['apenomb'].upper()
    dni = request.form['dni']
    cuil = request.form['cuil']
    correo = request.form['correo']
    fecha_nacimiento = request.form['fecha_nacimiento'] or None  # Puede estar vacío

    query = """
        INSERT INTO clientes (apenomb, dni, cuil, correo, fecha_nacimiento)
        VALUES (%s, %s, %s, %s, %s)
    """

    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute(query, (apenomb, dni, cuil, correo, fecha_nacimiento))
    conexion.commit()
    conexion.close()

    return redirect(url_for('home_clientes', message='Cliente Registrado Correctamente'))


# Ruta para modificar clientes
@app.route("/Update_Clientes/<int:id>", methods=["POST"])
def update_Clientes(id):
    if "id" not in session:
        return redirect(url_for("home"))

    apenomb = request.form["apenomb"].upper()
    dni = request.form["dni"]
    cuil = request.form["cuil"]
    correo = request.form["correo"]
    fecha_nacimiento = request.form["fecha_nacimiento"] or None

    query = """
        UPDATE clientes
        SET apenomb=%s, dni=%s, cuil=%s, correo=%s, fecha_nacimiento=%s
        WHERE idclientes=%s
    """

    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute(query, (apenomb, dni, cuil, correo, fecha_nacimiento, id))
    conexion.commit()
    conexion.close()

    return redirect(url_for('home_clientes', message='Cliente Actualizado Correctamente'))


# Ruta para eliminar clientes
@app.route("/delete_Clientes/<int:id>")
def eliminar_Clientes(id):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM clientes WHERE idclientes=%s", (id,))
    conexion.commit()
    conexion.close()

    return redirect(url_for('home_clientes', message='Cliente Eliminado Correctamente'))

#Buscar Clientes
@app.route("/buscar_clientes")
def buscar_clientes():
    q = request.args.get("q", "").strip()

    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT idclientes, apenomb, dni
        FROM clientes
        WHERE apenomb LIKE %s
           OR dni LIKE %s
        ORDER BY apenomb
        LIMIT 10
    """, (f"%{q}%", f"%{q}%"))

    clientes = cursor.fetchall()
    conexion.close()

    return jsonify(clientes)

#Guardar Clientes Modal
@app.route("/guardar_ClientesMODAL", methods=['POST'])
def guardar_ClientesMOD():
    if "id" not in session:
        return redirect(url_for('home'))

    apenomb = request.form['apenomb'].upper()
    dni = request.form['dni']
    cuil = request.form['cuil']
    correo = request.form['correo']
    fecha_nacimiento = request.form['fecha_nacimiento'] or None  # Puede estar vacío

    query = """
        INSERT INTO clientes (apenomb, dni, cuil, correo, fecha_nacimiento)
        VALUES (%s, %s, %s, %s, %s)
    """

    conexion = getConnection()
    cursor = conexion.cursor()
    cursor.execute(query, (apenomb, dni, cuil, correo, fecha_nacimiento))
    conexion.commit()
    conexion.close()

    return redirect(url_for('ventas_home', message='Cliente Registrado Correctamente'))

# ------------------------------Jornadas----------------------------------

# =====================================================
# LISTADO GENERAL DE JORNADAS
# =====================================================
@app.route("/Jornadas", methods=["GET"])
def jornadas_listado():
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT idjornada, nombre, finicio, ffinal, estado
        FROM jornadas
        ORDER BY idjornada DESC
    """)
    jornadas = cursor.fetchall()

    cursor.execute("""
        SELECT idpunto, nombre
        FROM puntos_venta
        WHERE estado='Activo'
    """)
    puntos_venta = cursor.fetchall()

    cursor.execute("""
        SELECT idproductos, nombre, importe
        FROM productos
        WHERE estado='Activo'
    """)
    productos = cursor.fetchall()

    conexion.close()

    return render_template(
        "jornadas.html",
        jornadas=jornadas,
        puntos_venta=puntos_venta,
        productos=productos,
        usuario=session["nombre"],
        rol=session["rol"]
    )

# =====================================================
# CREAR JORNADA
# =====================================================
@app.route("/guardar_Jornadas", methods=["POST"])
def jornadas_crear():
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    try:
        nombre = request.form["nombre"].upper()
        clave = request.form["clave"]
        finicio = request.form["finicio"]
        ffinal = request.form["ffin"]

        cursor.execute("""
            INSERT INTO jornadas (nombre, clave, finicio, ffinal, estado)
            VALUES (%s, %s, %s, %s, 'Activo')
        """, (nombre, clave, finicio, ffinal))

        idjornada = cursor.lastrowid

        # --------- EQUIPOS ---------
        equipos = request.form.getlist("equipos[]")
        for e in equipos:
            cursor.execute("""
                INSERT INTO jornadas_puntos (idjornada, idpunto)
                VALUES (%s, %s)
            """, (idjornada, e))

        # --------- PRODUCTOS ---------
        productos = request.form.getlist("productos[]")
        for p in productos:
            cursor.execute("""
                INSERT INTO jornadas_productos (idjornada, idproducto)
                VALUES (%s, %s)
            """, (idjornada, p))

        conexion.commit()

    except Exception as e:
        conexion.rollback()
        print("❌ Error al crear jornada:", e)
        return redirect(url_for("jornadas_listado"))

    finally:
        conexion.close()

    return redirect(url_for("jornadas_listado"))
# =====================================================
# ACTUALIZAR JORNADA
# =====================================================
@app.route("/Update_Jornadas/<int:idjornada>", methods=["POST"])
def jornadas_actualizar(idjornada):
    if "id" not in session:
        return redirect(url_for("home"))

    nombre = request.form["nombre"]
    clave = request.form["clave"]
    finicio = request.form["finicio"]
    ffinal = request.form["ffinal"]

    conexion = getConnection()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE jornadas
        SET nombre = %s,
            clave = %s,
            finicio = %s,
            ffinal = %s
        WHERE idjornada = %s
    """, (nombre, clave, finicio, ffinal, idjornada))

    conexion.commit()
    conexion.close()

    return redirect(url_for("jornadas_admin"))


# =====================================================
# LISTADO / ADMINISTRACIÓN DE JORNADAS
# =====================================================
@app.route("/Jornadas_Admin")
def jornadas_admin():
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT 
            idjornada,
            nombre,
            clave,
            finicio,
            ffinal,
            estado
        FROM jornadas
        ORDER BY idjornada DESC
    """)
    jornadas = cursor.fetchall()

    conexion.close()

    return render_template(
        "jornadas_admin.html",
        jornadas=jornadas,
        usuario=session["nombre"],
        rol=session["rol"]
    )


# =====================================================
# ADMINISTRAR JORNADA (DETALLE)
# =====================================================
@app.route("/Jornadas_Admin/<int:idjornada>")
def jornadas_admin_detalle(idjornada):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    # -----------------------------
    # JORNADA SELECCIONADA
    # -----------------------------
    cursor.execute("""
        SELECT *
        FROM jornadas
        WHERE idjornada = %s
    """, (idjornada,))
    jornada = cursor.fetchone()

    if not jornada:
        conexion.close()
        return redirect(url_for("jornadas_admin"))

    # -----------------------------
    # PUNTOS DE VENTA
    # -----------------------------
    cursor.execute("""
        SELECT 
            pv.idpunto,
            pv.nombre,
            IF(jp.id IS NULL, 0, 1) AS asignado
        FROM puntos_venta pv
        LEFT JOIN jornadas_puntos jp
            ON pv.idpunto = jp.idpunto
            AND jp.idjornada = %s
        WHERE pv.estado = 'Activo'
        ORDER BY pv.nombre
    """, (idjornada,))
    puntos_venta = cursor.fetchall()

    # -----------------------------
    # PRODUCTOS
    # -----------------------------
    cursor.execute("""
        SELECT 
            p.idproductos,
            p.nombre,
            p.importe,
            IF(jpr.id IS NULL, 0, 1) AS asignado
        FROM productos p
        LEFT JOIN jornadas_productos jpr
            ON p.idproductos = jpr.idproducto
            AND jpr.idjornada = %s
        WHERE p.estado = 'Activo'
        ORDER BY p.nombre
    """, (idjornada,))
    productos = cursor.fetchall()

    conexion.close()

    return render_template(
        "jornada_administrar.html",
        jornada=jornada,
        puntos_venta=puntos_venta,
        productos=productos,
        usuario=session["nombre"],
        rol=session["rol"]
    )


# =====================================================
# AGREGAR PUNTO DE VENTA A JORNADA
# =====================================================
@app.route("/agregar_punto_jornada/<int:idjornada>/<int:idpunto>")
def agregar_punto_jornada(idjornada, idpunto):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT IGNORE INTO jornadas_puntos (idjornada, idpunto)
        VALUES (%s, %s)
    """, (idjornada, idpunto))

    conexion.commit()
    conexion.close()

    return redirect(f"/Jornadas_Admin/{idjornada}")


# =====================================================
# AGREGAR PRODUCTO A JORNADA
# =====================================================
@app.route("/agregar_producto_jornada/<int:idjornada>/<int:idproducto>")
def agregar_producto_jornada(idjornada, idproducto):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT IGNORE INTO jornadas_productos (idjornada, idproducto)
        VALUES (%s, %s)
    """, (idjornada, idproducto))

    conexion.commit()
    conexion.close()

    return redirect(f"/Jornadas_Admin/{idjornada}")







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

#-----------------------------Modo Pago----------------------------------
#ruta principal modo de pago
@app.route("/Modopago", methods=["GET"])
def home_Modopago():
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM modopago")
    data = cursor.fetchall()

    message = request.args.get("message")

    conexion.close()

    return render_template(
        "modopago.html",
        modo=data,
        message=message,
        usuario=session["nombre"],
        rol=session["rol"]
    )

# ruta para guardar modo de pago
@app.route("/guardar_Modopago", methods=["POST"])
def save_Modopago():
    if "id" not in session:
        return redirect(url_for("home"))

    modo = request.form["modopago"].upper()
    estado = request.form["estado"]

    conexion = getConnection()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO modopago (modo, estado)
        VALUES (%s, %s)
    """, (modo, estado))

    conexion.commit()
    conexion.close()

    return redirect(
        url_for("home_Modopago", message="Modo de Pago registrado correctamente")
    )


# ruta para actualizar modo de pago
@app.route("/Update_Modopago/<int:id>", methods=["POST"])
def update_Modopago(id):
    if "id" not in session:
        return redirect(url_for("home"))

    modo = request.form["modo"].upper()
    estado = request.form["estado"]

    conexion = getConnection()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE modopago
        SET modo = %s, estado = %s
        WHERE idmodopago = %s
    """, (modo, estado, id))

    conexion.commit()
    conexion.close()

    return redirect(
        url_for("home_Modopago", message="Modo de Pago actualizado correctamente")
    )

#ruta para eliminar modo de pago
@app.route("/delete_Modopago/<int:id>")
def delete_Modopago(id):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor()

    cursor.execute(
        "DELETE FROM modopago WHERE idmodopago = %s",
        (id,)
    )

    conexion.commit()
    conexion.close()

    return redirect(
        url_for("home_Modopago", message="Modo de Pago eliminado correctamente")
    )
#------------------------------ TIKET DE VENTA ----------------------------------
#Ticket de venta 
@app.route("/ticket/<int:idventa>")
def ticket(idventa):

    # ======================
    # CONEXIÓN
    # ======================
    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    # ======================
    # DATOS DE LA VENTA
    # ======================
    cursor.execute("""
        SELECT v.idventa,
               v.fecha_hora AS fecha,
               v.total,
               IFNULL(c.apenomb, 'Consumidor Final') AS cliente,
               j.nombre AS jornada
        FROM ventas v
        LEFT JOIN clientes c ON c.idclientes = v.idclientes
        JOIN jornadas j ON j.idjornada = v.idjornada
        WHERE v.idventa = %s
    """, (idventa,))

    venta = cursor.fetchone()

    if not venta:
        conexion.close()
        return "Venta no encontrada", 404

    # ======================
    # DETALLE DE PRODUCTOS
    # ======================
    cursor.execute("""
        SELECT p.nombre AS producto,
               d.cantidad,
               d.subtotal
        FROM ventas_detalle d
        JOIN productos p ON p.idproductos = d.idproductos
        WHERE d.idventa = %s
    """, (idventa,))

    detalle = cursor.fetchall()

    conexion.close()

    # ======================
    # GENERAR QR
    # ======================
    qr_texto = (
        f"TICKETJETS\n"
        f"Venta: {venta['idventa']}\n"
        f"Total: ${venta['total']}\n"
        f"Fecha: {venta['fecha'].strftime('%d/%m/%Y %H:%M')}"
    )

    qr = qrcode.make(qr_texto)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # ======================
    # RENDER TEMPLATE
    # ======================
    return render_template(
        "ticket.html",
        idventa=venta["idventa"],
        jornada=venta["jornada"],
        fecha_hora=venta["fecha"].strftime("%d/%m/%Y %H:%M"),
        cliente=venta["cliente"],
        detalle=detalle,
        subtotal=venta["total"],
        total=venta["total"],
        qr_base64=qr_base64
    )


@app.route("/ver_ticket/<token>")
def ver_ticket(token):
    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT v.idventa, v.fecha_hora, v.total, v.estado_ticket,
               j.nombre AS jornada
        FROM ventas v
        JOIN jornadas j ON v.idjornada = j.idjornada
        WHERE v.qr_token = %s
    """, (token,))

    venta = cursor.fetchone()
    conexion.close()

    if not venta:
        return "TICKET NO VÁLIDO", 404

    return render_template("validar_ticket.html", venta=venta)








#-------------------------------Arranque-----------------------------------
if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0',port=6900)