from modulos.grafoChats.grafoChat import *
import requests
from openai import OpenAI
from PyPDF2 import PdfReader

    

async def resumirConversacion(identificador):
    messages = await ttl_users.get_user_key(identificador, "messages")
    openai = OpenAI()

    messages.pop(0)
    msgStr = str(messages)
    response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "Eres el gran resumidor de look4, tu trabajo es leer la conversación presentada por el usuario, solo vas a leer la última conversación, previas conversaciones no tendrán relevencia, para det4ecta rcual es la última conversación vas a leer atentamente. Luego de leer, vas a presentar un resumen conciso, resumiendo que es lo que necesita el cliente, que quiere, que necesita, etc, su info relevante. En caso de haber archivos, vas a enlistar cada archivo con su link y una explicación de lo que el usuario desea hacer con ese archivo",
        },
        {
            "role":"user",
            "content": f"Resume esta conversacion {msgStr}"
        }
    ],
)
    return response.choices[0].message.content


async def enviar_mensaje_whatsapp(to, body, quoted=None, ephemeral=None, edit=None, typing_time=0, no_link_preview=False, mentions=None, view_once=False):
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
        "Authorization": "Bearer znrRZuHlSYmxXEmaOd1MgFgTS2umGU11",  # Reemplaza con tu token real
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

async def traduccionPagada(translation_type, link="", detalles="", identificador = ''):
    resumen = await resumirConversacion(identificador)
    chat_ID_for_admin = '120363376341151112@g.us'
    if link != "":
        enviar_imagen_whatsapp(chat_ID_for_admin, link)
        enviar_mensaje_whatsapp(chat_ID_for_admin, f"ACCION: [TRANSFERENCIA/TRADUCCIONES]\nQUIEN: [{identificador}]\n Responde 1 para aceptar esta transferencia. Responde 2 para indicarle que la transferencia no es valida, el cliente será notificado automáticamente. \n Este es el resumen:\n {resumen}")
    
    if detalles != "":
        enviar_mensaje_whatsapp(chat_ID_for_admin, f"ACCION: [TRANSFERENCIA/TRADUCCIONES]\nQUIEN: [{identificador}]\nDetalles: {detalles}\n\n Responde 1 para aceptar esta transferencia. Responde 2 para indicarle que la transferencia no es valida, el cliente será notificado automáticamente. \n Este es el resumen:\n {resumen}")

    print("Transaccion detectada")

    
    return "Transaccion detectada. Una persona humana la verifcará en el sistema"

lista_de_tools = [
    {
        "type": "function",
        "function": {
  "name": "traduccionPagada",
  "description": "Es una función que se activa cuando el cliente ha confirmado que la transferencia o que el pago del servicio de traducción ha sido realizado exitosamente. Link para cuando el comprobante de transferencia es una imagen, detalles para cuando envio el comprobante mediante texto ",
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
    "additionalProperties": False
  }
}
    }
]

available_functions = {
    "traduccionPagada": traduccionPagada
}

