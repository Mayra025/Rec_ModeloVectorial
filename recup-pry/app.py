from flask import Flask, render_template, request, jsonify
import math
import time

app = Flask(__name__)

COMMON_WORDS = {'a', 'al', 'con', 'de', 'del', 'el', 'en', 'es', 'estan', 'esta', 'la', 'los', 'las', 'su', 'un', 'una', 'unos', 'unas', 'tiene', 'va', 'y'}
consulta = ""
vocabulario = set()  # Variable global para el vocabulario
documentos = []  # Variable global para los documentos
qtf_nuevo = []  # Definición global de la variable qtf_nuevo
max_doc_id_r = []

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

#################
def calcular_frecuencia_terminos(documentos, vocabulario):
    frecuencias = []
    print("\n Frecuencias")
    for documento in documentos:
        frecuencia_documento = [documento.count(palabra) for palabra in vocabulario]
        print("d= ",frecuencia_documento,"\n")
        frecuencias.append(frecuencia_documento)
    return frecuencias

def calcular_valor_idf(frecuencias_documentos, frecuencias_consulta):
    num_documentos = len(frecuencias_documentos)
    idf = []

    for i in range(len(frecuencias_consulta)):
        # Contar cuántos documentos contienen la palabra en los documentos
        num_apariciones_documentos = sum(1 for frecuencia in frecuencias_documentos if frecuencia[i] > 0)
        # Calcular el IDF para la palabra en la consulta
        idf_valor = math.log10((num_documentos) / (num_apariciones_documentos))
        idf.append(idf_valor)
    return idf

def calcular_pesos_tf_idf(frecuencias, idf):
    pesos = []
    print("\n\n Pesos tf.idf")
    for frecuencia_documento in frecuencias:
        peso_documento = [tf * idf_valor for tf, idf_valor in zip(frecuencia_documento, idf)]
        print("d=",peso_documento)
        pesos.append(peso_documento)
    return pesos

def calcular_peso_tf_idf_consulta(consulta, idf, vocabulario):
    frecuencia_consulta = [consulta.count(palabra) for palabra in vocabulario]
    peso_consulta = [tf * idf_valor for tf, idf_valor in zip(frecuencia_consulta, idf)]
    print("c= ",peso_consulta)
    return peso_consulta

def calcular_vectores_documentos(frecuencias, pesos_tf_idf):
    vectores = []
    for frecuencia_documento, peso_documento in zip(frecuencias, pesos_tf_idf):
        vector_documento = [tf * peso for tf, peso in zip(frecuencia_documento, peso_documento)]
        vectores.append(vector_documento)
    return vectores

def calcular_vectores_normalizados(pesos_tf_idf_documentos, peso_tf_idf_consulta):
    norma_consulta = calcular_norma(peso_tf_idf_consulta)
    print("\n\n Vectores normalizados")
    vectores_normalizados_documentos = []
    for vector_documento in pesos_tf_idf_documentos:
        norma_documento = calcular_norma(vector_documento)
        vector_normalizado = [componente / norma_documento for componente in vector_documento]
        print("d=",vector_normalizado)
        vectores_normalizados_documentos.append(vector_normalizado)
    
    if norma_consulta != 0:
        vector_normalizado_consulta = [componente / norma_consulta for componente in peso_tf_idf_consulta]
    else:
        vector_normalizado_consulta = peso_tf_idf_consulta
    print("c=",vector_normalizado_consulta)

    return vectores_normalizados_documentos, vector_normalizado_consulta


