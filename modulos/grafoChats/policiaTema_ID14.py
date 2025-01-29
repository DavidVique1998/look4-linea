from modulos.grafoChats.grafoChat import *



cambiosIDS = {
    1:11,
    2:12,
    3:13
}

async def DetectarSiElUsuarioDeseaCambiarEleccion(eleccion, identificador=""):

    idDelGrafoChatEleccion = cambiosIDS[eleccion]
    idActual = await ttl_users.get_user_key(identificador, "chatID")

    if idDelGrafoChatEleccion == idActual:
        return "No hubo cambio"


    await ttl_users.add_or_update_user(identificador, {"idPrevio": idActual})
    await ttl_users.add_or_update_user(identificador, {"redirreccion": True})
    await ttl_users.add_or_update_user(identificador, {"chatID": idDelGrafoChatEleccion})

    return f"El usuario ha solicitado cambiar su elección, redirigiendo al ID {idDelGrafoChatEleccion}."
#
lista_de_tools = [
    {
        "type": "function",
        "function": {
            "name": "DetectarSiElUsuarioDeseaCambiarEleccion",
            "description": "Esta función se llama cuando el usuario quiere cambiar su elección sea porque se equivocó anteriormete o quiere otro seleccionar otro proceso en vez del actual.",
            "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "eleccion": {
                            "type": "number",
                            "enum": [1, 2, 3],
                            "description": """
                            Valor entero que representa la elección al que el usuario se quiere cambiar
                            1: Assesments
                            2: Visas 
                            3: Traducciones

                            En donde cada entero se le asigna con los dos puntos la elección que quiere tomar el usuario
                            """
                        },
                    },
                    "additionalProperties": False,
                    "required": ["eleccion"]
                }
            }
        }]

available_functions = {
    "DetectarSiElUsuarioDeseaCambiarEleccion": DetectarSiElUsuarioDeseaCambiarEleccion
}

def getGrafoChatID14():
    prompt = """Eres un asistente virtual. Cuando el usuario indique que desea cambiar su elección previa, sea porque se equivoco o porque solo desea cambiar de proceso, vas a detectarlo. Por ejmplo como cambiar de visa a traducciones debes detectarlo.
        Tu trabajo es que cuando el usuario te diga que te dio mal su eleccion del tema que necesita informacion, que necesita corregirlo, vas a detectarlo"""
    

    return GrafoChat(14, available_functions, lista_de_tools, prompt, False, True, True)

getGrafoChatID14()
#jaja dejaste la compu encendida luisa