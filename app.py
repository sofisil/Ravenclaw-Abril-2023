#Importamos las librerias necesarias
import pandas as pd, sqlite3,os.path
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


# Creamos una instancia de la clase Flask
app = Flask(__name__)
# Configuramos la ruta de la base de datos SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# Creamos una instancia del objeto SQLAlchemy e inicializamos con la aplicacion
db = SQLAlchemy(app)

# Creamos la clase Funcionarios que hereda de db.Model
class Datos_personales(db.Model):
    
    # Definimos las columnas de la tabla Datos_personales
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    apellido = db.Column(db.String(200), nullable=False)
    fecha_nacimiento = db.Column(db.Integer)
    ci = db.Column(db.Integer)
    email = db.Column(db.Text)
    telefono = db.Column(db.Integer)
    direccion = db.Column(db.Text)

    # Definimos el constructor de la clase
    def __init__(self, nombre,apellido, fecha_nacimiento, ci, email, telefono, direccion):
        self.nombre = nombre
        self.apellido = apellido
        self.fecha_nacimiento = fecha_nacimiento
        self.ci = ci
        self.email = email
        self.telefono = telefono
        self.direccion = direccion

    # Agregamos la relación con la tabla Datos_institucionales
    institucionales = db.relationship('Datos_institucionales', backref='datos_personales', uselist=False)

class Datos_institucionales(db.Model):
    # Definimos las columnas de la tabla Datos_institucionales
    id = db.Column(db.Integer, primary_key=True)
    ci = db.Column(db.Integer)
    fecha_ingreso = db.Column(db.Integer)
    cargo = db.Column(db.Text)
    piso_departamento = db.Column(db.Text)
    nro_interno = db.Column(db.Text)
    correo_institucional = db.Column(db.Text)


    def __init__(self, ci, fecha_ingreso, cargo, piso_departamento, nro_interno, correo_institucional):
        self.ci = ci
        self.fecha_ingreso = fecha_ingreso
        self.cargo = cargo
        self.piso_departamento = piso_departamento
        self.nro_interno = nro_interno
        self.correo_institucional = correo_institucional

    # Agregamos la columna de clave foránea que hace referencia a la tabla Datos_personales
    datos_personales_id = db.Column(db.Integer, db.ForeignKey('datos_personales.id'))

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login")
def login():
    return render_template('login.html')

# Definimos la ruta '/form' que responde a los métodos GET y POST
@app.route("/cargar_datos", methods=["GET", "POST"])
def cargar_datos():
    # Verificamos si se recibió un POST
    if request.method == "POST":
        # Obtenemos los datos del formulario
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        fecha_nacimiento = request.form["fecha_nacimiento"]
        ci = request.form["ci"]
        email = request.form["email"]
        telefono = request.form["telefono"]
        direccion = request.form["direccion"]

        #datos institucionales
        fecha_ingreso = request.form["fecha_ingreso"]
        cargo = request.form["cargo"]
        piso_departamento = request.form["piso_departamento"]
        nro_interno = request.form["nro_interno"]
        correo_institucional = request.form["correo_institucional"]

        datos_personales = Datos_personales(nombre, apellido, fecha_nacimiento, ci, email, telefono, direccion)
        datos_institucionales = Datos_institucionales(ci,fecha_ingreso, cargo, piso_departamento, nro_interno, correo_institucional)

        
        # Agregamos el nuevo funcionario a la sesión
        db.session.add(datos_personales)
        db.session.add(datos_institucionales)

        # Confirmamos los cambios en la base de datos
        db.session.commit()
        # Devolvemos una respuesta al usuario
        return render_template("cargar_datos.html")
    
    # Si se recibió un GET, mostramos el formulario
    return render_template('cargar_datos.html')

# ---Ruta de acceso para carga de planillas de Excel---
@app.route("/cargar_planilla" , methods= ["GET", "POST"])
def cargar_planilla():

    if request.method == "POST":
        file = request.files["file"]
        file.save(file.filename)
        file_path = os.path.dirname(os.path.abspath(file.name))
        df1 = pd.read_excel(file_path + '/' + file.filename, sheet_name='datos_personales')
        df2 = pd.read_excel(file_path + '/' + file.filename, sheet_name='datos_institucionales')
        con = sqlite3.connect("instance/project.db")
        df_reset1 = df1.set_index("nombre")
        df_reset2 = df2.set_index("fecha_ingreso")
        df_reset1.to_sql("datos_personales", con, if_exists = "append")
        df_reset2.to_sql("datos_institucionales", con, if_exists = "append")

        return "Plantilla cargada exitosamente"

    else:
        return render_template("cargar_planilla.html")
    

# Definimos la ruta '/modif' que responde a los métodos GET y POST
@app.route("/modificar_datos" , methods=["GET", "POST"])
def modificar_datos():

    #Display de los funcionarios en el area de modificacion
    funcionarios = Datos_personales.query.all()
    print(funcionarios)    

    return render_template('modificar_datos.html', funcionarios=funcionarios)


@app.route("/buscar", methods=["GET","POST"])
def buscar():
        # Obtenemos los parámetros de búsqueda del formulario
        ci = request.args.get("search", default="", type=int)

        # Realizamos la búsqueda en la base de datos con los criterios recibidos
        funcionarios = db.session.query(Datos_personales).filter_by(ci=ci).all()
        institucionales= db.session.query(Datos_institucionales).filter_by(ci=ci).all()

        for i in institucionales:
            i.ci= ""


        general = funcionarios + institucionales
        print("######################")
        print(funcionarios)
        print("######################")
        print(institucionales)
        print("######################")
        print(general)
         # Devolvemos una vista con los resultados de la búsqueda

        return render_template("resultados_busqueda.html", general=general)

@app.route('/eliminar_datos', methods=["GET", "POST"])
def eliminar_datos():
    datos_personales = Datos_personales.query.all()  
    datos_institucionales = Datos_institucionales.query.all()
        
    return render_template('eliminar_datos.html', datos_personales = datos_personales, datos_institucionales = datos_institucionales)



@app.route('/eliminar_datos/<nombre>',methods = ["GET","POST"])
def eliminar_datos_nombre(nombre):
    datos_personales = Datos_personales.query.all()  
    datos_institucionales = Datos_institucionales.query.all()

    if request.method == 'GET':

        # nombre = request.args.get('nombre')
        nombre = nombre
        print(f' este trae el nombre {nombre}')
        # usuario_eliminar = Datos_personales.query.get(nombre)
        # print(usuario_eliminar)
        usuario_a_eliminar = db.session.query(Datos_personales).filter_by(nombre=nombre).first() # filtrar los datos por el valor de nombre
        print(usuario_a_eliminar)

        db.session.delete(usuario_a_eliminar)
        db.session.commit()
            

        return redirect(url_for("eliminar_datos"))

    return render_template('eliminar_datos.html', datos_personales=datos_personales, datos_institucionales=datos_institucionales)


@app.route('/perfil_funcionario')
def perfil_funcionario():

    return render_template('perfil_funcionario_comun.html')


@app.route('/solicitudes_funcionario')
def solicitudes_funcionario():

    return render_template('solicitudes_funcionario_comun.html')


@app.route('/solicitudes_talentos_humanos')
def solicitudes_talentos_humanos():

    return render_template('solicitudes_talento_humano.html')

@app.route('/perfil_talentos_humanos')
def perfil_talentos_humanos():

    return render_template('perfil_talento_humano.html')


# Creamos las tablas en la base de datos
with app.app_context():
    db.create_all(bind_key='__all__')

# Iniciamos la aplicación
if __name__ == "__main__":
    app.run(debug=True)