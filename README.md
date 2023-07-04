# ModeloVectorial
 Proyecto IB, Recuperación de la Información

# CÓMO EMPEZAR
1. Desde un Terminal abierto en la dirección escogida, clonar el repositorio con el siguiente comando:
   > git clone https://github.com/Mayra025/Rec_ModeloVectorial.git

2. Para descargar todas las librerías necesarias para iniciar el proyecto use el comando:
   > npm install
   
   2.1 El proyecto usa como base Python, puede necesitar crear el entorno e instalar flask manualmente:
      > python3 -m venv app-env
      > app-env\Scripts\activate
      > pip install flask
      y continuar en 4.

3. Ahora deberá iniciar el entorno de python (windows) con el siguiente comando:
   > app-env\Scripts\activate

4. Luego deberá dirigirse a la nueva carpeta generada con el comando:
   > cd recup-appy

5. Para iniciar el servidor en modo desarrollador use el siguiente comando:
   > py app.py
