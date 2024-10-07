
# Para subir archivo tipo foto al servidor
from werkzeug.utils import secure_filename
import uuid  # Modulo de python para crear un string

from conexion.conexionBD import connectionBD  # Conexión a BD
from datetime import datetime

import re
import os

from os import remove  # Modulo  para remover archivo
from os import path  # Modulo para obtener la ruta o directorio

import openpyxl  # Para generar el excel
# biblioteca o modulo send_file para forzar la descarga
from flask import send_file,session


# Lista de Usuarios creados
def lista_usuariosBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id, name_surname, email_user,rol, created_user FROM users WHERE email_user !='admin@admin.com' ORDER BY created_user DESC"
                cursor.execute(querySQL,)
                usuariosBD = cursor.fetchall()
        return usuariosBD
    except Exception as e:
        print(f"Error en lista_usuariosBD : {e}")
        return []


# Eliminar usuario
def eliminarUsuario(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM users WHERE id=%s"
                cursor.execute(querySQL, (id,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount

        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarUsuario : {e}")
        return []


#### CONTRATOS

# Ruta de almacenamiento de archivos PDF
basepath = os.path.abspath(os.path.dirname(__file__))
upload_dir = os.path.join(basepath, 'static', 'upload_folder')

# Asegurarse de que la carpeta existe
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Verifica si el archivo es PDF."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def procesar_form_contratos(dataForm, request):
    try:
        print("Procesando datos del formulario...")

        # Conectarse a la base de datos
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                
                # Validar si se reciben todos los campos
                print(f"Formulario recibido: {dataForm}")
                
                # Inserción en tbl_contratos
                sql_contrato = ("INSERT INTO tbl_contratos "
                                "(documento, razon_social, cantidad, objeto_contractual, fecha_inicio, fecha_fin, usuario_registro) "
                                "VALUES (%s, %s, %s, %s, %s, %s, %s)")
                
                valores_contrato = (
                    dataForm['documento'], dataForm['razon_social'],
                    dataForm['valor'],  # Asegúrate de que este campo esté correcto
                    dataForm['objeto_contractual'], 
                    dataForm['date_inicio'], dataForm['date_fin'],  # Estabas usando nombres incorrectos
                    session['name_surname']
                )
                
                # Verificar si los valores son los esperados
                print(f"Valores del contrato a insertar: {valores_contrato}")
                
                cursor.execute(sql_contrato, valores_contrato)
                conexion_MySQLdb.commit()
                id_contrato = cursor.lastrowid  # Obtenemos el id del contrato recién insertado
                print(f"Contrato insertado con id {id_contrato}")

                # Procesar los archivos PDF subidos
                if 'documentos_pdf' in request.files:
                    documentos_pdf = request.files.getlist('documentos_pdf')
                    print(f"Archivos subidos: {[doc.filename for doc in documentos_pdf]}")

                    for documento in documentos_pdf:
                        if documento and allowed_file(documento.filename):
                            # Agregar marca de tiempo al nombre del archivo para evitar sobrescrituras
                            filename = secure_filename(documento.filename)
                            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                            filename_with_timestamp = f"{timestamp}_{filename}"

                            # Guardar el archivo en el servidor
                            file_path = os.path.join(upload_dir, filename_with_timestamp)
                            documento.save(file_path)
                            print(f"Archivo guardado en: {file_path}")

                            # Insertar información del archivo en tbl_documentos
                            sql_documento = ("INSERT INTO tbl_documentos "
                                                "(id_contrato, nombre_documento, usuario_registro) "
                                                "VALUES (%s, %s, %s)")
                            valores_documento = (id_contrato, filename_with_timestamp, session['name_surname'])
                            cursor.execute(sql_documento, valores_documento)

                conexion_MySQLdb.commit()
                return "Registro exitoso", 200

    except Exception as e:
        print(f"Error: {str(e)}")  # Agregar depuración
        return f'Se produjo un error en procesar_form_contratos: {str(e)}', 500
    
    
def sql_lista_contratosBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    SELECT 
                        c.id_contrato,
                        c.documento,
                        c.razon_social,
                        c.cantidad,
                        c.objeto_contractual,
                        c.fecha_inicio,
                        c.fecha_fin,
                        c.fecha_registro
                    FROM tbl_contratos as c
                    ORDER BY fecha_registro DESC
                    """
                cursor.execute(querySQL)
                contratosBD = cursor.fetchall()  # Devuelve la lista de contratos
        return contratosBD
    except Exception as e:
        print(f"Error en la función sql_lista_contratosBD: {e}")
        return None

def sql_detalles_contratosBD(id_contrato):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                # Obtener detalles del contrato
                querySQL = ("""
                    SELECT 
                        c.id_contrato,
                        c.documento,
                        c.razon_social,
                        c.cantidad,
                        c.objeto_contractual,
                        c.fecha_inicio,
                        c.fecha_fin,
                        DATE_FORMAT(c.fecha_registro, '%Y-%m-%d %h:%i %p') AS fecha_registro,
                        c.usuario_registro
                    FROM tbl_contratos AS c
                    WHERE id_contrato = %s
                """)
                cursor.execute(querySQL, (id_contrato,))
                contratoBD = cursor.fetchone()

                # Obtener los documentos asociados al contrato
                querySQL_docs = ("""
                    SELECT 
                        d.nombre_documento
                    FROM tbl_documentos AS d
                    WHERE d.id_contrato = %s
                """)
                cursor.execute(querySQL_docs, (id_contrato,))
                documentosBD = cursor.fetchall()

                # Agregar los documentos al resultado del contrato
                contratoBD['documentos'] = documentosBD

        return contratoBD
    except Exception as e:
        print(f"Error en la función sql_detalles_contratosBD: {e}")
        return None
    
def buscarContratoUnico(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                querySQL = ("""
                        SELECT 
                            c.id_contrato,
                            c.documento,
                            c.razon_social,
                            c.cantidad,
                            c.objeto_contractual,
                            c.fecha_inicio,
                            c.fecha_fin,
                            c.fecha_registro,
                            c.usuario_registro
                        FROM tbl_contratos AS c
                        WHERE c.id_contrato =%s LIMIT 1
                    """)
                mycursor.execute(querySQL, (id,))
                contrato = mycursor.fetchone()
                return contrato
    except Exception as e:
        print(f"Ocurrió un error en def buscarContratoUnico: {e}")
        return []
    
def procesar_actualizacion_contrato(data):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                id_contrato = data.form['id_contrato']
                documento = data.form['documento']
                razon_social = data.form['razon_social']
                objeto_contractual = data.form['objeto_contractual']
                cantidad = data.form['valor']
                fecha_inicio = data.form['fecha_inicio'] 
                fecha_fin = data.form['fecha_fin']             
                querySQL = """
                    UPDATE tbl_contratos
                    SET 
                        documento = %s,
                        razon_social = %s,
                        objeto_contractual=%s,
                        cantidad = %s,
                        fecha_inicio = %s,
                        fecha_fin= %s
                    WHERE id_contrato = %s
                """
                values = (documento, razon_social,objeto_contractual, cantidad,fecha_inicio,fecha_fin,id_contrato)

                cursor.execute(querySQL, values)
                conexion_MySQLdb.commit()

        return cursor.rowcount or []
    except Exception as e:
        print(f"Ocurrió un error en procesar_actualizar_contrato: {e}")
        return None
    
# Eliminar OPeracion
def eliminarOperacion(id_operacion):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM tbl_operaciones WHERE id_operacion=%s"
                cursor.execute(querySQL, (id_operacion,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminar operacion : {e}")
        return []
    
# Eliminar Contrato
def eliminarContrato(id_contrato):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM tbl_contratos WHERE id_contrato=%s"
                cursor.execute(querySQL, (id_contrato,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminar el contrato : {e}")
        return []
 
 
###INNOVACION  
def procesar_form_innovaciones(dataForm):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:

                sql = ("INSERT INTO tbl_innovacion (titulo_idea, fecha_inicio, descripcion_idea, espacio_problema, aspecto, roles, estrategias, diseño, implementacion,fecha_plazo, evaluacion, aprender_planear, ajustes, fecha_fin, usuario_registro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

                # Creando una tupla con los valores del INSERT
                valores = (
                    dataForm.get('titulo'),
                    dataForm.get('date_inicio'),
                    dataForm.get('idea'),
                    dataForm.get('problema'),
                    dataForm.get('afecta'),
                    dataForm.get('definir_role'),
                    dataForm.get('estrategias'),
                    dataForm.get('diseño'),
                    dataForm.get('implementacion'),
                    dataForm.get('date_implementacion'),
                    dataForm.get('evaluacion'),
                    dataForm.get('diseñar'),
                    dataForm.get('ajustes'),
                    dataForm.get('date_fin'),
                    session.get('name_surname')
                )
                
                print("Tupla de valores:", valores)
                
                cursor.execute(sql, valores)

                conexion_MySQLdb.commit()
                resultado_insert = cursor.rowcount
                print("Inserción completada con resultado:", resultado_insert)
                return resultado_insert

    except Exception as e:
        print(f'Error en procesar_form_innovaciones: {e}')
        raise  # Para que Flask muestre el error en la consola y/o navegador


def obtener_id_innovacion():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = ("""
                    SELECT 
                        DISTINCT 
                        concat(e.nombre_empleado," ",e.apellido_empleado) as nombre_empleado,
                        e.id_empleado
                    FROM tbl_empleados AS e
                    WHERE fecha_borrado IS NULL
                    ORDER BY e.id_empleado ASC
                    """)
                cursor.execute(querySQL,)
                innovacionesBD = cursor.fetchall()
                
                # Extraer solo los valores de id_innovacion de los diccionarios
                id_innovaciones = [innovacion['nombre_innovacion'] for innovacion in innovacionesBD]
        return id_innovaciones
    except Exception as e:
        print(f"Error en la función obtener_id_innovacion: {e}")
        return None
    
    # Lista de Innovación
def sql_lista_innovacionesBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    SELECT 
                        `id_innovacion`,
                        `titulo_idea`,
                        `fecha_inicio`,
                        `descripcion_idea` ,
                        `espacio_problema`,
                        `aspecto`,
                        `roles`,
                        `estrategias`,
                        `diseño`,
                        `implementacion`,
                        `fecha_plazo`,
                        `evaluacion`,
                        `aprender_planear`,
                        `ajustes`,
                        `fecha_fin`,
                        `fecha_registro`,
                        `usuario_registro`
                        FROM bd_contratos.tbl_innovacion
                        ORDER BY id_innovacion DESC
                    """
                cursor.execute(querySQL)
                innovacionBD = cursor.fetchall()
        return innovacionBD
    except Exception as e:
        print(f"Error en la función sql_lista_innovacionesBD: {e}")
        return None
    
    
def sql_detalles_innovacionesBD(id_innovacion):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = ("""
                    SELECT 
                        `id_innovacion`,
                        `titulo_idea`,
                        `fecha_inicio`,
                        `descripcion_idea` ,
                        `espacio_problema`,
                        `aspecto`,
                        `roles`,
                        `estrategias`,
                        `diseño`,
                        `implementacion`,
                        `fecha_plazo`,
                        `evaluacion`,
                        `aprender_planear`,
                        `ajustes`,
                        `fecha_fin`,
                        DATE_FORMAT(fecha_registro, '%Y-%m-%d %h:%i %p') AS fecha_registro,
                        usuario_registro
                    FROM bd_contratos.tbl_innovacion
                    WHERE id_innovacion =%s
                    """)
                cursor.execute(querySQL, (id_innovacion,))
                innovacionBD = cursor.fetchone()
                print(innovacionBD) 
        return innovacionBD
    except Exception as e:
        print(
            f"Errro en la función sql_detalles_innovacionesBD: {e}")
        return None


# Eliminar Innovación
def eliminarInnovacion(id_innovacion):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM tbl_innovacion WHERE id_innovacion=%s"
                cursor.execute(querySQL, (id_innovacion,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminar el registro : {e}")
        return []
    
    
    
## PERCEPCION
def procesar_form_percepcion(dataForm):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:

                sql = ("INSERT INTO tbl_percepcion (tipo, pregunta, respuesta, usuario_registro) VALUES (%s, %s, %s, %s)")

                # Definir los grupos y las preguntas
                tipos_preguntas = {
                    'Performance Expectancy': {
                        'pregunta1': '-El uso de la idea de innovación mejorará mi eficiencia en las tareas relacionadas con el proceso.',
                        'pregunta2': '-La implementación de la nueva tecnología digital aumentará la calidad de los resultados de la empresa.'
                    },
                    'Effort Expectancy': {
                        'pregunta3': '-Aprender a utilizar la nueva tecnología digital implementada en el proceso de innovación es fácil.',
                        'pregunta4': '-Me siento comod@ utilizando la nueva tecnología digital para completar las tareas asignadas en el proceso de innovación.'
                    }
                }

                # Recorrer las preguntas y almacenar sus respuestas
                for tipo, preguntas in tipos_preguntas.items():
                    for key, pregunta in preguntas.items():
                        respuesta = dataForm.get(key)
                        if respuesta:  # Solo guardar si la respuesta existe
                            valores = (
                                tipo,  # Tipo de pregunta (grupo)
                                pregunta,  # Pregunta específica
                                respuesta,  # Respuesta del usuario
                                session.get('name_surname')  # Nombre del usuario
                            )

                            print("Insertando valores:", valores)
                            cursor.execute(sql, valores)

                conexion_MySQLdb.commit()
                resultado_insert = cursor.rowcount
                print("Inserción completada con resultado:", resultado_insert)
                return resultado_insert

    except Exception as e:
        print(f'Error en procesar_form_percepcion: {e}')
        raise  # Para que Flask muestre el error en la consola y/o navegador


    # Lista de Innovación
def sql_lista_percepcionesBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    SELECT 
                        id_percepcion,
                        tipo, 
                        pregunta, 
                        respuesta, 
                        fecha_registro,
                        usuario_registro
                        FROM bd_contratos.tbl_percepcion
                        ORDER BY fecha_registro DESC,tipo DESC, pregunta DESC
                    """
                cursor.execute(querySQL)
                percepcionBD = cursor.fetchall()
        return percepcionBD
    except Exception as e:
        print(f"Error en la función sql_lista_percepcionesBD: {e}")
        return None 


def eliminarPercepcion(id_percepcion):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM tbl_percepcion WHERE id_percepcion=%s"
                cursor.execute(querySQL, (id_percepcion,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminar el registro : {e}")
        return []   
    