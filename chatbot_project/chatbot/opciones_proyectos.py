from urllib.parse import urlparse

# Función para obtener las opciones de comunas y proyectos según la URL y la comuna (opcional)
def obtener_opciones_proyectos_por_comuna(url_cliente, comuna=None):
    # Extraer el dominio de la URL
    parsed_url = urlparse(url_cliente)
    dominio = parsed_url.hostname

    # Depuración para verificar qué URL se está procesando
    print(f"Dominio cliente recibido: {dominio}")
    print(f"Comuna recibida: {comuna}")

    # Definir comunas y proyectos por URL
    opciones_por_url = {
        "localhost": {
            "comunas": {
                "La Florida": [
                    {'text': 'Parque Machalí', 'value': 'pmc'},
                    {'text': 'Altos de Asís', 'value': 'ada'}
                ],
                "Las Condes": [
                    {'text': 'Parque Estébanez', 'value': 'pae'}
                ]
            }
        },
        "127.0.0.1": {
            "comunas": {
                "La Florida": [
                    {'text': 'Parque Machalí', 'value': 'pmc'}
                ]
            }
        },
        "desarrollos.want.cl": {
            "comunas": {
                "Quillota": [
                    {'text': 'Altos del Valle 2', 'value': 'QU2'}
                ],
                "Quilpué": [
                    {'text': 'Parque Pinares 2', 'value': 'pp2'}, 
                    {'text': 'Parque Pinares 3', 'value': 'pp3'}, 
                ],
                "Villa alemana": [
                    {'text': 'Edificio Viena', 'value': 'vie'}, 
                    {'text': 'Condominio El Alba', 'value': 'cea'}
                ]
            }
        },
        "vimac.cl": {
            "comunas": {
                "Concón": [
                    {'text': 'Edificio Costa', 'value': 'cos'}, 
                    {'text': 'Edificio Duo', 'value': 'duo'}
                ],
                "Viña del mar": [
                    {'text': 'Edificio Itaca', 'value': 'ita'},
                    {'text': 'Edificio Vía Poniente', 'value': 'vpo'}
                ]
            }
        },
        "ivmc.cl": {
            "comunas": {
                "Quillota": [
                    {'text': 'Altos del Valle 2', 'value': 'QU2'}
                ],
                "Quilpué": [
                    {'text': 'Parque Pinares 2', 'value': 'pp2'}, 
                    {'text': 'Parque Pinares 3', 'value': 'pp3'}, 
                ],
                "Villa alemana": [
                    {'text': 'Edificio Viena', 'value': 'vie'}, 
                    {'text': 'Condominio El Alba', 'value': 'cea'}
                ]
            }
        },
        "desarrollo.iconcreta.com": {
            "comunas": {
                "La Florida": [
                    {'text': 'Parque Machalí', 'value': 'pmc'},
                    {'text': 'Altos de Asís', 'value': 'ada'}
                ],
                "Las Condes": [
                    {'text': 'Parque Estébanez', 'value': 'pae'}
                ]
            }
        },
        "chatbot.iconcreta.com": {
            "comunas": {
                "La Florida": [
                    {'text': 'Parque Machalí', 'value': 'pmc'},
                    {'text': 'Altos de Asís', 'value': 'ada'}
                ],
                "Las Condes": [
                    {'text': 'Parque Estébanez', 'value': 'pae'}
                ]
            }
        },
        # Añadir más URLs y comunas según sea necesario
    }

    # Verificar si el dominio existe en el diccionario
    if dominio in opciones_por_url:
        comunas = opciones_por_url[dominio].get("comunas", {})

        # Si se proporciona una comuna, devolver los proyectos asociados a esa comuna
        if comuna:
            comuna_lower = comuna.lower()  # Convertir la comuna del usuario a minúsculas para la búsqueda
            for key_comuna in comunas.keys():
                if key_comuna.lower() == comuna_lower:
                    return comunas[key_comuna]  # Devuelve los proyectos de la comuna seleccionada
            # Si no hay coincidencia con la comuna, devolver un array vacío
            return []

        # Si no se proporciona la comuna, devolver la lista de comunas disponibles
        return [{'text': key_comuna, 'value': key_comuna.lower()} for key_comuna in comunas.keys()]

    # Si no coincide la URL, devolver un array vacío
    print("No se encontraron comunas ni proyectos para esta URL.")
    return []
