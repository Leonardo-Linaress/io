import tkinter as tk
from tkinter import messagebox, Menu
from PIL import Image, ImageTk
import cv2
import firebase_admin
from firebase_admin import credentials, firestore
import os,json
from tkinter import filedialog
import base64
from io import BytesIO
from tkinter import Toplevel, StringVar
import datetime
import webbrowser
import pygame

productos_carrito = []

def reproducir_musica():

    try:

        pygame.mixer.init()

        ruta_musica = "E:/programas/song.mp3"  

        pygame.mixer.music.load(ruta_musica)
        pygame.mixer.music.set_volume(0.5) 
        pygame.mixer.music.play(-1) 
        print("Música de fondo reproduciéndose.")
    except Exception as e:
        print(f"Error al reproducir música: {e}")

def abrir_link(url):
    webbrowser.open_new(url)
def obtener_producto_mas_consumido(correo_usuario):
   
    try:
        
        usuarios_ref = db.collection("usuarios")
        query = usuarios_ref.where("correo", "==", correo_usuario).limit(1).stream()
        
        for doc in query:
            datos_usuario = doc.to_dict()
            
           
            if "estadisticas_productos" in datos_usuario and datos_usuario["estadisticas_productos"]:
                estadisticas = datos_usuario["estadisticas_productos"]
                
                # Encontrar el producto más consumido
                producto_max = max(estadisticas.items(), key=lambda x: x[1])
                return producto_max  # (nombre_producto, cantidad)
            
            return (None, 0)  # No hay estadísticas
        
        return (None, 0)  # Usuario no encontrado
        
    except Exception as e:
        print(f"Error al obtener producto más consumido: {e}")
        return (None, 0)

def actualizar_estadisticas_productos(correo_usuario, productos):
   
    try:
        # Buscar el documento del usuario
        usuarios_ref = db.collection("usuarios")
        query = usuarios_ref.where("correo", "==", correo_usuario).limit(1).stream()
        
        doc_id = None
        for doc in query:
            doc_id = doc.id
            break
        
        if not doc_id:
            print(f"No se encontró el usuario {correo_usuario} para actualizar estadísticas")
            return
        
        # Obtener el documento del usuario
        doc_ref = db.collection("usuarios").document(doc_id)
        doc = doc_ref.get()
        datos_usuario = doc.to_dict()
        
        # Inicializar o recuperar estadísticas de productos
        if "estadisticas_productos" not in datos_usuario:
            estadisticas = {}
        else:
            estadisticas = datos_usuario["estadisticas_productos"]
        
        # Actualizar estadísticas para cada producto comprado
        for producto in productos:
            nombre_producto = producto["nombre"]
            cantidad = producto["cantidad"]
            
            if nombre_producto in estadisticas:
                estadisticas[nombre_producto] += cantidad
            else:
                estadisticas[nombre_producto] = cantidad
        
        # Actualizar el documento del usuario con las nuevas estadísticas
        doc_ref.update({"estadisticas_productos": estadisticas})
        print(f"Estadísticas de productos actualizadas para {correo_usuario}")
        
    except Exception as e:
        print(f"Error al actualizar estadísticas de productos: {e}")


