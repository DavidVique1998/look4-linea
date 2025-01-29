from modulos.grafoChats.grafoChat import *
import requests


def enviar_imagen_whatsapp(to, media):
    # URL del endpoint
    url = "https://gate.whapi.cloud/messages/image"
    
    # Token de autenticación
    token = "orL40u4yiReW6m0NmDTJdMemLNQpWqfA"
    
    # Encabezados de la solicitud
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Cuerpo de la solicitud
    payload = {
        "to": to,
        "media": media
    }
    
    # Realizar la solicitud POST
    response = requests.post(url, json=payload, headers=headers)
    
    # Verificar la respuesta
    if response.status_code == 200:
        print("Imagen enviada con éxito!")
        print("Respuesta:", response.json())
    else:
        print("Error al enviar la imagen.")
        print("Código de estado:", response.status_code)
        print("Respuesta:", response.text)

def enviar_mensaje_whatsapp(to, body, quoted=None, ephemeral=None, edit=None, typing_time=0, no_link_preview=False, mentions=None, view_once=False):
    """
    Envía un mensaje de texto a través del endpoint de Whapi.Cloud.
    
    Args:
        to (str): Número de WhatsApp destino en formato internacional (e.g., "12345678910@s.whatsapp.net").
        body (str): Cuerpo del mensaje.
        quoted (str, optional): ID del mensaje citado. Default es None.
        ephemeral (int, optional): Tiempo de duración del mensaje (en segundos). Default es None.
        edit (str, optional): ID del mensaje que se está editando. Default es None.
        typing_time (int, optional): Tiempo de escritura (en milisegundos). Default es 0.
        no_link_preview (bool, optional): Si es True, deshabilita la vista previa de enlaces. Default es False.
        mentions (list, optional): Lista de menciones (en formato ID). Default es None.
        view_once (bool, optional): Si es True, envía un mensaje de visualización única. Default es False.
        
    Returns:
        dict: Respuesta del servidor.
    """
    url = "https://gate.whapi.cloud/messages/text"
    headers = {
        "Authorization": "Bearer orL40u4yiReW6m0NmDTJdMemLNQpWqfA",  # Reemplaza con tu token real
        "Content-Type": "application/json"
    }
    
    payload = {
        "to": to,
        "body": body,
        "typing_time": typing_time,
        "no_link_preview": no_link_preview,
        "view_once": view_once
    }
    
    if quoted is not None:
        payload["quoted"] = quoted
    if ephemeral is not None:
        payload["ephemeral"] = ephemeral
    if edit is not None:
        payload["edit"] = edit
    if mentions is not None:
        payload["mentions"] = mentions
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()  # Respuesta exitosa
        else:
            return {"error": response.status_code, "message": response.text}
    except Exception as e:
        return {"error": "exception", "message": str(e)}

async def activar_verificacion_transferencia(link = "", detalles = "", identificador = ""):
    chat_ID_for_admin = '120363376341151112@g.us'
    print(link)
    if link != "":
        enviar_imagen_whatsapp(chat_ID_for_admin, link)
        enviar_mensaje_whatsapp(chat_ID_for_admin, f"ACCION: [TRANSFERENCIA/ASSESMENT]\nQUIEN: [{identificador}]\n Responde 1 para aceptar esta transferencia. Responde 2 para indicarle que la transferencia no es valida, el cliente será notificado automáticamente")
    
    if detalles != "":
        enviar_mensaje_whatsapp(chat_ID_for_admin, f"ACCION: [TRANSFERENCIA/ASSESMENT]\nQUIEN: [{identificador}]\nDetalles: {detalles}\n\n Responde 1 para aceptar esta transferencia. Responde 2 para indicarle que la transferencia no es valida, el cliente será notificado automáticamente")

    print("Transaccion detectada")

    
    return "Transaccion detectada. Una persona humana la verifcará en el sistema"

