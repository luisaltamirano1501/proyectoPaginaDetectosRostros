#librerias flask
from flask import Flask, render_template, request, url_for, redirect, session, flash, Response
from markupsafe import escape
from datetime import timedelta # libreria que crea lapsos de tiempo

## librerias de pymongoDB
from pymongo import MongoClient, InsertOne, UpdateOne, DeleteOne
from pymongo.errors import BulkWriteError
from bson.objectid import ObjectId
import pandas as pd
from bson.son import SON
from pandas import ExcelWriter
from bson import json_util

#librerias funcion camara
import cv2
import time
import datetime


#dirección
MOMGO_URI= "mongodb+srv://luis_rayh:jji3YFzkcQO2zyKh@pruebamongo.epav23g.mongodb.net/?retryWrites=true&w=majority"

# creación del cliente en MongoDB
client = MongoClient(MOMGO_URI)

#base de datos
db = client["rostros"]

#coleccion
collection = db["rostros_detector"]

# Inicializar el clasificador de cascada de Haar
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


#función dectector de rostro  
def detect_faces(frame):
    # Convertir la imagen a escala de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detectar los rostros en la imagen
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Dibujar un rectángulo alrededor de cada rostro detectado
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    cantidadPersonas = len(faces)
    fecha = datetime.date.today()
    hora = datetime.datetime.now().strftime("%H:%M:%S")
    
    return frame,cantidadPersonas,fecha,hora
           
        


    #return frame,cantidadPersonas,fecha,hora

def generate_video():
    # Iniciar la cámara
    cap = cv2.VideoCapture(0)

    tiempo_previo = time.time()
    while True:
        # Leer un frame de la cámara
        ret, frame = cap.read()

        # Detectar los rostros en el frame
        frame,cantidadPersonas,fecha,hora = detect_faces(frame)

        # Codificar el frame como JPEG
        ret, buffer = cv2.imencode('.jpg', frame)

        # Convertir el buffer codificado a bytes
        frame_bytes = buffer.tobytes()

        # Generar un frame de video
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

         # cada 5 segundos verifica los datos necesarios para la base da datos
        tiempo_actual = time.time()
        if tiempo_actual - tiempo_previo >= 5:
            tiempo_previo = tiempo_previo + 5  # Actualiza el tiempo previo para el siguiente intervalo de 5 segundos
            collection.insert_one({"fecha":str(fecha),"hora":str(hora),"CantidadPersonas":cantidadPersonas})
    
    

def get_info():
    while True:
        registros = collection.find().sort('_id', -1).limit(9)

        return registros

app = Flask(__name__, static_url_path='/static')# se define la aplicación

#funcion para obtener camara 
@app.route('/video_feed')
def video_feed():
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/',methods=["GET","POST"]) # ruta por defecto de la app web
def index():
    registros = get_info()

    return render_template("index.html",registros=registros)

if __name__=='__main__': # verifica si esta la aplicación
    app.run(port=3000, debug=True)

            





    