def realimentar_consulta_relevante(relevantes, no_relevantes, vector_consulta_original, documentos, vocabulario):
    alpha = 1
    beta = 0.75
    gamma = 0.25
    
    # Calcula el término de la sumatoria de Relevantes (β/R.∑d∈Rtf)
    suma_relevantes = [0] * len(vector_consulta_original)
    for doc_id in relevantes:
        vector_doc_relevante = documentos[doc_id]  # Usar el vector normalizado del documento
        suma_relevantes = [a + (beta / len(relevantes)) * b for a, b in zip(suma_relevantes, vector_doc_relevante)]
    
    # Calcula el término de la sumatoria de No Relevantes (−γ.∑d∈Ntf)
    suma_no_relevantes = [0] * len(vector_consulta_original)
    for doc_id in no_relevantes:
        vector_doc_no_relevante = documentos[doc_id]  # Usar el vector normalizado del documento
        suma_no_relevantes = [a - (gamma / len(no_relevantes)) * b for a, b in zip(suma_no_relevantes, vector_doc_no_relevante)]
    
    # Calcula el nuevo vector de consulta
    qtf_nuevo = [alpha * term + beta_term + gamma_term for term, beta_term, gamma_term in zip(vector_consulta_original, suma_relevantes, suma_no_relevantes)]
    
    # Elimina valores negativos del nuevo vector consulta
    qtf_nuevo = [max(0, term) for term in qtf_nuevo]

    # Convierte el conjunto vocabulario en una lista
    vocabulario_lista = list(vocabulario)

    # Luego, utiliza vocabulario_lista en lugar de vocabulario en tu función
    terminos_consulta_nueva = [vocabulario_lista[i] for i, term in enumerate(qtf_nuevo) if term > 0]
    print("\n\n Después de calcular Rocchio:",terminos_consulta_nueva)
    print("\nq'=",qtf_nuevo)

    return qtf_nuevo, terminos_consulta_nueva


def calcular_similitud_consulta_realimentada(vectores_documentos, consulta_realimentada, vocabulario):
    tabla_similitud_nueva = []
    norma_consulta = calcular_norma(consulta_realimentada)
    print("\n|q'|= ", norma_consulta,"\n")
    for i, vector_documento in enumerate(vectores_documentos):
        producto = calcular_producto_interno(vector_documento, consulta_realimentada)
        norma_documento = calcular_norma(vector_documento)
        norma_producto = norma_documento * norma_consulta
        
        if norma_producto != 0:
            similitud = producto / norma_producto
        else:
            similitud = 0
        print (" d",i+1,"= ",vector_documento, "\n \t|d|=",norma_documento)
        print ("\tq*d =",producto)
        print ("\t|q*d|=", norma_producto)
        print("\tsim(q,d)= ",similitud,"\n")
        tabla_similitud_nueva.append((i, producto, norma_documento, norma_consulta, similitud))
    
    return tabla_similitud_nueva


@app.route('/realimentar', methods=['POST'])

