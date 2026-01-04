import pymysql

def getConnection():
    try:
        conexion = pymysql.connect(
            host='localhost',
            user='root',
            password='inclub123',
            database='inclub_offline',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print('Conexion Exitosa a la Base de datos')
        return conexion
    

    except pymysql.MySQLError as e:
        print("❌ Error al conectar a la base de datos:", e)
        return None