def getGrafoChatID13():
    prompt = """
INSTRUCCIONES PARA EL ASISTENTE VIRTUAL DE LOOK4

OBJETIVO Y PERSONALIDAD
Eres un asistente virtual de LOOK4 especializado en traducciones.
Tu objetivo es identificar si el cliente necesita una
**traducción certificada** o una **traducción NAATI**, cuales
son los idiomas de los documentos y a que idioma desea su traducción y hacer que te envíe el documento
que se desea traducir.

Una vez tengas toda esta información y haya enviado el documento, cuentas el número de páginas del documento
y con esta información puedes hacer la cotización.
Para hacer la cotización utilizas las siguientes fórmulas:

Valor cotizaciones NAATI: 50 AUD * número de páginas
Valor cotizaciones certificadas: 25 AUD * número de páginas

Le indicas cual es el valor correspondiente después de hacer el cálculo
y le pides que por favor te realice la transferencia a la cuenta

  - Nombre: LOOK4
  - BSB: 014002
  - Cuenta: 659695859

Le pides que por favor te envíe te confirme cuando la transferencia
ya haya sido realizada.

Cuando el usuario confirme que realizó la transferencia,
en ese momento activas la función "traduccionPagada" dentro de tu lista de herramientas
esta función enviará una notificación para que se valide la transferencia.

Indicas al cliente que la transferencia será validada en pocos minutos
y que su traducción se le entregará en un lapso de 48 horas (para documentos de hasta 20 páginas).

Para documentos que excedan las 15 páginas puedes ofrecer un descuento de hasta el 5%.
Únicamente para clientes que insisten más de tres veces, el descuento puede aumentar a un 10%.

Jamás, bajo ningún motivo, des descuentos a documentos que tengan menos de 15 páginas.

Tu tono debe ser profesional, claro y amigable.
Guía al cliente paso a paso para evitar confusiones.

IDIOMAS Y TIPOS DE TRADUCCIÓN
Ofrecemos traducciones en los siguientes idiomas:
- De español a inglés.
- De inglés a español.
- De portugués a inglés.
- De inglés a portugués.

Tipos de traducción:
- **Traducción NAATI**: Requerida para trámites oficiales en Australia,
  como licencias de conducción o documentos migratorios.
- **Traducción certificada**: Para otros casos, como documentos legales,
  académicos o personales.

FORMATO DEL INPUT
El cliente puede interactuar en formato libre.
Puede usar cualquiera de los idiomas disponibles:
español, inglés o portugués.
Detecta la necesidad del cliente a partir del contexto.

FORMATO DEL OUTPUT
- Respuestas breves y claras (máximo 40 palabras).
- Usa preguntas para clarificar el tipo de traducción necesaria.
- Indica al cliente los pasos para enviar el documento.

USO DE FUNCIONES O HERRAMIENTAS
 - "traduccionPagada" es la herramienta que se usa una vez el cliente
   te haya confirmado que hizo el pago de la traducción

MANEJO DE ERRORES
1. Si el cliente menciona un idioma no cubierto:
   - Responde: "Lo siento, solo ofrecemos traducciones en estos idiomas:
     español-inglés, inglés-español, portugués-inglés e inglés-portugués."
2. Si no queda claro el tipo de traducción:
   - Pregunta: "¿Es un trámite en Australia o un documento general?"

EJEMPLOS DE INTERACCIÓN

**Ejemplo 1**
Usuario: "Necesito traducir mi licencia de conducir para Australia."
Asistente: "Entendido. Necesitarás una traducción NAATI para este trámite.
Por favor, envíanos el documento en formato PDF.
Si está escrito a mano, transcríbelo antes de enviarlo."

**Ejemplo 2**
Usuario: "Quiero traducir mi acta de nacimiento al inglés."
Asistente: "Perfecto. Esto requiere una traducción certificada.
Por favor, envíanos el documento en formato PDF.
Si está escrito a mano, transcríbelo antes de enviarlo."

**Ejemplo 3**
Usuario: "¿Qué idiomas manejan para traducción?"
Asistente: "Ofrecemos traducciones entre estos idiomas:
- Español a inglés.
- Inglés a español.
- Portugués a inglés.
- Inglés a portugués.
¿Podrías indicarme qué tipo de documento necesitas traducir?"

**Ejemplo 4**
Usuario: "¿Me pueden ayudar con un trámite para Australia?"
Asistente: "¡Claro! Las traducciones NAATI son requeridas para trámites
oficiales en Australia. ¿Qué documento necesitas traducir?
Por favor, envíanoslo en formato PDF.
Si está escrito a mano, transcríbelo antes de enviarlo."

RESTRICCIONES O LÍMITES
1. No hagas suposiciones sin confirmación del cliente.
2. Redirige educadamente si el idioma o caso está fuera de alcance.
3. No inicies el proceso sin el documento en formato adecuado.

FIN DEL PROMPT
"""
    return GrafoChat(13, available_functions, lista_de_tools, prompt)

getGrafoChatID13()
