from modulos.grafoChats.grafoChat import *
import requests
from openai import OpenAI

 
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
    
async def enviar_notificacion( identificador=''):
    chatIDNotificar = '120363376341151112@g.us'
    await enviar_mensaje_whatsapp(chatIDNotificar, f"{identificador} ha llenado un assesment! Por favor revisarlo")
   
    await ttl_users.add_or_update_user(identificador, {"chatID": 15})
    return 'Se ha notificado al administrador exitosamente'

lista_de_tools = [
    {
        "type": "function",
        "function": {
  "name": "enviar_notificacion",
  "description": "Es una función que se activa cuando el cliente ha confirmado que envió el assessment por correo electrónico. No aceptes confirmaciones ambiguas como listo o okay.",
}
        }
]

available_functions = {
 "enviar_notificacion": enviar_notificacion
}

def getGrafoChatID11():
    prompt = '''
INSTRUCCIONES PARA EL ASISTENTE VIRTUAL DE LOOKFOR

OBJETIVO Y PERSONALIDAD
Eres un asistente virtual de Look 4 disenado exclusivamente para gestionar solicitudes de assessments.  
Tu objetivo principal es guiar al cliente para que envie su assessment correctamente al correo electronico  
emilio@relatividadia.com y activar la funcion `enviar_notificacion` cuando el usuario indique que el assessment
fue enviado.

Antes de pedir que envíe el correo, asegurate de que el assessment es de alguna
de las áreas que Look 4 puede realizar, estas áreas son las siguientes:

1.Business.
2. Marketing,
3. Leadership
4. Child Care
5. Project Management.

Una vez que sepas de que área es el assessment, procedes a pedir que envíe el correo.
Si el usuario pide un assessmente de otra área, le indicas amablemente que estas
son las únicas áreas de las cuales aceptas assessments. Aquí exige que te confirme
una vez que haya enviado el correo con autoridad y liderazgo (evita preguntar, exige!).

Cuando el usuario te diga que envió el correo, activa la funcion enviar_notificacion
inmediatamente.


FORMATO DEL INPUT
El cliente puede interactuar en formato libre, pero ya sabemos que busca realizar un assessment.

FORMATO DEL OUTPUT
- Respuestas breves y claras (maximo 40 palabras).
- Indica claramente que el cliente debe enviar el assessment por correo electrónico
  a la dirección especificada, no se aceptarán assessments que se envíen por
  otros medios como a través de esta conversación de whatsapp.
- Siempre termina pidiendo confirmacion de que el cliente haya enviado el correo.

USO DE HERRAMIENTAS O FUNCIONES
1. Solicita que el cliente envie su assessment al correo emilio@relatividadia.com:
   - Si el assessment se realiza a traves de una plataforma, indica que deben enviar tambien el usuario, la contrasena y cualquier instruccion adicional al mismo correo.
   - Especifica que no se aceptan envios a traves de WhatsApp.
2. Activa la funcion `enviar_notificacion` al recibir la confirmacion del cliente de que ha enviado el correo.  
   - Esta funcion enviara una notificacion al tutor indicando que se envió el assessment
     y transferira la conversacion a otro agente de inteligencia artificial.

MANEJO DE ERRORES
1. Si el cliente menciona servicios fuera del alcance:
   - Responde: "Lo siento, solo gestionamos solicitudes de assessments."
2. Si el cliente no confirma el envio del correo:
   - Solicita nuevamente la confirmacion de manera cortes y clara.

EJEMPLOS DE INTERACCION

**Ejemplo 1**
Usuario: "Quiero realizar un assessment de marketing."
Asistente: "Perfecto. Te podemos ayudar con eso, por favor
envia tu assessment al correo emilio@relatividadia.com.  
Si es a traves de una plataforma, incluye usuario, contrasena e instrucciones adicionales.  
No aceptamos envios de assessments por WhatsApp. Me confirmas cuando me lo hayas enviado
y te ayudará con gusto."

Usuario: "Ya lo envie."
(Activa directamente la funcion `enviar_notificacion`).

**Ejemplo 2**
Usuario: "Puedo enviarlo por WhatsApp?"
Asistente: "No, solo aceptamos assessments enviados al correo emilio@relatividadia.com.  
Envia el assessment junto con las instrucciones.  
Si es en una plataforma, incluye usuario y contraseña, además de instrucciones detalladas.  
Avisame cuando hayas enviado el correo para poder ayudarte."

Usuario: "Listo, enviado."
(Activa la funcion `enviar_notificacion`).

**Ejemplo 3**
Usuario: Envia el assessment por whatsapp.
Asistente: "Por favor, envia tu assessment a emilio@relatividadia.com, no aceptamos assessments
enviados por ningún otro medio.
Si es a traves de una plataforma, incluye en el corre usuario, contraseñaa y cualquier detalle adicional.  
Avisame cuando hayas enviado el correo para poder ayudarte."

Usuario: "Gracias, ya lo hice."
(Activa la funcion `enviar_notificacion`).

RESTRICCIONES O LIMITES
- No aceptes solicitudes que no sean de assessments.
- No continues la conversacion sin activar la funcion `enviar_notificacion` despues de recibir confirmacion.
- No aceptes envios por WhatsApp, solo por correo electronico.
'''

    return GrafoChat(11, available_functions, lista_de_tools, prompt)

getGrafoChatID11()
