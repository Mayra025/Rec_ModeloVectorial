import math
import time
from flask import Flask, render_template, request

app = Flask(__name__)

COMMON_WORDS = {'a', 'al', 'con', 'de', 'del', 'el', 'en', 'es', 'estan', 'esta', 'la', 'los', 'las', 'su', 'un', 'una', 'unos', 'unas', 'tiene', 'va', 'y'}

def eliminar_palabras_comunes(documento):
    palabras = documento.lower().split()
    palabras_filtradas = [palabra for palabra in palabras if palabra not in COMMON_WORDS]
    documento_filtrado = " ".join(palabras_filtradas)
    return documento_filtrado


def crear_vocabulario(documentos):
    vocabulario = set()
    for documento in documentos:
        palabras = documento.lower().split()
        vocabulario.update(palabras)
    return vocabulario

def calcular_producto_interno(vector1,vector2):
    if len(vector1) != len(vector2):
        raise ValueError("Los vectores deben tener la misma longitud.")
    producto = sum(a * b for a, b in zip(vector1, vector2))
    return producto

def calcular_norma(vector):
    norma = math.sqrt(sum(a ** 2 for a in vector))
    return norma

def calcular_producto_interno_normalizado(documentos, consulta, vocabulario):
    tabla = []
    norma_consulta = calcular_norma(consulta)
    print("|q|= ", norma_consulta,"\n")
    for i, documento in enumerate(documentos):
        palabras_documento = documento.lower().split() #separar palabras
        vector_documento = [palabras_documento.count(palabra) for palabra in vocabulario] #vector del doc
        producto = calcular_producto_interno(vector_documento, consulta) #q*d
        norma_documento = calcular_norma(vector_documento)
        norma_producto = norma_consulta * norma_documento #|q|*|d|
        if norma_producto != 0:
            similitud = producto / norma_producto
        else:
            similitud = 0
        print (" d",i+1,"= ",vector_documento, "; |d|=",norma_documento)
        print ("\tq*d =",producto)
        print ("\t|q*d|=", norma_producto)
        print("\tsim(q,d)= ",similitud,"\n")
        tabla.append((i, producto, norma_documento,norma_consulta, similitud))
    return tabla

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_time = time.time()
        num_documentos = int(request.form.get("num_documentos", 0))
        documentos = [eliminar_palabras_comunes(request.form['documento{}'.format(i)]) for i in range(num_documentos)]
        consulta = eliminar_palabras_comunes(request.form['consulta'])
        vocabulario = crear_vocabulario(documentos)
        vector_consulta = [consulta.count(palabra) for palabra in vocabulario]
        print("\nV:", vocabulario,"\n")
        print("D:", documentos,"\n")
        print("q:", consulta,"  ->", vector_consulta)

        tabla_similitud = calcular_producto_interno_normalizado(documentos, vector_consulta, vocabulario)

       # Encontrar el documento de mayor similitud
        max_similitud = 0
        max_doc_id = []
        for doc_id, pi,nd,nq,similitud in tabla_similitud:
            if similitud > max_similitud:
                max_similitud = similitud
                max_doc_id = [doc_id+1]
            elif similitud == max_similitud:
                max_doc_id.append(doc_id+1)
        print("\nEl documento con mayor similitud es d", max_doc_id)
        #Tiempo
        end_time = time.time()
        execution_time = end_time - start_time
        print("Tiempo de ejecución: {:.6f} segundos".format(execution_time),"\n\n")
        return render_template('index.html', tabla_similitud=tabla_similitud,vocabulario=vocabulario,documentos=documentos,consulta=consulta,max_doc_id=max_doc_id)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