lista_de_tools = [
        {

            "type": "function",
            "function": {
                "name": "activar_verificacion_transferencia",
                "description": "Esta función se llama cuando el usuario indica que ya hizo una trasaccion al negocio",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "link": {
                            "type": "string",
                            "description": """Link de la imagen del comprobante de la transacción"""
                        },
                        "detalles": {
                            "type": "string",
                            "description": """En caso de que no sea una imagen, este parámetro describe los detalles de la transaccción de modo que recopila, nombre del cliente, banco, cuenta, monto. EN CASO DE TENER UNA IMAGEN DE TRANSFERENCIA, SIEMPRE USARAS LINK"""
                        }
                    },
                    "additionalProperties": False,
                    "required": ["eleccion"]
                }}
        }
        ]

available_functions = {
            "activar_verificacion_transferencia":activar_verificacion_transferencia
        }

def getGrafoChatID15():

    prompt = '''

Emilio Rosado
mié, 15 ene, 14:42 (hace 17 horas)
para mí

"""
INSTRUCCIONES PARA EL ASISTENTE VIRTUAL EN EL PROCESO DE TRANSFERENCIA

OBJETIVO DEL CHATBOT
El objetivo principal es guiar a los clientes en el proceso de transferencia para el pago del servicio de assessment, asegurándose de que la comunicación sea clara, profesional y eficiente.

ESTILO Y TONO
- Tono: Profesional, claro y amigable.
- Lenguaje aceptable: "Por favor," "Muchas gracias," "Validaremos en los siguientes minutos."
- Lenguaje a evitar: Informalidades, jergas o frases no profesionales.

FORMATO DEL INPUT
- El cliente ya ha confirmado por correo electrónico que envió el assessment.
- El chatbot recibirá esta confirmación y debe iniciar el proceso de solicitud de pago.

FORMATO DEL OUTPUT
- Respuestas breves y claras (máximo 60 palabras por respuesta).
- Uso de viñetas para datos específicos (como detalles de la cuenta bancaria).
- Confirmación educada y clara tras la transferencia.

USO DE FUNCIONES O HERRAMIENTAS
1. Asegúrate de enviar correctamente los detalles de la cuenta bancaria:
   - Nombre: LOOK4
   - BSB: 014002.
   - Cuenta: 659695859.
2. Acepta comprobantes solo en formatos válidos:
   - Imagen o texto con formato estándar australiano, debe incluir de que banco se hace la
   transferencia, el nombre de Look4 debe aparecer como receptor, la cantidad, etc.
3. Envía confirmación una vez recibido el comprobante.
4. Activa la función `activar_verificacion_transferencia` una vez que el cliente confirma que ha realizado la transferencia. Indica que validarás el comprobante para continuar con el proceso. En la función usarás UNO DE DOS PARAMETROS, O LINK, O DETALLES, PERO NO AMBOS, BAJO NINGUNA CONDICION, VAS A USAR AMBOS A LA VEZ
5. EN CASO DE TENER UNA IMAGEN DE TRANSFERENCIA, SIEMPRE USARAS LINK
MANEJO DE ERRORES
1. Si el cliente solicita un método de pago distinto:
   - Responde: "Por el momento, solo aceptamos transferencias bancarias a esta cuenta."
2. Si el comprobante no indica claramente el monto correcto, o no indica el nombre de Look4 como receptor
del dinero:
   - Responde: "Por favor verifica que tu comprobante sea el correcto, mientras tanto nosotros lo validaremos."

EJEMPLOS DE INTERACCIÓN

**Ejemplo 1**
Cliente: "Ya envié el assessment por correo."
Asistente: "Perfecto. Tu assessment ha sido redirigido al tutor correspondiente.
Por favor, realiza el pago de 125 AUD para comenzar.
Realiza la transferencia a esta cuenta:
   - Nombre: LOOK4
   - BSB: 014002.
   - Cuenta: 659695859.
Una vez realizada, envíanos el comprobante en formato válido (imagen o texto)."
Cliente: Perfecto.
Asistente: Espero los datos de trasnferencia.
Cliente: Certificado de transferencia
banco pepito
123456
Asistente: Este no es un comprobante válido.

**Ejemplo 2**
Cliente: "Aquí está el comprobante de la transferencia."
Asistente: "Muchas gracias por tu transferencia. Validaremos la transferencia en los siguientes
minutos para comenzar el trabajo y entregártelo en las próximas 48 horas.
Nos pondremos en contacto contigo lo antes posible."


FIN DEL PROMPT
'''



    return GrafoChat(15, available_functions, lista_de_tools, prompt)
getGrafoChatID15()