from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from .rutas import *
from .functions import *
from .validators import *
from .opciones_proyectos import * 
from .posibles_preguntas import obtener_pregunta
from urllib.parse import urlparse

# Función correspondiente al flujo del chatbot para cotizar departamentos y casas
def flujo_dptos_casas(request):
    chat_session_id = request.GET.get('chatSessionId', '')
    
    if not chat_session_id:
        return JsonResponse({'error': 'No chat session ID provided'}, status=400)

    session_key = f"chat_data_{chat_session_id}"
    session_data = request.session.get(session_key, {'state': 'inicio', 'context': []})

    url_cliente = request.GET.get('url', '')

    user_message = request.GET.get('message', '').strip().lower()

    # Bandera para verificar si es una segunda cotización
    cotizacion_subsecuente = session_data.get('cotizacion_subsecuente', False)

    # Lista de dominios donde no se debe mostrar la opción de "reclamo"
    dominios_sin_reclamo = [
        "desarrollos.want.cl",
        "vimac.cl",
        "www.vimac.cl",
        "localhost"
        # Añadir más dominios según sea necesario
    ]

    # Extraer el dominio de la URL para la comparación
    parsed_url = urlparse(url_cliente)
    dominio_actual = parsed_url.hostname

    # Determinar si el dominio actual está en la lista de dominios sin reclamo
    mostrar_opcion_reclamo = dominio_actual not in dominios_sin_reclamo

    precio_a_texto = {
        'menos_1800': 'Menos de 1800 UF',
        'entre_1800_2499': 'Entre 1800 y 2499 UF',
        'entre_2500_3999': 'Entre 2500 y 3999 UF',
        'entre_4000_6999': 'Entre 4000 y 6999 UF',
        'mas_7000': 'Más de 7000 UF'
    }

    # Parsea el rango de precio a texto
    convertir_rango_precio_a_texto = next((precio_a_texto[item['rango_precio']] for item in session_data['context'] if 'rango_precio' in item), "Desconocido")

    if 'context' not in session_data:
        session_data['context'] = []
        
    response = ''
    options = []

    from_reclamo = session_data.get('from_reclamo', False)
    from_cotizacion = session_data.get('from_cotizacion', False)

    session_data['from_reclamo'] = False
    session_data['from_cotizacion'] = False

    if user_message == 'inicio':
        session_data.clear()
        session_data['state'] = 'inicio'
        session_data['context'] = []
        session_data['ha_dado_telefono'] = False
        
        ruta_archivo_configuracion = seleccionar_ruta_configuracion(url_cliente)
        configuracion = leer_archivo_configuracion(ruta_archivo=ruta_archivo_configuracion)
        respuesta_inicial = configuracion.get('RESPUESTA_INICIAL', 'Hola, soy un Asistente Virtual, ¿En qué puedo ayudarte?')
        
        if from_reclamo or from_cotizacion:
            response = 'Hola nuevamente, ¿En qué puedo ayudarte esta vez?'
        else:
            response = respuesta_inicial
        
        session_data['state'] = 'inicio'
        # Definir opciones de respuesta según la URL
        options = [{'text': 'Necesito ayuda para cotizar', 'value': 'cotizar'}]
        if mostrar_opcion_reclamo:
            options.append({'text': 'Deseo realizar un reclamo', 'value': 'reclamo'})

    elif session_data['state'] == 'inicio':
        if 'cotizar' in user_message:
            # Preguntar por la comuna
            session_data['state'] = 'solicitando_comuna'
            response = '¿En cuál comuna deseas cotizar?'
            options = obtener_opciones_proyectos_por_comuna(url_cliente)
            if not options:
                response = 'Lo siento, no tenemos proyectos disponibles en esta URL.'
            else:
                print(f"Opciones obtenidas: {options}")  # Depuración para revisar las opciones obtenidas
        elif 'reclamo' in user_message:
            ruta_archivo_configuracion = seleccionar_ruta_configuracion(url_cliente)
            configuracion = leer_archivo_configuracion(ruta_archivo=ruta_archivo_configuracion)
            session_data['state'] = 'inicio'
            session_data['from_reclamo'] = True
            response = configuracion.get('RESPUESTA_RECLAMO', 'No se encontró una respuesta para reclamos.')
            options = [
                {'text': 'Continuar', 'value': 'inicio'}
            ]

    elif session_data['state'] == 'solicitando_comuna':
        comuna_seleccionada = user_message.lower()  # Convierte la entrada del usuario a minúsculas para hacer la búsqueda
        opciones_comunas = obtener_opciones_proyectos_por_comuna(url_cliente)
        
        # Busca la comuna ingresada por el usuario en las opciones sin modificar el formato original
        comuna_exacta = None
        for opcion in opciones_comunas:
            if opcion['value'] == comuna_seleccionada:
                comuna_exacta = opcion['text']  # Guarda la comuna con el formato exacto
        
        if comuna_exacta:
            proyectos = obtener_opciones_proyectos_por_comuna(url_cliente, comuna=comuna_exacta)
            if proyectos:
                session_data['state'] = 'seleccionando_proyecto'
                response = f'Tenemos los siguientes proyectos disponibles en {comuna_exacta}, Por favor selecciona en cual de ellos estás interesado.'
                options = proyectos
            else:
                response = f'Lo siento, no tenemos proyectos en la comuna {comuna_exacta}. ¿Puedes intentar con otra?'
                options = obtener_opciones_proyectos_por_comuna(url_cliente)
        else:
            response = 'Lo siento, no reconocemos esa comuna. ¿Puedes intentar con otra?'
            options = obtener_opciones_proyectos_por_comuna(url_cliente)
            
    elif session_data['state'] == 'seleccionando_proyecto':
        proyecto_seleccionado = user_message  # Actualiza el proyecto seleccionado con el mensaje del usuario
        print(f"Proyecto seleccionado: {proyecto_seleccionado}")  # Depuración

        ruta_archivo_configuracion = seleccionar_ruta_configuracion(url_cliente, proyecto_seleccionado)
        print(f"Ruta archivo configuración: {ruta_archivo_configuracion}")  # Depuración

        parametros_archivo_configuracion = leer_archivo_configuracion(ruta_archivo=ruta_archivo_configuracion)  # Cargar los parámetros de configuración del archivo
        print(f"Parámetros archivo configuración cargados: {parametros_archivo_configuracion}")  # Depuración

        # Actualizar el proyecto y la configuración en el contexto
        session_data['context'].append({'config': parametros_archivo_configuracion, 'proyecto': proyecto_seleccionado})

        # Obtener los productos activos del proyecto seleccionado
        productos = obtener_productos_activos(url_cliente, proyecto_seleccionado)

        if productos:
            # Limpiar cualquier producto anterior en el contexto y agregar los nuevos productos
            session_data['context'] = [item for item in session_data['context'] if 'todos_los_productos' not in item]
            session_data['context'].append({'todos_los_productos': productos})

            # Filtrar las opciones de rango de precio basadas en los productos disponibles
            precios_disponibles = set()
            for producto in productos:
                precio = producto.get('PrecioTotalUF', None)
                if precio is not None:
                    precios_disponibles.add(float(precio))

            # Crear las opciones de precios basadas en los rangos disponibles
            opciones_precio = []
            if any(precio < 1800 for precio in precios_disponibles):
                opciones_precio.append({'text': 'Menos de 1800 UF', 'value': 'menos_1800'})
            if any(1800 <= precio < 2500 for precio in precios_disponibles):
                opciones_precio.append({'text': 'Entre 1800 y 2499 UF', 'value': 'entre_1800_2499'})
            if any(2500 <= precio < 4000 for precio in precios_disponibles):
                opciones_precio.append({'text': 'Entre 2500 y 3999 UF', 'value': 'entre_2500_3999'})
            if any(4000 <= precio < 7000 for precio in precios_disponibles):
                opciones_precio.append({'text': 'Entre 4000 y 6999 UF', 'value': 'entre_4000_6999'})
            if any(precio >= 7000 for precio in precios_disponibles):
                opciones_precio.append({'text': 'Más de 7000 UF', 'value': 'mas_7000'})

            # Guardar las opciones filtradas en el contexto
            session_data['context'].append({
                'opciones_precio': opciones_precio,
                'opciones_dormitorios': sorted(set(int(producto['Dormitorios']) for producto in productos if producto['Dormitorios'] not in [None, '', ' '])),
                'opciones_banos': sorted(set(int(producto['Banos']) for producto in productos if producto['Banos'] not in [None, '', ' ']))
            })

            # Extraer información del usuario (nombre y correo) si ya fue proporcionada
            nombre_completo = next((item['nombre_completo'] for item in session_data['context'] if 'nombre_completo' in item), None)
            correo = next((item['correo'] for item in session_data['context'] if 'correo' in item), None)

            # Extraer automáticamente el tipo de inmueble y guardarlo en el contexto
            tipo_inmueble = productos[0]['TipoInmueble'] 
            session_data['context'] = [item for item in session_data['context'] if 'tipo_inmueble' not in item]  # Limpiar tipo_inmueble anterior
            session_data['context'].append({'tipo_inmueble': tipo_inmueble})

            # Revisar el flujo dependiendo de si el usuario ya ha proporcionado nombre y correo
            if not nombre_completo:
                session_data['state'] = 'solicitando_nombre'
                response = obtener_pregunta('nombre')
                options = []  # No hay opciones aquí, solo se pide el nombre
            elif not correo:
                session_data['state'] = 'solicitando_correo'
                primer_nombre = extraer_primer_nombre(nombre_completo) if nombre_completo else "cliente"
                response = obtener_pregunta('correo', primer_nombre=primer_nombre)
                options = []  # No hay opciones aquí, solo se pide el correo
            else:
                # Si ya se tiene el nombre y correo, preguntar por el rango de precios usando las opciones filtradas
                session_data['state'] = 'solicitando_rango_precio'
                primer_nombre = extraer_primer_nombre(nombre_completo) if nombre_completo else "cliente"
                response = obtener_pregunta('rango_precios')
                options = opciones_precio  # Mostrar las opciones de precios filtradas en rangos
        else:
            # Si no se encuentran productos disponibles, permitir al usuario seleccionar otro proyecto o volver al inicio
            response = 'Lo siento, no encontramos productos disponibles para el proyecto seleccionado. ¿Deseas intentar con otro proyecto?'
            session_data['state'] = 'inicio'
            options = [
                {'text': 'Sí, intentar con otro proyecto', 'value': 'cotizar'},
                {'text': 'No, gracias', 'value': 'inicio'}
            ]
            
    elif session_data['state'] == 'solicitando_nombre':
        if es_nombre_potencial(user_message):
            prompt_validar_nombre = f"El usuario dijo: '{user_message}'. Teniendo en cuenta que el usuario puede incluir agradecimientos o frases adicionales antes y/o después de dar su nombre (recordar que es opcional), el usuario en la frase que ha dicho, ¿En alguna parte menciona su nombre? responde si o no (tener en cuenta de que algunas personas de manera opcional puede que ingresen sus dos nombres y dos apellidos). Sólo es obligatorio ingresar el primer nombre."
            response_openai = llamar_openai(prompt_validar_nombre)
            if "sí" in response_openai.lower():
                prompt_extraer_nombre = f"Extrae el nombre completo (nombre y apellido) del siguiente texto: '{user_message}'. (En caso de sólo haber un nombre solo extrae eso, ya que el segundo nombre y los apellidos son opcionales)."
                nombre_completo = llamar_openai(prompt_extraer_nombre).strip()
                primer_nombre = extraer_primer_nombre(nombre_completo)
                session_data['context'].append({'nombre_completo': nombre_completo, 'primer_nombre': primer_nombre})

                # Obtener los productos disponibles del contexto
                todos_los_productos = next((item['todos_los_productos'] for item in session_data['context'] if 'todos_los_productos' in item), [])

                # Filtrar las opciones de rango de precio basadas en los productos disponibles
                precios_disponibles = set()
                for producto in todos_los_productos:
                    precio = producto.get('PrecioTotalUF', None)
                    if precio is not None:
                        precios_disponibles.add(float(precio))

                # Crear las opciones de precios basadas en los rangos disponibles
                opciones_precio = []
                if precios_disponibles:
                    if any(precio < 1800 for precio in precios_disponibles):
                        opciones_precio.append({'text': 'Menos de 1800 UF', 'value': 'menos_1800'})
                    if any(1800 <= precio < 2500 for precio in precios_disponibles):
                        opciones_precio.append({'text': 'Entre 1800 y 2499 UF', 'value': 'entre_1800_2499'})
                    if any(2500 <= precio < 4000 for precio in precios_disponibles):
                        opciones_precio.append({'text': 'Entre 2500 y 3999 UF', 'value': 'entre_2500_3999'})
                    if any(4000 <= precio < 7000 for precio in precios_disponibles):
                        opciones_precio.append({'text': 'Entre 4000 y 6999 UF', 'value': 'entre_4000_6999'})
                    if any(precio >= 7000 for precio in precios_disponibles):
                        opciones_precio.append({'text': 'Más de 7000 UF', 'value': 'mas_7000'})
                else:
                    # Opciones por defecto en caso de que no haya precios disponibles
                    opciones_precio = [
                        {'text': 'Menos de 1800 UF', 'value': 'menos_1800'},
                        {'text': 'Entre 1800 y 2499 UF', 'value': 'entre_1800_2499'},
                        {'text': 'Entre 2500 y 3999 UF', 'value': 'entre_2500_3999'},
                        {'text': 'Entre 4000 y 6999 UF', 'value': 'entre_4000_6999'},
                        {'text': 'Más de 7000 UF', 'value': 'mas_7000'},
                    ]

                session_data['state'] = 'solicitando_rango_precio'
                response = obtener_pregunta('rango_precios')
                options = opciones_precio
            else:
                response = 'Parece que no has ingresado tu nombre de manera válida. Por favor, intenta nuevamente ingresando al menos tu primer nombre.'
        else:
            response = 'Por favor, ingresa al menos tu primer nombre.'

    elif session_data['state'] == 'solicitando_tipo_inmueble':
        session_data['context'].append({'tipo_inmueble': user_message})
        session_data['state'] = 'solicitando_rango_precio'
        options = [
            {'text': 'Menos de 1800 UF', 'value': 'menos_1800'},
            {'text': 'Entre 1800 y 2499 UF', 'value': 'entre_1800_2499'},
            {'text': 'Entre 2500 y 3999 UF', 'value': 'entre_2500_3999'},
            {'text': 'Entre 4000 y 6999 UF', 'value': 'entre_4000_6999'},
            {'text': 'Más de 7000 UF', 'value': 'mas_7000'},
        ]
        response = obtener_pregunta('rango_precios')

    elif session_data['state'] == 'solicitando_rango_precio':
        # Eliminar cualquier entrada previa de rango_precio para evitar conflictos
        session_data['context'] = [item for item in session_data['context'] if 'rango_precio' not in item]

        session_data['context'].append({'rango_precio': user_message})

        # Utilizar un nombre predeterminado si no se encontró el primer nombre
        primer_nombre = next((item['primer_nombre'] for item in session_data['context'] if 'primer_nombre' in item), "cliente")

        # Verifica si ya existe un correo almacenado
        correo_existente = next((item['correo'] for item in session_data['context'] if 'correo' in item), None)

        # Obtener los productos disponibles según el rango de precios seleccionado
        rango_precio_seleccionado = user_message
        todos_los_productos = next((item['todos_los_productos'] for item in session_data['context'] if 'todos_los_productos' in item), [])
        productos_filtrados = [
            producto for producto in todos_los_productos
            if cumple_con_rango_precio(producto['PrecioTotalUF'], rango_precio_seleccionado)
        ]

        # Filtrar las opciones de dormitorios basadas en los productos filtrados
        opciones_dormitorios = sorted(set(int(producto['Dormitorios']) for producto in productos_filtrados))

        # Si el correo ya existe, no volver a pedirlo
        if correo_existente:
            session_data['state'] = 'solicitando_dormitorios'

            # Aquí solo se muestran las opciones de dormitorios disponibles en el proyecto
            options = [
                {'text': f'{dormitorios} dormitorio(s)', 'value': dormitorios} for dormitorios in opciones_dormitorios
            ]

            response = obtener_pregunta('dormitorios', primer_nombre=primer_nombre)
        else:
            # Solicitar el correo en una nueva cotización si no se tiene aún
            session_data['state'] = 'solicitando_correo'
            response = obtener_pregunta('correo', primer_nombre=primer_nombre)
            options = []

    elif session_data['state'] == 'solicitando_correo':
        primer_nombre = next((item['primer_nombre'] for item in session_data['context'] if 'primer_nombre' in item), "cliente")
        
        # Verifica si el mensaje del usuario contiene un correo electrónico
        prompt_verificar_correo = f"El usuario dijo: '{user_message}'. ¿Contiene esto una dirección de correo electrónico válida? Responde 'sí' o 'no'."
        respuesta_verificar_correo = llamar_openai(prompt_verificar_correo)
        
        if "sí" in respuesta_verificar_correo.lower():
            # Si hay un correo, intenta extraerlo
            prompt_extraer_correo = f"Extrae la dirección de correo electrónico del siguiente mensaje del usuario: '{user_message}'."
            correo_extraido = llamar_openai(prompt_extraer_correo).strip()
            
            # Valida el correo extraído
            if validar_correo(correo_extraido):
                # Si el correo es válido, continúa con el flujo
                session_data['context'].append({'correo': correo_extraido})
                session_data['state'] = 'solicitando_dormitorios'
                
                # Filtrar opciones de dormitorios basadas en el proyecto seleccionado
                opciones_dormitorios = next((item['opciones_dormitorios'] for item in session_data['context'] if 'opciones_dormitorios' in item), [])
                if opciones_dormitorios:
                    options = [
                        {'text': f'{dormitorios} dormitorio(s)', 'value': dormitorios} for dormitorios in opciones_dormitorios
                    ]
                else:
                    # Opciones por defecto en caso de que no se encuentren dormitorios
                    options = [
                        {'text': '1 dormitorio', 'value': '1'},
                        {'text': '2 dormitorios', 'value': '2'},
                        {'text': '3 dormitorios', 'value': '3'},
                        {'text': '4 dormitorios', 'value': '4'},
                        {'text': 'Más de 4 dormitorios', 'value': '5+'},
                    ]
                
                response = obtener_pregunta('dormitorios', primer_nombre=primer_nombre)
            else:
                # Si OpenAI proporciona una cadena que no es un correo válido, solicita que se ingrese de nuevo
                response = obtener_pregunta('correo_invalido')
        else:
            # Si OpenAI indica que no hay un correo, solicita que se ingrese de nuevo
            response = obtener_pregunta('correo_no_detectado')

    elif session_data['state'] == 'solicitando_dormitorios':
        
        cantidad_dormitorios = user_message.split()[0]  # Esto extraerá el número de la respuesta
        session_data['context'].append({'dormitorios': cantidad_dormitorios})

        session_data['state'] = 'solicitando_banos'

        # Obtener el rango de precios seleccionado
        rango_precio_seleccionado = next((item['rango_precio'] for item in session_data['context'] if 'rango_precio' in item), None)

        # Obtener los productos disponibles
        todos_los_productos = next((item['todos_los_productos'] for item in session_data['context'] if 'todos_los_productos' in item), [])

        # Filtrar los productos en base al rango de precios y la cantidad de dormitorios seleccionada
        productos_filtrados = [
            producto for producto in todos_los_productos
            if cumple_con_rango_precio(producto['PrecioTotalUF'], rango_precio_seleccionado) and
            int(producto['Dormitorios']) == int(cantidad_dormitorios)
        ]

        # Filtrar las opciones de baños disponibles en base a los productos filtrados
        opciones_banos = sorted(set(int(producto['Banos']) for producto in productos_filtrados))

        if opciones_banos:
            # Mostrar solo las opciones de baños disponibles
            options = [
                {'text': f'{banos} baño(s)', 'value': banos} for banos in opciones_banos
            ]
        else:
            # Opciones por defecto en caso de que no se encuentren baños disponibles
            options = [
                {'text': '1 baño', 'value': '1'},
                {'text': '2 baños', 'value': '2'},
                {'text': '3 baños', 'value': '3'},
                {'text': '4 o más baños', 'value': '4+'},
            ]

        response = obtener_pregunta('banos')

    elif session_data['state'] == 'solicitando_banos':
        print("Estado actual: solicitando_banos")  # Depuración
        print(f"ha_dado_telefono antes de verificar: {session_data.get('ha_dado_telefono')}")  # Depuración
        # Extracción del primer nombre antes de usarlo en la respuesta
        primer_nombre = next((item['primer_nombre'] for item in session_data['context'] if 'primer_nombre' in item), "cliente")

        # Asume que 'user_message' contiene la cantidad de baños
        cantidad_banos = user_message.split()[0]  # Esto extraerá el número de la respuesta
        session_data['context'].append({'banos': cantidad_banos})

        # Inicializa variables para almacenar los valores necesarios
        tipo_inmueble = rango_precio = dormitorios = banos = proyecto = None

        # Itera sobre el contexto para extraer los valores necesarios
        for item in session_data['context']:
            if 'tipo_inmueble' in item:
                tipo_inmueble = item['tipo_inmueble']
            elif 'rango_precio' in item:
                rango_precio = item['rango_precio']
            elif 'dormitorios' in item:
                dormitorios = item['dormitorios']
            elif 'banos' in item:
                banos = item['banos']
            elif 'proyecto' in item:
                proyecto = item['proyecto']

        # Verifica que todos los valores necesarios estén presentes
        if all(value is not None for value in [tipo_inmueble, rango_precio, url_cliente, dormitorios, banos, proyecto]):
            todos_los_productos = next((item['todos_los_productos'] for item in session_data['context'] if 'todos_los_productos' in item), [])
            try:
                productos_filtrados = [
                    producto for producto in todos_los_productos
                    if (producto['TipoInmueble'].lower() == tipo_inmueble) and
                    cumple_con_rango_precio(producto['PrecioTotalUF'], rango_precio) and
                    (int(producto['Dormitorios']) == int(dormitorios)) and
                    (int(producto['Banos']) == int(banos))
                ]
            except ValueError as e:
                # Maneja el error de conversión de valores a enteros
                response = "Ha ocurrido un error al procesar tu solicitud. Por favor, verifica los datos ingresados y vuelve a intentarlo."
                session_data['state'] = 'solicitando_banos'
                options = [
                    {'text': '1 baño', 'value': '1'},
                    {'text': '2 baños', 'value': '2'},
                    {'text': '3 baños', 'value': '3'},
                    {'text': '4 o más baños', 'value': '4+'},
                ]
                return JsonResponse({'respuesta': response, 'options': options})

            # Decide qué hacer con los productos obtenidos
            producto_destacado = obtener_producto_mas_barato(productos_filtrados) if productos_filtrados else None

            if producto_destacado:
                # Marca la búsqueda como exitosa
                session_data['busqueda_exitosa'] = True

                if session_data.get('ha_dado_telefono') is not None and session_data.get('cotizacion_subsecuente', False):
                    # Suponiendo que 'cotizacion_subsecuente' se establece a True después de la primera cotización
                    nombre_completo = next((item['nombre_completo'] for item in session_data['context'] if 'nombre_completo' in item), "Desconocido")
                    correo = next((item['correo'] for item in session_data['context'] if 'correo' in item), "Desconocido")
                    telefono = next((item['telefono'] for item in session_data['context'] if 'telefono' in item), "")
                    convertir_rango_precio_a_texto = next((precio_a_texto[item['rango_precio']] for item in session_data['context'] if 'rango_precio' in item), "Desconocido")
                    tipo_inmueble = next((item['tipo_inmueble'] for item in session_data['context'] if 'tipo_inmueble' in item), "Desconocido")
                    dormitorios = next((item['dormitorios'] for item in session_data['context'] if 'dormitorios' in item), "Desconocido")
                    banos = next((item['banos'] for item in session_data['context'] if 'banos' in item), "Desconocido")
                    proyecto = next((item['proyecto'] for item in session_data['context'] if 'proyecto' in item), "Desconocido")
                    
                    # Enviar correo a Iconcreta para procesar al cotizante y subirlo al CRM
                    enviar_correo_iconcreta(nombre_completo, correo, telefono, convertir_rango_precio_a_texto, tipo_inmueble, dormitorios, banos, url_cliente, proyecto)

                # Determina el tipo de inmueble para el mensaje, basado en la elección del usuario
                tipo_inmueble_texto = "Departamento" if tipo_inmueble.lower() == "departamento" else "Casa"
                url_plano_comercial = producto_destacado.get('URLPlanoComercial', 'no especificado')
                # Determina el prefijo adecuado ('el' o 'la') según el tipo de inmueble
                if tipo_inmueble.lower() == 'departamento':
                    tipo_inmueble_texto = 'el departamento'
                elif tipo_inmueble.lower() == 'casa':
                    tipo_inmueble_texto = 'la casa'
                else:
                    tipo_inmueble_texto = f"el {tipo_inmueble}"  # O cualquier formato por defecto que prefieras

                # Lista de mensajes de despedida
                mensajes_despedida = [
                    f"Te hemos enviado a tu correo electrónico más productos según tu cotización. Ha sido un placer ayudarte, {primer_nombre}.",
                    f"Revisa tu correo para más opciones que hemos seleccionado especialmente para ti. ¡Gracias por confiar en nosotros, {primer_nombre}!",
                    f"Hemos enviado detalles adicionales a tu email. ¡Esperamos haberte sido de ayuda, {primer_nombre}!",
                    f"Consulta la bandeja de tu correo para encontrar más propiedades que se ajusten a tus preferencias. ¡Fue un gusto asistirte, {primer_nombre}!",
                    f"En tu email encontrarás más información sobre las propiedades seleccionadas. ¡Agradecemos la oportunidad de servirte, {primer_nombre}!",
                ]

                # Selecciona un mensaje de despedida al azar
                mensaje_despedida_seleccionado = random.choice(mensajes_despedida)

                mensaje_respuesta = (
                    f"Tenemos {tipo_inmueble_texto} número {producto_destacado.get('Numero', 'no especificado')} "
                    f"del proyecto {producto_destacado.get('NombreProyecto', 'no especificado').lower()} "
                    f"a un precio total de {producto_destacado.get('PrecioTotalUF', 'no especificado')} UF. "
                    f"Puedes ver el plano del inmueble en el siguiente enlace:<br>"
                    f"<a href='{url_plano_comercial}' target='_blank'>Ver plano</a><br>"
                    f"{mensaje_despedida_seleccionado}"
                )
                
                # Añade el mensaje construido a la variable de respuesta
                response = mensaje_respuesta

                productos_aleatorios = random.sample(productos_filtrados, min(len(productos_filtrados), 5))
                correo_destinatario = next((item['correo'] for item in session_data['context'] if 'correo' in item), None)

                if correo_destinatario and productos_aleatorios:
                    # Leer la configuración personalizada
                    configuracion = leer_archivo_configuracion(url_cliente, proyecto)
                    max_productos = int(configuracion.get('MAX_PRODUCTOS', 5))
                    
                    # Obtener los valores de dormitorios y baños del primer producto para el mensaje general
                    primer_producto = productos_aleatorios[0] if productos_aleatorios else {}
                    dormitorios = primer_producto.get('Dormitorios', 'N/A')
                    banos = primer_producto.get('Banos', 'N/A')
                    # Obtener el nombre del proyecto
                    nombre_proyecto = primer_producto.get('NombreProyecto', 'Nombre del Proyecto Desconocido')
                    saludo_correo = configuracion.get('SALUDO_CORREO', 'Saludo por defecto').format(primer_nombre=primer_nombre).upper()
                    mensaje_presentacion = configuracion.get('MENSAJE_PRESENTACION', 'Mensaje de presentación por defecto').format(dormitorios=dormitorios, banos=banos, nombre_proyecto=nombre_proyecto)
                    
                    cierre_negrita = configuracion.get('CIERRE_CORREO_NEGRITA', 'Esperamos que estas opciones sean de tu agrado.')
                    cierre_normal = configuracion.get('CIERRE_CORREO_NORMAL', 'Estamos a tu disposición para cualquier consulta o para ofrecerte más información.')
                    template_name = configuracion.get('EMAIL_TEMPLATE', 'email_template.html')

                    # Leer los colores del span desde el archivo de configuración
                    color_fondo_span = configuracion.get('COLOR_FONDO_SPAN', '#004A90')  # Color de fondo por defecto
                    color_texto_span = configuracion.get('COLOR_TEXTO_SPAN', 'white')    # Color de texto por defecto

                    # Generar la lista de productos con imágenes de planos
                    productos_html = ""
                    for producto in productos_aleatorios[:max_productos]:
                        numero_producto = producto.get('Numero', 'desconocido')
                        nombre_proyecto = producto.get('NombreProyecto', 'desconocido').lower()
                        tipo_texto = 'Departamento' if tipo_inmueble.lower() == 'departamento' else 'Casa' if tipo_inmueble.lower() == 'casa' else 'Inmueble'
                        
                        url_plano_comercial = producto.get('URLPlanoComercial', '')
                        precio_total_uf = producto.get('PrecioTotalUF', '0')

                        productos_html += f"""
                        <tr>
                            <td align="center" style="padding: 0;">
                                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border: 1px solid #eaeaea; border-radius: 10px; margin: 0 auto 20px auto; overflow: hidden; background-color: white; max-width: 600px;">
                                    <tr>
                                        <td align="center" style="padding: 0;">
                                            <img src="{url_plano_comercial}" alt="Plano Comercial" width="100%" style="display: block; max-width: 600px; margin: 0 auto 5px auto;">
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 10px; color: #082F4D; font-family: Arial, sans-serif; text-align: center; background-color: white;">
                                            <h2 style="margin: 0; font-size: 18px; font-weight: bold;">
                                                {tipo_texto} N° {numero_producto} 
                                                <span style="background-color: {color_fondo_span}; color: {color_texto_span}; padding: 5px 10px; font-size: 14px; border-radius: 5px;">
                                                    {precio_total_uf} UF
                                                </span>
                                            </h2>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        """

                    # Leer el contenido del archivo HTML
                    template_path = os.path.join(settings.BASE_DIR, 'templates', template_name)
                    try:
                        with open(template_path, 'r', encoding='utf-8') as file:
                            contenido_correo = file.read()
                    except UnicodeDecodeError:
                        with open(template_path, 'r', encoding='latin-1') as file:
                            contenido_correo = file.read()

                    # Reemplazar los marcadores de posición en el HTML
                    contenido_correo = contenido_correo.replace('{{ saludo_correo }}', saludo_correo)
                    contenido_correo = contenido_correo.replace('{{ mensaje_presentacion }}', mensaje_presentacion)
                    contenido_correo = contenido_correo.replace('{{ productos_html }}', productos_html)
                    contenido_correo = contenido_correo.replace('{{ cierre_negrita }}', cierre_negrita)
                    contenido_correo = contenido_correo.replace('{{ cierre_normal }}', cierre_normal)

                    # Enviar el correo con el contenido generado al cotizante
                    enviar_correo_a_cotizante(correo_destinatario.strip(), contenido_correo, url_cliente, proyecto)

                # Verifica si ya se ha proporcionado el número de teléfono
                if not session_data.get('ha_dado_telefono', False):
                    print("ha_dado_telefono es False, se debería pedir el teléfono.")  # Depuración
                    response += obtener_pregunta('numero_telefono')
                    options = [
                        {'text': 'Sí, deseo dar mi número de teléfono', 'value': 'dar_telefono'},
                        {'text': 'No, gracias', 'value': 'no_dar_telefono'}
                    ]
                    session_data['state'] = 'solicitando_telefono'
                else:
                    print("ha_dado_telefono es True, no se pide el teléfono.")  # Depuración
                    # Continuar al estado de finalización si ya se ha dado el teléfono
                    response += obtener_pregunta('necesitas_ayuda')
                    options = [
                        {'text': 'Sí, quiero seguir cotizando', 'value': 'cotizar'},
                        {'text': 'No, volver a inicio', 'value': 'inicio'}
                    ]
                    session_data['state'] = 'finalizacion'
            else:
                if not producto_destacado:
                    # Verifica si ya se ha proporcionado el número de teléfono
                    if not session_data.get('ha_dado_telefono', False):
                        response = obtener_pregunta('no_inmuebles_ayuda_telefono')
                        options = [
                            {'text': 'Sí, deseo dar mi número de teléfono', 'value': 'dar_telefono'},
                            {'text': 'No, gracias', 'value': 'no_dar_telefono'}  
                        ]
                        session_data['state'] = 'solicitando_telefono'  # Cambio de estado para solicitar el teléfono
                    else:
                        response = obtener_pregunta('no_inmuebles_ayuda')
                        options = [
                            {'text': 'Sí, quiero seguir cotizando', 'value': 'cotizar'},
                            {'text': 'No, gracias', 'value': 'inicio'}
                        ]
                        session_data['state'] = 'finalizacion'  # Cambia a finalización para manejar la siguiente acción
        else:
            # Si falta información, ofrece volver al paso donde falta la información.
            response = "Parece que falta información para completar tu solicitud. Por favor, verifica que has ingresado todos los datos requeridos."
            session_data['state'] = 'solicitando_banos'
            options = [
                {'text': '1 baño', 'value': '1'},
                {'text': '2 baños', 'value': '2'},
                {'text': '3 baños', 'value': '3'},
                {'text': '4 o más baños', 'value': '4+'},
            ]

    elif session_data['state'] == 'solicitando_telefono':
        if user_message == 'dar_telefono':
            response = obtener_pregunta('ingresar_telefono')
            session_data['state'] = 'ingresando_telefono'
            options = []
        elif user_message == 'no_dar_telefono':
            session_data['ha_dado_telefono'] = True
            response = obtener_pregunta('necesitas_ayuda')
            session_data['state'] = 'finalizacion'
            options = [
                {'text': 'Sí, quiero seguir cotizando', 'value': 'cotizar'},
                {'text': 'No, volver a inicio', 'value': 'inicio'}
            ]
            
            # Obtener datos del contexto para enviar por correo
            nombre_completo = next((item['nombre_completo'] for item in session_data['context'] if 'nombre_completo' in item), "Desconocido")
            correo = next((item['correo'] for item in session_data['context'] if 'correo' in item), "Desconocido")
            telefono = next((item['telefono'] for item in session_data['context'] if 'telefono' in item), "")
            convertir_rango_precio_a_texto = next((precio_a_texto[item['rango_precio']] for item in session_data['context'] if 'rango_precio' in item), "Desconocido")
            tipo_inmueble = next((item['tipo_inmueble'] for item in session_data['context'] if 'tipo_inmueble' in item), "Desconocido")
            dormitorios = next((item['dormitorios'] for item in session_data['context'] if 'dormitorios' in item), "Desconocido")
            banos = next((item['banos'] for item in session_data['context'] if 'banos' in item), "Desconocido")
            proyecto = next((item['proyecto'] for item in session_data['context'] if 'proyecto' in item), "Desconocido")

            # Enviar correo a Iconcreta para procesar al cotizante y subirlo al CRM
            enviar_correo_iconcreta(nombre_completo, correo, telefono, convertir_rango_precio_a_texto, tipo_inmueble, dormitorios, banos, url_cliente, proyecto)

    elif session_data['state'] == 'ingresando_telefono':
        # Extracción de datos previos necesarios para enviar por correo
        nombre_completo = next((item['nombre_completo'] for item in session_data['context'] if 'nombre_completo' in item), "Desconocido")
        correo = next((item['correo'] for item in session_data['context'] if 'correo' in item), "Desconocido")
        convertir_rango_precio_a_texto = next((precio_a_texto[item['rango_precio']] for item in session_data['context'] if 'rango_precio' in item), "Desconocido")
        tipo_inmueble = next((item['tipo_inmueble'] for item in session_data['context'] if 'tipo_inmueble' in item), "Desconocido")
        dormitorios = next((item['dormitorios'] for item in session_data['context'] if 'dormitorios' in item), "Desconocido")
        banos = next((item['banos'] for item in session_data['context'] if 'banos' in item), "Desconocido")
        proyecto = next((item['proyecto'] for item in session_data['context'] if 'proyecto' in item), "Desconocido")

        # Eliminar espacios en blanco y el carácter '+' para la verificación
        mensaje_limpio = user_message.replace(' ', '').replace('+', '')
        if mensaje_limpio.isdigit():
            # Procesamiento para un número que parece ser chileno
            numero = mensaje_limpio
            if len(numero) == 8:  # Número local sin código de área, asumir que es un móvil
                telefono = '+569' + numero
            elif len(numero) == 9:  # Número con 9 dígitos
                if numero.startswith('9'):  # Móvil sin código de país
                    telefono = '+56' + numero
                elif numero.startswith('2'):  # Fijo potencial, pero con un dígito adicional
                    telefono = '+562' + numero[1:]  # Se asume el número corregido, quitando el dígito extra
                else:
                    telefono = None
            elif len(numero) in [11, 12] and (numero.startswith('569') or numero.startswith('562')):  # Número completo con o sin '+'
                telefono = '+' + numero
            else:
                telefono = None

            if telefono:
                session_data['context'].append({'telefono': telefono})
                session_data['ha_dado_telefono'] = True
                response = f"Gracias por proporcionar tu número de teléfono. ¿Te puedo ayudar en algo más?"
                # Enviar correo con datos recopilados, incluyendo el teléfono
                enviar_correo_iconcreta(nombre_completo, correo, telefono, convertir_rango_precio_a_texto, tipo_inmueble, dormitorios, banos, url_cliente, proyecto)
                options = [{'text': 'Sí, quiero seguir cotizando', 'value': 'cotizar'},
                        {'text': 'No, volver al inicio', 'value': 'inicio'}]
                session_data['state'] = 'finalizacion'
            else:
                response = "No pude reconocer el número de teléfono en el formato esperado. ¿Puedes intentar de nuevo?"
                options = []
        else:
            prompt_validar_telefono = f"¿La frase '{user_message}' contiene un número de teléfono con al menos 8 dígitos numéricos? Solo responde sí o no."
            respuesta_verificacion = llamar_openai(prompt_validar_telefono)

            if respuesta_verificacion.lower() == "sí":
                prompt_ajustar_telefono = f"Extrae y ajusta al formato chileno el número de teléfono presente en la frase '{user_message}'. El formato chileno es '+569' seguido de los 8 dígitos locales para teléfonos móviles o '+562' seguido de los 8 dígitos locales para teléfonos fijos, entrégame como respuesta solo el número junto con el prefijo."
                telefono = llamar_openai(prompt_ajustar_telefono)
                
                if telefono:
                    session_data['context'].append({'telefono': telefono})
                    session_data['ha_dado_telefono'] = True
                    response = "Gracias por proporcionar tu número de teléfono. ¿Te puedo ayudar en algo más?"
                    enviar_correo_iconcreta(nombre_completo, correo, telefono, convertir_rango_precio_a_texto, tipo_inmueble, dormitorios, banos, url_cliente, proyecto)
                    options = [{'text': 'Sí, quiero seguir cotizando', 'value': 'cotizar'},
                            {'text': 'No, volver al inicio', 'value': 'inicio'}]
                    session_data['state'] = 'finalizacion'
                else:
                    response = "No pude encontrar un número de teléfono válido en tu mensaje. ¿Podrías proporcionarlo nuevamente?"
                    options = []
            else:
                response = "No detecté un número de teléfono en tu mensaje. ¿Podrías proporcionarlo nuevamente?"
                options = []

    elif session_data['state'] == 'finalizacion':
        if 'cotizar' in user_message or 'seguir cotizando' in user_message:
            session_data['cotizacion_subsecuente'] = True  # Marcar como segunda cotización
            
            # Limpiar datos de productos, pero mantener nombre y correo
            datos_a_mantener = ['nombre_completo', 'correo']
            session_data['context'] = [item for item in session_data['context'] if any(clave in item for clave in datos_a_mantener)]
            
            # Limpiar productos anteriores
            session_data['context'] = [item for item in session_data['context'] if 'todos_los_productos' not in item]
            session_data['state'] = 'solicitando_comuna'
            response = "Genial, ¿en cuál comuna deseas cotizar?"
            options = obtener_opciones_proyectos_por_comuna(url_cliente)
            session_data['busqueda_exitosa'] = False
        elif 'inicio' in user_message:
            session_data.clear()
            session_data['state'] = 'inicio'
            response = "Hola, soy un Asistente Virtual, ¿En qué puedo ayudarte?"

    request.session[session_key] = session_data

    return JsonResponse({'respuesta': response, 'options': options, 'state': session_data['state']})

def chatbot_index(request):
    return render(request, 'chatbot_index.html', {})