def realimentar_consulta():
    start_time = time.time()

    relevantes = request.json.get('relevantes', [])
    no_relevantes = request.json.get('no_relevantes', [])
    
    print("\n---------------------------------------------- CONSULTA REALIMENTADA ----------------------------------------------")
    print("\nrelevantes:", relevantes)
    print("no_relevantes:", no_relevantes)

    # Acceder a la consulta original desde la variable global
    vector_consulta_original = consulta_original

    # Calcular las frecuencias de términos para los documentos y la consulta
    frecuencias_documentos = calcular_frecuencia_terminos(documentos, vocabulario)
    frecuencias_consulta = vector_consulta_original  ##??
    print("c=",frecuencias_consulta)

    # Calcular el valor IDF
    idf = calcular_valor_idf(frecuencias_documentos, frecuencias_consulta)
    
    # Calcular los pesos TF-IDF para los documentos y la consulta
    pesos_tf_idf_documentos = calcular_pesos_tf_idf(frecuencias_documentos, idf)
    peso_tf_idf_consulta = calcular_peso_tf_idf_consulta(consulta, idf, vocabulario)

    # Calcular los vectores normalizados de los documentos y la consulta
    vectores_normalizados_documentos, vector_normalizado_consulta = calcular_vectores_normalizados(pesos_tf_idf_documentos, peso_tf_idf_consulta)
   
     # # Obtener el nuevo vector consulta con Rocchio
    qtf_nuevo,terminos_qtf_nuevo = realimentar_consulta_relevante(relevantes, no_relevantes, vector_normalizado_consulta, vectores_normalizados_documentos, vocabulario)
    
    # # Calcular la tabla de similitud con la consulta realimentada
    tabla_similitud_nueva = calcular_similitud_consulta_realimentada(vectores_normalizados_documentos, qtf_nuevo, vocabulario)

    # Encontrar el documento de mayor similitud
    max_similitud = 0
    max_doc_id_r=0
    for doc_id,pi,nd,nqm, similitud in tabla_similitud_nueva:
            if similitud > max_similitud:
                max_similitud = similitud
                max_doc_id_r = [doc_id+1]
            elif similitud == max_similitud:
                max_doc_id_r.append(doc_id+1)
    print("\nEl documento con mayor similitud es d", max_doc_id_r)
    qtf_nuevo=[] #??
    #Tiempo
    end_time = time.time()
    execution_time = end_time - start_time
    print("Tiempo de ejecución: {:.6f} segundos".format(execution_time),"\n\n")

    return jsonify({'tabla_similitud_nueva': tabla_similitud_nueva, 'max_doc_id_r': max_doc_id_r, 'terminos_qtf_nuevo': terminos_qtf_nuevo})

@app.route('/reiniciar', methods=['POST'])
def reiniciar():
    global vocabulario
    global documentos
    global consulta_original
    global consulta

    # Restablece las variables globales a su estado inicial
    vocabulario = []
    documentos = []
    consulta_original = []
    consulta = []

    return jsonify({'mensaje': 'Datos reiniciados en el server'})


@app.route('/', methods=['GET', 'POST'])
def index():
    global vocabulario
    global documentos
    
    global consulta_original    
    global consulta

    if request.method == 'POST':
        start_time = time.time()
        num_documentos = int(request.form.get("num_documentos", 0))
        # documentos = [eliminar_palabras_comunes(request.form['documento{}'.format(i)]) for i in range(num_documentos)]
        documentos = []
        
        for i in range(num_documentos):
            documento_content = request.form.get('contenido_archivo{}'.format(i), "")
            documentos.append(eliminar_palabras_comunes(documento_content))

        consulta = eliminar_palabras_comunes(request.form['consulta'])
        vocabulario = crear_vocabulario(documentos)
        vector_consulta = [consulta.count(palabra) for palabra in vocabulario]
        print("\n---------------------------------------------- CONSULTA ORIGINAL ----------------------------------------------")
        print("\nV:", vocabulario,"\n")
        print("D:", documentos,"\n")
        print("q:", consulta,"  ->", vector_consulta)

        tabla_similitud = calcular_producto_interno_normalizado(documentos, vector_consulta, vocabulario)

       # Encontrar el documento de mayor similitud
        max_similitud = 0
        max_doc_id = []
        for doc_id,pi,nd,nqm, similitud in tabla_similitud:
            if similitud > max_similitud:
                max_similitud = similitud
                max_doc_id = [doc_id+1]
            elif similitud == max_similitud:
                max_doc_id.append(doc_id+1)
        print("\nEl documento con mayor similitud es d", max_doc_id)
        consulta_original = vector_consulta 
        
        #Tiempo
        end_time = time.time()
        execution_time = end_time - start_time
        print("Tiempo de ejecución: {:.6f} segundos".format(execution_time),"\n\n")

        return render_template('index.html', tabla_similitud=tabla_similitud, vocabulario=vocabulario, documentos=documentos, consulta=consulta, max_doc_id=max_doc_id)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

#OBS: NO recargar la pagina, los datos previos se guardan .. no generá error en un nuevo cálculo pero puede ser confuso para el usuario
#la tabla de reconsulta se va aumentado si se Realimenta de nuevo