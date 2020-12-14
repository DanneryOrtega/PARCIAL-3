from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'spbYO0JJOPUFLUikKYbKrpS5w3KUEnab5KcYDdYb'
db = sqlite3.connect('data.db', check_same_thread=False)
class Categoria:
    id = 0
    
    def setId(self, id):
        self.id = id

    def getId(self):
        return self.id
categoriaC = Categoria()

class Producto:
    id = 0
    
    def setId(self, id):
        self.id = id

    def getId(self):
        return self.id
productoC = Producto()

class Perfil:
    id = 0
    
    def setId(self, id):
        self.id = id

    def getId(self):
        return self.id
perfilC = Perfil()

# Rutas
@app.route('/index') # / significa la ruta raiz
def index():
    return render_template('index.html')


@app.route('/registro')
def registro():
        return render_template('registro.html')


@app.route('/guardar_registro', methods=['POST'])
def guardar_registro():
    if request.method == 'POST':
        
        nombres = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('contrasena')

        mensaje = ''

        if(nombres == ""):
            mensaje += 'El campo nombres es requerido '
        
        if(email == ""):
            mensaje += 'El campo email es requerido '

        if(password == ""):
            mensaje += 'El campo password es requerido '
        
        if(len(mensaje) > 0):
            flash(mensaje, 'error')
            return redirect(url_for('registro'))
        
        correo = db.execute('select * from usuarios where email = ?', (email,)).fetchall()
        if(len(correo) > 0):
            flash('Ya existe un usuario con este email', 'error')
            return redirect(url_for('registro'))

        cursor = db.cursor()
        cursor.execute("""insert into usuarios(
                nombres,
                email,
                password
            )values (?,?,?)
        """, (nombres, email, password,))

        db.commit()

        return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST']) 
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email')
    password = request.form.get('password') #ENCRIPTACION

    usuario = db.execute("""select * from usuarios where 
        email = ? and password = ?""", (email, password,)).fetchone()
    
    if usuario is None:
        flash('Las credenciales no son válidas', 'error')
        return redirect(request.url)

    session['usuario'] = usuario

    return redirect(url_for('index'))

@app.route('/logout') 
def logout():
    session.clear()

    return redirect(url_for('login'))

@app.route('/usuarios')
def usuarios():
    if not 'usuario' in session:
        return redirect(url_for('login'))
    print(session['usuario'])
    usuarios = db.execute('select * from usuarios')

    usuarios = usuarios.fetchall()

    return render_template('usuarios/listar.html', usuarios=usuarios)

@app.route('/usuarios/crear', methods=['GET', 'POST'])
def crear_usuarios():
    if request.method == 'GET':
        return render_template('usuarios/crear.html')
    
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    email = request.form.get('email')
    password = request.form.get('password')

    #Validando que el correo no este en uso
    usuario = db.execute('select * from usuarios where email = ?', (email,)).fetchall()

    if(nombres == ""):
        flash('El campo nombres es requerido', 'error')
        return redirect(request.url)

    if(len(usuario) > 0):
        flash('Ya existe un usuario con este email', 'error')
        return redirect(request.url)

    try:
        cursor = db.cursor()
        cursor.execute("""insert into usuarios(
                nombres,
                apellidos,
                email,
                password
            )values (?,?,?,?)
        """, (nombres, apellidos, email, password,))

        db.commit()
    except:
        flash('No se ha podido guardar el usuario', 'error')
        return redirect(url_for('usuarios'))

    flash('Usuario creado correctamente', 'success')

    return redirect(url_for('usuarios'))


@app.route('/perfil')
def perfil():
    return render_template('perfil.html')


@app.route('/editar_perfil')
def editar_perfil():
    return render_template('editar_per.html')

@app.route('/actualizar_per', methods=['GET', 'POST'])
def actualizar_per():
     if request.method == 'POST':        
        #SIN Id
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        email = request.form.get('email')
        mensaje = ''

        #print(session['usuario'][0])

        if(nombres == ""):
            mensaje += 'El campo nombre es requerido '
        if(apellidos == ""):
            mensaje += 'El campo apellido es requerido '
        if(email == ""):
            mensaje += 'El campo email es requerido '

        if(len(mensaje) > 0):
            flash(mensaje,'error')
            return redirect(url_for('editar_perfil'))

        cursor = db.cursor()
        cursor.execute("""update usuarios set nombres = ?, apellidos = ?, email = ? where id = ? 
        """, (nombres, apellidos, email, session['usuario'][0],))

        db.commit()

        flash('Su perfil se edito correctamente', 'success')

        return redirect(url_for('index'))



@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if request.method == 'GET':
        usuario = db.execute('select * from usuarios where id = ?', (id,)).fetchone()
        
        return render_template('usuarios/editar.html', usuario=usuario)

    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    email = request.form.get('email')

    cursor = db.cursor()
    cursor.execute("""update usuarios set nombres = ?,
        apellidos = ?, email = ? where id = ? 
    """, (nombres, apellidos, email, id,))

    db.commit()

    flash('Usuario editado correctamente', 'success')

    return redirect(url_for('usuarios'))

