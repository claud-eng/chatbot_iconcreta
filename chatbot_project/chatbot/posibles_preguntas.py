import random

# Diccionario con variaciones de preguntas
POSIBLES_PREGUNTAS = {
    'nombre': [
        '¡Gracias por tu interés en nuestro proyecto! Para una atención más personalizada, ¿podrías decirme tu nombre, por favor?',
        '¡Qué gusto que estés interesado en nuestro proyecto! ¿Me podrías dar tu nombre para continuar?',
        'Estoy encantada de ayudarte. ¿Me puedes decir tu nombre para ofrecerte una atención más personalizada?',
        'Me alegra mucho tu interés en el proyecto. ¿Podrías proporcionarme tu nombre?',
    ],
    'correo': [
        'Excelente {primer_nombre}, antes de continuar, ¿podrías proporcionarme tu correo electrónico para enviarte información detallada sobre tu cotización?',
        'Perfecto {primer_nombre}, ¿me puedes dar tu correo electrónico para enviarte la información completa de tu cotización?',
        'Gracias {primer_nombre}, ¿podrías proporcionarme tu correo electrónico para enviarte la información de la cotización?',
        'Gracias, {primer_nombre}. Para enviarte los detalles de tu cotización, ¿me puedes proporcionar tu correo electrónico?',
    ],
    'tipo_inmueble': [
        'Genial, {primer_nombre}, ¿qué tipo de inmueble estás buscando?',
        'Perfecto, {primer_nombre}, ¿estás buscando un departamento o una casa?',
        'Muy bien, {primer_nombre}, ¿qué tipo de propiedad te interesa?',
        'Entendido, {primer_nombre}, ¿qué tipo de inmueble prefieres?',
        'Genial, {primer_nombre}, ¿qué tipo de propiedad estás buscando?',
        'Perfecto, {primer_nombre}, ¿me puedes decir qué tipo de inmueble prefieres?',
        'Muy bien, {primer_nombre}, ¿estás interesado en un departamento o una casa?',
        'Entendido, {primer_nombre}, ¿me puedes decir qué tipo de propiedad te gustaría cotizar?',
    ],
    'rango_precios': [
        'Muy bien, ¿en qué rango de precios estás interesado?',
        'Perfecto, ¿me puedes decir el rango de precios que te interesa?',
        'Genial, ¿qué rango de precios estás buscando?',
        'Para continuar, ¿en qué rango de precios te gustaría cotizar?',
        'Entendido, ¿me puedes decir el rango de precios de tu interés?',
        'Muy bien, ¿qué rango de precios prefieres?',
        'Genial, ¿me puedes decir el rango de precios que estás considerando?',
        'Para seguir, ¿qué rango de precios te interesa?',
    ],
    'rut': [
        'Gracias, {primer_nombre}. Ahora, por favor, dime tu RUT para continuar.',
        'Perfecto, {primer_nombre}. ¿Me puedes proporcionar tu RUT?',
    ],
    'rut_invalido': [
        'El RUT ingresado no parece válido, {primer_nombre}. Por favor, inténtalo de nuevo.',
        'No pude reconocer el RUT que ingresaste, {primer_nombre}. Por favor, verifica que esté bien escrito e inténtalo de nuevo.',
        'Hubo un error al validar tu RUT, {primer_nombre}. ¿Podrías intentarlo otra vez?',
    ],
    'rut_no_detectado': [
        '{primer_nombre}, parece que no ingresaste un RUT. ¿Puedes proporcionarlo, por favor?',
        'Parece que no proporcionaste un RUT, {primer_nombre}. Por favor, escríbelo de nuevo para que podamos continuar.',
    ],
    'dormitorios': [
        'Perfecto, {primer_nombre}, ¿cuántos dormitorios necesitas?',
        'Genial, {primer_nombre}, ¿me puedes decir cuántos dormitorios te gustaría tener?',
        'Muy bien, {primer_nombre}, ¿cuántos dormitorios prefieres?',
        'Para continuar, {primer_nombre}, ¿cuántos dormitorios estás buscando?',
        'Entendido, {primer_nombre}, ¿me puedes decir cuántos dormitorios necesitas?',
        'Perfecto, {primer_nombre}, ¿me puedes decir cuántos dormitorios te interesan?',
        'Genial, {primer_nombre}, ¿cuántos dormitorios te gustaría tener?',
        'Muy bien, {primer_nombre}, ¿cuántos dormitorios necesitas?',
    ],
    'correo_invalido': [
        'El correo proporcionado no parece ser válido. Por favor, ingresa un correo electrónico válido.',
        'No detecté un correo válido. ¿Puedes intentar con otra dirección de correo?',
        'El correo que ingresaste no parece ser válido. Por favor, ingresa un correo electrónico correcto.',
        'Necesito un correo válido para continuar. ¿Puedes ingresar una dirección de correo correcta?',
        'El correo proporcionado no es válido. Por favor, ingresa una dirección de correo válida.',
        'Necesito un correo electrónico válido para continuar. ¿Podrías ingresarlo nuevamente?',
    ],
    'correo_no_detectado': [
        'No he detectado un correo electrónico en tu mensaje. Por favor, ingresa tu correo electrónico para continuar.',
        'No encontré un correo en tu mensaje. ¿Puedes ingresar tu correo electrónico para seguir?',
        'No veo un correo electrónico en tu mensaje. Por favor, ingresa tu correo para continuar.',
        'Parece que no ingresaste un correo electrónico. ¿Puedes proporcionar tu correo para seguir?',
        'No detecté un correo en tu mensaje. Por favor, ingresa tu correo electrónico para continuar.',
        'No veo un correo en tu mensaje. ¿Puedes proporcionar tu correo electrónico para continuar?',
        'Parece que no ingresaste un correo. ¿Puedes proporcionar tu correo para continuar?',
        'No encontré un correo en tu mensaje. Por favor, ingresa tu correo para continuar.',
    ],
    'banos': [
        '¿Cuántos baños prefieres?',
        '¿Me puedes decir cuántos baños te gustaría tener?',
        '¿Cuántos baños necesitas?',
        '¿En cuántos baños estás interesado?',
        '¿Cuántos baños te gustaría tener?',
        '¿Me puedes decir cuántos baños necesitas?',
        '¿Cuántos baños te interesan?',
        '¿Me puedes decir cuántos baños estás buscando?',
    ],
    'numero_telefono': [
        ' Para una forma de contacto más directa, ¿deseas otorgar tu número de teléfono?',
        ' Para seguir en contacto, ¿me puedes proporcionar tu número de teléfono?',
        ' ¿Te gustaría darme tu número de teléfono para estar en contacto más directo?',
        ' Para facilitar la comunicación, ¿me podrías dar tu número de teléfono?',
        ' Para seguir en contacto, ¿puedes darme tu número de teléfono?',
        ' ¿Te gustaría proporcionar tu número de teléfono para estar en contacto más directo?',
        ' Para una comunicación más directa, ¿me puedes dar tu número de teléfono?',
        ' ¿Podrías darme tu número de teléfono para seguir en contacto?',
        ' Para facilitar la comunicación, ¿puedes proporcionarme tu número de teléfono?',
        ' ¿Me puedes dar tu número de teléfono para una comunicación más directa?',
    ],
    'necesitas_ayuda': [
        ' ¿Necesitas ayuda con otra cosa?',
        ' ¿Te puedo asistir en algo más?',
        ' ¿Puedo ayudarte con algo más?',
        ' ¿Hay algo más en lo que pueda asistirte?',
        ' ¿Necesitas ayuda con algo más?',
        ' ¿Te puedo ayudar en algo más?',
        ' ¿Puedo asistirte en algo más?',
        ' ¿Hay algo más en lo que pueda ayudarte?',
        ' ¿Te puedo ayudar con otra cosa?',
        ' ¿Puedo asistirte con otra cosa?',
    ],
    'no_inmuebles_ayuda_telefono': [
        'Lo siento, no he encontrado inmuebles que coincidan con tus criterios. Para continuar con la cotización y tener una comunicación más directa, ¿te gustaría proporcionarme un número de teléfono?',
        'No he encontrado inmuebles que coincidan con tus criterios. Para seguir y tener una comunicación más directa, ¿me puedes dar tu número de teléfono?',
        'Lo siento, no he encontrado inmuebles que coincidan con tus criterios. Para continuar, ¿puedes proporcionarme un número de teléfono para una mejor comunicación?',
        'No he encontrado inmuebles que coincidan con tus criterios. Para seguir, ¿te gustaría darme tu número de teléfono para una comunicación más directa?',
        'Lo siento, no he encontrado inmuebles según tus criterios. Para continuar, ¿puedes proporcionarme tu número de teléfono?',
        'No he encontrado inmuebles que coincidan con tus criterios. Para seguir con la cotización, ¿me puedes dar tu número de teléfono para una mejor comunicación?',
        'Lo siento, no he encontrado inmuebles que coincidan con tus criterios. Para continuar, ¿puedes proporcionarme tu número de teléfono?',
        'No he encontrado inmuebles que coincidan con tus criterios. Para continuar con la cotización, ¿puedes darme tu número de teléfono para una comunicación más directa?',
        'Lo siento, no he encontrado inmuebles según tus criterios. Para seguir, ¿puedes proporcionarme tu número de teléfono?',
        'No he encontrado inmuebles que coincidan con tus criterios. Para continuar, ¿me puedes dar tu número de teléfono para una mejor comunicación?',
    ],
    'no_inmuebles_ayuda': [
        'Lo siento, no he encontrado inmuebles que coincidan con tus criterios. ¿Te puedo asistir en algo más?',
        'No he encontrado inmuebles que coincidan con tus criterios. ¿Puedo ayudarte con algo más?',
        'Lo siento, no he encontrado inmuebles que coincidan con tus criterios. ¿Necesitas ayuda con algo más?',
        'No he encontrado inmuebles según tus criterios. ¿Hay algo más en lo que pueda asistirte?',
        'Lo siento, no he encontrado inmuebles que coincidan con tus criterios. ¿Te puedo ayudar en algo más?',
        'No he encontrado inmuebles que coincidan con tus criterios. ¿Puedo asistirte en algo más?',
        'Lo siento, no he encontrado inmuebles según tus criterios. ¿Necesitas ayuda con otra cosa?',
        'No he encontrado inmuebles que coincidan con tus criterios. ¿Puedo ayudarte con otra cosa?',
        'Lo siento, no he encontrado inmuebles según tus criterios. ¿Te puedo asistir con algo más?',
        'No he encontrado inmuebles que coincidan con tus criterios. ¿Hay algo más en lo que pueda ayudarte?',
    ],
    'ingresar_telefono': [
        'Por favor, ingresa tu número de teléfono.',
        '¿Puedes ingresar tu número de teléfono, por favor?',
        'Por favor, ingresa tu número de teléfono para continuar.',
        'Proporciona tu número de teléfono, por favor.',
        'Necesito tu número de teléfono. Por favor, ingrésalo.',
        '¿Puedes proporcionar tu número de teléfono, por favor?',
        'Por favor, ingresa tu número de teléfono para seguir.',
        'Proporciona tu número de teléfono para continuar, por favor.',
    ],
    # Añadir más tipos de preguntas según sea necesario...
}

def obtener_pregunta(tipo_pregunta, **kwargs):
    """Obtiene una pregunta aleatoria del tipo especificado y la formatea."""
    pregunta = random.choice(POSIBLES_PREGUNTAS[tipo_pregunta])
    return pregunta.format(**kwargs)