def editar_perfil():
    
    correo_actual = cargar_sesion()
    if not correo_actual:
        messagebox.showwarning("Advertencia", "Debes iniciar sesión para editar tu perfil.")
        return
    
    # Buscar los datos actuales del usuario
    try:
        usuarios_ref = db.collection("usuarios")
        query = usuarios_ref.where("correo", "==", correo_actual).limit(1).stream()
        
        doc_id = None
        datos_usuario = None
        
        for doc in query:
            doc_id = doc.id
            datos_usuario = doc.to_dict()
            break
        
        if not doc_id or not datos_usuario:
            messagebox.showerror("Error", "No se encontró el usuario en la base de datos.")
            return
        
        # Crear ventana emergente para editar datos
        ventana_editar = Toplevel()
        ventana_editar.title("Editar Perfil")
        ventana_editar.geometry("400x450")
        ventana_editar.configure(bg="#E3F2FD")
        
        # Hacer que la ventana sea modal
        ventana_editar.transient(ventana)
        ventana_editar.grab_set()
        
        # Título de la ventana
        tk.Label(ventana_editar, text="Editar Perfil", 
                font=("Arial", 18, "bold"), bg="#E3F2FD", fg="#0D47A1").pack(pady=15)
        
        # Frame para los campos de edición
        frame_campos = tk.Frame(ventana_editar, bg="#E3F2FD", bd=2, relief="groove")
        frame_campos.pack(padx=20, pady=10, fill="x")
        
        # Nombre
        frame_nombre = tk.Frame(frame_campos, bg="#E3F2FD")
        frame_nombre.pack(fill="x", pady=10)
        
        tk.Label(frame_nombre, text="Nombre:", font=("Arial", 12, "bold"), 
                bg="#E3F2FD", fg="#0D47A1").pack(side="left", padx=10)
        
        nombre_var = StringVar(value=datos_usuario.get("nombre", ""))
        entrada_nombre = tk.Entry(frame_nombre, textvariable=nombre_var, width=25, 
                                font=("Arial", 12))
        entrada_nombre.pack(side="left", padx=5)
        
        # Teléfono
        frame_telefono = tk.Frame(frame_campos, bg="#E3F2FD")
        frame_telefono.pack(fill="x", pady=10)
        
        tk.Label(frame_telefono, text="Teléfono:", font=("Arial", 12, "bold"), 
                bg="#E3F2FD", fg="#0D47A1").pack(side="left", padx=10)
        
        telefono_var = StringVar(value=datos_usuario.get("telefono", ""))
        entrada_telefono = tk.Entry(frame_telefono, textvariable=telefono_var, width=25, 
                                  font=("Arial", 12))
        entrada_telefono.pack(side="left", padx=5)
        
        # Dirección
        frame_direccion = tk.Frame(frame_campos, bg="#E3F2FD")
        frame_direccion.pack(fill="x", pady=10)
        
        tk.Label(frame_direccion, text="Dirección:", font=("Arial", 12, "bold"), 
                bg="#E3F2FD", fg="#0D47A1").pack(side="left", padx=10)
        
        direccion_var = StringVar(value=datos_usuario.get("direccion", ""))
        entrada_direccion = tk.Entry(frame_direccion, textvariable=direccion_var, width=25, 
                                   font=("Arial", 12))
        entrada_direccion.pack(side="left", padx=5)
        
        # Contraseña actual
        frame_pass_actual = tk.Frame(frame_campos, bg="#E3F2FD")
        frame_pass_actual.pack(fill="x", pady=10)
        
        tk.Label(frame_pass_actual, text="Contraseña\nActual:", font=("Arial", 12, "bold"), 
                bg="#E3F2FD", fg="#0D47A1").pack(side="left", padx=10)
        
        pass_actual_var = StringVar()
        entrada_pass_actual = tk.Entry(frame_pass_actual, textvariable=pass_actual_var, width=25, 
                                     font=("Arial", 12), show="*")
        entrada_pass_actual.pack(side="left", padx=5)
        
        # Nueva contraseña
        frame_pass_nueva = tk.Frame(frame_campos, bg="#E3F2FD")
        frame_pass_nueva.pack(fill="x", pady=10)
        
        tk.Label(frame_pass_nueva, text="Nueva\nContraseña:", font=("Arial", 12, "bold"), 
                bg="#E3F2FD", fg="#0D47A1").pack(side="left", padx=10)
        
        pass_nueva_var = StringVar()
        entrada_pass_nueva = tk.Entry(frame_pass_nueva, textvariable=pass_nueva_var, width=25, 
                                    font=("Arial", 12), show="*")
        entrada_pass_nueva.pack(side="left", padx=5)
        
        # Función para guardar los cambios
        def guardar_cambios():
            # Verificar contraseña actual
            if pass_actual_var.get() != datos_usuario.get("contrasena", ""):
                messagebox.showerror("Error", "La contraseña actual es incorrecta.")
                return
            
            # Preparar datos actualizados
            datos_actualizados = {}
            
            # Solo actualizar campos que han cambiado
            if nombre_var.get() != datos_usuario.get("nombre", ""):
                datos_actualizados["nombre"] = nombre_var.get()
            
            if telefono_var.get() != datos_usuario.get("telefono", ""):
                datos_actualizados["telefono"] = telefono_var.get()
            
            if direccion_var.get() != datos_usuario.get("direccion", ""):
                datos_actualizados["direccion"] = direccion_var.get()
            
            if pass_nueva_var.get():
                datos_actualizados["contrasena"] = pass_nueva_var.get()
            
            # Si no hay cambios, no hacer nada
            if not datos_actualizados:
                messagebox.showinfo("Sin cambios", "No se detectaron cambios en los datos.")
                ventana_editar.destroy()
                return
            
            # Actualizar en Firebase
            try:
                db.collection("usuarios").document(doc_id).update(datos_actualizados)
                messagebox.showinfo("Éxito", "Datos actualizados correctamente.")
                ventana_editar.destroy()
                
                # Recargar los datos del perfil
                cargar_datos_perfil()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron actualizar los datos: {e}")
        
        # Botones para guardar o cancelar
        frame_botones = tk.Frame(ventana_editar, bg="#E3F2FD")
        frame_botones.pack(pady=20)
        
        btn_guardar = tk.Button(frame_botones, text="Guardar Cambios", 
                              command=guardar_cambios,
                              bg="#1565C0", fg="white", font=("Arial", 12, "bold"), 
                              relief="flat", padx=15, pady=5)
        btn_guardar.pack(side="left", padx=10)
        
        btn_cancelar = tk.Button(frame_botones, text="Cancelar", 
                               command=ventana_editar.destroy,
                               bg="#78909C", fg="white", font=("Arial", 12), 
                               relief="flat", padx=15, pady=5)
        btn_cancelar.pack(side="left", padx=10)
        
        # Centrar la ventana emergente en la pantalla
        ventana_editar.update_idletasks()
        ancho = ventana_editar.winfo_width()
        alto = ventana_editar.winfo_height()
        x = (ventana_editar.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana_editar.winfo_screenheight() // 2) - (alto // 2)
        ventana_editar.geometry(f"{ancho}x{alto}+{x}+{y}")
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la edición de perfil: {e}")


def guardar_carrito_en_firebase():
    """
    Guarda el contenido del carrito en Firebase para el usuario actual.
    """
    correo_actual = cargar_sesion()
    if not correo_actual:
        return  # No hay sesión activa, no se puede guardar el carrito

    try:
        # Buscar el documento del usuario
        usuarios_ref = db.collection("usuarios")
        query = usuarios_ref.where("correo", "==", correo_actual).limit(1).stream()

        doc_id = None
        for doc in query:
            doc_id = doc.id
            break

        if doc_id:
            # Convertir los productos a un formato serializable
            productos_serializables = []
            for producto in productos_carrito:
                producto_serializable = {
                    "nombre": producto["nombre"],
                    "cantidad": producto["cantidad"],
                    "tamaño": producto["tamaño"],
                    "precio_unitario": float(producto["precio_unitario"]),
                    "precio_total": float(producto["precio_total"])
                }
                productos_serializables.append(producto_serializable)

            # Actualizar el documento con el carrito (puede ser vacío)
            db.collection("usuarios").document(doc_id).update({
                "carrito": productos_serializables
            })
            print(f"Carrito actualizado en Firebase para el usuario {correo_actual}")
        else:
            print(f"No se encontró el usuario {correo_actual} para guardar el carrito")

    except Exception as e:
        print(f"Error al guardar el carrito: {e}")


def cargar_carrito_desde_firebase():
    """
    Carga el contenido del carrito desde Firebase para el usuario actual.
    """
    global productos_carrito
    correo_actual = cargar_sesion()
    if not correo_actual:
        return
    
    try:
        # Buscar el documento del usuario
        usuarios_ref = db.collection("usuarios")
        query = usuarios_ref.where("correo", "==", correo_actual).limit(1).stream()
        
        for doc in query:
            datos_usuario = doc.to_dict()
            if "carrito" in datos_usuario and datos_usuario["carrito"]:
                # Cargar los productos del carrito
                productos_carrito = datos_usuario["carrito"]
                print(f"Carrito cargado para el usuario {correo_actual}: {len(productos_carrito)} productos")
                return
        
        print(f"No se encontró carrito para el usuario {correo_actual}")
    
    except Exception as e:
        print(f"Error al cargar el carrito: {e}")

def agregar_al_carrito(producto, cantidad, tamaño, precio_unitario):
    print(f"Agregando al carrito: {producto}, {cantidad}, {tamaño}, {precio_unitario}")
    
    # Calcular precio total según tamaño y cantidad
    multiplicador = 1.0
    if tamaño == "Mediano":
        multiplicador = 1.5
    elif tamaño == "Grande":
        multiplicador = 2.0
    
    precio_ajustado = precio_unitario * multiplicador
    precio_total = precio_ajustado * cantidad
    
    # Crear objeto de producto
    nuevo_producto = {
        "nombre": producto,
        "cantidad": cantidad,
        "tamaño": tamaño,
        "precio_unitario": precio_ajustado,
        "precio_total": precio_total
    }
    
    # Agregar al carrito
    productos_carrito.append(nuevo_producto)
    print(f"Productos en carrito después de agregar: {len(productos_carrito)}")
    
    # Guardar el carrito en Firebase
    guardar_carrito_en_firebase()
    
    # Mostrar mensaje de confirmación
    messagebox.showinfo("Producto agregado", f"{cantidad} {producto} ({tamaño}) agregado(s) al carrito.")

def eliminar_del_carrito(indice):
    """
    Elimina un producto del carrito por su índice.
    """
    if 0 <= indice < len(productos_carrito):
        producto = productos_carrito[indice]
        productos_carrito.pop(indice)
        messagebox.showinfo("Producto eliminado", f"{producto['nombre']} eliminado del carrito.")
        actualizar_carrito()
        
        # Guardar el carrito actualizado en Firebase
        guardar_carrito_en_firebase()

def actualizar_carrito():
    """
    Actualiza la visualización del carrito de compras.
    """
    # Limpiar el frame de productos
    for widget in frame_productos_carrito.winfo_children():
        if widget != frame_encabezados:  # Mantener los encabezados
            widget.destroy()
    
    # Mostrar productos en el carrito
    if productos_carrito:
        for i, producto in enumerate(productos_carrito):
            # Fondo alternado para mejor visualización
            bg_color = "#F5F5F5" if i % 2 == 0 else "#FFFFFF"
            
            # Frame para cada fila de producto
            frame_producto = tk.Frame(frame_productos_carrito, bg=bg_color)
            frame_producto.pack(fill="x", pady=1)
            
            # Configurar columnas para los datos
            frame_producto.columnconfigure(0, weight=3)  # Producto
            frame_producto.columnconfigure(1, weight=1)  # Cantidad
            frame_producto.columnconfigure(2, weight=1)  # Tamaño
            frame_producto.columnconfigure(3, weight=1)  # Precio Unit.
            frame_producto.columnconfigure(4, weight=1)  # Precio Total
            frame_producto.columnconfigure(5, weight=1)  # Eliminar
            
            # Datos del producto
            tk.Label(frame_producto, text=producto["nombre"], font=("Arial", 11), 
                     bg=bg_color, anchor="w").grid(row=0, column=0, padx=10, pady=8, sticky="w")
            tk.Label(frame_producto, text=str(producto["cantidad"]), font=("Arial", 11), 
                     bg=bg_color).grid(row=0, column=1, padx=10, pady=8)
            tk.Label(frame_producto, text=producto["tamaño"], font=("Arial", 11), 
                     bg=bg_color).grid(row=0, column=2, padx=10, pady=8)
            tk.Label(frame_producto, text=f"${producto['precio_unitario']:.2f}", font=("Arial", 11), 
                     bg=bg_color).grid(row=0, column=3, padx=10, pady=8)
            tk.Label(frame_producto, text=f"${producto['precio_total']:.2f}", font=("Arial", 11, "bold"), 
                     bg=bg_color, fg="#01579B").grid(row=0, column=4, padx=10, pady=8)
            
            # Botón para eliminar producto
            btn_eliminar = tk.Button(frame_producto, text="X", bg="#F44336", fg="white", 
                                    font=("Arial", 8, "bold"), relief="flat", width=2,
                                    activebackground="#D32F2F", activeforeground="white",
                                    command=lambda idx=i: eliminar_del_carrito(idx))
            btn_eliminar.grid(row=0, column=5, padx=10, pady=8)
        
        # Actualizar el total
        actualizar_total()
    else:
        # Mensaje cuando el carrito está vacío
        frame_carrito_vacio = tk.Frame(frame_productos_carrito, bg="#E1F5FE", height=200)
        frame_carrito_vacio.pack(fill="both", expand=True)
        
        tk.Label(frame_carrito_vacio, text="Tu carrito está vacío", 
                 font=("Arial", 16, "italic"), bg="#E1F5FE", fg="#78909C").place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(frame_carrito_vacio, text="Agrega productos desde nuestro menú", 
                 font=("Arial", 12), bg="#E1F5FE", fg="#78909C").place(relx=0.5, rely=0.6, anchor="center")
        
        # Actualizar el total a cero
        actualizar_total()

def actualizar_total():
    """
    Actualiza el total mostrado en el carrito.
    """
    # Eliminar el frame de total anterior si existe
    for widget in frame_resumen.winfo_children():
        widget.destroy()
    
    # Calcular el total
    total = sum(producto["precio_total"] for producto in productos_carrito)
    
    # Mostrar el total
    frame_total = tk.Frame(frame_resumen, bg="#B3E5FC", bd=1, relief="raised")
    frame_total.pack(side="right", padx=30)
    
    tk.Label(frame_total, text="Total:", font=("Arial", 14, "bold"), 
             bg="#B3E5FC", fg="#01579B", padx=15, pady=10).pack(side="left")
    tk.Label(frame_total, text=f"${total:.2f}", font=("Arial", 16, "bold"), 
             bg="#B3E5FC", fg="#01579B", padx=15, pady=10).pack(side="left")

def finalizar_compra():
    """
    Procesa la finalización de la compra y registra el historial de compras.
    """
    if not productos_carrito:
        messagebox.showwarning("Carrito vacío", "No hay productos en el carrito.")
        return
    
    correo_actual = cargar_sesion()
    if not correo_actual:
        messagebox.showwarning("Advertencia", "Debes iniciar sesión para finalizar la compra.")
        return
    
    try:
        # Crear registro de compra
        fecha_compra = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_compra = sum(producto["precio_total"] for producto in productos_carrito)
        
        # Datos de la compra
        datos_compra = {
            "correo_usuario": correo_actual,
            "fecha": fecha_compra,
            "total": total_compra,
            "productos": []
        }
        
        # Añadir detalles de cada producto
        for producto in productos_carrito:
            detalle_producto = {
                "nombre": producto["nombre"],
                "cantidad": producto["cantidad"],
                "tamaño": producto["tamaño"],
                "precio_unitario": float(producto["precio_unitario"]),
                "precio_total": float(producto["precio_total"])
            }
            datos_compra["productos"].append(detalle_producto)
        
        # Guardar la compra en Firebase
        db.collection("pedidos").add(datos_compra)
        
        # Actualizar estadísticas de productos comprados por el usuario
        actualizar_estadisticas_productos(correo_actual, productos_carrito)
        
        # Limpiar el carrito localmente
        productos_carrito.clear()
        
        # Actualizar el carrito en Firebase (ahora vacío)
        usuarios_ref = db.collection("usuarios")
        query = usuarios_ref.where("correo", "==", correo_actual).limit(1).stream()
        
        doc_id = None
        for doc in query:
            doc_id = doc.id
            break
        
        if doc_id:
            db.collection("usuarios").document(doc_id).update({"carrito": []})
            print(f"Carrito vacío actualizado en Firebase para el usuario {correo_actual}")
        
        # Mostrar mensaje de confirmación
        messagebox.showinfo("Compra finalizada", "¡Gracias por tu compra! Tu pedido ha sido procesado.")
        
        # Actualizar la visualización
        actualizar_carrito()
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo procesar la compra: {e}")


def mostrar_opciones_producto(producto, precio_base):
    """
    Muestra una ventana emergente con opciones para agregar un producto al carrito.
    """
    print(f"Mostrando opciones para: {producto}, precio base: {precio_base}")
    
    # Crear una ventana emergente
    ventana_opciones = Toplevel()
    ventana_opciones.title(f"Agregar {producto}")
    ventana_opciones.geometry("350x400")
    ventana_opciones.configure(bg="#F8E0F7")
    
    # Hacer que la ventana sea modal (bloquea la interacción con la ventana principal)
    ventana_opciones.transient(ventana)
    ventana_opciones.grab_set()
    
    # Título de la ventana
    tk.Label(ventana_opciones, text=f"Opciones para {producto}", 
             font=("Arial", 16, "bold"), bg="#F8E0F7", fg="#9C27B0").pack(pady=15)
    
    # Frame para las opciones
    frame_opciones = tk.Frame(ventana_opciones, bg="#F8E0F7", bd=2, relief="groove")
    frame_opciones.pack(padx=20, pady=10, fill="x")
    
    # Cantidad
    frame_cantidad = tk.Frame(frame_opciones, bg="#F8E0F7")
    frame_cantidad.pack(fill="x", pady=10)
    
    tk.Label(frame_cantidad, text="Cantidad:", font=("Arial", 12, "bold"), 
             bg="#F8E0F7", fg="#9C27B0").pack(side="left", padx=10)
    
    # Variable para almacenar la cantidad
    cantidad_var = StringVar(value="1")
    
    # Función para actualizar el precio total
    def actualizar_precio(*args):
        try:
            cantidad = int(cantidad_var.get())
            if cantidad < 1:
                cantidad = 1
                cantidad_var.set("1")
            
            tamaño_seleccionado = tamaño_var.get()
            if tamaño_seleccionado == "Pequeño":
                precio_ajustado = precio_base
            elif tamaño_seleccionado == "Mediano":
                precio_ajustado = precio_base * 1.5
            else:  # Grande
                precio_ajustado = precio_base * 2
            
            precio_total = precio_ajustado * cantidad
            precio_total_var.set(f"${precio_total:.2f}")
        except ValueError:
            precio_total_var.set("$0.00")
    
    # Botones para aumentar/disminuir cantidad
    btn_menos = tk.Button(frame_cantidad, text="-", font=("Arial", 12, "bold"), 
                         bg="#D370D3", fg="white", width=2,
                         command=lambda: cantidad_var.set(str(max(1, int(cantidad_var.get()) - 1))))
    btn_menos.pack(side="left", padx=5)
    
    entrada_cantidad = tk.Entry(frame_cantidad, textvariable=cantidad_var, width=3, 
                               font=("Arial", 12), justify="center")
    entrada_cantidad.pack(side="left", padx=5)
    
    btn_mas = tk.Button(frame_cantidad, text="+", font=("Arial", 12, "bold"), 
                       bg="#D370D3", fg="white", width=2,
                       command=lambda: cantidad_var.set(str(int(cantidad_var.get()) + 1)))
    btn_mas.pack(side="left", padx=5)
    
    # Tamaño
    frame_tamaño = tk.Frame(frame_opciones, bg="#F8E0F7")
    frame_tamaño.pack(fill="x", pady=10)
    
    tk.Label(frame_tamaño, text="Tamaño:", font=("Arial", 12, "bold"), 
             bg="#F8E0F7", fg="#9C27B0").pack(side="left", padx=10)
    
    # Variable para almacenar el tamaño
    tamaño_var = StringVar(value="Pequeño")
    
    # Opciones de tamaño
    tamaños = ["Pequeño", "Mediano", "Grande"]
    
    # Frame para los radio buttons
    frame_radio = tk.Frame(frame_tamaño, bg="#F8E0F7")
    frame_radio.pack(side="left", padx=10)
    
    for tamaño in tamaños:
        rb = tk.Radiobutton(frame_radio, text=tamaño, variable=tamaño_var, value=tamaño,
                           bg="#F8E0F7", fg="#9C27B0", selectcolor="#F5C5F3",
                           command=actualizar_precio)
        rb.pack(anchor="w")
    
    # Precio total
    frame_precio = tk.Frame(frame_opciones, bg="#F8E0F7")
    frame_precio.pack(fill="x", pady=15)
    
    tk.Label(frame_precio, text="Precio Total:", font=("Arial", 14, "bold"), 
             bg="#F8E0F7", fg="#9C27B0").pack(side="left", padx=10)
    
    precio_total_var = StringVar(value=f"${precio_base:.2f}")
    tk.Label(frame_precio, textvariable=precio_total_var, font=("Arial", 14, "bold"), 
             bg="#F8E0F7", fg="#D370D3").pack(side="left", padx=10)
    
    # Función para agregar al carrito y cerrar la ventana
    def confirmar_agregar():
     try:
        cantidad = int(cantidad_var.get())
        tamaño = tamaño_var.get()
        
        print(f"Confirmando agregar: {producto}, {cantidad}, {tamaño}, {precio_base}")
        
        # Agregar al carrito
        agregar_al_carrito(producto, cantidad, tamaño, precio_base)
        
        # Cerrar la ventana
        ventana_opciones.destroy()
        
        # Mostrar el carrito (opcional)
        mostrar_frame(frame_carro)
     except ValueError:
        messagebox.showerror("Error", "Por favor ingresa una cantidad válida.")

    
    # Botón para agregar al carrito
    btn_agregar_carrito = tk.Button(ventana_opciones, text="Agregar al carrito", 
                                   font=("Arial", 12, "bold"), bg="#D370D3", fg="white",
                                   relief="flat", padx=20, pady=10,
                                   command=confirmar_agregar)
    btn_agregar_carrito.pack(pady=20)
    
    # Vincular cambios en la cantidad para actualizar el precio
    cantidad_var.trace_add("write", actualizar_precio)
    
    # Centrar la ventana emergente en la pantalla
    ventana_opciones.update_idletasks()
    ancho = ventana_opciones.winfo_width()
    alto = ventana_opciones.winfo_height()
    x = (ventana_opciones.winfo_screenwidth() // 2) - (ancho // 2)
    y = (ventana_opciones.winfo_screenheight() // 2) - (alto // 2)
    ventana_opciones.geometry(f"{ancho}x{alto}+{x}+{y}")


def seleccionar_sabores(paquete):
    """
    Muestra un menú emergente para seleccionar los sabores de los productos de un paquete.
    """
    ventana_sabores = Toplevel()
    ventana_sabores.title(f"Seleccionar Sabores - {paquete['nombre']}")
    ventana_sabores.geometry("400x600")
    ventana_sabores.configure(bg="#F3E5F5")

    tk.Label(ventana_sabores, text=f"Selecciona los sabores para el paquete '{paquete['nombre']}'",
             font=("Arial", 14, "bold"), bg="#F3E5F5", fg="#6A1B9A", wraplength=350).pack(pady=10)

    # Diccionario para almacenar los sabores seleccionados
    sabores_seleccionados = {}

    # Lista de sabores disponibles (puedes personalizarla según los productos)
    sabores_disponibles = [
        "Fresa", "Chocolate", "Vainilla", "Mango", "Limón", "Coco", "Maracuyá", "Piña", "Nuez", "Galleta Oreo"
    ]

    # Crear una sección para cada producto del paquete
    for producto in paquete["productos"]:
        frame_producto = tk.Frame(ventana_sabores, bg="#F3E5F5", bd=1, relief="solid")
        frame_producto.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_producto, text=f"{producto}:", font=("Arial", 12, "bold"),
                 bg="#F3E5F5", fg="#6A1B9A").pack(anchor="w", padx=10, pady=5)

        # Combobox para seleccionar el sabor
        sabor_var = tk.StringVar(value="Seleccionar sabor")
        sabores_seleccionados[producto] = sabor_var
        combobox_sabor = tk.OptionMenu(frame_producto, sabor_var, *sabores_disponibles)
        combobox_sabor.config(font=("Arial", 10), bg="#E1BEE7", fg="#6A1B9A", width=20)
        combobox_sabor.pack(padx=10, pady=5)

    def confirmar_seleccion():
        """
        Confirma la selección de sabores y agrega el paquete al carrito.
        """
        # Verificar que todos los sabores hayan sido seleccionados
        for producto, sabor_var in sabores_seleccionados.items():
            if sabor_var.get() == "Seleccionar sabor":
                messagebox.showwarning("Selección incompleta", f"Por favor selecciona un sabor para '{producto}'.")
                return

        # Crear una copia del paquete con los sabores seleccionados
        paquete_con_sabores = {
            "nombre": paquete["nombre"],
            "productos": [
                {"producto": producto, "sabor": sabor_var.get()} for producto, sabor_var in sabores_seleccionados.items()
            ],
            "precio": paquete["precio"]
        }

        # Agregar el paquete al carrito
        agregar_paquete_al_carrito(paquete_con_sabores)

        # Cerrar la ventana
        ventana_sabores.destroy()

        # Mostrar mensaje de confirmación
        messagebox.showinfo("Paquete agregado", f"El paquete '{paquete['nombre']}' ha sido agregado al carrito.")

    # Botón para confirmar la selección
    btn_confirmar = tk.Button(ventana_sabores, text="Confirmar selección", font=("Arial", 12, "bold"),
                              bg="#AB47BC", fg="white", relief="flat", command=confirmar_seleccion)
    btn_confirmar.pack(pady=20)


def agregar_paquete_al_carrito(paquete):
    """
    Muestra un menú emergente para seleccionar los sabores de los productos del paquete.
    """
    ventana_sabores = Toplevel()
    ventana_sabores.title(f"Seleccionar sabores - {paquete['nombre']}")
    ventana_sabores.geometry("500x700")
    ventana_sabores.configure(bg="#F3E5F5")

    tk.Label(ventana_sabores, text=f"Selecciona los sabores para {paquete['nombre']}", 
             font=("Arial", 16, "bold"), bg="#F3E5F5", fg="#6A1B9A").pack(pady=10)

    # Lista de sabores disponibles
    sabores_disponibles = ["Fresa", "Chocolate", "Vainilla", "Mango", "Limón", "Coco"]
    seleccionados = []

    # Crear una sección para cada producto del paquete
    for producto in paquete["productos"]:
        frame_producto = tk.Frame(ventana_sabores, bg="#E1BEE7", bd=1, relief="solid", padx=10, pady=10)
        frame_producto.pack(fill="x", padx=20, pady=10)

        tk.Label(frame_producto, text=f"{producto}:", font=("Arial", 14, "bold"), bg="#E1BEE7", fg="#6A1B9A").pack(anchor="w", pady=5)

        # Crear una cuadrícula para los sabores
        frame_sabores = tk.Frame(frame_producto, bg="#E1BEE7")
        frame_sabores.pack(fill="x")

        sabores_producto = []
        for i, sabor in enumerate(sabores_disponibles):
            fila = i // 3
            columna = i % 3

            # Crear un contador para cada sabor
            frame_sabor = tk.Frame(frame_sabores, bg="#E1BEE7", padx=5, pady=5)
            frame_sabor.grid(row=fila, column=columna, padx=5, pady=5)

            tk.Label(frame_sabor, text=sabor, font=("Arial", 12), bg="#E1BEE7", fg="#4A148C").pack()

            cantidad_var = tk.IntVar(value=0)

            def aumentar_cantidad(var=cantidad_var):
                var.set(var.get() + 1)

            def disminuir_cantidad(var=cantidad_var):
                if var.get() > 0:
                    var.set(var.get() - 1)

            frame_controles = tk.Frame(frame_sabor, bg="#E1BEE7")
            frame_controles.pack()

            btn_menos = tk.Button(frame_controles, text="-", font=("Arial", 10, "bold"), bg="#AB47BC", fg="white", width=2,
                                  command=lambda var=cantidad_var: disminuir_cantidad(var))
            btn_menos.pack(side="left", padx=2)

            lbl_cantidad = tk.Label(frame_controles, textvariable=cantidad_var, font=("Arial", 12), bg="#E1BEE7", fg="#4A148C", width=2)
            lbl_cantidad.pack(side="left", padx=2)

            btn_mas = tk.Button(frame_controles, text="+", font=("Arial", 10, "bold"), bg="#AB47BC", fg="white", width=2,
                                command=lambda var=cantidad_var: aumentar_cantidad(var))
            btn_mas.pack(side="left", padx=2)

            sabores_producto.append((sabor, cantidad_var))

        seleccionados.append((producto, sabores_producto))

    # Función para confirmar selección
    def confirmar_seleccion():
        sabores_elegidos = {}
        for producto, sabores_producto in seleccionados:
            sabores_seleccionados = {sabor: var.get() for sabor, var in sabores_producto if var.get() > 0}
            if not sabores_seleccionados:
                messagebox.showwarning("Advertencia", f"Debes seleccionar al menos un sabor para {producto}.")
                return
            sabores_elegidos[producto] = sabores_seleccionados

        # Crear un producto con el nombre del paquete y el precio
        producto_paquete = {
            "nombre": paquete["nombre"],
            "cantidad": 1,
            "tamaño": "Paquete",
            "precio_unitario": paquete["precio"],
            "precio_total": paquete["precio"],
            "sabores": sabores_elegidos
        }
        productos_carrito.append(producto_paquete)
        guardar_carrito_en_firebase()
        messagebox.showinfo("Paquete agregado", f"El {paquete['nombre']} ha sido agregado al carrito.")
        ventana_sabores.destroy()

    # Botones para confirmar o cancelar
    frame_botones = tk.Frame(ventana_sabores, bg="#F3E5F5")
    frame_botones.pack(pady=20)

    btn_confirmar = tk.Button(frame_botones, text="Confirmar", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", 
                              relief="flat", command=confirmar_seleccion)
    btn_confirmar.pack(side="left", padx=10)

    btn_cancelar = tk.Button(frame_botones, text="Cancelar", font=("Arial", 14, "bold"), bg="#F44336", fg="white", 
                             relief="flat", command=ventana_sabores.destroy)
    btn_cancelar.pack(side="left", padx=10)


def mostrar_menu_finalizar_compra():
    """
    Muestra un menú emergente para solicitar los datos de entrega y registrar el pedido.
    """
    if not productos_carrito:
        messagebox.showwarning("Carrito vacío", "No hay productos en el carrito.")
        return

    # Crear ventana emergente
    ventana_finalizar = Toplevel()
    ventana_finalizar.title("Finalizar Compra")
    ventana_finalizar.geometry("400x600")
    ventana_finalizar.configure(bg="#E3F2FD")

    # Hacer que la ventana sea modal
    ventana_finalizar.transient(ventana)
    ventana_finalizar.grab_set()

    # Título
    tk.Label(ventana_finalizar, text="Datos de Entrega", font=("Arial", 18, "bold"), bg="#E3F2FD", fg="#0D47A1").pack(pady=10)

    # Frame para los campos
    frame_campos = tk.Frame(ventana_finalizar, bg="#E3F2FD")
    frame_campos.pack(padx=20, pady=10, fill="x")

    # Dirección
    tk.Label(frame_campos, text="Dirección:", font=("Arial", 12, "bold"), bg="#E3F2FD", fg="#0D47A1").pack(anchor="w", pady=5)
    entrada_direccion = tk.Entry(frame_campos, font=("Arial", 12))
    entrada_direccion.pack(fill="x", pady=5)

    # Referencias
    tk.Label(frame_campos, text="Referencias:", font=("Arial", 12, "bold"), bg="#E3F2FD", fg="#0D47A1").pack(anchor="w", pady=5)
    entrada_referencias = tk.Entry(frame_campos, font=("Arial", 12))
    entrada_referencias.pack(fill="x", pady=5)

    # Método de pago
    tk.Label(frame_campos, text="Método de Pago:", font=("Arial", 12, "bold"), bg="#E3F2FD", fg="#0D47A1").pack(anchor="w", pady=5)
    metodo_pago_var = StringVar(value="Efectivo")
    opciones_pago = ["Efectivo", "Tarjeta", "Transferencia"]
    for opcion in opciones_pago:
        tk.Radiobutton(frame_campos, text=opcion, variable=metodo_pago_var, value=opcion, bg="#E3F2FD", fg="#0D47A1", font=("Arial", 12)).pack(anchor="w")

    # Día de entrega
    tk.Label(frame_campos, text="Día de Entrega:", font=("Arial", 12, "bold"), bg="#E3F2FD", fg="#0D47A1").pack(anchor="w", pady=5)
    entrada_dia_entrega = tk.Entry(frame_campos, font=("Arial", 12))
    entrada_dia_entrega.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))  # Fecha actual por defecto
    entrada_dia_entrega.pack(fill="x", pady=5)

    # Total de la compra
    total_compra = sum(producto["precio_total"] for producto in productos_carrito)
    tk.Label(ventana_finalizar, text=f"Total: ${total_compra:.2f}", font=("Arial", 16, "bold"), bg="#E3F2FD", fg="#0D47A1").pack(pady=10)

    # Cargar dirección desde Firebase
    correo_actual = cargar_sesion()
    if correo_actual:
        try:
            usuarios_ref = db.collection("usuarios")
            query = usuarios_ref.where("correo", "==", correo_actual).limit(1).stream()

            for doc in query:
                datos_usuario = doc.to_dict()
                direccion = datos_usuario.get("direccion", "")
                entrada_direccion.insert(0, direccion)  # Cargar la dirección en el campo
                break
        except Exception as e:
            print(f"Error al cargar la dirección: {e}")

    # Función para registrar el pedido
    def registrar_pedido():
        direccion = entrada_direccion.get().strip()
        referencias = entrada_referencias.get().strip()
        metodo_pago = metodo_pago_var.get()
        dia_entrega = entrada_dia_entrega.get().strip()

        if not direccion or not dia_entrega:
            messagebox.showwarning("Campos vacíos", "Por favor, completa todos los campos obligatorios.")
            return

        if not correo_actual:
            messagebox.showwarning("Advertencia", "Debes iniciar sesión para finalizar la compra.")
            return

        try:
            # Crear registro del pedido
            datos_pedido = {
                "correo_usuario": correo_actual,
                "direccion": direccion,
                "referencias": referencias,
                "metodo_pago": metodo_pago,
                "dia_entrega": dia_entrega,
                "productos": productos_carrito,
                "total": total_compra,
                "fecha_pedido": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Guardar el pedido en Firebase
            db.collection("pedidos").add(datos_pedido)

            # Limpiar el carrito localmente y en Firebase
            productos_carrito.clear()
            guardar_carrito_en_firebase()

            # Mostrar mensaje de éxito
            messagebox.showinfo("Pedido registrado", "¡Tu pedido ha sido registrado exitosamente!")
            ventana_finalizar.destroy()
            actualizar_carrito()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el pedido: {e}")

    # Botón para registrar el pedido
    tk.Button(ventana_finalizar, text="Registrar Pedido", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", command=registrar_pedido).pack(pady=20)

    # Botón para cancelar
    tk.Button(ventana_finalizar, text="Cancelar", font=("Arial", 12), bg="#F44336", fg="white", command=ventana_finalizar.destroy).pack()


# ------------------------ Inicializar Firebase ------------------------
cred = credentials.Certificate("E:/programas/heladeria.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ------------------------ Variables globales ------------------------
sesion_iniciada = False


# ------------------------ Funciones ------------------------

from tkinter import filedialog
import base64
from io import BytesIO

def seleccionar_foto_perfil():
    correo_actual = cargar_sesion()
    if not correo_actual:
        messagebox.showwarning("Advertencia", "Debes iniciar sesión para cambiar tu foto de perfil.")
        return
    
    # Abrir diálogo para seleccionar archivo
    ruta_archivo = filedialog.askopenfilename(
        title="Seleccionar foto de perfil",
        filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif")]
    )
    
    if not ruta_archivo:  # Si el usuario cancela la selección
        return
    
    try:
        # Abrir y redimensionar la imagen
        img = Image.open(ruta_archivo)
        img = img.resize((200, 200))
        
        # Convertir la imagen a base64 para guardarla en Firebase
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Buscar el documento del usuario
        usuarios_ref = db.collection("usuarios")
        query = usuarios_ref.where("correo", "==", correo_actual).limit(1).stream()
        
        doc_id = None
        for doc in query:
            doc_id = doc.id
            break
        
        if doc_id:
            # Actualizar el documento con la nueva foto
            db.collection("usuarios").document(doc_id).update({
                "foto_perfil": img_base64
            })
            
            # Actualizar la foto en la interfaz
            global foto_perfil, label_foto
            foto_perfil = ImageTk.PhotoImage(img)
            label_foto.configure(image=foto_perfil)
            
            messagebox.showinfo("Éxito", "Foto de perfil actualizada correctamente.")
        else:
            messagebox.showerror("Error", "No se encontró el usuario en la base de datos.")
    
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar la foto de perfil: {e}")


def cargar_datos_perfil():
    correo_actual = cargar_sesion()
    if not correo_actual:
        return

    # Limpiar widgets existentes
    for widget in frame_perfil.winfo_children():
        widget.destroy()

    try:
        # Buscar el usuario por su correo en la base de datos
        usuarios_ref = db.collection("usuarios")
        query = usuarios_ref.where("correo", "==", correo_actual).limit(1).stream()

        usuario_encontrado = False
        for doc in query:
            usuario_encontrado = True
            datos_usuario = doc.to_dict()

            # Contenedor principal
            frame_contenido_perfil = tk.Frame(frame_perfil, bg="#E3F2FD", padx=20, pady=20)
            frame_contenido_perfil.pack(fill="both", expand=True)

            # Foto de perfil
            global foto_perfil
            if "foto_perfil" in datos_usuario and datos_usuario["foto_perfil"]:
                try:
                    # Decodificar la imagen base64
                    img_data = base64.b64decode(datos_usuario["foto_perfil"])
                    img = Image.open(BytesIO(img_data))
                    img = img.resize((150, 150))  # Tamaño de la imagen
                    foto_perfil = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Error al cargar foto de perfil: {e}")
                    foto_perfil_img = Image.open("E:/IMGprogramas/usuario.png").resize((150, 150))
                    foto_perfil = ImageTk.PhotoImage(foto_perfil_img)
            else:
                foto_perfil_img = Image.open("E:/IMGprogramas/usuario.png").resize((150, 150))
                foto_perfil = ImageTk.PhotoImage(foto_perfil_img)

            # Marco para la foto de perfil
            frame_foto = tk.Frame(frame_contenido_perfil, bg="#BBDEFB", bd=2, relief="solid")
            frame_foto.pack(pady=10)
            tk.Label(frame_foto, image=foto_perfil, bg="#BBDEFB").pack()

            # Botón para cambiar foto
            btn_cambiar_foto = tk.Button(frame_contenido_perfil, text="Cambiar Foto", font=("Arial", 12, "bold"),
                                         bg="#1565C0", fg="white", relief="flat", command=seleccionar_foto_perfil)
            btn_cambiar_foto.pack(pady=10)

            # Datos del usuario
            frame_datos = tk.Frame(frame_contenido_perfil, bg="#E3F2FD", padx=10, pady=10)
            frame_datos.pack(fill="x", pady=10)

            datos = [
                ("Nombre:", datos_usuario.get("nombre", "No disponible")),
                ("Teléfono:", datos_usuario.get("telefono", "No disponible")),
                ("Correo:", datos_usuario.get("correo", "No disponible")),
                ("Dirección:", datos_usuario.get("direccion", "No disponible"))
            ]

            # Mostrar los datos con íconos
            for etiqueta, valor in datos:
                frame_dato = tk.Frame(frame_datos, bg="#E3F2FD", pady=5)
                frame_dato.pack(fill="x", anchor="w")

                # Ícono
                icono = None
                if "Nombre" in etiqueta:
                    icono = "E:/IMGprogramas/nombre.png"
                elif "Teléfono" in etiqueta:
                    icono = "E:/IMGprogramas/telefono.png"
                elif "Correo" in etiqueta:
                    icono = "E:/IMGprogramas/correo.png"
                elif "Dirección" in etiqueta:
                    icono = "E:/IMGprogramas/dirección.png"

                if icono:
                    img_icono = Image.open(icono).resize((20, 20))
                    img_icono = ImageTk.PhotoImage(img_icono)
                    tk.Label(frame_dato, image=img_icono, bg="#E3F2FD").pack(side="left", padx=5)
                    frame_dato.img_icono = img_icono  # Guardar referencia

                # Etiqueta y valor
                tk.Label(frame_dato, text=etiqueta, font=("Arial", 12, "bold"), bg="#E3F2FD", fg="#0D47A1").pack(side="left", padx=5)
                tk.Label(frame_dato, text=valor, font=("Arial", 12), bg="#E3F2FD", fg="#01579B").pack(side="left")

            # Producto más consumido
            producto_mas_consumido, cantidad = obtener_producto_mas_consumido(correo_actual)
            if producto_mas_consumido:
                frame_producto = tk.Frame(frame_contenido_perfil, bg="#E3F2FD", pady=10)
                frame_producto.pack(fill="x", anchor="w")
                tk.Label(frame_producto, text=f"Producto más consumido: {producto_mas_consumido} ({cantidad} unidades)",
                         font=("Arial", 12, "italic"), bg="#E3F2FD", fg="#0277BD").pack(side="left", padx=10)

            # Botones de acción
            frame_botones = tk.Frame(frame_contenido_perfil, bg="#E3F2FD", pady=20)
            frame_botones.pack()

            btn_editar = tk.Button(frame_botones, text="Editar Perfil", font=("Arial", 12, "bold"),
                                   bg="#1565C0", fg="white", relief="flat", command=editar_perfil)
            btn_editar.pack(side="left", padx=10)

            break

        if not usuario_encontrado:
            tk.Label(frame_perfil, text="No se encontraron datos del usuario", font=("Arial", 14, "bold"),
                     bg="#E3F2FD", fg="red").pack(pady=20)

    except Exception as e:
        tk.Label(frame_perfil, text=f"Error al cargar datos: {e}", font=("Arial", 14, "bold"),
                 bg="#E3F2FD", fg="red").pack(pady=20)
    btn_cerrar_sesion = tk.Button(frame_perfil, text="Cerrar Sesión", font=("Arial", 12, "bold"),
                                      bg="#F44336", fg="white", relief="flat", command=cerrar_sesion)
    btn_cerrar_sesion.pack(pady=10)


def guardar_sesion(correo):
    with open("sesion.json", "w") as f:
        json.dump({"correo": correo}, f)

def cargar_sesion():
    if os.path.exists("sesion.json"):
        with open("sesion.json", "r") as f:
            datos = json.load(f)
            return datos.get("correo")
    return None

def cerrar_sesion():
    if os.path.exists("sesion.json"):
        os.remove("sesion.json")
    mostrar_frame(frame_login)
    messagebox.showinfo("Sesión cerrada", "Has cerrado sesión correctamente.")
    
def mostrar_frame(frame):
    frame.tkraise()
    if frame == frame_carro:
        actualizar_carrito()


def registrar_usuario():
    nombre = entrada_registro_nombre.get().strip()
    correo = entrada_registro_correo.get().strip()
    telefono = entrada_registro_telefono.get().strip()
    contrasena = entrada_registro_contrasena.get().strip()

    if not nombre or not correo or not telefono or not contrasena:
        messagebox.showwarning("Campos vacíos", "Por favor, completa todos los campos.")
        return

    try:
        usuarios_ref = db.collection("usuarios")
        existe_correo = list(usuarios_ref.where("correo", "==", correo).limit(1).stream())
        existe_telefono = list(usuarios_ref.where("telefono", "==", telefono).limit(1).stream())

        if existe_correo:
            messagebox.showerror("Registro", "El correo ya está registrado. Usa otro correo o inicia sesión.")
            return
        if existe_telefono:
            messagebox.showerror("Registro", "El número de teléfono ya está registrado. Usa otro número.")
            return

        datos_usuario = {
            "nombre": nombre,
            "correo": correo,
            "telefono": telefono,
            "contrasena": contrasena,
            "estadisticas_productos": {}
        }

        db.collection("usuarios").add(datos_usuario)
        messagebox.showinfo("Registro exitoso", "Tu cuenta ha sido registrada correctamente.")
        mostrar_frame(frame_login)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo registrar: {e}")


def activar_botones():
    boton_inicio.config(state="normal")
    boton_productos.config(state="normal")
    boton_servicio.config(state="normal")
    menu_hamburguesa.entryconfig("Perfil", state="normal")
    menu_hamburguesa.entryconfig("Ofertas", state="normal")
    menu_hamburguesa.entryconfig("Carro de compras", state="normal")
    menu_hamburguesa.entryconfig("Pagos", state="normal")
    menu_hamburguesa.entryconfig("Pedidos personalizados", state="normal")

def abrir_menu(event):
    try:
        menu_hamburguesa.tk_popup(event.x_root, event.y_root)
    finally:
        menu_hamburguesa.grab_release()

def reproducir_video():
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (900, 550))
        img = ImageTk.PhotoImage(Image.fromarray(frame))
        label_video.imgtk = img
        label_video.configure(image=img)
        label_video.after(30, reproducir_video)
    else:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        label_video.after(30, reproducir_video)

def enviar_a_firebase():
    servicio = entrada_cal_servicio.get("1.0", tk.END).strip()
    aplicacion = entrada_cal_aplicacion.get("1.0", tk.END).strip()
    if not servicio and not aplicacion:
        messagebox.showwarning("Advertencia", "Por favor, llena al menos un campo.")
        return

    correo_usuario = cargar_sesion()
    datos = {
        "correo_usuario": correo_usuario,
        "calificacion_servicio": servicio,
        "calificacion_aplicacion": aplicacion
    }
    try:
        db.collection("Servicio al cliente").add(datos)
        messagebox.showinfo("Enviado", "¡Gracias por tus comentarios!")
        entrada_cal_servicio.delete("1.0", tk.END)
        entrada_cal_aplicacion.delete("1.0", tk.END)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo enviar: {e}")
        
def enviar_ayuda_firebase():
    problema = entry_problema.get("1.0", tk.END).strip()
    correo = entry_gmail.get().strip()
    if not problema or not correo:
        messagebox.showwarning("Advertencia", "Por favor, completa ambos campos.")
        return

    datos = {
        "problema": problema,
        "correo": correo
    }

    try:
        db.collection("Ayuda_no_registrados").add(datos)
        messagebox.showinfo("Enviado", "¡Gracias! Tu mensaje ha sido enviado.")
        entry_problema.delete("1.0", tk.END)
        entry_gmail.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo enviar: {e}")

        
def validar_login():
    global sesion_iniciada
    correo = entrada_login_correo.get().strip()
    contrasena = entrada_login_contrasena.get().strip()

    if not correo or not contrasena:
        messagebox.showwarning("Campos vacíos", "Por favor, completa todos los campos.")
        return

    try:
        usuarios_ref = db.collection("usuarios")
        query = usuarios_ref.where("correo", "==", correo).where("contrasena", "==", contrasena).stream()

        usuario_encontrado = False
        for doc in query:
            usuario_encontrado = True
            break

        if usuario_encontrado:
            sesion_iniciada = True
            guardar_sesion(correo)  
            activar_botones()
            
            # Cargar el carrito desde Firebase
            cargar_carrito_desde_firebase()
            
            mostrar_frame(frame_inicio)
        else:
            messagebox.showerror("Error", "Correo o contraseña incorrectos.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo verificar el inicio de sesión: {e}")


def cargar_pagos_completados():
    """
    Carga los pagos completados desde Firebase y los muestra en el frame de pagos.
    """
    # Limpiar el contenido del frame
    for widget in frame_pagos_contenido.winfo_children():
        widget.destroy()

    correo_actual = cargar_sesion()
    if not correo_actual:
        messagebox.showwarning("Advertencia", "Debes iniciar sesión para ver los pagos.")
        return

    try:
        # Consultar los pagos del usuario en Firebase
        pagos_ref = db.collection("pedidos")
        query = pagos_ref.where("correo_usuario", "==", correo_actual).stream()

        # Mostrar cada pago
        for doc in query:
            datos_pago = doc.to_dict()

            # Crear un frame para cada pago
            frame_pago = tk.Frame(frame_pagos_contenido, bg="#E3F2FD", bd=1, relief="solid")
            frame_pago.pack(fill="x", padx=10, pady=5)

            # Mostrar los datos del pago
            tk.Label(frame_pago, text=f"Pago con: {datos_pago.get('metodo_pago', 'No especificado')}", 
                     font=("Arial", 12, "bold"), bg="#E3F2FD", anchor="w").pack(fill="x", padx=10, pady=2)
            tk.Label(frame_pago, text=f"Monto pagado: ${datos_pago.get('total', 0):.2f}", 
                     font=("Arial", 12), bg="#E3F2FD", anchor="w").pack(fill="x", padx=10, pady=2)
            tk.Label(frame_pago, text=f"Día de entrega: {datos_pago.get('dia_entrega', 'No especificado')}", 
                     font=("Arial", 12), bg="#E3F2FD", anchor="w").pack(fill="x", padx=10, pady=2)
            tk.Label(frame_pago, text=f"Entrega en: {datos_pago.get('direccion', 'No especificado')}", 
                     font=("Arial", 12), bg="#E3F2FD", anchor="w").pack(fill="x", padx=10, pady=2)

            # Mostrar los productos
            productos = datos_pago.get("productos", [])
            productos_texto = "\n".join([f"- {p['nombre']} (x{p['cantidad']})" for p in productos])
            tk.Label(frame_pago, text=f"Productos:\n{productos_texto}", 
                     font=("Arial", 12), bg="#E3F2FD", anchor="w", justify="left").pack(fill="x", padx=10, pady=2)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar los pagos: {e}")

# ------------------------ Interfaz Principal ------------------------
ventana = tk.Tk()
ventana.title("Heladería Twins")
ventana.geometry("900x650")
ventana.config(bg="#B3E5FC")
ventana.rowconfigure(1, weight=1)
ventana.columnconfigure(0, weight=1)

# ------------------------ Frame Superior ------------------------
frame_superior = tk.Frame(ventana, bg="#4FC3F7")
frame_superior.grid(row=0, column=0, sticky="ew")

icono_hamburguesa = Image.open("E:/IMGprogramas/si.png").resize((40, 40))
icono_hamburguesa = ImageTk.PhotoImage(icono_hamburguesa)
boton_menu = tk.Label(frame_superior, image=icono_hamburguesa, bg="white", cursor="hand2")
boton_menu.pack(side="left", padx=10)
boton_menu.bind("<Button-1>", abrir_menu)

logo = Image.open("E:/IMGprogramas/logo.jpg").resize((80, 80))
logo = ImageTk.PhotoImage(logo)
tk.Label(frame_superior, image=logo, bg="white").pack(side="left", padx=10)

boton_inicio = tk.Button(frame_superior, text="Inicio", font=("Arial", 12, "bold"), bg="#4FC3F7", fg="white", bd=0, state="disabled", command=lambda: mostrar_frame(frame_inicio))
boton_inicio.pack(side="left", padx=20)
boton_productos = tk.Button(frame_superior, text="Productos", font=("Arial", 12, "bold"), bg="#4FC3F7", fg="white", bd=0, state="disabled", command=lambda: mostrar_frame(frame_productos))
boton_productos.pack(side="left", padx=20)
boton_servicio = tk.Button(frame_superior, text="Servicio al cliente", font=("Arial", 12, "bold"), bg="#4FC3F7", fg="white", bd=0, state="disabled", command=lambda: mostrar_frame(frame_servicio))
boton_servicio.pack(side="left", padx=20)

# ------------------------ Menú Hamburguesa ------------------------
menu_hamburguesa = Menu(ventana, tearoff=0)
menu_hamburguesa.add_command(label="Perfil", state="disabled", command=lambda: [mostrar_frame(frame_perfil), cargar_datos_perfil()])
menu_hamburguesa.add_command(label="Ofertas", state="disabled", command=lambda: mostrar_frame(frame_ofertas))
menu_hamburguesa.add_command(label="Carro de compras", state="disabled", command=lambda: mostrar_frame(frame_carro))
menu_hamburguesa.add_command(label="Pagos", state="disabled", command=lambda: mostrar_frame(frame_pagos))
menu_hamburguesa.add_command(label="Pedidos personalizados", state="disabled", command=lambda: mostrar_frame(frame_personalizados))

# ------------------------ Frames de Contenido ------------------------
frame_contenido = tk.Frame(ventana, bg="#BBDEFB")
frame_contenido.grid(row=1, column=0, sticky="nsew")
frame_contenido.rowconfigure(0, weight=1)
frame_contenido.columnconfigure(0, weight=1)

frames = {
    'inicio': tk.Frame(frame_contenido, bg="#BBDEFB"),
    'productos': tk.Frame(frame_contenido, bg="#BBDEFB"),
    'servicio': tk.Frame(frame_contenido, bg="#BBDEFB"),
    'pagos': tk.Frame(frame_contenido, bg="#BBDEFB"),
    'perfil': tk.Frame(frame_contenido, bg="#BBDEFB"),
    'carro': tk.Frame(frame_contenido, bg="#BBDEFB"),
    'personalizados': tk.Frame(frame_contenido, bg="#BBDEFB"),
    'ofertas': tk.Frame(frame_contenido, bg="#BBDEFB"),
    'registro': tk.Frame(frame_contenido, bg="#BBDEFB"),
    'login': tk.Frame(frame_contenido, bg="#BBDEFB"),
    'paletas': tk.Frame(frame_contenido, bg="#BBDEFB"),
    'gelatos': tk.Frame(frame_contenido, bg="#BBDEFB"),
    'otros': tk.Frame(frame_contenido, bg="#BBDEFB")
}


for frame in frames.values():
    frame.grid(row=0, column=0, sticky="nsew")

# Accesos individuales
frame_inicio = frames['inicio']
frame_productos = frames['productos']
frame_servicio = frames['servicio']
frame_pagos = frames['pagos']
frame_perfil = frames['perfil']
frame_carro = frames['carro']
frame_personalizados = frames['personalizados']
frame_ofertas = frames['ofertas']
frame_registro = frames['registro']
frame_login = frames['login']
frame_paletas = frames['paletas']
frame_gelatos = frames['gelatos']
frame_otros = frames['otros']

# Establece el mismo color de fondo para ambos frames
color_fondo = "#E3F2FD"  # Azul muy claro y agradable

frame_registro.configure(bg=color_fondo)
frame_login.configure(bg=color_fondo)


# ------------------------ Frame Bienvenida ------------------------
frame_bienvenida = tk.Frame(frame_contenido, bg="#E3F2FD")
frames['bienvenida'] = frame_bienvenida
frame_bienvenida.grid(row=0, column=0, sticky="nsew")

# ------------------------ Título ------------------------
tk.Label(frame_bienvenida, text="Bienvenido a Heladería Twins", font=("Arial Rounded MT Bold", 28, "bold"),
         bg="#E3F2FD", fg="#0D47A1").pack(pady=(30, 1))

tk.Label(frame_bienvenida, text="Estos deliciosos postres y muchos más, en Heladería Twins", font=("Arial", 18),
         bg="#E3F2FD", fg="#1976D2").pack(pady=(0, 1))

# ------------------------ Productos ------------------------
productos = [
    {"nombre": "Paleta de Mango", "descripcion": "Fresca y natural", "img": "E:/IMGprogramas/paleta_mango.jpeg"},
    {"nombre": "Gelato de Avellana", "descripcion": "Cremoso y suave", "img": "E:/IMGprogramas/gelato_avellana.jpeg"},
    {"nombre": "Malteada de chocolate", "descripcion": "Deliciosa bebida", "img": "E:/IMGprogramas/malteada.jpeg"},
    {"nombre": "Banana Split", "descripcion": "Con crema y cerezas", "img": "E:/IMGprogramas/banana_split.jpeg"},
    {"nombre": "Paleta de Chocolate", "descripcion": "Amor en cada mordida", "img": "E:/IMGprogramas/paleta_chocolate.jpeg"},
    {"nombre": "Paleta de Kiwi", "descripcion": "Ácida y deliciosa", "img": "E:/IMGprogramas/paleta_wiki.jpeg"},
    {"nombre": "Tarta de Limón", "descripcion": "Sutil y elegante", "img": "E:/IMGprogramas/tarta_limon.jpeg"},
    {"nombre": "Chocobanana", "descripcion": "Exquisito y natural", "img": "E:/IMGprogramas/choco.jpeg"},
    {"nombre": "Flan", "descripcion": "Dulce y suave", "img": "E:/IMGprogramas/flan.jpeg"},
    {"nombre": "Helado de Nutella", "descripcion": "Puro placer", "img": "E:/IMGprogramas/nutella.jpeg"},
]

contenedor_productos = tk.Frame(frame_bienvenida, bg="#E3F2FD")
contenedor_productos.pack(pady=20)
filas = (len(productos) + 1) // 5
for i, producto in enumerate(productos):
    columna = i % 5
    fila = i // 5

    frame_item = tk.Frame(contenedor_productos, bg="#BBDEFB", bd=2, relief="raised", padx=18, pady=18)
    frame_item.grid(row=fila, column=columna, padx=30, pady=10)

    try:
        img = Image.open(producto["img"]).resize((90, 90))
        img = ImageTk.PhotoImage(img)
        label_img = tk.Label(frame_item, image=img, bg="#BBDEFB")
        label_img.image = img
        label_img.pack(pady=(0, 5))
    except:
        tk.Label(frame_item, text="Imagen no disponible", bg="#BBDEFB", fg="#E53935", font=("Arial", 10, "bold")).pack(pady=(0, 8))

    tk.Label(frame_item, text=producto["nombre"], font=("Arial Rounded MT Bold", 15, "bold"), bg="#BBDEFB", fg="#0D47A1").pack(pady=(0, 2))
    tk.Label(frame_item, text=producto["descripcion"], font=("Arial", 12, "italic"), bg="#BBDEFB", fg="#1976D2").pack()
    tk.Frame(frame_item, bg="#1976D2", height=2, width=120).pack(pady=1)

# ------------------------ Botones ------------------------
frame_botones = tk.Frame(frame_bienvenida, bg="#E3F2FD")
frame_botones.pack(pady=(40, 1))

btn_login = tk.Button(frame_botones, text="Iniciar sesión / Registrarme", font=("Arial Rounded MT Bold", 16),
                      bg="#5C43FF", fg="white", width=25, height=2, command=lambda: mostrar_frame(frame_registro))
btn_login.grid(row=0, column=0, padx=10)

btn_ayuda = tk.Button(frame_botones, text="¿Necesitas ayuda?", font=("Arial Rounded MT Bold", 14),
                      bg="#5C43FF", fg="white", width=20, height=2, command=lambda: mostrar_frame(frame_ayuda))
btn_ayuda.grid(row=0, column=1, padx=10)


# ------------------------ Frame Ayuda ------------------------
frame_ayuda = tk.Frame(frame_contenido, bg="#E3F2FD")
frames['ayuda'] = frame_ayuda
frame_ayuda.grid(row=0, column=0, sticky="nsew")

# Título
titulo = tk.Label(frame_ayuda, text="¿Necesitas ayuda?", font=("Arial Rounded MT Bold", 28), bg="#E3F2FD", fg="#0D47A1")
titulo.pack(pady=(40, 10))

subtitulo = tk.Label(frame_ayuda, text="Por favor describe tu problema y un correo de contacto:", font=("Arial", 16), bg="#E3F2FD", fg="#1976D2")
subtitulo.pack(pady=(0, 20))

# Entradas
entry_problema = tk.Text(frame_ayuda, height=3, width=70, font=("Arial", 14))
entry_problema.pack(pady=10)

tk.Label(frame_ayuda, text="Correo electrónico:", font=("Arial", 14), bg="#E3F2FD", fg="#1976D2").pack(pady=(10, 5))
entry_gmail = tk.Entry(frame_ayuda, width=40, font=("Arial", 14))
entry_gmail.pack(pady=10)

# Botón para enviar ayuda (debajo de las cajas de texto)
btn_enviar = tk.Button(frame_ayuda, text="Enviar ayuda", font=("Arial Rounded MT Bold", 14),
                       bg="#1565C0", fg="white", width=20, height=1, command=enviar_ayuda_firebase)
btn_enviar.pack(pady=(0, 1))

# Botón para regresar a la bienvenida
btn_regresar = tk.Button(frame_ayuda, text="Regresar a inicio", font=("Arial Rounded MT Bold", 14),
                         bg="#1565C0", fg="white", width=20, height=1, command=lambda: mostrar_frame(frame_bienvenida))
btn_regresar.pack(pady=(0, 1))

# Contacto de la empresa y Sucursales en dos columnas
frame_contacto_sucursales = tk.Frame(frame_ayuda, bg="#E3F2FD")
frame_contacto_sucursales.pack(pady=30)

# Columna izquierda: Contacto de la empresa
columna_contacto = tk.Frame(frame_contacto_sucursales, bg="#E3F2FD")
columna_contacto.grid(row=0, column=0, padx=40, sticky="n")

tk.Label(columna_contacto, text="Contacto de la empresa:", font=("Arial Rounded MT Bold", 18), bg="#E3F2FD", fg="#0D47A1").pack(anchor="w", pady=(0, 5))
tk.Label(columna_contacto, text="Correo: heladeria_twins@gmail.com", font=("Arial", 14), bg="#E3F2FD", fg="#0D47A1").pack(anchor="w")
tk.Label(columna_contacto, text="Teléfono: 22 13 72 43 09", font=("Arial", 14), bg="#E3F2FD", fg="#0D47A1").pack(anchor="w")
tk.Label(columna_contacto, text="Atención en sucursales: 12:00 am - 4:00 pm", font=("Arial", 14), bg="#E3F2FD", fg="#0D47A1").pack(anchor="w")

# Columna derecha: Sucursales
columna_sucursales = tk.Frame(frame_contacto_sucursales, bg="#E3F2FD")
columna_sucursales.grid(row=0, column=1, padx=40, sticky="n")

tk.Label(columna_sucursales, text="Sucursales:", font=("Arial Rounded MT Bold", 18), bg="#E3F2FD", fg="#0D47A1").pack(anchor="w", pady=(0, 5))
sucursales = [
    ("Lomas de Angelópolis", "Puebla Pue."),
    ("Mayorazgo", "Puebla Pue."),
    ("CDMX - Santa Fe", "CDMX")
]
for nombre, ubicacion in sucursales:
    tk.Label(columna_sucursales, text=f"{nombre} - {ubicacion}", font=("Arial", 14), bg="#E3F2FD", fg="#1976D2").pack(anchor="w")

# ------------------------ Frame Registro ------------------------
tk.Label(frame_registro, text="Crear cuenta", font=("Arial", 18, "bold"), bg=color_fondo, fg="#0D47A1").pack(pady=(20, 10))
tk.Label(frame_registro, text="Para ingresar a la aplicación y disfrutar de nuestros \nservicios inicia sesión", font=("Arial", 18, "bold"), bg=color_fondo, fg="#0D47A1").pack(pady=(20, 10))

# Nombre
tk.Label(frame_registro, text="Nombre", font=("Arial", 11), bg=color_fondo, anchor="w").pack(fill="x", padx=40)
entrada_registro_nombre = tk.Entry(frame_registro, font=("Arial", 11))
entrada_registro_nombre.pack(fill="x", padx=40, pady=(0, 10))

# Correo
tk.Label(frame_registro, text="Correo", font=("Arial", 11), bg=color_fondo, anchor="w").pack(fill="x", padx=40)
entrada_registro_correo = tk.Entry(frame_registro, font=("Arial", 11))
entrada_registro_correo.pack(fill="x", padx=40, pady=(0, 10))

# Teléfono
tk.Label(frame_registro, text="Teléfono", font=("Arial", 11), bg=color_fondo, anchor="w").pack(fill="x", padx=40)
entrada_registro_telefono = tk.Entry(frame_registro, font=("Arial", 11))
entrada_registro_telefono.pack(fill="x", padx=40, pady=(0, 10))

# Contraseña
tk.Label(frame_registro, text="Contraseña", font=("Arial", 11), bg=color_fondo, anchor="w").pack(fill="x", padx=40)
entrada_registro_contrasena = tk.Entry(frame_registro, show="*", font=("Arial", 11))
entrada_registro_contrasena.pack(fill="x", padx=40, pady=(0, 20))

# Botón Registrarse
tk.Button(frame_registro, text="Registrarse", command=registrar_usuario,
          bg="#1565C0", fg="white", font=("Arial", 12), relief="flat").pack(pady=(0, 15))

# Botón para cambiar a inicio de sesión
tk.Button(frame_registro, text="¿Ya tienes una cuenta? Iniciar sesión",
          command=lambda: mostrar_frame(frame_login),
          bg=color_fondo, fg="#1565C0", font=("Arial", 10), bd=0).pack()

# ------------------------ Frame Login ------------------------
tk.Label(frame_login, text="Iniciar sesión", font=("Arial", 18, "bold"), bg=color_fondo, fg="#0D47A1").pack(pady=(20, 10))
tk.Label(frame_login, text="Para ingresar a la aplicación y disfrutar de nuestros \nservicios inicia sesión", font=("Arial", 18, "bold"), bg=color_fondo, fg="#0D47A1").pack(pady=(20, 10))

tk.Label(frame_login, text="Correo", font=("Arial", 11), bg=color_fondo, anchor="w").pack(fill="x", padx=40)
entrada_login_correo = tk.Entry(frame_login, font=("Arial", 11))
entrada_login_correo.pack(fill="x", padx=40, pady=(0, 10))

tk.Label(frame_login, text="Contraseña", font=("Arial", 11), bg=color_fondo, anchor="w").pack(fill="x", padx=40)
entrada_login_contrasena = tk.Entry(frame_login, show="*", font=("Arial", 11))
entrada_login_contrasena.pack(fill="x", padx=40, pady=(0, 20))

tk.Button(frame_login, text="Acceder", command=validar_login,
          bg="#1565C0", fg="white", font=("Arial", 12), relief="flat").pack(pady=(0, 15))

tk.Button(frame_login, text="¿No tienes una cuenta? Regístrate",
          command=lambda: mostrar_frame(frame_registro),
          bg=color_fondo, fg="#1565C0", font=("Arial", 10), bd=0).pack()

# ------------------------ Frame Inicio Estilizado y Escalable ------------------------
cap = cv2.VideoCapture("E:/IMGprogramas/heladeria.mp4")

# Configura el fondo general
frame_inicio.config(bg="#E3F2FD")

# Contenedor principal escalable
container = tk.Frame(frame_inicio, bg="#E3F2FD")
container.pack(fill="both", expand=True, padx=30, pady=30)

# Título
tk.Label(container, text="🍦 BIENVENIDO A HELADERÍA TWINS 🍦", 
         font=("Helvetica", 32, "bold"), bg="#E3F2FD", fg="#0D47A1").pack(pady=(10, 5))

# Subtítulo
tk.Label(container, text="Donde cada cucharada congela 🌈", 
         font=("Helvetica", 16, "italic"), bg="#E3F2FD", fg="#1976D2").pack(pady=(0, 20))

# Frame de contenido expandible
frame_contenido = tk.Frame(container, bg="#E3F2FD")
frame_contenido.pack(fill="both", expand=True)

# Video sin bordes, expandible
label_video = tk.Label(frame_contenido, bg="#E3F2FD")
label_video.pack(side="left", expand=True, fill="both", padx=(0, 40), ipadx=10, ipady=10)

# Frame de información
frame_info = tk.Frame(frame_contenido, bg="#E3F2FD")
frame_info.pack(side="left", expand=True, fill="both", padx=(0, 20))

# Título de sucursales
tk.Label(frame_info, text="📍 Nuestras Sucursales", font=("Helvetica", 20, "bold"), 
         bg="#E3F2FD", fg="#0D47A1").pack(anchor="w", pady=(0, 20))

# Lista de sucursales
sucursales = [
    ("Lomas de Angelópolis", "Puebla Pue.", "9:00am - 5:00pm"),
    ("Mayorazgo", "Puebla Pue.", "9:00am - 5:00pm"),
    ("CDMX - Santa Fe", "", "9:00am - 5:00pm")
]

for nombre, ciudad, horario in sucursales:
    card = tk.Frame(frame_info, bg="white", bd=0, relief="flat")
    card.pack(fill="x", pady=10, padx=5)
    tk.Label(card, text=f"🏬 {nombre}", font=("Helvetica", 14, "bold"), bg="white", fg="#1A237E").pack(anchor="w", pady=(5, 0), padx=10)
    tk.Label(card, text=f"{ciudad}\n🕘 {horario}", font=("Helvetica", 12), bg="white", fg="#37474F", justify="left").pack(anchor="w", padx=10, pady=(0, 5))

# Imagen decorativa (logo o dibujo de helado)
img_path = "E:/IMGprogramas/helado.png"
if os.path.exists(img_path):
    helado_img = Image.open(img_path)
    helado_img = helado_img.resize((100, 100), Image.Resampling.LANCZOS)
    helado_tk = ImageTk.PhotoImage(helado_img)
    logo_label = tk.Label(container, image=helado_tk, bg="#E3F2FD")
    logo_label.image = helado_tk
    logo_label.pack(side="bottom", pady=10)

# Inicia la reproducción del video
reproducir_video()

# ------------------------ Frame Productos ------------------------
frame_productos.configure(bg="#BBDEFB")  # Fondo azul claro

# Título del frame
titulo_frame_productos = tk.Frame(frame_productos, bg="#4FC3F7")  # Azul medio
titulo_frame_productos.pack(fill="x")

tk.Label(titulo_frame_productos, text="HELADERÍA TWINS", 
         font=("Arial", 28, "bold"), bg="#4FC3F7", fg="white").pack(pady=(15, 0))
tk.Label(titulo_frame_productos, text="Explora Nuestros Productos", 
         font=("Arial", 22), bg="#4FC3F7", fg="white").pack(pady=(0, 15))

# Banner con una sola imagen destacada
frame_banner_productos = tk.Frame(frame_productos, bg="#BBDEFB")
frame_banner_productos.pack(fill="x", pady=20)

try:
    # Cargar una imagen para el banner
    ruta_banner = "E:/IMGprogramas/banner2.png"
    img = Image.open(ruta_banner)
    img = img.resize((900, 220))  # Tamaño más grande para el banner
    img_tk = ImageTk.PhotoImage(img)

    # Mostrar la imagen en el banner
    tk.Label(frame_banner_productos, image=img_tk, bg="#BBDEFB").pack()

    # Guardar referencia para evitar que se elimine
    frame_productos.img_banner = img_tk

except Exception as e:
    tk.Label(frame_banner_productos, text=f"Error al cargar la imagen del banner: {e}",
             font=("Arial", 14), bg="#BBDEFB", fg="red").pack()

# Botones para explorar categorías
frame_categorias_productos = tk.Frame(frame_productos, bg="#BBDEFB")
frame_categorias_productos.pack(pady=30)

categorias = [
    ("Paletas", "E:/IMGprogramas/paletas.png", lambda: mostrar_frame(frame_paletas)),
    ("Gelatos y Nieves", "E:/IMGprogramas/gelatos.jpg", lambda: mostrar_frame(frame_gelatos)),
    ("Otros Productos", "E:/IMGprogramas/otros.jpg", lambda: mostrar_frame(frame_otros))
]

for categoria, ruta_imagen, comando in categorias:
    try:
        # Cargar imagen de la categoría
        img = Image.open(ruta_imagen)
        img = img.resize((150, 150))  # Tamaño más grande para las imágenes de los botones
        img_tk = ImageTk.PhotoImage(img)

        # Crear botón con imagen y texto
        frame_categoria = tk.Frame(frame_categorias_productos, bg="#BBDEFB")
        frame_categoria.pack(side="left", padx=40)

        btn_categoria = tk.Button(frame_categoria, image=img_tk, bg="#4FC3F7", bd=0,
                                  activebackground="#4FC3F7", command=comando, cursor="hand2")
        btn_categoria.pack()

        tk.Label(frame_categoria, text=categoria, font=("Arial", 18, "bold"),
                 bg="#BBDEFB", fg="#0277BD").pack(pady=10)

        # Guardar referencia de la imagen
        frame_productos.__dict__.setdefault("imagenes_categorias", []).append(img_tk)

    except Exception as e:
        tk.Label(frame_categorias_productos, text=f"Error al cargar categoría {categoria}: {e}",
                 font=("Arial", 14), bg="#BBDEFB", fg="red").pack()

#------------------------- Frame reflexión------------------------



# ------------------------ Frame Servicio ------------------------
frame_servicio.configure(bg="#BBDEFB")
tk.Label(frame_servicio,text="HELADERIA TWINS\nServicio al cliente",font=("Arial", 22, "bold"),bg="#BBDEFB",fg="#01579B",justify="center").pack(pady=(15, 10))
comentarios_frame = tk.LabelFrame(frame_servicio, text="Comentarios y Sugerencias", 
                                  font=("Arial", 12, "bold"), bg="#E3F2FD", fg="#0277BD", bd=2, relief="ridge")
comentarios_frame.pack(padx=20, pady=10, fill="both", expand=True)
tk.Label(comentarios_frame, text="Problemas o sugerencias:", font=("Arial", 11), bg="#E3F2FD").pack(pady=(10, 5))
tk.Label(comentarios_frame, text="Comentario sobre el servicio", font=("Arial", 10), bg="#E3F2FD").pack()
entrada_cal_servicio = tk.Text(comentarios_frame, height=4, width=60, bd=2, relief="groove", wrap="word")
entrada_cal_servicio.pack(pady=5)
tk.Label(comentarios_frame, text="Sugerencias para la aplicación", font=("Arial", 10), bg="#E3F2FD").pack()
entrada_cal_aplicacion = tk.Text(comentarios_frame, height=4, width=60, bd=2, relief="groove", wrap="word")
entrada_cal_aplicacion.pack(pady=5)
tk.Button(comentarios_frame, text="Enviar", font=("Arial", 12, "bold"), 
          bg="#4FC3F7", fg="white", width=12, relief="raised", cursor="hand2", command=enviar_a_firebase).pack(pady=10)
contacto_frame = tk.LabelFrame(frame_servicio, text="Contacto de Servicio", 
                               font=("Arial", 12, "bold"), bg="#E3F2FD", fg="#0277BD", bd=2, relief="ridge")
contacto_frame.pack(padx=20, pady=10, fill="x")
tk.Label(contacto_frame, text="Correo: heladeria_twins@gmail.com", font=("Arial", 10), bg="#E3F2FD").pack(pady=2)
tk.Label(contacto_frame, text="Teléfono: 22 81 86 76 05", font=("Arial", 10), bg="#E3F2FD").pack(pady=2)
tk.Label(contacto_frame, text="Atención en sucursales: 10:00 am - 5:00 pm", font=("Arial", 10), bg="#E3F2FD").pack(pady=2)

# ------------------------ Frame Pagos ------------------------
frame_pagos.configure(bg="#E3F2FD")  # Fondo azul claro

# Título del frame
titulo_frame_pagos = tk.Frame(frame_pagos, bg="#2196F3")  # Azul medio
titulo_frame_pagos.pack(fill="x")

tk.Label(titulo_frame_pagos, text="HELADERÍA TWINS", 
         font=("Arial", 22, "bold"), bg="#2196F3", fg="white").pack(pady=(15, 0))
tk.Label(titulo_frame_pagos, text="Pagos Completados", 
         font=("Arial", 18), bg="#2196F3", fg="white").pack(pady=(0, 15))

# Crear un canvas con scrollbar para el contenido
frame_canvas_pagos = tk.Frame(frame_pagos, bg="#E3F2FD")
frame_canvas_pagos.pack(fill="both", expand=True, padx=20, pady=10)

# Añadir scrollbar vertical
scrollbar_pagos = tk.Scrollbar(frame_canvas_pagos, orient="vertical")
scrollbar_pagos.pack(side="right", fill="y")

# Crear canvas
canvas_pagos = tk.Canvas(frame_canvas_pagos, bg="#E3F2FD", yscrollcommand=scrollbar_pagos.set, 
                         highlightthickness=0)  # Quitar borde del canvas
canvas_pagos.pack(side="left", fill="both", expand=True)

# Configurar scrollbar para controlar el canvas
scrollbar_pagos.config(command=canvas_pagos.yview)

# Crear frame dentro del canvas para contener el contenido
frame_pagos_contenido = tk.Frame(canvas_pagos, bg="#E3F2FD")
canvas_pagos.create_window((0, 0), window=frame_pagos_contenido, anchor="nw")

# Botón para recargar los pagos
btn_recargar_pagos = tk.Button(frame_pagos, text="Mostrar Pagos", 
                               font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", 
                               command=cargar_pagos_completados)
btn_recargar_pagos.pack(pady=10)

# Función para cargar los pagos completados
def cargar_pagos_completados():
    """
    Carga los pagos completados desde Firebase y los muestra en el frame de pagos.
    """
    # Limpiar el contenido del frame
    for widget in frame_pagos_contenido.winfo_children():
        widget.destroy()

    correo_actual = cargar_sesion()
    if not correo_actual:
        messagebox.showwarning("Advertencia", "Debes iniciar sesión para ver los pagos.")
        return

    try:
        # Consultar los pagos del usuario en Firebase
        pagos_ref = db.collection("pedidos")
        query = pagos_ref.where("correo_usuario", "==", correo_actual).stream()

        # Mostrar cada pago
        for doc in query:
            datos_pago = doc.to_dict()

            # Crear un frame para cada pago
            frame_pago = tk.Frame(frame_pagos_contenido, bg="#E3F2FD", bd=2, relief="solid", padx=10, pady=10)
            frame_pago.pack(fill="x", padx=20, pady=10)

            # Mostrar los datos del pago
            tk.Label(frame_pago, text=f"Pago con: {datos_pago.get('metodo_pago', 'No especificado')}", 
                     font=("Arial", 14, "bold"), bg="#E3F2FD", anchor="w").pack(fill="x", padx=10, pady=5)
            tk.Label(frame_pago, text=f"Monto pagado: ${datos_pago.get('total', 0):.2f}", 
                     font=("Arial", 12), bg="#E3F2FD", anchor="w").pack(fill="x", padx=10, pady=5)
            tk.Label(frame_pago, text=f"Día de entrega: {datos_pago.get('dia_entrega', 'No especificado')}", 
                     font=("Arial", 12), bg="#E3F2FD", anchor="w").pack(fill="x", padx=10, pady=5)
            tk.Label(frame_pago, text=f"Entrega en: {datos_pago.get('direccion', 'No especificado')}", 
                     font=("Arial", 12), bg="#E3F2FD", anchor="w").pack(fill="x", padx=10, pady=5)

            # Mostrar los productos
            productos = datos_pago.get("productos", [])
            productos_texto = "\n".join([f"- {p['nombre']} (x{p['cantidad']})" for p in productos])
            tk.Label(frame_pago, text=f"Productos:\n{productos_texto}", 
                     font=("Arial", 12), bg="#E3F2FD", anchor="w", justify="left").pack(fill="x", padx=10, pady=5)

        # Centrar los frames de los pagos
        frame_pagos_contenido.update_idletasks()
        canvas_pagos.config(scrollregion=canvas_pagos.bbox("all"))

    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar los pagos: {e}")

# Asegurarse de que el canvas se ajuste cuando cambie de tamaño
def _configure_canvas_pagos(event):
    canvas_pagos.configure(scrollregion=canvas_pagos.bbox("all"))
    canvas_pagos.itemconfig(canvas_pagos.find_withtag("all")[0], width=event.width)

canvas_pagos.bind("<Configure>", _configure_canvas_pagos)

# ------------------------ Frame Carro de Compras ------------------------
# Cambiar el fondo a un gradiente simulado (usando frames con diferentes tonos)
frame_carro.configure(bg="#E1F5FE")  # Fondo azul claro para carrito

# Título con mejor diseño
titulo_frame_carro = tk.Frame(frame_carro, bg="#03A9F4")  # Azul medio
titulo_frame_carro.pack(fill="x")

tk.Label(titulo_frame_carro, text="HELADERÍA TWINS", 
         font=("Arial", 22, "bold"), bg="#03A9F4", fg="white").pack(pady=(15, 0))
tk.Label(titulo_frame_carro, text="Carrito de Compras", 
         font=("Arial", 18), bg="#03A9F4", fg="white").pack(pady=(0, 15))

# Crear un canvas con scrollbar para el contenido
frame_canvas_carro = tk.Frame(frame_carro, bg="#E1F5FE")
frame_canvas_carro.pack(fill="both", expand=True, padx=20, pady=10)

# Añadir scrollbar vertical con mejor diseño
scrollbar_carro = tk.Scrollbar(frame_canvas_carro, orient="vertical")
scrollbar_carro.pack(side="right", fill="y")

# Crear canvas
canvas_carro = tk.Canvas(frame_canvas_carro, bg="#E1F5FE", yscrollcommand=scrollbar_carro.set, 
                  highlightthickness=0)  # Quitar borde del canvas
canvas_carro.pack(side="left", fill="both", expand=True)

# Configurar scrollbar para controlar el canvas
scrollbar_carro.config(command=canvas_carro.yview)

# Crear frame dentro del canvas para contener el contenido
frame_contenido_carro = tk.Frame(canvas_carro, bg="#E1F5FE")
canvas_carro.create_window((0, 0), window=frame_contenido_carro, anchor="nw", width=canvas_carro.winfo_width())

# Título de la sección de productos en el carrito
titulo_productos_carrito_frame = tk.Frame(frame_contenido_carro, bg="#E1F5FE")
titulo_productos_carrito_frame.pack(fill="x", pady=(20, 10))

# Fondo decorativo para el título
titulo_productos_carrito_bg = tk.Frame(titulo_productos_carrito_frame, bg="#B3E5FC", padx=20, pady=10)
titulo_productos_carrito_bg.pack()

tk.Label(titulo_productos_carrito_bg, text="Productos en tu carrito", 
         font=("Arial", 18, "bold"), bg="#B3E5FC", fg="#01579B").pack(side="top")

# Línea decorativa debajo del título
linea_productos_carrito = tk.Frame(titulo_productos_carrito_bg, height=2, bg="#01579B")
linea_productos_carrito.pack(fill="x", padx=50, pady=5)

# Frame para los productos en el carrito
frame_productos_carrito = tk.Frame(frame_contenido_carro, bg="#E1F5FE")
frame_productos_carrito.pack(fill="both", expand=True, pady=15)

# Encabezados de la tabla
frame_encabezados = tk.Frame(frame_productos_carrito, bg="#B3E5FC")
frame_encabezados.pack(fill="x", pady=(0, 10))

# Configurar columnas para los encabezados
frame_encabezados.columnconfigure(0, weight=3)  # Producto
frame_encabezados.columnconfigure(1, weight=1)  # Cantidad
frame_encabezados.columnconfigure(2, weight=1)  # Tamaño
frame_encabezados.columnconfigure(3, weight=1)  # Precio Unit.
frame_encabezados.columnconfigure(4, weight=1)  # Precio Total
frame_encabezados.columnconfigure(5, weight=1)  # Eliminar

# Encabezados
tk.Label(frame_encabezados, text="Producto", font=("Arial", 12, "bold"), 
         bg="#B3E5FC", fg="#01579B").grid(row=0, column=0, padx=10, pady=5, sticky="w")
tk.Label(frame_encabezados, text="Cantidad", font=("Arial", 12, "bold"), 
         bg="#B3E5FC", fg="#01579B").grid(row=0, column=1, padx=10, pady=5)
tk.Label(frame_encabezados, text="Tamaño", font=("Arial", 12, "bold"), 
         bg="#B3E5FC", fg="#01579B").grid(row=0, column=2, padx=10, pady=5)
tk.Label(frame_encabezados, text="Precio Unit.", font=("Arial", 12, "bold"), 
         bg="#B3E5FC", fg="#01579B").grid(row=0, column=3, padx=10, pady=5)
tk.Label(frame_encabezados, text="Precio Total", font=("Arial", 12, "bold"), 
         bg="#B3E5FC", fg="#01579B").grid(row=0, column=4, padx=10, pady=5)
tk.Label(frame_encabezados, text="Eliminar", font=("Arial", 12, "bold"), 
         bg="#B3E5FC", fg="#01579B").grid(row=0, column=5, padx=10, pady=5)

# Sección de resumen y total
frame_resumen = tk.Frame(frame_contenido_carro, bg="#E1F5FE")
frame_resumen.pack(fill="x", pady=20)

# Botones para finalizar compra y seguir comprando
frame_botones = tk.Frame(frame_contenido_carro, bg="#E1F5FE")
frame_botones.pack(fill="x", pady=20)

btn_comprar = tk.Button(frame_botones, text="Finalizar Compra", bg="#03A9F4", fg="white", 
                        font=("Arial", 14, "bold"), relief="flat", padx=30, pady=10,
                        activebackground="#0288D1", activeforeground="white",
                        cursor="hand2", command=mostrar_menu_finalizar_compra)
btn_comprar.pack(side="right", padx=30)

btn_seguir_comprando = tk.Button(frame_botones, text="Seguir Comprando", bg="#4FC3F7", fg="white", 
                                font=("Arial", 12), relief="flat", padx=20, pady=8,
                                activebackground="#29B6F6", activeforeground="white",
                                cursor="hand2", command=lambda: mostrar_frame(frame_productos))
btn_seguir_comprando.pack(side="right", padx=10)

# Inicializar la visualización del carrito
print("Inicializando visualización del carrito")
actualizar_carrito()



# Actualizar el scrollregion después de añadir el contenido
frame_contenido_carro.update_idletasks()
canvas_carro.config(scrollregion=canvas_carro.bbox("all"))

# Asegurarse de que el canvas se ajuste cuando cambie de tamaño
def _configure_canvas_carro(event):
    canvas_carro.configure(scrollregion=canvas_carro.bbox("all"))
    canvas_carro.itemconfig(canvas_carro.find_withtag("all")[0], width=event.width)

canvas_carro.bind("<Configure>", _configure_canvas_carro)

# Cambiar el diseño del frame de ofertas a tonos morados/lila
frame_ofertas.configure(bg="#F3E5F5")  # Fondo lila claro

# Título del frame
titulo_frame_ofertas = tk.Frame(frame_ofertas, bg="#AB47BC")  # Lila medio
titulo_frame_ofertas.pack(fill="x")

tk.Label(titulo_frame_ofertas, text="HELADERÍA TWINS", 
         font=("Arial", 22, "bold"), bg="#AB47BC", fg="white").pack(pady=(15, 0))
tk.Label(titulo_frame_ofertas, text="Ofertas y Promociones", 
         font=("Arial", 18), bg="#AB47BC", fg="white").pack(pady=(0, 15))

# Crear un canvas con scrollbar para el contenido
frame_canvas_ofertas = tk.Frame(frame_ofertas, bg="#F3E5F5")
frame_canvas_ofertas.pack(fill="both", expand=True, padx=20, pady=10)

# Añadir scrollbar vertical
scrollbar_ofertas = tk.Scrollbar(frame_canvas_ofertas, orient="vertical")
scrollbar_ofertas.pack(side="right", fill="y")

# Crear canvas
canvas_ofertas = tk.Canvas(frame_canvas_ofertas, bg="#F3E5F5", yscrollcommand=scrollbar_ofertas.set, 
                           highlightthickness=0)  # Quitar borde del canvas
canvas_ofertas.pack(side="left", fill="both", expand=True)

# Configurar scrollbar para controlar el canvas
scrollbar_ofertas.config(command=canvas_ofertas.yview)

# Crear frame dentro del canvas para contener el contenido
frame_contenido_ofertas = tk.Frame(canvas_ofertas, bg="#F3E5F5")
canvas_ofertas.create_window((0, 0), window=frame_contenido_ofertas, anchor="nw", width=canvas_ofertas.winfo_width())

# Dividir las ofertas en dos columnas y centrar los paquetes
def cargar_ofertas():
    """
    Carga las ofertas disponibles y las muestra en el frame de ofertas.
    """
    # Limpiar el contenido del frame
    for widget in frame_contenido_ofertas.winfo_children():
        widget.destroy()

    # Lista de paquetes promocionales
    paquetes = [
        {
            "nombre": "Paquete Familiar",
            "productos": ["4 Paletas", "2 Gelatos", "1 Malteada"],
            "precio": 200.00
        },
        {
            "nombre": "Paquete Pareja",
            "productos": ["2 Paletas", "2 Gelatos"],
            "precio": 120.00
        },
        {
            "nombre": "Paquete Fiesta",
            "productos": ["10 Paletas", "5 Gelatos", "3 Malteadas"],
            "precio": 500.00
        },
        {
            "nombre": "Paquete Infantil",
            "productos": ["5 Paletas", "3 Gelatos"],
            "precio": 150.00
        },
        {
            "nombre": "Paquete Deluxe",
            "productos": ["6 Paletas", "4 Gelatos", "2 Malteadas"],
            "precio": 300.00
        },
        {
            "nombre": "Paquete Económico",
            "productos": ["3 Paletas", "2 Gelatos"],
            "precio": 100.00
        },
        {
            "nombre": "Paquete Premium",
            "productos": ["8 Paletas", "6 Gelatos", "2 Malteadas"],
            "precio": 400.00
        },
        {
            "nombre": "Paquete Tropical",
            "productos": ["5 Paletas de Fruta", "3 Gelatos de Mango"],
            "precio": 180.00
        },
        {
            "nombre": "Paquete Especial",
            "productos": ["4 Paletas", "4 Gelatos", "1 Malteada", "1 Chamoyada"],
            "precio": 250.00
        },
        {
            "nombre": "Paquete Gourmet",
            "productos": ["6 Paletas", "6 Gelatos", "2 Malteadas", "2 Postres"],
            "precio": 450.00
        }
    ]

    # Mostrar cada paquete en dos columnas
    for i, paquete in enumerate(paquetes):
        columna = i % 2
        fila = i // 2

        frame_paquete = tk.Frame(frame_contenido_ofertas, bg="#E1BEE7", bd=1, relief="solid")
        frame_paquete.grid(row=fila, column=columna, padx=20, pady=20, sticky="nsew")

        # Nombre del paquete
        tk.Label(frame_paquete, text=paquete["nombre"], font=("Arial", 14, "bold"), bg="#E1BEE7", fg="#6A1B9A").pack(anchor="w", padx=10, pady=5)

        # Lista de productos
        productos_texto = "\n".join([f"- {producto}" for producto in paquete["productos"]])
        tk.Label(frame_paquete, text=f"Productos:\n{productos_texto}", font=("Arial", 12), bg="#E1BEE7", anchor="w", justify="left").pack(anchor="w", padx=10, pady=5)

        # Precio
        tk.Label(frame_paquete, text=f"Precio: ${paquete['precio']:.2f}", font=("Arial", 12, "bold"), bg="#E1BEE7", fg="#4A148C").pack(anchor="w", padx=10, pady=5)

        # Botón para agregar al carrito con menú de sabores
        tk.Button(frame_paquete, text="Agregar al carrito", font=("Arial", 12, "bold"), bg="#AB47BC", fg="white", relief="flat",
                  command=lambda p=paquete: agregar_paquete_al_carrito(p)).pack(pady=10)

    # Centrar los paquetes
    frame_contenido_ofertas.columnconfigure(0, weight=1)
    frame_contenido_ofertas.columnconfigure(1, weight=1)

# Cargar las ofertas
cargar_ofertas()

# Actualizar el scrollregion después de añadir el contenido
frame_contenido_ofertas.update_idletasks()
canvas_ofertas.config(scrollregion=canvas_ofertas.bbox("all"))

# Asegurarse de que el canvas se ajuste cuando cambie de tamaño
def _configure_canvas_ofertas(event):
    canvas_ofertas.configure(scrollregion=canvas_ofertas.bbox("all"))
    canvas_ofertas.itemconfig(canvas_ofertas.find_withtag("all")[0], width=event.width)

canvas_ofertas.bind("<Configure>", _configure_canvas_ofertas)

# Cambiar el fondo a tonos rosas
frame_personalizados.configure(bg="#FCE4EC")  # Fondo rosa claro

# Título del frame
titulo_frame_personalizados = tk.Frame(frame_personalizados, bg="#EC407A")  # Rosa medio
titulo_frame_personalizados.pack(fill="x")

tk.Label(titulo_frame_personalizados, text="HELADERÍA TWINS", 
         font=("Arial", 22, "bold"), bg="#EC407A", fg="white").pack(pady=(15, 0))
tk.Label(titulo_frame_personalizados, text="Pedidos Personalizados", 
         font=("Arial", 18), bg="#EC407A", fg="white").pack(pady=(0, 15))

# Contenedor principal
frame_contenido_personalizados = tk.Frame(frame_personalizados, bg="#FCE4EC")
frame_contenido_personalizados.pack(fill="both", expand=True, padx=20, pady=20)

# Caja de texto para indicaciones del pedido
tk.Label(frame_contenido_personalizados, text="Indica los detalles de tu pedido:", 
         font=("Arial", 14, "bold"), bg="#FCE4EC", fg="#AD1457").pack(anchor="w", pady=(10, 5))

entrada_indicaciones = tk.Text(frame_contenido_personalizados, height=8, width=60, 
                               font=("Arial", 12), bd=2, relief="groove", wrap="word")
entrada_indicaciones.pack(fill="x", pady=(0, 20))

# Botón para subir una imagen de referencia
tk.Label(frame_contenido_personalizados, text="Sube una imagen de referencia (opcional):", 
         font=("Arial", 14, "bold"), bg="#FCE4EC", fg="#AD1457").pack(anchor="w", pady=(10, 5))

frame_imagen = tk.Frame(frame_contenido_personalizados, bg="#FCE4EC")
frame_imagen.pack(fill="x", pady=(0, 20))

ruta_imagen = tk.StringVar(value="No se ha seleccionado ninguna imagen")

def seleccionar_imagen():
    """
    Abre un diálogo para seleccionar una imagen y guarda la ruta en la variable.
    """
    ruta = filedialog.askopenfilename(
        title="Seleccionar imagen de referencia",
        filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif")]
    )
    if ruta:
        ruta_imagen.set(ruta)
        label_ruta_imagen.config(text=f"Imagen seleccionada: {os.path.basename(ruta)}")
    else:
        ruta_imagen.set("No se ha seleccionado ninguna imagen")
        label_ruta_imagen.config(text=ruta_imagen.get())

btn_subir_imagen = tk.Button(frame_imagen, text="Seleccionar Imagen", 
                             font=("Arial", 12, "bold"), bg="#EC407A", fg="white", 
                             relief="flat", command=seleccionar_imagen)
btn_subir_imagen.pack(side="left", padx=10)

label_ruta_imagen = tk.Label(frame_imagen, textvariable=ruta_imagen, 
                             font=("Arial", 12), bg="#FCE4EC", fg="#AD1457", anchor="w")
label_ruta_imagen.pack(side="left", padx=10)

# Botón para enviar el pedido personalizado
def enviar_pedido_personalizado():
    """
    Envía el pedido personalizado a la base de datos.
    """
    indicaciones = entrada_indicaciones.get("1.0", tk.END).strip()
    imagen_ruta = ruta_imagen.get()

    if not indicaciones:
        messagebox.showwarning("Campos vacíos", "Por favor, proporciona las indicaciones para tu pedido.")
        return

    try:
        # Preparar los datos del pedido
        datos_pedido = {
            "indicaciones": indicaciones,
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Si se seleccionó una imagen, convertirla a base64
        if imagen_ruta != "No se ha seleccionado ninguna imagen":
            with open(imagen_ruta, "rb") as img_file:
                imagen_base64 = base64.b64encode(img_file.read()).decode("utf-8")
                datos_pedido["imagen_referencia"] = imagen_base64

        # Guardar el pedido en Firebase
        db.collection("pedidos_personalizados").add(datos_pedido)

        # Obtener el número de teléfono del perfil
        correo_actual = cargar_sesion()
        telefono_usuario = "No disponible"
        if correo_actual:
            usuarios_ref = db.collection("usuarios")
            query = usuarios_ref.where("correo", "==", correo_actual).limit(1).stream()
            for doc in query:
                datos_usuario = doc.to_dict()
                telefono_usuario = datos_usuario.get("telefono", "No disponible")
                break

        # Mostrar mensaje de éxito
        messagebox.showinfo("Pedido solicitado", f"Pedido solicitado. Nos pondremos en contacto para cotizar más detalles al número: {telefono_usuario}")
        
        # Limpiar los campos
        entrada_indicaciones.delete("1.0", tk.END)
        ruta_imagen.set("No se ha seleccionado ninguna imagen")
        label_ruta_imagen.config(text=ruta_imagen.get())

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo enviar el pedido: {e}")

btn_enviar_pedido = tk.Button(frame_contenido_personalizados, text="Enviar Pedido", 
                              font=("Arial", 14, "bold"), bg="#AD1457", fg="white", 
                              relief="flat", command=enviar_pedido_personalizado)
btn_enviar_pedido.pack(pady=20)

# ------------------------ Frame Productos ------------------------
# Contenedor principal centrado
frame_productos_container = tk.Frame(frame_productos, bg="#BBDEFB")
frame_productos_container.pack(expand=True)

# Frame para los botones de categorías
frame_categorias = tk.Frame(frame_productos_container, bg="#BBDEFB")
frame_categorias.pack(pady=20)

# Cargar imágenes
img_paletas = Image.open("E:/IMGprogramas/paletas.png")
img_paletas = img_paletas.resize((120, 120))
img_paletas = ImageTk.PhotoImage(img_paletas)

img_gelatos = Image.open("E:/IMGprogramas/gelatos.jpg")
img_gelatos = img_gelatos.resize((120, 120))
img_gelatos = ImageTk.PhotoImage(img_gelatos)

img_otros = Image.open("E:/IMGprogramas/otros.jpg")
img_otros = img_otros.resize((120, 120))
img_otros = ImageTk.PhotoImage(img_otros)

# Función para crear botones de categoría
def crear_boton_categoria(parent, imagen, texto, comando):
    frame = tk.Frame(parent, bg="#BBDEFB")
    frame.pack(side="left", padx=30)
    
    # Botón con imagen
    btn = tk.Button(frame, image=imagen, bg="#BBDEFB", bd=0, 
                   activebackground="#BBDEFB", command=comando)
    btn.pack()
    
    # Etiqueta de texto
    tk.Label(frame, text=texto, font=("Arial", 14, "bold"), 
             bg="#BBDEFB", fg="#0277BD").pack(pady=5)
    
    return frame


# Guardar referencias de imagen para evitar que se borren
frame_productos.img_paletas = img_paletas
frame_productos.img_gelatos = img_gelatos
frame_productos.img_otros = img_otros

# ------------------------ Frame Paletas ------------------------
# Cambiar el fondo a un gradiente simulado (usando frames con diferentes tonos)
frame_paletas.configure(bg="#F8E0F7")  # Fondo lila claro para paletas

# Título con mejor diseño
titulo_frame_paletas = tk.Frame(frame_paletas, bg="#D370D3")  # Lila medio
titulo_frame_paletas.pack(fill="x")

tk.Label(titulo_frame_paletas, text="HELADERÍA TWINS", 
         font=("Arial", 22, "bold"), bg="#D370D3", fg="white").pack(pady=(15, 0))
tk.Label(titulo_frame_paletas, text="Paletas", 
         font=("Arial", 18), bg="#D370D3", fg="white").pack(pady=(0, 15))

# Botón para volver a productos con mejor diseño
btn_volver_frame = tk.Frame(frame_paletas, bg="#F8E0F7")
btn_volver_frame.pack(pady=10)

tk.Button(btn_volver_frame, text="← Volver a Productos", 
          command=lambda: mostrar_frame(frame_productos),
          bg="#D370D3", fg="white", font=("Arial", 12, "bold"), 
          relief="flat", padx=15, pady=5).pack()

# Crear un canvas con scrollbar para el contenido
frame_canvas = tk.Frame(frame_paletas, bg="#F8E0F7")
frame_canvas.pack(fill="both", expand=True, padx=20, pady=10)

# Añadir scrollbar vertical con mejor diseño
scrollbar = tk.Scrollbar(frame_canvas, orient="vertical")
scrollbar.pack(side="right", fill="y")

# Crear canvas
canvas = tk.Canvas(frame_canvas, bg="#F8E0F7", yscrollcommand=scrollbar.set, 
                  highlightthickness=0)  # Quitar borde del canvas
canvas.pack(side="left", fill="both", expand=True)

# Configurar scrollbar para controlar el canvas
scrollbar.config(command=canvas.yview)

# Crear frame dentro del canvas para contener el contenido
frame_contenido_paletas = tk.Frame(canvas, bg="#F8E0F7")
canvas.create_window((0, 0), window=frame_contenido_paletas, anchor="nw", width=canvas.winfo_width())

# Título de la sección de frutas con mejor diseño
titulo_frame = tk.Frame(frame_contenido_paletas, bg="#F8E0F7")
titulo_frame.pack(fill="x", pady=(20, 10))

# Fondo decorativo para el título
titulo_bg = tk.Frame(titulo_frame, bg="#F5C5F3", padx=20, pady=10)
titulo_bg.pack()

tk.Label(titulo_bg, text="Fruta", 
         font=("Arial", 18, "bold"), bg="#F5C5F3", fg="#9C27B0").pack(side="top")

# Línea decorativa debajo del título
linea = tk.Frame(titulo_bg, height=2, bg="#9C27B0")
linea.pack(fill="x", padx=50, pady=5)

# Frame para las imágenes destacadas (centrado)
frame_imagenes_container = tk.Frame(frame_contenido_paletas, bg="#F8E0F7")
frame_imagenes_container.pack(fill="x", pady=15)

frame_imagenes = tk.Frame(frame_imagenes_container, bg="#F8E0F7")
frame_imagenes.pack(side="top", pady=15)

# Cargar y mostrar 3 imágenes destacadas con mejor diseño
try:
    # Puedes cambiar estas rutas por las imágenes que desees mostrar
    rutas_imagenes = [
        "E:/IMGprogramas/uno.jpg",
        "E:/IMGprogramas/dos.jpeg",
        "E:/IMGprogramas/tres.jpeg"
    ]
    
    imagenes_destacadas = []
    for i, ruta in enumerate(rutas_imagenes):
        img = Image.open(ruta)
        img = img.resize((150, 150))
        img_tk = ImageTk.PhotoImage(img)
        imagenes_destacadas.append(img_tk)
        
        frame_img = tk.Frame(frame_imagenes, bg="#E8F5E9")
        frame_img.pack(side="left", padx=15)
        
        # Imagen con borde redondeado y sombra
        img_frame = tk.Frame(frame_img, bd=2, relief="raised", bg="#4CAF50")
        img_frame.pack(padx=5, pady=5)
        
        tk.Label(img_frame, image=img_tk, bg="#E8F5E9").pack(padx=2, pady=2)
    
    # Guardar referencias para evitar que se eliminen
    frame_paletas.imagenes_destacadas = imagenes_destacadas
    
except Exception as e:
    tk.Label(frame_imagenes, text=f"Error al cargar imágenes: {e}", 
             font=("Arial", 12), bg="#E8F5E9", fg="red").pack()

# Lista de sabores de frutas
sabores_frutas = [
    "Fresa", "Plátano", "Mango", "Maracuyá", "Limón", 
    "Naranja", "Piña", "Sandía", "Piña", "Uva"
]

# Frame para el menú de sabores (centrado)
frame_menu_container = tk.Frame(frame_contenido_paletas, bg="#F8E0F7")
frame_menu_container.pack(fill="x", pady=15)

frame_menu = tk.Frame(frame_menu_container, bg="#F8E0F7")
frame_menu.pack(side="top", pady=15)

# Crear una cuadrícula para los sabores (2 columnas) con mejor diseño
for i, sabor in enumerate(sabores_frutas):
    fila = i // 3
    columna = i % 3
    
    # Frame para cada elemento del menú
    frame_item = tk.Frame(frame_menu, bg="#F8E0F7", bd=0)
    frame_item.grid(row=fila, column=columna, padx=15, pady=10)
    
    # Marco con borde redondeado y sombra
    item_border = tk.Frame(frame_item, bg="#D370D3", bd=1, relief="raised")
    item_border.pack(padx=2, pady=2)
    
    # Frame interno para organizar el contenido verticalmente
    frame_interno = tk.Frame(item_border, bg="#FFFFFF")  # Fondo blanco para contraste
    frame_interno.pack(padx=2, pady=2)
    
    # Nombre del sabor con fondo de color
    titulo_sabor = tk.Frame(frame_interno, bg="#F5C5F3", width=180)
    titulo_sabor.pack(fill="x")
    tk.Label(titulo_sabor, text=sabor, font=("Arial", 14, "bold"), 
             bg="#F5C5F3", fg="#9C27B0", width=15).pack(pady=8)
    
    # Precio (ejemplo) con mejor diseño
    precio_frame = tk.Frame(frame_interno, bg="#FFFFFF")
    precio_frame.pack(fill="x", pady=5)
    tk.Label(precio_frame, text="$25.00", font=("Arial", 12, "bold"), 
             bg="#FFFFFF", fg="#2E7D32").pack()
    
    # Botón para añadir al carrito con mejor diseño
    btn_frame = tk.Frame(frame_interno, bg="#FFFFFF")
    btn_frame.pack(pady=10, fill="x")
    
    btn_agregar = tk.Button(btn_frame, text="Agregar", bg="#D370D3", fg="white", 
                           font=("Arial", 10, "bold"), relief="flat", width=10,
                           activebackground="#9C27B0", activeforeground="white",
                           cursor="hand2",
                           command=lambda s=sabor: mostrar_opciones_producto(s, 25.00))
    btn_agregar.pack()



# Título de la sección de Base de crema con mejor diseño
titulo_crema_frame = tk.Frame(frame_contenido_paletas, bg="#F8E0F7")
titulo_crema_frame.pack(fill="x", pady=(30, 10))

# Fondo decorativo para el título
titulo_crema_bg = tk.Frame(titulo_crema_frame, bg="#F5C5F3", padx=20, pady=10)
titulo_crema_bg.pack()

tk.Label(titulo_crema_bg, text="Base de crema", 
         font=("Arial", 18, "bold"), bg="#F5C5F3", fg="#9C27B0").pack(side="top")

# Línea decorativa debajo del título
linea_crema = tk.Frame(titulo_crema_bg, height=2, bg="#9C27B0")
linea_crema.pack(fill="x", padx=50, pady=5)

# Frame para las imágenes destacadas de crema (centrado)
frame_imagenes_crema_container = tk.Frame(frame_contenido_paletas, bg="#F8E0F7")
frame_imagenes_crema_container.pack(fill="x", pady=15)

frame_imagenes_crema = tk.Frame(frame_imagenes_crema_container, bg="#F8E0F7")
frame_imagenes_crema.pack(side="top", pady=15)

# Cargar y mostrar 3 imágenes destacadas para la sección de crema
try:
    # Puedes cambiar estas rutas por las imágenes que desees mostrar
    rutas_imagenes_crema = [
        "E:/IMGprogramas/tres3.jpg",
        "E:/IMGprogramas/dos2.jpg",
        "E:/IMGprogramas/uno1.jpg"
    ]
    
    imagenes_destacadas_crema = []
    for i, ruta in enumerate(rutas_imagenes_crema):
        img = Image.open(ruta)
        img = img.resize((150, 150))
        img_tk = ImageTk.PhotoImage(img)
        imagenes_destacadas_crema.append(img_tk)
        
        frame_img = tk.Frame(frame_imagenes_crema, bg="#E8F5E9")
        frame_img.pack(side="left", padx=15)
        
        # Imagen con borde redondeado y sombra
        img_frame = tk.Frame(frame_img, bd=2, relief="raised", bg="#4CAF50")
        img_frame.pack(padx=5, pady=5)
        
        tk.Label(img_frame, image=img_tk, bg="#E8F5E9").pack(padx=2, pady=2)
    
    # Guardar referencias para evitar que se eliminen
    frame_paletas.imagenes_destacadas_crema = imagenes_destacadas_crema
    
except Exception as e:
    tk.Label(frame_imagenes_crema, text=f"Error al cargar imágenes: {e}", 
             font=("Arial", 12), bg="#E8F5E9", fg="red").pack()

# Lista de sabores de base de crema
sabores_crema = [
    "Vainilla", "Chocolate", "Fresa con crema", "Coco", "Capuchino",
    "Dulce de leche", "Galleta Oreo", "Pistacho", "Queso con zarzamora", "Choco-plátano"
]

# Frame para el menú de sabores de crema (centrado)
frame_menu_crema_container = tk.Frame(frame_contenido_paletas, bg="#F8E0F7")
frame_menu_crema_container.pack(fill="x", pady=15)

frame_menu_crema = tk.Frame(frame_menu_crema_container, bg="#F8E0F7")
frame_menu_crema.pack(side="top", pady=15)

# Crear una cuadrícula para los sabores de crema (2 columnas)
for i, sabor in enumerate(sabores_crema):
    fila = i // 3
    columna = i % 3
    
    # Frame para cada elemento del menú
    frame_item = tk.Frame(frame_menu_crema, bg="#F8E0F7", bd=0)
    frame_item.grid(row=fila, column=columna, padx=15, pady=10)
    
    # Marco con borde redondeado y sombra
    item_border = tk.Frame(frame_item, bg="#D370D3", bd=1, relief="raised")
    item_border.pack(padx=2, pady=2)
    
    # Frame interno para organizar el contenido verticalmente
    frame_interno = tk.Frame(item_border, bg="#FFFFFF")
    frame_interno.pack(padx=2, pady=2)
    
    # Nombre del sabor con fondo de color (diferente color para distinguir de frutas)
    titulo_sabor = tk.Frame(frame_interno, bg="#F5C5F3", width=180)
    titulo_sabor.pack(fill="x")
    tk.Label(titulo_sabor, text=sabor, font=("Arial", 14, "bold"), 
             bg="#F5C5F3", fg="#9C27B0", width=15).pack(pady=8)
    
    # Precio (ejemplo)
    precio_frame = tk.Frame(frame_interno, bg="#FFFFFF")
    precio_frame.pack(fill="x", pady=5)
    tk.Label(precio_frame, text="$30.00", font=("Arial", 12, "bold"), 
             bg="#FFFFFF", fg="#2E7D32").pack()
    
    # Botón para añadir al carrito con mejor diseño
    btn_frame = tk.Frame(frame_interno, bg="#FFFFFF")
    btn_frame.pack(pady=10, fill="x")

    btn_agregar = tk.Button(btn_frame, text="Agregar", bg="#D370D3", fg="white", 
                       font=("Arial", 10, "bold"), relief="flat", width=10,
                       activebackground="#9C27B0", activeforeground="white",
                       cursor="hand2",
                       command=lambda s=sabor: mostrar_opciones_producto(s, 30.00))
    btn_agregar.pack()


# Título de la sección de Base de yogurth con mejor diseño
titulo_yogurth_frame = tk.Frame(frame_contenido_paletas, bg="#F8E0F7")
titulo_yogurth_frame.pack(fill="x", pady=(30, 10))

# Fondo decorativo para el título
titulo_yogurth_bg = tk.Frame(titulo_yogurth_frame, bg="#F5C5F3", padx=20, pady=10)
titulo_yogurth_bg.pack()

tk.Label(titulo_yogurth_bg, text="Base de yogurth", 
         font=("Arial", 18, "bold"), bg="#F5C5F3", fg="#9C27B0").pack(side="top")

# Línea decorativa debajo del título
linea_yogurth = tk.Frame(titulo_yogurth_bg, height=2, bg="#9C27B0")
linea_yogurth.pack(fill="x", padx=50, pady=5)

# Frame para las imágenes destacadas de yogurth (centrado)
frame_imagenes_yogurth_container = tk.Frame(frame_contenido_paletas, bg="#F8E0F7")
frame_imagenes_yogurth_container.pack(fill="x", pady=15)

frame_imagenes_yogurth = tk.Frame(frame_imagenes_yogurth_container, bg="#F8E0F7")
frame_imagenes_yogurth.pack(side="top", pady=15)

# Cargar y mostrar 3 imágenes destacadas para la sección de yogurth
try:
    # Puedes cambiar estas rutas por las imágenes que desees mostrar
    rutas_imagenes_yogurth = [
        "E:/IMGprogramas/yogu1.jpg",
        "E:/IMGprogramas/yogu2.jpg",
        "E:/IMGprogramas/yogu3.jpg"
    ]
    
    imagenes_destacadas_yogurth = []
    for i, ruta in enumerate(rutas_imagenes_yogurth):
        img = Image.open(ruta)
        img = img.resize((150, 150))
        img_tk = ImageTk.PhotoImage(img)
        imagenes_destacadas_yogurth.append(img_tk)
        
        frame_img = tk.Frame(frame_imagenes_yogurth, bg="#E8F5E9")
        frame_img.pack(side="left", padx=15)
        
        # Imagen con borde redondeado y sombra
        img_frame = tk.Frame(frame_img, bd=2, relief="raised", bg="#4CAF50")
        img_frame.pack(padx=5, pady=5)
        
        tk.Label(img_frame, image=img_tk, bg="#E8F5E9").pack(padx=2, pady=2)
    
    # Guardar referencias para evitar que se eliminen
    frame_paletas.imagenes_destacadas_yogurth = imagenes_destacadas_yogurth
    
except Exception as e:
    tk.Label(frame_imagenes_yogurth, text=f"Error al cargar imágenes: {e}", 
             font=("Arial", 12), bg="#E8F5E9", fg="red").pack()

# Lista de sabores de base de yogurth
sabores_yogurth = [
    "Yogurth con\nfresa", "Yogurth con\nmora azul", "Yogurth con\nmaracuyá",
    "Yogurth con\nmango", "Yogurth con\npiña", "Yogurth con\nfrutos rojos"
]

# Frame para el menú de sabores de yogurth (centrado)
frame_menu_yogurth_container = tk.Frame(frame_contenido_paletas, bg="#F8E0F7")
frame_menu_yogurth_container.pack(fill="x", pady=15)

frame_menu_yogurth = tk.Frame(frame_menu_yogurth_container, bg="#F8E0F7")
frame_menu_yogurth.pack(side="top", pady=15)

# Crear una cuadrícula para los sabores de yogurth (2 columnas)
for i, sabor in enumerate(sabores_yogurth):
    fila = i // 3
    columna = i % 3
    
    # Frame para cada elemento del menú
    frame_item = tk.Frame(frame_menu_yogurth, bg="#F8E0F7", bd=0)
    frame_item.grid(row=fila, column=columna, padx=15, pady=10)
    
    # Marco con borde redondeado y sombra
    item_border = tk.Frame(frame_item, bg="#D370D3", bd=1, relief="raised")
    item_border.pack(padx=2, pady=2)
    
    # Frame interno para organizar el contenido verticalmente
    frame_interno = tk.Frame(item_border, bg="#FFFFFF")
    frame_interno.pack(padx=2, pady=2)
    
    # Nombre del sabor con fondo de color (diferente color para distinguir de yogurth)
    titulo_sabor = tk.Frame(frame_interno, bg="#F8E0F7", width=180)
    titulo_sabor.pack(fill="x")
    tk.Label(titulo_sabor, text=sabor, font=("Arial", 14, "bold"), 
             bg="#F8E0F7", fg="#9C27B0", width=15).pack(pady=8)
    
    # Precio (ejemplo)
    precio_frame = tk.Frame(frame_interno, bg="#FFFFFF")
    precio_frame.pack(fill="x", pady=5)
    tk.Label(precio_frame, text="$35.00", font=("Arial", 12, "bold"), 
             bg="#FFFFFF", fg="#2E7D32").pack()
    
    # Botón para añadir al carrito con mejor diseño
    btn_frame = tk.Frame(frame_interno, bg="#FFFFFF")
    btn_frame.pack(pady=10, fill="x")

    btn_agregar = tk.Button(btn_frame, text="Agregar", bg="#D370D3", fg="white", 
                       font=("Arial", 10, "bold"), relief="flat", width=10,
                       activebackground="#9C27B0", activeforeground="white",
                       cursor="hand2",
                       command=lambda s=sabor: mostrar_opciones_producto(s, 35.00))
    btn_agregar.pack()


# Configurar el grid para que las columnas tengan el mismo ancho
frame_menu_yogurth.columnconfigure(0, weight=1)
frame_menu_yogurth.columnconfigure(1, weight=1)

# Actualizar el scrollregion después de añadir el nuevo contenido
frame_contenido_paletas.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))

# Asegurarse de que el canvas se ajuste cuando cambie de tamaño
def _configure_canvas(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width)

canvas.bind("<Configure>", _configure_canvas)


# ------------------------ Frame Gelatos ------------------------
# Cambiar el fondo a un gradiente simulado (usando frames con diferentes tonos)
frame_gelatos.configure(bg="#E3F2FD")  # Fondo azul claro para gelatos

# Título con mejor diseño
titulo_frame_gelatos = tk.Frame(frame_gelatos, bg="#2196F3")  # Azul medio
titulo_frame_gelatos.pack(fill="x")

tk.Label(titulo_frame_gelatos, text="HELADERÍA TWINS", 
         font=("Arial", 22, "bold"), bg="#2196F3", fg="white").pack(pady=(15, 0))
tk.Label(titulo_frame_gelatos, text="Gelatos y Nieves", 
         font=("Arial", 18), bg="#2196F3", fg="white").pack(pady=(0, 15))

# Botón para volver a productos con mejor diseño
btn_volver_frame_gelatos = tk.Frame(frame_gelatos, bg="#E3F2FD")
btn_volver_frame_gelatos.pack(pady=10)

tk.Button(btn_volver_frame_gelatos, text="← Volver a Productos", 
          command=lambda: mostrar_frame(frame_productos),
          bg="#1565C0", fg="white", font=("Arial", 12, "bold"), 
          relief="flat", padx=15, pady=5).pack()

# Crear un canvas con scrollbar para el contenido
frame_canvas_gelatos = tk.Frame(frame_gelatos, bg="#E3F2FD")
frame_canvas_gelatos.pack(fill="both", expand=True, padx=20, pady=10)

# Añadir scrollbar vertical con mejor diseño
scrollbar_gelatos = tk.Scrollbar(frame_canvas_gelatos, orient="vertical")
scrollbar_gelatos.pack(side="right", fill="y")

# Crear canvas
canvas_gelatos = tk.Canvas(frame_canvas_gelatos, bg="#E3F2FD", yscrollcommand=scrollbar_gelatos.set, 
                  highlightthickness=0)  # Quitar borde del canvas
canvas_gelatos.pack(side="left", fill="both", expand=True)

# Configurar scrollbar para controlar el canvas
scrollbar_gelatos.config(command=canvas_gelatos.yview)

# Crear frame dentro del canvas para contener el contenido
frame_contenido_gelatos = tk.Frame(canvas_gelatos, bg="#E3F2FD")
canvas_gelatos.create_window((0, 0), window=frame_contenido_gelatos, anchor="nw", width=canvas_gelatos.winfo_width())

# -------------------- SECCIÓN DE NIEVES --------------------
# Título de la sección de Nieves con mejor diseño
titulo_nieves_frame = tk.Frame(frame_contenido_gelatos, bg="#E3F2FD")
titulo_nieves_frame.pack(fill="x", pady=(20, 10))

# Fondo decorativo para el título
titulo_nieves_bg = tk.Frame(titulo_nieves_frame, bg="#BBDEFB", padx=20, pady=10)
titulo_nieves_bg.pack()

tk.Label(titulo_nieves_bg, text="Nieves", 
         font=("Arial", 18, "bold"), bg="#BBDEFB", fg="#0D47A1").pack(side="top")

# Línea decorativa debajo del título
linea_nieves = tk.Frame(titulo_nieves_bg, height=2, bg="#0D47A1")
linea_nieves.pack(fill="x", padx=50, pady=5)

# Frame para las imágenes destacadas de nieves (centrado)
frame_imagenes_nieves_container = tk.Frame(frame_contenido_gelatos, bg="#E3F2FD")
frame_imagenes_nieves_container.pack(fill="x", pady=15)

frame_imagenes_nieves = tk.Frame(frame_imagenes_nieves_container, bg="#E3F2FD")
frame_imagenes_nieves.pack(side="top", pady=15)

# Cargar y mostrar 2 imágenes destacadas para la sección de nieves
try:
    # Puedes cambiar estas rutas por las imágenes que desees mostrar
    rutas_imagenes_nieves = [
        "E:/IMGprogramas/nieve1.jpg",
        "E:/IMGprogramas/nieve2.jpg"
    ]
    
    imagenes_destacadas_nieves = []
    for i, ruta in enumerate(rutas_imagenes_nieves):
        img = Image.open(ruta)
        img = img.resize((150, 150))
        img_tk = ImageTk.PhotoImage(img)
        imagenes_destacadas_nieves.append(img_tk)
        
        frame_img = tk.Frame(frame_imagenes_nieves, bg="#E3F2FD")
        frame_img.pack(side="left", padx=15)
        
        # Imagen con borde redondeado y sombra
        img_frame = tk.Frame(frame_img, bd=2, relief="raised", bg="#1565C0")
        img_frame.pack(padx=5, pady=5)
        
        tk.Label(img_frame, image=img_tk, bg="#E3F2FD").pack(padx=2, pady=2)
    
    # Guardar referencias para evitar que se eliminen
    frame_gelatos.imagenes_destacadas_nieves = imagenes_destacadas_nieves
    
except Exception as e:
    tk.Label(frame_imagenes_nieves, text=f"Error al cargar imágenes: {e}", 
             font=("Arial", 12), bg="#E3F2FD", fg="red").pack()

# Lista de sabores de nieves
sabores_nieves = [
    "Limón", "Tamarindo", "Mango", "Maracuyá", "Fresa", 
    "Naranja", "Piña", "Sandía", "Jamaica", "Coco"
]

# Frame para el menú de sabores de nieves (centrado)
frame_menu_nieves_container = tk.Frame(frame_contenido_gelatos, bg="#E3F2FD")
frame_menu_nieves_container.pack(fill="x", pady=15)

frame_menu_nieves = tk.Frame(frame_menu_nieves_container, bg="#E3F2FD")
frame_menu_nieves.pack(side="top", pady=15)

# Crear una cuadrícula para los sabores de nieves (2 columnas)
for i, sabor in enumerate(sabores_nieves):
    fila = i // 3
    columna = i % 3
    
    # Frame para cada elemento del menú
    frame_item = tk.Frame(frame_menu_nieves, bg="#E3F2FD", bd=0)
    frame_item.grid(row=fila, column=columna, padx=15, pady=10)
    
    # Marco con borde redondeado y sombra
    item_border = tk.Frame(frame_item, bg="#1565C0", bd=1, relief="raised")
    item_border.pack(padx=2, pady=2)
    
    # Frame interno para organizar el contenido verticalmente
    frame_interno = tk.Frame(item_border, bg="#FFFFFF")
    frame_interno.pack(padx=2, pady=2)
    
    # Nombre del sabor con fondo de color
    titulo_sabor = tk.Frame(frame_interno, bg="#BBDEFB", width=180)
    titulo_sabor.pack(fill="x")
    tk.Label(titulo_sabor, text=sabor, font=("Arial", 14, "bold"), 
             bg="#BBDEFB", fg="#0D47A1", width=15).pack(pady=8)
    
    # Precio (ejemplo)
    precio_frame = tk.Frame(frame_interno, bg="#FFFFFF")
    precio_frame.pack(fill="x", pady=5)
    tk.Label(precio_frame, text="$20.00", font=("Arial", 12, "bold"), 
             bg="#FFFFFF", fg="#0D47A1").pack()
    
    # Botón para añadir al carrito con mejor diseño
    btn_frame = tk.Frame(frame_interno, bg="#FFFFFF")
    btn_frame.pack(pady=10, fill="x")
    
    btn_agregar = tk.Button(btn_frame, text="Agregar", bg="#1565C0", fg="white", 
                           font=("Arial", 10, "bold"), relief="flat", width=10,
                           activebackground="#0D47A1", activeforeground="white",
                           cursor="hand2",
                           command=lambda s=sabor: mostrar_opciones_producto(s, 20.00))
    btn_agregar.pack()

# -------------------- SECCIÓN DE HELADOS --------------------
# Título de la sección de Helados con mejor diseño
titulo_helados_frame = tk.Frame(frame_contenido_gelatos, bg="#E3F2FD")
titulo_helados_frame.pack(fill="x", pady=(30, 10))

# Fondo decorativo para el título
titulo_helados_bg = tk.Frame(titulo_helados_frame, bg="#BBDEFB", padx=20, pady=10)
titulo_helados_bg.pack()

tk.Label(titulo_helados_bg, text="Helados", 
         font=("Arial", 18, "bold"), bg="#BBDEFB", fg="#0D47A1").pack(side="top")

# Línea decorativa debajo del título
linea_helados = tk.Frame(titulo_helados_bg, height=2, bg="#0D47A1")
linea_helados.pack(fill="x", padx=50, pady=5)

# Frame para las imágenes destacadas de helados (centrado)
frame_imagenes_helados_container = tk.Frame(frame_contenido_gelatos, bg="#E3F2FD")
frame_imagenes_helados_container.pack(fill="x", pady=15)

frame_imagenes_helados = tk.Frame(frame_imagenes_helados_container, bg="#E3F2FD")
frame_imagenes_helados.pack(side="top", pady=15)

# Cargar y mostrar 2 imágenes destacadas para la sección de helados
try:
    # Puedes cambiar estas rutas por las imágenes que desees mostrar
    rutas_imagenes_helados = [
        "E:/IMGprogramas/helado1.jpg",
        "E:/IMGprogramas/helado2.jpg"
    ]
    
    imagenes_destacadas_helados = []
    for i, ruta in enumerate(rutas_imagenes_helados):
        img = Image.open(ruta)
        img = img.resize((150, 150))
        img_tk = ImageTk.PhotoImage(img)
        imagenes_destacadas_helados.append(img_tk)
        
        frame_img = tk.Frame(frame_imagenes_helados, bg="#E3F2FD")
        frame_img.pack(side="left", padx=15)
        
        # Imagen con borde redondeado y sombra
        img_frame = tk.Frame(frame_img, bd=2, relief="raised", bg="#1565C0")
        img_frame.pack(padx=5, pady=5)
        
        tk.Label(img_frame, image=img_tk, bg="#E3F2FD").pack(padx=2, pady=2)
    
    # Guardar referencias para evitar que se eliminen
    frame_gelatos.imagenes_destacadas_helados = imagenes_destacadas_helados
    
except Exception as e:
    tk.Label(frame_imagenes_helados, text=f"Error al cargar imágenes: {e}", 
             font=("Arial", 12), bg="#E3F2FD", fg="red").pack()

# Lista de sabores de helados
sabores_helados = [
    "Coco", "Chocolate", "Ron con Pasas", "Galleta Oreo", "Pistacho", "Fresa Queso",
    "Mora Queso", "Cereza", "Crema de Maracuyá", "Vainilla", "Chocomenta", "Chococereza"
]

# Frame para el menú de sabores de helados (centrado)
frame_menu_helados_container = tk.Frame(frame_contenido_gelatos, bg="#E3F2FD")
frame_menu_helados_container.pack(fill="x", pady=15)

frame_menu_helados = tk.Frame(frame_menu_helados_container, bg="#E3F2FD")
frame_menu_helados.pack(side="top", pady=15)

# Crear una cuadrícula para los sabores de helados (2 columnas)
for i, sabor in enumerate(sabores_helados):
    fila = i // 3
    columna = i % 3
    
    # Frame para cada elemento del menú
    frame_item = tk.Frame(frame_menu_helados, bg="#E3F2FD", bd=0)
    frame_item.grid(row=fila, column=columna, padx=15, pady=10)
    
    # Marco con borde redondeado y sombra
    item_border = tk.Frame(frame_item, bg="#1565C0", bd=1, relief="raised")
    item_border.pack(padx=2, pady=2)
    
    # Frame interno para organizar el contenido verticalmente
    frame_interno = tk.Frame(item_border, bg="#FFFFFF")
    frame_interno.pack(padx=2, pady=2)
    
    # Nombre del sabor con fondo de color
    titulo_sabor = tk.Frame(frame_interno, bg="#BBDEFB", width=180)
    titulo_sabor.pack(fill="x")
    tk.Label(titulo_sabor, text=sabor, font=("Arial", 14, "bold"), 
             bg="#BBDEFB", fg="#0D47A1", width=15).pack(pady=8)
    
    # Precio (ejemplo)
    precio_frame = tk.Frame(frame_interno, bg="#FFFFFF")
    precio_frame.pack(fill="x", pady=5)
    tk.Label(precio_frame, text="$40.00", font=("Arial", 12, "bold"), 
             bg="#FFFFFF", fg="#0D47A1").pack()
    
    # Botón para añadir al carrito con mejor diseño
    btn_frame = tk.Frame(frame_interno, bg="#FFFFFF")
    btn_frame.pack(pady=10, fill="x")
    
    btn_agregar = tk.Button(btn_frame, text="Agregar", bg="#1565C0", fg="white", 
                           font=("Arial", 10, "bold"), relief="flat", width=10,
                           activebackground="#0D47A1", activeforeground="white",
                           cursor="hand2",
                           command=lambda s=sabor: mostrar_opciones_producto(s, 40.00))
    btn_agregar.pack()

# Configurar el grid para que las columnas tengan el mismo ancho
frame_menu_nieves.columnconfigure(0, weight=1)
frame_menu_nieves.columnconfigure(1, weight=1)
frame_menu_helados.columnconfigure(0, weight=1)
frame_menu_helados.columnconfigure(1, weight=1)

# Actualizar el scrollregion después de añadir el nuevo contenido
frame_contenido_gelatos.update_idletasks()
canvas_gelatos.config(scrollregion=canvas_gelatos.bbox("all"))

# Asegurarse de que el canvas se ajuste cuando cambie de tamaño
def _configure_canvas_gelatos(event):
    canvas_gelatos.configure(scrollregion=canvas_gelatos.bbox("all"))
    canvas_gelatos.itemconfig(canvas_gelatos.find_withtag("all")[0], width=event.width)

canvas_gelatos.bind("<Configure>", _configure_canvas_gelatos)
# ------------------------ Frame Otros Productos ------------------------
# Cambiar el fondo a un gradiente simulado (usando frames con diferentes tonos)
frame_otros.configure(bg="#FCE4EC")  # Fondo rosa claro para otros productos

# Título con mejor diseño
titulo_frame_otros = tk.Frame(frame_otros, bg="#EC407A")  # Rosa medio
titulo_frame_otros.pack(fill="x")

tk.Label(titulo_frame_otros, text="HELADERÍA TWINS", 
         font=("Arial", 22, "bold"), bg="#EC407A", fg="white").pack(pady=(15, 0))
tk.Label(titulo_frame_otros, text="Otros Productos", 
         font=("Arial", 18), bg="#EC407A", fg="white").pack(pady=(0, 15))

# Botón para volver a productos con mejor diseño
btn_volver_frame_otros = tk.Frame(frame_otros, bg="#FCE4EC")
btn_volver_frame_otros.pack(pady=10)

tk.Button(btn_volver_frame_otros, text="← Volver a Productos", 
          command=lambda: mostrar_frame(frame_productos),
          bg="#EC407A", fg="white", font=("Arial", 12, "bold"), 
          relief="flat", padx=15, pady=5).pack()

# Crear un canvas con scrollbar para el contenido
frame_canvas_otros = tk.Frame(frame_otros, bg="#FCE4EC")
frame_canvas_otros.pack(fill="both", expand=True, padx=20, pady=10)

# Añadir scrollbar vertical con mejor diseño
scrollbar_otros = tk.Scrollbar(frame_canvas_otros, orient="vertical")
scrollbar_otros.pack(side="right", fill="y")

# Crear canvas
canvas_otros = tk.Canvas(frame_canvas_otros, bg="#FCE4EC", yscrollcommand=scrollbar_otros.set, 
                  highlightthickness=0)  # Quitar borde del canvas
canvas_otros.pack(side="left", fill="both", expand=True)

# Configurar scrollbar para controlar el canvas
scrollbar_otros.config(command=canvas_otros.yview)

# Crear frame dentro del canvas para contener el contenido
frame_contenido_otros = tk.Frame(canvas_otros, bg="#FCE4EC")
canvas_otros.create_window((0, 0), window=frame_contenido_otros, anchor="nw", width=canvas_otros.winfo_width())

# -------------------- SECCIÓN DE AGUAS --------------------
# Título de la sección de Aguas con mejor diseño
titulo_aguas_frame = tk.Frame(frame_contenido_otros, bg="#FCE4EC")
titulo_aguas_frame.pack(fill="x", pady=(20, 10))

# Fondo decorativo para el título
titulo_aguas_bg = tk.Frame(titulo_aguas_frame, bg="#F8BBD0", padx=20, pady=10)
titulo_aguas_bg.pack()

tk.Label(titulo_aguas_bg, text="Aguas", 
         font=("Arial", 18, "bold"), bg="#F8BBD0", fg="#AD1457").pack(side="top")

# Línea decorativa debajo del título
linea_aguas = tk.Frame(titulo_aguas_bg, height=2, bg="#AD1457")
linea_aguas.pack(fill="x", padx=50, pady=5)

# Frame para las imágenes destacadas de aguas (centrado)
frame_imagenes_aguas_container = tk.Frame(frame_contenido_otros, bg="#FCE4EC")
frame_imagenes_aguas_container.pack(fill="x", pady=15)

frame_imagenes_aguas = tk.Frame(frame_imagenes_aguas_container, bg="#FCE4EC")
frame_imagenes_aguas.pack(side="top", pady=15)

# Cargar y mostrar 3 imágenes destacadas para la sección de aguas
try:
    # Puedes cambiar estas rutas por las imágenes que desees mostrar
    rutas_imagenes_aguas = [
        "E:/IMGprogramas/agua1.jpeg",
        "E:/IMGprogramas/agua2.jpeg",
        "E:/IMGprogramas/agua3.jpeg"
    ]
    
    imagenes_destacadas_aguas = []
    for i, ruta in enumerate(rutas_imagenes_aguas):
        img = Image.open(ruta)
        img = img.resize((150, 150))
        img_tk = ImageTk.PhotoImage(img)
        imagenes_destacadas_aguas.append(img_tk)
        
        frame_img = tk.Frame(frame_imagenes_aguas, bg="#FCE4EC")
        frame_img.pack(side="left", padx=15)
        
        # Imagen con borde redondeado y sombra
        img_frame = tk.Frame(frame_img, bd=2, relief="raised", bg="#EC407A")
        img_frame.pack(padx=5, pady=5)
        
        tk.Label(img_frame, image=img_tk, bg="#FCE4EC").pack(padx=2, pady=2)
    
    # Guardar referencias para evitar que se eliminen
    frame_otros.imagenes_destacadas_aguas = imagenes_destacadas_aguas
    
except Exception as e:
    tk.Label(frame_imagenes_aguas, text=f"Error al cargar imágenes: {e}", 
             font=("Arial", 12), bg="#FCE4EC", fg="red").pack()

# Lista de sabores de aguas
sabores_aguas = [
    "Agua de limón con chía", "Agua de jamaica", "Agua de horchata con fresa",
    "Agua de piña con hierbabuena", "Agua de sandía", "Agua de pepino con limón",
    "Agua de tamarindo", "Agua de mango con maracuyá", "Agua de naranja con zanahoria", "Agua de melón"
]

# Frame para el menú de sabores de aguas (centrado)
frame_menu_aguas_container = tk.Frame(frame_contenido_otros, bg="#FCE4EC")
frame_menu_aguas_container.pack(fill="x", pady=15)

frame_menu_aguas = tk.Frame(frame_menu_aguas_container, bg="#FCE4EC")
frame_menu_aguas.pack(side="top", pady=15)

# Crear una cuadrícula para los sabores de aguas (3 columnas)
for i, sabor in enumerate(sabores_aguas):
    fila = i // 3
    columna = i % 3
    
    # Frame para cada elemento del menú
    frame_item = tk.Frame(frame_menu_aguas, bg="#FCE4EC", bd=0)
    frame_item.grid(row=fila, column=columna, padx=15, pady=10)
    
    # Marco con borde redondeado y sombra
    item_border = tk.Frame(frame_item, bg="#EC407A", bd=1, relief="raised")
    item_border.pack(padx=2, pady=2)
    
    # Frame interno para organizar el contenido verticalmente
    frame_interno = tk.Frame(item_border, bg="#FFFFFF")
    frame_interno.pack(padx=2, pady=2)
    
    # Nombre del sabor con fondo de color
    titulo_sabor = tk.Frame(frame_interno, bg="#F8BBD0", width=180)
    titulo_sabor.pack(fill="x")
    tk.Label(titulo_sabor, text=sabor, font=("Arial", 14, "bold"), 
             bg="#F8BBD0", fg="#AD1457", width=15).pack(pady=8)
    
    # Precio (ejemplo)
    precio_frame = tk.Frame(frame_interno, bg="#FFFFFF")
    precio_frame.pack(fill="x", pady=5)
    tk.Label(precio_frame, text="$25.00", font=("Arial", 12, "bold"), 
             bg="#FFFFFF", fg="#AD1457").pack()
    
    # Botón para añadir al carrito con mejor diseño
    btn_frame = tk.Frame(frame_interno, bg="#FFFFFF")
    btn_frame.pack(pady=10, fill="x")
    
    btn_agregar = tk.Button(btn_frame, text="Agregar", bg="#EC407A", fg="white", 
                           font=("Arial", 10, "bold"), relief="flat", width=10,
                           activebackground="#C2185B", activeforeground="white",
                           cursor="hand2",
                           command=lambda s=sabor: mostrar_opciones_producto(s, 25.00))
    btn_agregar.pack()

# -------------------- SECCIÓN DE POSTRES --------------------
# Título de la sección de Postres con mejor diseño
titulo_postres_frame = tk.Frame(frame_contenido_otros, bg="#FCE4EC")
titulo_postres_frame.pack(fill="x", pady=(30, 10))

# Fondo decorativo para el título
titulo_postres_bg = tk.Frame(titulo_postres_frame, bg="#F8BBD0", padx=20, pady=10)
titulo_postres_bg.pack()

tk.Label(titulo_postres_bg, text="Postres", 
         font=("Arial", 18, "bold"), bg="#F8BBD0", fg="#AD1457").pack(side="top")

# Línea decorativa debajo del título
linea_postres = tk.Frame(titulo_postres_bg, height=2, bg="#AD1457")
linea_postres.pack(fill="x", padx=50, pady=5)

# Frame para las imágenes destacadas de postres (centrado)
frame_imagenes_postres_container = tk.Frame(frame_contenido_otros, bg="#FCE4EC")
frame_imagenes_postres_container.pack(fill="x", pady=15)

frame_imagenes_postres = tk.Frame(frame_imagenes_postres_container, bg="#FCE4EC")
frame_imagenes_postres.pack(side="top", pady=15)

# Cargar y mostrar 3 imágenes destacadas para la sección de postres
try:
    # Puedes cambiar estas rutas por las imágenes que desees mostrar
    rutas_imagenes_postres = [
        "E:/IMGprogramas/postre1.jpeg",
        "E:/IMGprogramas/postre2.jpeg",
        "E:/IMGprogramas/postre3.jpeg"
    ]
    
    imagenes_destacadas_postres = []
    for i, ruta in enumerate(rutas_imagenes_postres):
        img = Image.open(ruta)
        img = img.resize((150, 150))
        img_tk = ImageTk.PhotoImage(img)
        imagenes_destacadas_postres.append(img_tk)
        
        frame_img = tk.Frame(frame_imagenes_postres, bg="#FCE4EC")
        frame_img.pack(side="left", padx=15)
        
        # Imagen con borde redondeado y sombra
        img_frame = tk.Frame(frame_img, bd=2, relief="raised", bg="#EC407A")
        img_frame.pack(padx=5, pady=5)
        
        tk.Label(img_frame, image=img_tk, bg="#FCE4EC").pack(padx=2, pady=2)
    
    # Guardar referencias para evitar que se eliminen
    frame_otros.imagenes_destacadas_postres = imagenes_destacadas_postres
    
except Exception as e:
    tk.Label(frame_imagenes_postres, text=f"Error al cargar imágenes: {e}", 
             font=("Arial", 12), bg="#FCE4EC", fg="red").pack()

# Lista de postres
postres = [
    "Malteada", "Banana Split", "Chocobanana", 
    "Chamoyada", "Flanes", "Gelatinas"
]

# Frame para el menú de postres (centrado)
frame_menu_postres_container = tk.Frame(frame_contenido_otros, bg="#FCE4EC")
frame_menu_postres_container.pack(fill="x", pady=15)

frame_menu_postres = tk.Frame(frame_menu_postres_container, bg="#FCE4EC")
frame_menu_postres.pack(side="top", pady=15)

# Crear una cuadrícula para los postres (3 columnas)
for i, postre in enumerate(postres):
    fila = i // 3
    columna = i % 3
    
    # Frame para cada elemento del menú
    frame_item = tk.Frame(frame_menu_postres, bg="#FCE4EC", bd=0)
    frame_item.grid(row=fila, column=columna, padx=15, pady=10)
    
    # Marco con borde redondeado y sombra
    item_border = tk.Frame(frame_item, bg="#EC407A", bd=1, relief="raised")
    item_border.pack(padx=2, pady=2)
    
    # Frame interno para organizar el contenido verticalmente
    frame_interno = tk.Frame(item_border, bg="#FFFFFF")
    frame_interno.pack(padx=2, pady=2)
    
    # Nombre del postre con fondo de color
    titulo_sabor = tk.Frame(frame_interno, bg="#F8BBD0", width=180)
    titulo_sabor.pack(fill="x")
    tk.Label(titulo_sabor, text=postre, font=("Arial", 14, "bold"), 
             bg="#F8BBD0", fg="#AD1457", width=15).pack(pady=8)
    
    # Precio (ejemplo)
    precio_frame = tk.Frame(frame_interno, bg="#FFFFFF")
    precio_frame.pack(fill="x", pady=5)
    tk.Label(precio_frame, text="$45.00", font=("Arial", 12, "bold"), 
             bg="#FFFFFF", fg="#AD1457").pack()
    
    # Botón para añadir al carrito con mejor diseño
    btn_frame = tk.Frame(frame_interno, bg="#FFFFFF")
    btn_frame.pack(pady=10, fill="x")
    
    btn_agregar = tk.Button(btn_frame, text="Agregar", bg="#EC407A", fg="white", 
                           font=("Arial", 10, "bold"), relief="flat", width=10,
                           activebackground="#C2185B", activeforeground="white",
                           cursor="hand2",
                           command=lambda s=postre: mostrar_opciones_producto(s, 45.00))
    btn_agregar.pack()

# Configurar el grid para que las columnas tengan el mismo ancho
frame_menu_aguas.columnconfigure(0, weight=1)
frame_menu_aguas.columnconfigure(1, weight=1)
frame_menu_aguas.columnconfigure(2, weight=1)
frame_menu_postres.columnconfigure(0, weight=1)
frame_menu_postres.columnconfigure(1, weight=1)
frame_menu_postres.columnconfigure(2, weight=1)

# Actualizar el scrollregion después de añadir el nuevo contenido
frame_contenido_otros.update_idletasks()
canvas_otros.config(scrollregion=canvas_otros.bbox("all"))

# Asegurarse de que el canvas se ajuste cuando cambie de tamaño
def _configure_canvas_otros(event):
    canvas_otros.configure(scrollregion=canvas_otros.bbox("all"))
    canvas_otros.itemconfig(canvas_otros.find_withtag("all")[0], width=event.width)

canvas_otros.bind("<Configure>", _configure_canvas_otros)


# Footer
frame_footer = tk.Frame(ventana, bg="#B3E5FC")
frame_footer.grid(row=2, column=0, sticky="ew", pady=10)
tk.Label(frame_footer, text="Derechos Reservados\nHeladería Twins ®", font=("Arial", 10, "bold"), bg="#B3E5FC", fg="#0277BD").pack(side="left", padx=20)

# Redes Sociales
frame_redes = tk.Frame(frame_footer, bg="#B3E5FC")
frame_redes.pack(side="right", padx=20)

# Instagram
icono_instagram = Image.open("E:/IMGprogramas/instagram.png").resize((20, 20))
icono_instagram = ImageTk.PhotoImage(icono_instagram)
frame_ig = tk.Frame(frame_redes, bg="#B3E5FC")
frame_ig.pack()
tk.Label(frame_ig, image=icono_instagram, bg="#B3E5FC").pack(side="left")

etiqueta_ig = tk.Label(frame_ig, text="Instagram Ice_twins", font=("Arial", 10, "underline"), fg="#0277BD", bg="#B3E5FC", cursor="hand2")
etiqueta_ig.pack(side="left", padx=5)
etiqueta_ig.bind("<Button-1>", lambda e: abrir_link("https://www.instagram.com/heladeria_twins_?igsh=MTlsaWg5dXc5MnkwNQ=="))

# TikTok
icono_tiktok = Image.open("E:/IMGprogramas/tiktok.png").resize((20, 20))
icono_tiktok = ImageTk.PhotoImage(icono_tiktok)
frame_tt = tk.Frame(frame_redes, bg="#B3E5FC")
frame_tt.pack()
tk.Label(frame_tt, image=icono_tiktok, bg="#B3E5FC").pack(side="left")

etiqueta_tt = tk.Label(frame_tt, text="TikTok Ice_twins", font=("Arial", 10, "underline"), fg="#0277BD", bg="#B3E5FC", cursor="hand2")
etiqueta_tt.pack(side="left", padx=5)
etiqueta_tt.bind("<Button-1>", lambda e: abrir_link("https://www.tiktok.com/@heladeria.twins?_t=ZS-8w8RUvlYRe5&_r=1"))

# Inicio de la aplicación
correo_guardado = cargar_sesion()
if correo_guardado:
    sesion_iniciada = True
    activar_botones()
    cargar_carrito_desde_firebase()  # Asegúrate de cargar el carrito al iniciar
    mostrar_frame(frame_inicio)
else:
    mostrar_frame(frame_bienvenida)

reproducir_musica()

def al_cerrar_ventana():

    if sesion_iniciada:
        guardar_carrito_en_firebase()
    pygame.mixer.music.stop()  # Detener la música
    ventana.destroy()

# Configurar el manejador del evento de cierre
ventana.protocol("WM_DELETE_WINDOW", al_cerrar_ventana)

ventana.mainloop()
cap.release()
