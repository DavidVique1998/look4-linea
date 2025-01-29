
from modulos.grafoChats.grafoChat import *

async def extraerNombre(nombreCompleto, identificador=""):
    redirrecion = await ttl_users.get_user_key(identificador, "redirreccion")

    if redirrecion == True:
        idPrevio = await ttl_users.get_user_key(identificador, "idPrevio")
        await ttl_users.add_or_update_user(identificador, {"chatID": idPrevio})
        await ttl_users.delete_user_key(identificador, "idPrevio")
        await ttl_users.delete_user_key(identificador, "redirreccion")

    else:
        await ttl_users.add_or_update_user(identificador, {"chatID": 9})

    return f"El nombre {nombreCompleto} se ha extraido"

lista_de_tools = [
        {
            
            "type": "function",
            "function": {
                "name": "extraerNombre",
                "description": "Esta funcion extra el nombre del usuario cuando el te lo menciona",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nombreCompleto": {
                            "type": "string",
                            "description": "Nombre del usuario"
                        },
                    },
                    "additionalProperties": False,
                    "required": ["nombreCompleto"]
                }
            }
        }
        ]

available_functions = {
            "extraerNombre":extraerNombre
        }

def getGrafoChatID8():

    prompt = """Eres un asistente virtual de Look4, apenas inicies la conversacion con el usuario vas a presentarte como tal y a preguntar por nombre.
    Puedes usar emojis solo algunas veces para hacer la conversacion mas calida
    """

    return GrafoChat(8, available_functions, lista_de_tools, prompt)
getGrafoChatID8()