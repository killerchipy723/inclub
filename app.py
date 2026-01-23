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



# VALIDACION DE LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    nombre = request.form["nombre"]
    clave = request.form["clave"]
    equipo = obtener_mac()

    conexion = getConnection()
    if not conexion:
        return render_template("login.html", error="Error de conexión")

    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    try:
        # 1️⃣ VALIDAR USUARIO
        cursor.execute("""
            SELECT idusuarios, nombre, rol, estado
            FROM usuarios
            WHERE nombre = %s
              AND clave  = %s
        """, (nombre, clave))

        user = cursor.fetchone()

        if not user:
            return render_template("login.html", error="Usuario o contraseña incorrectos")

        if user["estado"] != "Activo":
            return render_template("login.html", error="Usuario inactivo")

        # 🟢 ADMIN
        if user["rol"] == "Administrador":
            session.clear()
            session.update({
                "id": user["idusuarios"],
                "nombre": user["nombre"],
                "rol": user["rol"],
                "equipo": equipo
            })
            return redirect(url_for("admin"))

        # 2️⃣ VALIDAR PUNTO
        cursor.execute("""
            SELECT idpunto, nombre
            FROM puntos_venta
            WHERE idequipo = %s
              AND estado  = 'Activo'
        """, (equipo,))

        punto = cursor.fetchone()

        if not punto:
            return render_template(
                "login.html",
                error="Este equipo no está habilitado como punto de venta"
            )

        # 3️⃣ VALIDAR USUARIO ↔ PUNTO
        cursor.execute("""
            SELECT 1
            FROM usuarios_puntos
            WHERE idusuario = %s
              AND idpunto   = %s
            LIMIT 1
        """, (user["idusuarios"], punto["idpunto"]))

        if not cursor.fetchone():
            return render_template(
                "login.html",
                error="Usuario no autorizado para este punto de venta"
            )

        # 4️⃣ SESIÓN
        session.clear()
        session.update({
            "id": user["idusuarios"],
            "nombre": user["nombre"],
            "rol": user["rol"],
            "idpunto": punto["idpunto"],
            "punto": punto["nombre"],
            "equipo": equipo
        })

        # 5️⃣ VALIDAR CAJA
        idjornada = session.get("idjornada")
        if idjornada:
            cursor.execute("""
                SELECT 1
                FROM cierres_caja
                WHERE idusuario = %s
                  AND idjornada = %s
                LIMIT 1
            """, (user["idusuarios"], idjornada))

            if cursor.fetchone():
                session.clear()
                return render_template(
                    "login.html",
                    error="❌ La caja ya fue cerrada. No puede volver a operar."
                )

        # 6️⃣ REDIRECCIÓN
        if user["rol"] == "Vendedor":
            return redirect(url_for("ventas_home"))

        if user["rol"] == "Boleteria":
            return redirect(url_for("boleteria_home"))

        return redirect(url_for("login"))

    finally:
        cursor.close()
        conexion.close()






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

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        cursor.execute("SELECT * FROM usuarios")
        data = cursor.fetchall()

        message = request.args.get('message')

        return render_template(
            "usuarios.html",
            usuarios=data,
            message=message,
            usuario=session["nombre"],
            rol=session["rol"]
        )

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()



#Ruta Registro de usuarios
@app.route("/reg_Usu", methods=["POST"])
def reg_usuario():
    if "id" not in session or session.get("rol") != "Administrador":
        return redirect(url_for("home"))

    nombre = request.form["nombre"].upper()
    clave = request.form["clave"]
    rol = request.form["rol"]
    estado = request.form["estado"]

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO usuarios (nombre, clave, rol, estado)
            VALUES (%s, %s, %s, %s)
            """,
            (nombre, clave, rol, estado)
        )

        conexion.commit()

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return redirect(
        url_for(
            "home_userReg",
            message="Usuario Registrado Correctamente!"
        )
    )


#Ruta para Eliminar Usuarios
@app.route("/delete_Usuario/<int:id>")
def delete_usuario(id):
    if "id" not in session or session.get("rol") != "Administrador":
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute(
            "DELETE FROM usuarios WHERE idusuarios = %s",
            (id,)
        )

        conexion.commit()

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return redirect(
        url_for(
            "home_userReg",
            message="Registro Eliminado Correctamente!"
        )
    )



@app.route("/Update_Usuario/<int:id>", methods=["POST"])
def update_usuario(id):
    if "id" not in session or session.get("rol") != "Administrador":
        return redirect(url_for("home"))

    nombre = request.form["nombre"].upper()
    clave = request.form["clave"]
    rol = request.form["rol"]
    estado = request.form["estado"]

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE usuarios
            SET nombre=%s, clave=%s, rol=%s, estado=%s
            WHERE idusuarios=%s
        """, (nombre, clave, rol, estado, id))

        conexion.commit()

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return redirect(url_for("home_userReg"))


