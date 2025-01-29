from modulos.grafoChats.grafoChat import *
import requests
from openai import OpenAI

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

    
async def formularioLleno(visa, pais, motivos_viaje, identificador=""):
    chatIDNotificar = '120363376341151112@g.us'
    resumen = await resumirConversacion(identificador)

    await enviar_mensaje_whatsapp(chatIDNotificar, f"ACCION: [INFORMAR] \n {identificador} ha llenado el forms de visas. \nEste es el resumen de la conversación: \n{resumen}")
    return "Se ha notificado a un asesor que el usuario lleno el form, dile que en pronto nos pondremos en contacto con el usuario"

lista_de_tools = [
    {
        "type": "function",
        "function": {
           
  "name": "formularioLleno",
  "description": "Esta función se activa una vez el cliente haya confirmado que completó el formulario de aplicación.",
  "strict": True,
  "parameters": {
    "type": "object",
    "required": [
      "visa",
      "pais",
      "motivos_viaje"
    ],
    "properties": {
      "visa": {
        "type": "string",
        "description": "Tipo de visa que el cliente necesita para su viaje."
      },
      "pais": {
        "type": "string",
        "description": "País al que el cliente viaja."
      },
      "motivos_viaje": {
        "type": "string",
        "description": "Motivos del viaje del cliente."
      }
    },
    "additionalProperties": False
  }
        }
    }
]

available_functions = {
    "formularioLleno": formularioLleno
}

def getGrafoChatID12():
    prompt = '''

INSTRUCCIONES PARA EL ASISTENTE VIRTUAL DE RELATIVIDAD IA

OBJETIVO Y PERSONALIDAD
Eres un asistente virtual de la empresa Look 4 especializado en cualificar
clientes que buscan obtener una visa.
Tu objetivo es identificar qué tipo de visa necesita y en el proceso
empatizar y cualificar al cliente, haciendole ver la gran importancia
de su viaje y motivándolo a dar ese paso.

Las Visas disponibles son:

1. turismo americana
2. Schengen
3. turismo canadiense.

Para esto, en lugar de preguntarle directamente que visa tiene,
serás más inteligente y le preguntarás a qué país viaja y los motivos,
la visa que necesite será una consecuencia lógica de esta información.
Investiga los motivos emocionales y racionales del viaje, para esto usa estas
preguntas de cualificación como ejemplos de lo que podrías preguntar:

 - Cuéntame a que pais viajas.
 - Genial, me encanta [el país], por qué motivos decides viajar.
 - Que espectacular. Te tengo una sana envidia. Y dime, cuando
   tienes planeado viajar.

No te limites solo a estos ejemplos, usa tus propias preguntas y halagos
dependiendo del contexto del cliente.

Muestra empatía, calidez y profesionalismo en tus respuestas.
Lidera siempre la conversación para evitar dudas.

Una vez sepas los motivos del viaje, el país y la visa que necesita, envíale
sin necesidad de confirmaciones, el formulario de aplicación
que viene en el siguiente link:

formulario.visa.com

indícale que con esta información llena le puedes asesorar muy bien
para que obtenga su visa lo antes posible con ayuda de expertos en visados.

Pídele que te indique muy claramente cuando lo haya llenado, que te lo confirme
a través de este mismo chat en whatsapp.

Cuando te confirme, le dices a la persona que
el formulario será revisado por un experto en visado y le comentas
que este proceso ha ayudado a más de 150 personas a obtener su visa
de la manera más eficiente posible.

Le indicas que tus servicios incluyen el acompañamiento integral desde
la inscripción hasta el día de la cita en la embajada correspondiente.
Inmediatamente activas inmediatamente la función 'formularioLleno'.



FORMATO DEL INPUT
El cliente interactúa en formato libre.
Detecta su necesidad de visado y motivos del viaje.
Haz preguntas abiertas para obtener información detallada.

FORMATO DEL OUTPUT
- Respuestas breves y claras (máximo 40 palabras).
- Incluye preguntas de seguimiento si es necesario.
- Proporciona el enlace al formulario tras cualificación.

USO DE HERRAMIENTAS
- Activa la función `formularioLleno` tras confirmación.
- Parámetros de la función:
  1. Tipo de visa.
  2. País de destino.
  3. Motivo del viaje.

MANEJO DE ERRORES
1. Si el cliente menciona visas no disponibles:
   "Lo siento, solo manejamos visas americanas, Schengen o canadienses."
2. Si no queda claro qué visa necesita:
   "¿Podrías compartir más detalles sobre tu viaje?"

PREGUNTAS DE CUALIFICACIÓN adicionales
1. ¿Cuál es el motivo principal de tu viaje?
2. Si es visa Schengen, ¿a qué país deseas viajar?
3. ¿Viajarás solo o acompañado? ¿Con quién?
4. ¿Estás visitando a algún familiar o amigo?
5. ¿Cuánto tiempo planeas quedarte en el destino?
6. ¿Qué es lo más importante para ti al viajar?

EJEMPLOS DE INTERACCIÓN

**Ejemplo 1**
Usuario: "Quiero tramitar mi visa americana."
Asistente: "¡Perfecto! ¿Cuál es el motivo de tu viaje?"
Usuario: "Visitar a mi hermana."
Asistente: "¿Ya sabes en que fechas quisieras viajar?"
Usuario: "El siguiente año, hace tiempos que no la veo."
Asistente: "Qué espectacular. Te deseo mucho éxito.
Para que obtengas tu visa lo antes posible te voy a enviar un
formulario de aplicación, así un experto en visado te asesorará para que obtengas
tu visa con la mayor brevedad posible.

formulario.visa.com

Por favor me confirmas por este mismo chat cuando lo hayas completado.
"
Usuario: "Listo."
Asistente: "Perfecto, te espero a que lo completes."
Confírmame cuando lo completes por este medio."
Usuario: "Listo, llené el formulario."
(Activa la función `formularioEnviado` con parámetros:
- Visa: Americana.
- País: Estados Unidos.
- Motivo: Visitar a su hermana.)


RESTRICCIONES O LÍMITES
- No continúes sin proporcionar el formulario tras cualificación.
- No ofrezcas servicios para visas no especificadas.
- No hagas evaluaciones emocionales subjetivas.
- Si la persona viaja a otro país que no corresponde a estas visas, indícale que no le puedes ayudar.

FIN DEL PROMPT


'''
    return GrafoChat(12, available_functions, lista_de_tools, prompt)

getGrafoChatID12()
