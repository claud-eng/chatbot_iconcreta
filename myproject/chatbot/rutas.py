# Función para acceder a un archivo de configuración específico para cada proyecto dependiendo de la URL
def seleccionar_ruta_configuracion(url_cliente, proyecto=None):
    configuraciones = {
        "localhost": {
            "default": r"D:\\chatbot_iconcreta\\App_Data\\demoinm.cfg",
            "pmc": r"D:\\chatbot_iconcreta\\App_Data\\demoinm-PMC.cfg",
            "ada": r"D:\\chatbot_iconcreta\\App_Data\\demoinm-ADA.cfg",
            "pae": r"D:\\chatbot_iconcreta\\App_Data\\demoinm-PAE.cfg",
            # Agregar más proyectos para localhost según sea necesario
        },
        "127.0.0.1": {
            "default": r"D:\\chatbot_iconcreta\\App_Data\\demoinm.cfg",
            "pmc": r"D:\\chatbot_iconcreta\\App_Data\\demoinm-PMC.cfg",
            # Agregar más proyectos para localhost según sea necesario
        },
        # Agregar más URLs y sus proyectos según sea necesario
    }

    for key in configuraciones:
        if key in url_cliente:
            if proyecto:
                return configuraciones[key].get(proyecto.lower(), configuraciones[key].get("default"))
            else:
                return configuraciones[key].get("default")
    return r"D:\\chatbot_iconcreta\\App_Data\\demoinm-PMC.cfg"