#Estado de Cajas
@app.route("/estado_caja")
def estado_caja():

    if "idjornada" not in session or "idpunto" not in session:
        return jsonify(estado="cerrada")

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        cursor.execute("""
            SELECT estado
            FROM jornadas_puntos
            WHERE idjornada = %s AND idpunto = %s
        """, (session["idjornada"], session["idpunto"]))

        row = cursor.fetchone()

        if not row:
            return jsonify(estado="cerrada")

        return jsonify(estado=row["estado"].lower())

    except Exception as e:
        # fallback seguro
        return jsonify(estado="cerrada")

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# ----------TIKET CAJA---------------
@app.route("/ticket_cierre_caja")
def ticket_cierre_caja():
    now = datetime.now()

    if "idjornada" not in session or "idpunto" not in session:
        return "No hay caja activa", 403

    idjornada = int(session["idjornada"])
    idpunto = int(session["idpunto"])

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        usuario = session.get("usuario", "OPERADOR")

        # Punto de venta
        cursor.execute("""
            SELECT nombre
            FROM puntos_venta
            WHERE idpunto = %s
        """, (idpunto,))
        punto = cursor.fetchone()
        nombre_punto = punto["nombre"] if punto else "PUNTO"

        # 🔹 DETALLE DE VENTAS (producto por producto)
        cursor.execute("""
            SELECT 
                v.fecha_hora AS fecha,
                DATE_FORMAT(v.fecha_hora, '%%d/%%m/%%Y %%H:%%i') AS fecha_hora,
                p.nombre AS producto,
                mp.modo AS pago,
                d.subtotal AS importe
            FROM ventas v
            JOIN ventas_detalle d ON d.idventa = v.idventa
            JOIN productos p ON p.idproductos = d.idproductos
            JOIN modopago mp ON mp.idmodopago = v.idmodopago
            WHERE v.idjornada = %s
              AND v.idpunto = %s
            ORDER BY v.fecha_hora ASC
        """, (idjornada, idpunto))

        detalle = cursor.fetchall()

        # 🔹 TOTALES POR FORMA DE PAGO
        cursor.execute("""
            SELECT mp.modo,
                   SUM(d.subtotal) total
            FROM ventas v
            JOIN ventas_detalle d ON d.idventa = v.idventa
            JOIN modopago mp ON mp.idmodopago = v.idmodopago
            WHERE v.idjornada = %s AND v.idpunto = %s
            GROUP BY mp.modo
        """, (idjornada, idpunto))

        totales_pago = cursor.fetchall()

        # 🔹 TOTAL GENERAL
        cursor.execute("""
            SELECT COALESCE(SUM(d.subtotal),0) total
            FROM ventas v
            JOIN ventas_detalle d ON d.idventa = v.idventa
            WHERE v.idjornada = %s AND v.idpunto = %s
        """, (idjornada, idpunto))

        row_total = cursor.fetchone()
        total_general = row_total["total"] if row_total else 0

        return render_template(
            "ticket_cierre_caja.html",
            punto=nombre_punto,
            usuario=usuario,
            detalle=detalle,
            totales_pago=totales_pago,
            total_general=total_general,
            fecha_impresion=now
        )

    except Exception as e:
        return "Error generando ticket de cierre", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()