@app.route('/eliminar/<id>')
def eliminar_usuarios(id):
    cursor = db.cursor()

    query ='DELETE FROM usuarios WHERE id=?'
    cursor.execute(query, (id,))
    db.commit()

    return redirect(url_for('usuarios'))

@app.route('/categoria')
def categoria():
    
    id_us = session['usuario'][0]

    categoria = db.execute("""select * from categoria where 
        id_usuario = ?""", ( id_us,)).fetchall()

    return render_template('categoria.html', categorias = categoria)

@app.route('/crear')
def crear_categoria():
    return render_template('reg_cat.html')


@app.route('/guardar', methods=['GET', 'POST'])
def guardar_categoria():

    if request.method == 'POST':
        
        nombres = request.form.get('nombre')

        mensaje = ''

        if(nombres == ""):
            mensaje += 'El campo nombre es requerido'
            flash(mensaje, 'error')
            return redirect(url_for('crear_categoria'))
        cursor = db.cursor()
        cursor.execute("""insert into categoria(
                nombre,
                id_usuario
            )values (?,?)
        """, (nombres, session['usuario'][0],))

        db.commit()

        return redirect(url_for('categoria'))

@app.route('/editar_cat/<int:id>')
def editar_cat(id):
    categoriaC.setId(id=id)
    return render_template('editar_cat.html')

@app.route('/actualizar_cat', methods=['GET', 'POST'])
def actualizar_cat():
    if request.method == 'POST':
    
        nombres = request.form.get('nombre')
        mensaje = ''

        if(nombres == ""):
            mensaje += 'El campo nombre es requerido '
            return redirect(url_for('editar_cat'))
        cursor = db.cursor()
        cursor.execute("""update categoria set nombre = ? where id = ? 
        """, (nombres, categoriaC.getId(),))

        db.commit()

        flash('Categoria editada correctamente', 'success')

        return redirect(url_for('categoria'))

@app.route('/eliminar_cat/<id>')
def eliminar_cat(id):
    cursor = db.cursor()

    query ='DELETE FROM categoria WHERE id=?'
    cursor.execute(query, (id,))
    db.commit()

    flash('Categoria eliminada correctamente', 'success')

    return redirect(url_for('categoria'))

@app.route('/producto')
def producto():
    
    id_us = session['usuario'][0]

    producto = db.execute("""select * from producto where 
        id_usuario = ?""", ( id_us,)).fetchall()

    return render_template('productos.html', productos=producto)

@app.route('/crear_pro')
def crear_pro():

     id_us = session['usuario'][0]
     categoria = db.execute("""select * from categoria where 
      id_usuario = ?""", ( id_us,)).fetchall()
     return render_template('reg_pro.html', categorias = categoria)


@app.route('/guardar_pro', methods=['GET', 'POST'])
def guardar_pro():

     if request.method == 'POST':
        
        nombres = request.form.get('nombre')
        precio = request.form.get('precio')
        categoria = str(request.form.get('categoria'))

        mensaje = ''

        if(nombres == ""):
            mensaje += 'El campo nombre es requerido '
        if(precio == ""):
            mensaje += 'El campo precio es requerido '
        if(categoria == "None"):
            mensaje += 'El campo categoria es requerido '
        if(len(mensaje) > 0):
            flash(mensaje,'error')
            return redirect(url_for('crear_pro'))
        
        cursor = db.cursor()
        cursor.execute("""insert into producto(
                 nombre,
                 precio,
                 categoria,
                 id_usuario
             )values (?,?,?,?)
         """, (nombres, precio, categoria, session['usuario'][0],))

        db.commit()
        return redirect(url_for('producto'))
#---------------------------------------------------------------
@app.route('/editar_pro/<int:id>')
def editar_pro(id):
    productoC.setId(id=id)
    categoria = db.execute("""select * from categoria where 
      id_usuario = ?""", ( session['usuario'][0],)).fetchall()
    return render_template('editar_pro.html', categorias = categoria)
########
     

@app.route('/actualizar_pro', methods=['GET', 'POST'])
def actualizar_pro():
    if request.method == 'POST':
    
        nombres = request.form.get('nombre')
        precio = request.form.get('precio')
        categoria = str(request.form.get('categoria'))
            
        mensaje = ''

        if(nombres == ""):
            mensaje += 'El campo nombre es requerido '
        if(precio == ""):
            mensaje += 'El campo precio es requerido '
        if(categoria == "None"):
            mensaje += 'El campo categoria es requerido '

        if(len(mensaje) > 0):
            flash(mensaje,'error')
            return redirect(url_for('editar_pro', id = productoC.getId()))
        
        cursor = db.cursor()
   
        cursor.execute("""update producto set nombre = ?, 
            precio = ?, categoria = ? where id = ? 
        """, (nombres, precio, categoria, productoC.getId(),))

        db.commit()

        flash('Producto editado correctamente', 'success')

        return redirect(url_for('producto'))

@app.route('/eliminar_pro/<id>')
def eliminar_pro(id):
     cursor = db.cursor()

     query ='DELETE FROM producto WHERE id=?'
     cursor.execute(query, (id,))
     db.commit()

     flash('Producto eliminado correctamente', 'success')

     return redirect(url_for('producto'))


app.run(debug=True)