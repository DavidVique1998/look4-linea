
from modulos.grafoChats.grafoChat import *

async def DetectarSiElUsuarioDeseaCorregirNombre(identificador=""):
    idDelGrafoChatConNombre = 8
    await ttl_users.add_or_update_user(identificador, {"idPrevio": 9})
    await ttl_users.add_or_update_user(identificador, {"redirreccion": True})
    await ttl_users.add_or_update_user(identificador, {"chatID": idDelGrafoChatConNombre})


    return f"Es necesario volver a obtener el nombre del usuario"

lista_de_tools = [
        {
            
            "type": "function",
            "function": {
                "name": "DetectarSiElUsuarioDeseaCorregirNombre",
                "description": "Esta funcion se llama cuando el usuario desea corregir el nombre que ha dado o cuando dice que te lo dio mal",
            }
        }
        ]

available_functions = {
            "DetectarSiElUsuarioDeseaCorregirNombre":DetectarSiElUsuarioDeseaCorregirNombre
        }

def getGrafoChatID10():

    prompt = """Eres un asistente virtual tu trabajo es que cuando el usuario te diga que te dio mal su nombre, que necesita corregirlo, vas a detectarlo"""

    return GrafoChat(10, available_functions, lista_de_tools, prompt, False, True, True)
getGrafoChatID10()