#--------------------------------------BOLETERIA---------------------------------
@app.route("/boleteria")
def boleteria_home():

    # ================= SEGURIDAD =================
    if "id" not in session or session.get("rol") != "Boleteria":
        return redirect(url_for("login"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        # ================= JORNADA ACTIVA =================
        cursor.execute("""
            SELECT idjornada, nombre
            FROM jornadas
            WHERE estado = 'Activo'
            ORDER BY idjornada DESC
            LIMIT 1
        """)
        jornada = cursor.fetchone()

        if not jornada:
            return render_template(
                "boleteria.html",
                jornada=None,
                sectores=[],
                recaudacion=0,
                entradas_vendidas=0,
                usuario=session["nombre"],
                rol=session["rol"],
                error="No hay jornada activa"
            )

        idjornada = jornada["idjornada"]

        # ================= SECTORES =================
        cursor.execute("""
            SELECT idsector, nombre, precio
            FROM sectores_entradas
            WHERE idjornada = %s
              AND estado = 'Activo'
            ORDER BY nombre
        """, (idjornada,))
        sectores = cursor.fetchall()

        # DEBUG útil (dejalo mientras probás)
        print("SECTORES:", sectores)

        # ================= RECAUDACIÓN =================
        cursor.execute("""
            SELECT COALESCE(SUM(total), 0) AS total
            FROM ventas_entradas
            WHERE idjornada = %s
              AND estado = 'OK'
        """, (idjornada,))
        row_recaudacion = cursor.fetchone()
        recaudacion = row_recaudacion["total"] if row_recaudacion else 0

        # ================= ENTRADAS VENDIDAS =================
        cursor.execute("""
            SELECT COALESCE(SUM(d.cantidad), 0) AS total
            FROM ventas_entradas_detalle d
            JOIN ventas_entradas v ON v.idventa = d.idventa
            WHERE v.idjornada = %s
              AND v.estado = 'OK'
        """, (idjornada,))
        row_entradas = cursor.fetchone()
        entradas_vendidas = row_entradas["total"] if row_entradas else 0

        return render_template(
            "boleteria.html",
            jornada=jornada,
            sectores=sectores,
            recaudacion=recaudacion,
            entradas_vendidas=entradas_vendidas,
            usuario=session["nombre"],
            rol=session["rol"]
        )

    except Exception as e:
        print("ERROR BOLETERIA:", e)
        return "Error interno en boletería", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    
#REGISTRO DE VENTAS DE ENTRADAS

@app.route("/registrar_venta_entrada", methods=["POST"])
def registrar_venta_entrada():

    if "id" not in session:
        return jsonify({"ok": False, "msg": "Sesión expirada"}), 401

    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)


    try:
        data = request.json
        print("DATA RECIBIDA:", data)

        idcliente = data["idcliente"]
        idsector = data["idsector"]
        cantidad = int(data["cantidad"])
        total = float(data["total"])
        idjornada = data["idjornada"]
        idusuario = session["id"]

        # 1️⃣ CABECERA
        cursor.execute("""
            INSERT INTO ventas_entradas
            (idjornada, idusuario, cliente, total, estado)
            VALUES (%s, %s, %s, %s, 'OK')
        """, (idjornada, idusuario, idcliente, total))

        idventa = cursor.lastrowid

        # 2️⃣ PRECIO SECTOR
        cursor.execute("""
            SELECT precio
            FROM sectores_entradas
            WHERE idsector = %s AND estado = 'Activo'
        """, (idsector,))

        sector = cursor.fetchone()
        if not sector:
            raise Exception("Sector no encontrado")

        precio = float(sector["precio"])

        subtotal = precio * cantidad

        # 3️⃣ DETALLE
        cursor.execute("""
            INSERT INTO ventas_entradas_detalle
            (idventa, idsector, cantidad, precio_unitario, subtotal)
            VALUES (%s, %s, %s, %s, %s)
        """, (idventa, idsector, cantidad, precio, subtotal))

        conexion.commit()
        conexion.close()

        return jsonify({
            "ok": True,
            "msg": "Entrada emitida correctamente",
            "idventa": idventa
})


    except Exception as e:
        print("ERROR REGISTRAR VENTA:", e)
        conexion.rollback()
        conexion.close()
        return jsonify({"ok": False, "msg": str(e)}), 500
    

#RUTA PARA TICKET DE VENTA
@app.route("/ticket_entrada/<int:idventa>")
def ticket_entrada(idventa):

    con = None
    cur = None

    try:
        con = getConnection()
        cur = con.cursor(pymysql.cursors.DictCursor)

        # ================= CABECERA =================
        cur.execute("""
            SELECT 
                v.idventa,
                v.fecha_emision,
                v.total,
                c.apenomb AS cliente,                
                j.nombre AS jornada,
                u.nombre AS usuario           
            FROM ventas_entradas v
            JOIN jornadas j ON j.idjornada = v.idjornada
            JOIN usuarios u ON u.idusuarios = v.idusuario
            JOIN clientes c ON c.idclientes = v.cliente        
            WHERE v.idventa = %s
        """, (idventa,))
        venta = cur.fetchone()

        # ================= DETALLE =================
        cur.execute("""
            SELECT 
                s.nombre AS sector,
                d.cantidad,
                d.precio_unitario,
                d.subtotal
            FROM ventas_entradas_detalle d
            JOIN sectores_entradas s ON s.idsector = d.idsector
            WHERE d.idventa = %s
        """, (idventa,))
        detalle = cur.fetchall()

        return render_template(
            "ticket_entrada.html",
            venta=venta,
            detalle=detalle
        )

    except Exception as e:
        print("ERROR TICKET ENTRADA:", e)
        return "Error al generar ticket", 500

    finally:
        if cur:
            cur.close()
        if con:
            con.close()


#Reporte Boleteria
@app.route("/reporte_boleteria")
def reporte_boleteria():

    if "id" not in session:
        return redirect(url_for("login"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        # ================= JORNADAS =================
        cursor.execute("""
            SELECT idjornada, nombre
            FROM jornadas
            ORDER BY idjornada DESC
        """)
        jornadas = cursor.fetchall()

        # Jornada seleccionada
        idjornada = request.args.get("idjornada")

        if not idjornada and jornadas:
            idjornada = jornadas[0]["idjornada"]

        if not idjornada:
            return render_template(
                "reporte_boleteria.html",
                jornadas=[],
                jornada_id=None,
                jornada_nombre="",
                cajas=[],
                total_general=0,
                fecha_hora=datetime.now().strftime("%d/%m/%Y %H:%M")
            )

        idjornada = int(idjornada)

        # ================= DATOS JORNADA =================
        cursor.execute("""
            SELECT nombre
            FROM jornadas
            WHERE idjornada = %s
        """, (idjornada,))
        jornada = cursor.fetchone()

        # ================= RECAUDACIÓN POR BOLETERÍA =================
        cursor.execute("""
            SELECT 
                u.nombre AS punto,
                COALESCE(SUM(v.total), 0) AS total
            FROM ventas_entradas v
            INNER JOIN usuarios u ON u.idusuarios = v.idusuario
            WHERE v.idjornada = %s
              AND v.estado = 'OK'
            GROUP BY u.idusuarios
            ORDER BY u.nombre
        """, (idjornada,))
        cajas = cursor.fetchall()

        # ================= TOTAL GENERAL =================
        cursor.execute("""
            SELECT COALESCE(SUM(total), 0) AS total
            FROM ventas_entradas
            WHERE idjornada = %s
              AND estado = 'OK'
        """, (idjornada,))
        total_general = cursor.fetchone()["total"]

        return render_template(
            "reporte_boleteria.html",
            jornadas=jornadas,
            jornada_id=idjornada,
            jornada_nombre=jornada["nombre"] if jornada else "",
            cajas=cajas,
            total_general=total_general,
            fecha_hora=datetime.now().strftime("%d/%m/%Y %H:%M")
        )

    except Exception as e:
        print("ERROR REPORTE BOLETERIA:", e)
        return "Error al generar reporte de boletería", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


#REPORTE DETALLADO DE BOLETERIA

@app.route("/reporte_boleteria_detallado", methods=["GET", "POST"])
def reporte_boleteria_detallado():

    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        # ================= FILTROS =================
        idjornada = request.form.get("idjornada")
        idusuario = request.form.get("idusuario")
        idsector  = request.form.get("idsector")

        # ================= JORNADAS =================
        cursor.execute("""
            SELECT idjornada, nombre
            FROM jornadas
            ORDER BY idjornada DESC
        """)
        jornadas = cursor.fetchall()

        # ================= USUARIOS BOLETERIA =================
        cursor.execute("""
            SELECT idusuarios, nombre
            FROM usuarios
            WHERE rol = 'Boleteria'
            ORDER BY nombre
        """)
        usuarios = cursor.fetchall()

        # ================= SECTORES =================
        cursor.execute("""
            SELECT idsector, nombre
            FROM sectores_entradas
            ORDER BY nombre
        """)
        sectores = cursor.fetchall()

        # ================= QUERY PRINCIPAL =================
        query = """
            SELECT
                v.fecha_emision,
                j.nombre  AS jornada,
                u.nombre  AS usuario,
                s.nombre  AS sector,
                d.cantidad,
                d.precio_unitario,
                d.subtotal
            FROM ventas_entradas v
            JOIN ventas_entradas_detalle d ON d.idventa = v.idventa
            JOIN jornadas j ON j.idjornada = v.idjornada
            JOIN sectores_entradas s ON s.idsector = d.idsector
            JOIN usuarios u ON u.idusuarios = v.idusuario
            WHERE v.estado = 'OK'
        """

        params = []

        # ================= FILTROS =================
        if idjornada:
            query += " AND v.idjornada = %s"
            params.append(int(idjornada))

        if idusuario:
            query += " AND v.idusuario = %s"
            params.append(int(idusuario))

        if idsector:
            query += " AND d.idsector = %s"
            params.append(int(idsector))

        query += " ORDER BY v.fecha_emision DESC"

        cursor.execute(query, params)
        ventas = cursor.fetchall()

        # ================= TOTAL GENERAL =================
        total_general = sum(float(v["subtotal"]) for v in ventas) if ventas else 0

        fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

        return render_template(
            "reporte_boleteria_detallado.html",
            ventas=ventas,
            jornadas=jornadas,
            usuarios=usuarios,
            sectores=sectores,
            total_general=total_general,
            fecha_hora=fecha_hora,
            filtro_jornada=idjornada,
            filtro_usuario=idusuario,
            filtro_sector=idsector
        )

    except Exception as e:
        print("ERROR REPORTE BOLETERIA DETALLADO:", e)
        return "Error interno en reporte", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

#################################################### hasta aca esta falta la siguiente ruta blindar 

#--------------------------------------Usuarios Puntos---------------------------

# ==============================
# RUTA PRINCIPAL ASIGNACIONES
# ==============================

@app.route("/usuarios_puntos")
def usuarios_puntos():
    if "id" not in session or session["rol"] != "Administrador":
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
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

    except Exception as e:
        print("ERROR USUARIOS_PUNTOS:", e)
        return "Error interno", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()



# ==============================
# REGISTRAR ASIGNACIÓN
# ==============================

@app.route("/reg_usuario_punto", methods=["POST"])
def reg_usuario_punto():
    if "id" not in session or session["rol"] != "Administrador":
        return redirect(url_for("home"))

    idusuario = request.form["idusuario"]
    idpunto = request.form["idpunto"]

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO usuarios_puntos (idusuario, idpunto)
            VALUES (%s, %s)
        """, (idusuario, idpunto))
        conexion.commit()
        msg = "Usuario asignado correctamente!"

    except Exception as e:
        print("ERROR REG_USUARIO_PUNTO:", e)
        msg = "El usuario ya está asignado a ese punto"

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return redirect(url_for("usuarios_puntos", message=msg))



# ==============================
# ELIMINAR ASIGNACIÓN
# ==============================

@app.route("/delete_usuario_punto/<int:id>")
def delete_usuario_punto(id):
    if "id" not in session or session["rol"] != "Administrador":
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute(
            "DELETE FROM usuarios_puntos WHERE id=%s",
            (id,)
        )
        conexion.commit()

    except Exception as e:
        print("ERROR DELETE_USUARIO_PUNTO:", e)
        # mantenemos el flujo original (redirige igual)

    finally:
        if cursor:
            cursor.close()
        if conexion:
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

    conexion = None
    cursor = None

    try:
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

    except Exception as e:
        print("ERROR VENTAS_HOME:", e)
        return "Error interno en ventas", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()




#------------------------------------REGISTRAR VENTA-----------------------------
@app.route("/registrar_venta", methods=["POST"])
def registrar_venta():
    if "id" not in session:
        return redirect(url_for("home"))

    idusuario = session["id"]
    idpunto   = session["idpunto"]
    idjornada = session["idjornada"]
    idcliente = request.form.get("cliente")
    idmodopago = request.form.get("modopago")

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        # ===============================
        # 🔒 VALIDAR CAJA ABIERTA
        # ===============================
        cursor.execute("""
            SELECT estado
            FROM jornadas_puntos
            WHERE idjornada = %s
              AND idpunto = %s
        """, (idjornada, idpunto))

        jp = cursor.fetchone()

        if not jp or jp["estado"] != "Abierto":
            return jsonify({
                "success": False,
                "error": "La caja de este punto de venta está cerrada"
            }), 403

        # ===============================
        # CONTINÚA LÓGICA ORIGINAL
        # ===============================
        total_str = request.form.get("total", "0")
        total_str = total_str.replace(".", "").replace(",", ".")
        total = float(total_str)

        productos  = request.form.getlist("productos[]")
        cantidades = request.form.getlist("cantidades[]")
        precios    = request.form.getlist("precios[]")
        cortesias  = request.form.getlist("cortesias[]")

        # 🔁 reutilizamos la MISMA conexión
        cursor = conexion.cursor()

        qr_token = uuid.uuid4().hex

        cursor.execute("""
            INSERT INTO ventas
            (idjornada, idusuario, idpunto, idclientes, idmodopago,
             total, descuento_total, fecha_hora, estado, observaciones,
             puntos_ganados, qr_token)
            VALUES (%s,%s,%s,%s,%s,%s,0,NOW(),'OK','',0,%s)
        """, (
            idjornada,
            idusuario,
            idpunto,
            idcliente if idcliente != "0" else None,
            idmodopago,
            total,
            qr_token
        ))

        idventa = cursor.lastrowid
        total_puntos = 0

        for i in range(len(productos)):
            idproducto = productos[i]
            cantidad = int(cantidades[i])
            precio = float(precios[i])

            es_cortesia = False
            if i < len(cortesias):
                es_cortesia = cortesias[i] == "1"

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

            if not es_cortesia:
                total_puntos += int(subtotal // 100)

        cursor.execute("""
            UPDATE ventas
            SET puntos_ganados = %s
            WHERE idventa = %s
        """, (total_puntos, idventa))

        conexion.commit()

        return jsonify({"success": True, "idventa": idventa})

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("ERROR REGISTRAR VENTA:", e)
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


#Ruta para actualizar la recaudacion por caja 
@app.route("/recaudacion_actual")
def recaudacion_actual():

    if "idpunto" not in session or "idjornada" not in session:
        return jsonify({"total": 0})

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        cursor.execute("""
            SELECT COALESCE(SUM(d.subtotal),0) AS total
            FROM ventas v
            JOIN ventas_detalle d ON d.idventa = v.idventa
            WHERE v.idpunto = %s
              AND v.idjornada = %s
        """, (
            session["idpunto"],
            session["idjornada"]
        ))

        total = cursor.fetchone()["total"]

        return jsonify({"total": float(total)})

    except Exception as e:
        print("ERROR RECAUDACION ACTUAL:", e)
        return jsonify({"total": 0}), 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


#finalizar jornada
@app.route("/finalizar_jornada", methods=["POST"])
def finalizar_jornada():
    if "id" not in session:
        return redirect(url_for("home"))

    idjornada = session.get("idjornada")

    if not idjornada:
        return redirect(url_for("ventas"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE jornadas
            SET estado = 'Cerrado'
            WHERE idjornada = %s
        """, (idjornada,))

        conexion.commit()

        # 🔹 Limpieza de sesión SOLO si el cierre fue correcto
        session.pop("idjornada", None)

        return redirect(
            url_for("ventas", message="Jornada finalizada")
        )

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("ERROR FINALIZAR JORNADA:", e)
        return "Error al finalizar la jornada", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


#--------------------------------------Clientes----------------------------------------------------------------

# Ruta principal clientes
@app.route("/clientes", methods=['GET'])
def home_clientes():
    # Solo Administrador
    if "id" not in session or session['rol'] != "Administrador":
        return redirect(url_for('home'))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        cursor.execute("SELECT * FROM clientes")
        data = cursor.fetchall()

        message = request.args.get('message')  # 👈 mensaje de confirmación

        return render_template(
            "clientes.html",
            clientes=data,
            message=message,
            usuario=session["nombre"],
            rol=session["rol"]
        )

    except Exception as e:
        print("ERROR CLIENTES:", e)
        return "Error interno en clientes", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()



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

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute(query, (apenomb, dni, cuil, correo, fecha_nacimiento))
        conexion.commit()

        return redirect(
            url_for(
                'home_clientes',
                message='Cliente Registrado Correctamente'
            )
        )

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("ERROR GUARDAR CLIENTE:", e)
        return "Error al guardar cliente", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()



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

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute(
            query,
            (apenomb, dni, cuil, correo, fecha_nacimiento, id)
        )
        conexion.commit()

        return redirect(
            url_for(
                'home_clientes',
                message='Cliente Actualizado Correctamente'
            )
        )

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("ERROR UPDATE CLIENTE:", e)
        return "Error al actualizar cliente", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()



# Ruta para eliminar clientes
@app.route("/delete_Clientes/<int:id>")
def eliminar_Clientes(id):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute(
            "DELETE FROM clientes WHERE idclientes=%s",
            (id,)
        )
        conexion.commit()

        return redirect(
            url_for(
                'home_clientes',
                message='Cliente Eliminado Correctamente'
            )
        )

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("ERROR DELETE CLIENTE:", e)
        return "Error al eliminar cliente", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


#Buscar Clientes
@app.route("/buscar_clientes")
def buscar_clientes():
    q = request.args.get("q", "").strip()

    conexion = None
    cursor = None

    try:
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
        return jsonify(clientes)

    except Exception as e:
        print("ERROR BUSCAR CLIENTES:", e)
        return jsonify([])

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

# Modal para guardar Clientes            
@app.route("/guardar_ClientesMODAL", methods=['POST'])
def guardar_ClientesMOD():
    if "id" not in session:
        return redirect(url_for('home'))

    apenomb = request.form['apenomb'].upper()
    dni = request.form['dni']
    cuil = request.form['cuil']
    correo = request.form['correo']
    fecha_nacimiento = request.form['fecha_nacimiento'] or None

    query = """
        INSERT INTO clientes (apenomb, dni, cuil, correo, fecha_nacimiento)
        VALUES (%s, %s, %s, %s, %s)
    """

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute(
            query,
            (apenomb, dni, cuil, correo, fecha_nacimiento)
        )
        conexion.commit()

        return redirect(
            url_for(
                'ventas_home',
                message='Cliente Registrado Correctamente'
            )
        )

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("ERROR GUARDAR CLIENTE MODAL:", e)
        return "Error al registrar cliente", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# ------------------------------Jornadas----------------------------------

# =====================================================
# LISTADO GENERAL DE JORNADAS
# =====================================================
@app.route("/Jornadas", methods=["GET"])
def jornadas_listado():
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
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

        return render_template(
            "jornadas.html",
            jornadas=jornadas,
            puntos_venta=puntos_venta,
            productos=productos,
            usuario=session["nombre"],
            rol=session["rol"]
        )

    except Exception as e:
        print("ERROR LISTADO JORNADAS:", e)
        return "Error interno al cargar jornadas", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# =====================================================
# CREAR JORNADA
# =====================================================
@app.route("/guardar_Jornadas", methods=["POST"])
def jornadas_crear():
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

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
        if conexion:
            conexion.rollback()
        print("❌ Error al crear jornada:", e)
        return redirect(url_for("jornadas_listado"))

    finally:
        if cursor:
            cursor.close()
        if conexion:
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

    conexion = None
    cursor = None

    try:
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

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("❌ Error al actualizar jornada:", e)

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return redirect(url_for("jornadas_admin"))

# =====================================================
# finalizar jornada 
# =====================================================
@app.route("/finalizar_jornada/<int:idjornada>", methods=["POST"])
def jornadas_update(idjornada):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        query = "UPDATE jornadas SET estado = 'Finalizado' WHERE idjornada = %s"
        cursor.execute(query, (idjornada,))

        conexion.commit()

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("❌ Error al finalizar jornada:", e)

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return redirect(url_for("jornadas_admin"))


# =====================================================
# LISTADO / ADMINISTRACIÓN DE JORNADAS
# =====================================================
@app.route("/Jornadas_Admin")
def jornadas_admin():
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
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

        return render_template(
            "jornadas_admin.html",
            jornadas=jornadas,
            usuario=session["nombre"],
            rol=session["rol"]
        )

    except Exception as e:
        print("❌ Error en jornadas_admin:", e)
        return "Error interno en jornadas admin", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()



# =====================================================
# ADMINISTRAR JORNADA (DETALLE)
# =====================================================
@app.route("/Jornadas_Admin/<int:idjornada>")
def jornadas_admin_detalle(idjornada):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
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

        return render_template(
            "jornada_administrar.html",
            jornada=jornada,
            puntos_venta=puntos_venta,
            productos=productos,
            usuario=session["nombre"],
            rol=session["rol"]
        )

    except Exception as e:
        print("❌ Error en jornadas_admin_detalle:", e)
        return "Error interno en administración de jornada", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()



# =====================================================
# AGREGAR PUNTO DE VENTA A JORNADA
# =====================================================
@app.route("/agregar_punto_jornada/<int:idjornada>/<int:idpunto>")
def agregar_punto_jornada(idjornada, idpunto):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT IGNORE INTO jornadas_puntos (idjornada, idpunto)
            VALUES (%s, %s)
        """, (idjornada, idpunto))

        conexion.commit()

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("❌ Error al agregar punto a jornada:", e)

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return redirect(f"/Jornadas_Admin/{idjornada}")



# =====================================================
# AGREGAR PRODUCTO A JORNADA
# =====================================================

    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT IGNORE INTO jornadas_productos (idjornada, idproducto)
            VALUES (%s, %s)
        """, (idjornada, idproducto))

        conexion.commit()

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("❌ Error al agregar producto a jornada:", e)

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return redirect(f"/Jornadas_Admin/{idjornada}")



#-----------------------------Productos----------------------------------
#Ruta Principal de productos
@app.route("/agregar_producto_jornada/<int:idjornada>/<int:idproducto>")
def agregar_producto_jornada(idjornada, idproducto):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT IGNORE INTO jornadas_productos (idjornada, idproducto)
            VALUES (%s, %s)
        """, (idjornada, idproducto))

        conexion.commit()

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("❌ Error al agregar producto a jornada:", e)

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return redirect(f"/Jornadas_Admin/{idjornada}")


#Ruta para guardar Productos

@app.route("/guardar_Productos", methods=['POST'])
def save_Productos():
    conexion = None
    cursor = None

    try:
        conexion = getConnection()

        nombre = request.form['nombre'].upper()
        importe = request.form['importe']
        estado = request.form['estado']

        query = 'INSERT INTO productos (nombre, importe, estado) VALUES (%s, %s, %s)'

        cursor = conexion.cursor()
        cursor.execute(query, (nombre, importe, estado))
        conexion.commit()

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("❌ Error al guardar producto:", e)

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return redirect(
        url_for(
            'home_Productos',
            message='Producto Agregado Correctamente'
        )
    )


#Ruta para modificar productos
@app.route("/Update_Productos/<int:id>", methods=['POST'])
def update_Productos(id):
    conexion = None
    cursor = None

    try:
        conexion = getConnection()

        nombre = request.form['nombre'].upper()
        importe = request.form['importe']
        estado = request.form['estado']

        query = """
            UPDATE productos
            SET nombre = %s,
                importe = %s,
                estado = %s
            WHERE idproductos = %s
        """

        cursor = conexion.cursor()
        cursor.execute(query, (nombre, importe, estado, id))
        conexion.commit()

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("❌ Error al actualizar producto:", e)

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return redirect(
        url_for(
            'home_Productos',
            message='Producto Modificado Correctamente'
        )
    )


#Ruta para eliminar productos
@app.route("/delete_Productos/<int:id>")
def delete_producto(id):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute(
            "DELETE FROM productos WHERE idproductos = %s",
            (id,)
        )
        conexion.commit()

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("❌ Error al eliminar producto:", e)

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return redirect(
        url_for(
            "home_Jornadas",
            message='Producto eliminado correctamente'
        )
    )


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

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM puntos_venta")
        data = cursor.fetchall()

    except Exception as e:
        print("❌ Error en puntos_venta:", e)
        data = []

    finally:
        if cursor:
            cursor.close()
        if conexion:
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

    conexion = None
    cursor = None

    try:
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

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("❌ Error al guardar punto de venta:", e)

    finally:
        if cursor:
            cursor.close()
        if conexion:
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

    conexion = None
    cursor = None

    try:
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

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("❌ Error al actualizar punto de venta:", e)

    finally:
        if cursor:
            cursor.close()
        if conexion:
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

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute(
            "DELETE FROM puntos_venta WHERE idpunto=%s",
            (id,)
        )
        conexion.commit()

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("❌ Error al eliminar punto de venta:", e)

    finally:
        if cursor:
            cursor.close()
        if conexion:
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

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        cursor.execute("SELECT * FROM modopago")
        data = cursor.fetchall()

        message = request.args.get("message")

        return render_template(
            "modopago.html",
            modo=data,
            message=message,
            usuario=session["nombre"],
            rol=session["rol"]
        )

    except Exception as e:
        print("❌ Error en Modopago:", e)
        return "Error interno en Modopago", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# ruta para guardar modo de pago
@app.route("/guardar_Modopago", methods=["POST"])
def save_Modopago():
    if "id" not in session:
        return redirect(url_for("home"))

    modo = request.form["modopago"].upper()
    estado = request.form["estado"]

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO modopago (modo, estado)
            VALUES (%s, %s)
        """, (modo, estado))

        conexion.commit()

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("❌ Error al guardar Modopago:", e)
        return redirect(
            url_for("home_Modopago", message="Error al registrar modo de pago")
        )

    finally:
        if cursor:
            cursor.close()
        if conexion:
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

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE modopago
            SET modo = %s, estado = %s
            WHERE idmodopago = %s
        """, (modo, estado, id))

        conexion.commit()

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("❌ Error al actualizar Modopago:", e)
        return redirect(
            url_for("home_Modopago", message="Error al actualizar modo de pago")
        )

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return redirect(
        url_for("home_Modopago", message="Modo de Pago actualizado correctamente")
    )


# ruta para eliminar modo de pago
@app.route("/delete_Modopago/<int:id>")
def delete_Modopago(id):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()

        cursor.execute(
            "DELETE FROM modopago WHERE idmodopago = %s",
            (id,)
        )

        conexion.commit()

    except Exception as e:
        if conexion:
            conexion.rollback()
        print("❌ Error al eliminar Modopago:", e)
        return redirect(
            url_for("home_Modopago", message="Error al eliminar modo de pago")
        )

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return redirect(
        url_for("home_Modopago", message="Modo de Pago eliminado correctamente")
    )

#------------------------------ TIKET DE VENTA ----------------------------------
#Ticket de venta 
@app.route("/ticket/<int:idventa>")
def ticket(idventa):

    conexion = None
    cursor = None

    try:
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

    except Exception as e:
        print("❌ Error al generar ticket:", e)
        return "Error interno al generar ticket", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
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

# Ruta para ver el ticket de Venta

@app.route("/ver_ticket/<token>")
def ver_ticket(token):

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        cursor.execute("""
            SELECT v.idventa, 
                   v.fecha_hora, 
                   v.total, 
                   v.estado_ticket,
                   j.nombre AS jornada,
                   p.nombre AS caja
            FROM ventas v
            JOIN jornadas j ON v.idjornada = j.idjornada
            JOIN puntos_venta p ON v.idpunto = p.idpunto
            WHERE v.qr_token = %s
        """, (token,))

        venta = cursor.fetchone()

        if not venta:
            return "TICKET NO VÁLIDO", 404

        return render_template(
            "validar_ticket.html",
            venta=venta
        )

    except Exception as e:
        print("❌ Error al validar ticket:", e)
        return "Error interno al validar ticket", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


#-----------------------------REPORTES-----------------------------------
@app.route("/admin/dashboard")
def admin_dashboard():
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        # ======================
        # JORNADA ACTIVA
        # ======================
        cursor.execute("""
            SELECT idjornada, nombre
            FROM jornadas
            WHERE estado = 'Activo'
            ORDER BY idjornada DESC
            LIMIT 1
        """)
        jornada_activa = cursor.fetchone()

        id_jornada = jornada_activa["idjornada"] if jornada_activa else None

        # ======================
        # TOTAL VENDIDO
        # ======================
        if id_jornada:
            cursor.execute("""
                SELECT COALESCE(SUM(d.subtotal),0) AS total_ventas
                FROM ventas v
                JOIN ventas_detalle d ON d.idventa = v.idventa
                WHERE v.idjornada = %s
            """, (id_jornada,))
        else:
            cursor.execute("""
                SELECT COALESCE(SUM(d.subtotal),0) AS total_ventas
                FROM ventas_detalle d
            """)

        total_ventas = cursor.fetchone()["total_ventas"]

        # ======================
        # TOTAL DE TICKETS
        # ======================
        if id_jornada:
            cursor.execute("""
                SELECT COUNT(*) AS total_tickets
                FROM ventas
                WHERE idjornada = %s
            """, (id_jornada,))
        else:
            cursor.execute("""
                SELECT COUNT(*) AS total_tickets
                FROM ventas
            """)

        total_tickets = cursor.fetchone()["total_tickets"]

        # ======================
        # BEBIDA MÁS VENDIDA
        # ======================
        if id_jornada:
            cursor.execute("""
                SELECT p.nombre, SUM(d.cantidad) AS total
                FROM ventas_detalle d
                JOIN productos p ON p.idproductos = d.idproductos
                JOIN ventas v ON v.idventa = d.idventa
                WHERE v.idjornada = %s
                GROUP BY p.nombre
                ORDER BY total DESC
                LIMIT 1
            """, (id_jornada,))
        else:
            cursor.execute("""
                SELECT p.nombre, SUM(d.cantidad) AS total
                FROM ventas_detalle d
                JOIN productos p ON p.idproductos = d.idproductos
                GROUP BY p.nombre
                ORDER BY total DESC
                LIMIT 1
            """)

        bebida_top = cursor.fetchone()

        # ======================
        # CAJA CON MÁS VENTAS
        # ======================
        if id_jornada:
            cursor.execute("""
                SELECT c.nombre, SUM(d.subtotal) AS total
                FROM ventas v
                JOIN ventas_detalle d ON d.idventa = v.idventa
                JOIN puntos_venta c ON c.idpunto = v.idpunto
                WHERE v.idjornada = %s
                GROUP BY c.nombre
                ORDER BY total DESC
                LIMIT 1
            """, (id_jornada,))
        else:
            cursor.execute("""
                SELECT c.nombre, SUM(d.subtotal) AS total
                FROM ventas v
                JOIN ventas_detalle d ON d.idventa = v.idventa
                JOIN puntos_venta c ON c.idpunto = v.idpunto
                GROUP BY c.nombre
                ORDER BY total DESC
                LIMIT 1
            """)

        caja_top = cursor.fetchone()

        return render_template(
            "admin_dashboard.html",
            total_ventas=total_ventas,
            total_tickets=total_tickets,
            bebida_top=bebida_top,
            caja_top=caja_top,
            jornada_activa=jornada_activa
        )

    except Exception as e:
        print("❌ Error en admin_dashboard:", e)
        return "Error interno al cargar el dashboard", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route("/admin/reportes", methods=["GET", "POST"])
def admin_reportes():
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        idjornada = request.form.get("idjornada")
        idcaja = request.form.get("idcaja")
        idproducto = request.form.get("idproducto")
        desde = request.form.get("desde")
        hasta = request.form.get("hasta")

        condiciones = []
        valores = []

        if idjornada:
            condiciones.append("v.idjornada = %s")
            valores.append(idjornada)

        if idcaja:
            condiciones.append("v.idpunto = %s")
            valores.append(idcaja)

        if idproducto:
            condiciones.append("d.idproductos = %s")
            valores.append(idproducto)

        if desde and hasta:
            condiciones.append("DATE(v.fecha_hora) BETWEEN %s AND %s")
            valores.extend([desde, hasta])

        where_sql = ""
        if condiciones:
            where_sql = "WHERE " + " AND ".join(condiciones)

        query = f"""
            SELECT v.fecha_hora,
                   j.nombre AS jornada,
                   pto.nombre AS caja,
                   pr.nombre AS producto,
                   d.cantidad,
                   d.subtotal
            FROM ventas v
            JOIN jornadas j ON j.idjornada = v.idjornada
            JOIN puntos_venta pto ON pto.idpunto = v.idpunto
            JOIN ventas_detalle d ON d.idventa = v.idventa
            JOIN productos pr ON pr.idproductos = d.idproductos
            {where_sql}
            ORDER BY v.fecha_hora DESC
        """

        cursor.execute(query, valores)
        ventas = cursor.fetchall()

        total_general = sum(v["subtotal"] for v in ventas)

        jornada_nombre = "Todas"
        if idjornada:
            cursor.execute(
                "SELECT nombre FROM jornadas WHERE idjornada = %s",
                (idjornada,)
            )
            j = cursor.fetchone()
            if j:
                jornada_nombre = j["nombre"]

        cursor.execute(
            "SELECT idjornada, nombre FROM jornadas ORDER BY idjornada DESC"
        )
        jornadas = cursor.fetchall()

        cursor.execute(
            "SELECT idpunto, nombre FROM puntos_venta"
        )
        cajas = cursor.fetchall()

        cursor.execute(
            "SELECT idproductos, nombre FROM productos"
        )
        productos = cursor.fetchall()

        return render_template(
            "admin_reportes.html",
            ventas=ventas,
            jornadas=jornadas,
            cajas=cajas,
            productos=productos,
            total_general=total_general,
            jornada_nombre=jornada_nombre,
            fecha_hora=datetime.now().strftime("%d/%m/%Y %H:%M")
        )

    except Exception as e:
        print("❌ Error en admin_reportes:", e)
        return "Error interno al generar el reporte", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()




#------------------------------- Grafico -------------------------------
@app.route("/grafico", methods=["GET"])
def grafico():
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = getConnection()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT idjornada, nombre FROM jornadas ORDER BY nombre")
    jornadas = cursor.fetchall()

    cursor.execute("SELECT idpunto, nombre FROM puntos_venta ORDER BY nombre")
    puntos = cursor.fetchall()

    conexion.close()

    return render_template(
        "grafico.html",
        usuario=session.get("nombre"),
        rol=session.get("rol"),
        jornadas=jornadas,
        puntos=puntos
    )
#--------------------------- REPORTES POR CAJA---------------------------------


@app.route("/reporte")
def reporte_cajas():
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        idjornada = request.args.get("idjornada")

        # ======================
        # JORNADA
        # ======================
        if not idjornada:
            cursor.execute("""
                SELECT idjornada, nombre
                FROM jornadas
                ORDER BY idjornada DESC
                LIMIT 1
            """)
            jornada = cursor.fetchone()
            idjornada = jornada["idjornada"]
        else:
            cursor.execute("""
                SELECT idjornada, nombre
                FROM jornadas
                WHERE idjornada = %s
            """, (idjornada,))
            jornada = cursor.fetchone()

        # ======================
        # RECAUDACIÓN REAL
        # ======================
        cursor.execute("""
            SELECT 
                p.nombre AS punto,
                COALESCE(SUM(d.subtotal),0) AS total
            FROM ventas v
            JOIN ventas_detalle d ON d.idventa = v.idventa
            JOIN puntos_venta p ON p.idpunto = v.idpunto
            WHERE v.idjornada = %s
            -- AND v.estado = 'OK'
            GROUP BY p.nombre
            ORDER BY p.nombre
        """, (idjornada,))

        cajas = cursor.fetchall()
        total_general = sum(c["total"] for c in cajas)

        cursor.execute("""
            SELECT idjornada, nombre 
            FROM jornadas 
            ORDER BY idjornada DESC
        """)
        jornadas = cursor.fetchall()

        return render_template(
            "reportes_cajas.html",
            jornadas=jornadas,
            jornada_nombre=jornada["nombre"],
            jornada_id=idjornada,
            fecha_hora=datetime.now().strftime("%d/%m/%Y %H:%M"),
            cajas=cajas,
            total_general=total_general
        )

    except Exception as e:
        print("❌ Error en reporte_cajas:", e)
        return "Error interno al generar el reporte", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

#--------------------------- Sectores Boleteria --------------------------------
# ===============================
# SECTORES ENTRADAS
# ===============================
###################################### esta hasta aca sigue la linea de abajo
# ======================
# RUTA: Sectores Entradas
# ======================
@app.route("/sectores_entradas")
def home_sectores_entradas():
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        cursor.execute("""
            SELECT s.*, j.nombre AS jornada
            FROM sectores_entradas s
            INNER JOIN jornadas j ON j.idjornada = s.idjornada
        """)
        sectores = cursor.fetchall()

        cursor.execute("SELECT idjornada, nombre FROM jornadas order by idjornada DESC")
        jornadas = cursor.fetchall()

        return render_template(
            "sectores_entradas.html",
            sectores=sectores,
            jornadas=jornadas,
            message=request.args.get("message"),
            usuario=session["nombre"],
            rol=session["rol"]
        )

    except Exception as e:
        print("❌ Error en home_sectores_entradas:", e)
        return "Error interno al cargar los sectores", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# ======================
# RUTA: Guardar Sector Entrada
# ======================
@app.route("/guardar_sector_entrada", methods=["POST"])
def guardar_sector_entrada():
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        idjornada = request.form["idjornada"]
        nombre = request.form["nombre"].upper()
        precio = request.form["precio"]
        estado = request.form["estado"]

        conexion = getConnection()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO sectores_entradas (idjornada, nombre, precio, estado)
            VALUES (%s, %s, %s, %s)
        """, (idjornada, nombre, precio, estado))

        conexion.commit()

        return redirect(url_for("home_sectores_entradas",
                                message="Sector registrado correctamente"))

    except Exception as e:
        print("❌ Error en guardar_sector_entrada:", e)
        return "Error interno al guardar el sector", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# ======================
# RUTA: Actualizar Sector Entrada
# ======================
@app.route("/update_sector_entrada/<int:id>", methods=["POST"])
def update_sector_entrada(id):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        idjornada = request.form["idjornada"]
        nombre = request.form["nombre"].upper()
        precio = request.form["precio"]
        estado = request.form["estado"]

        conexion = getConnection()
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE sectores_entradas
            SET idjornada=%s, nombre=%s, precio=%s, estado=%s
            WHERE idsector=%s
        """, (idjornada, nombre, precio, estado, id))

        conexion.commit()

        return redirect(url_for("home_sectores_entradas",
                                message="Sector actualizado correctamente"))

    except Exception as e:
        print("❌ Error en update_sector_entrada:", e)
        return "Error interno al actualizar el sector", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# ======================
# RUTA: Eliminar Sector Entrada
# ======================
@app.route("/delete_sector_entrada/<int:id>")
def delete_sector_entrada(id):
    if "id" not in session:
        return redirect(url_for("home"))

    conexion = None
    cursor = None

    try:
        conexion = getConnection()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM sectores_entradas WHERE idsector=%s", (id,))
        conexion.commit()

        return redirect(url_for("home_sectores_entradas",
                                message="Sector eliminado correctamente"))

    except Exception as e:
        print("❌ Error en delete_sector_entrada:", e)
        return "Error interno al eliminar el sector", 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()





#-------------------------------Arranque-----------------------------------
if __name__=='__main__':    
    app.run(host="0.0.0.0", port=6900)