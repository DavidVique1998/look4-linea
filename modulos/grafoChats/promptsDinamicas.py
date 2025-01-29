from usersTTL import ttl_users


async def recargarPrompt(ID, identificador):
    funcion_nombre = f'recargarPromptID{ID}'
    if funcion_nombre in globals():
        return await globals()[funcion_nombre](identificador)
    else:
        print("La función no existe.")
        raise Exception("Función de prompt dinámica, no ha sido creada")

async def getPromptDinamica(ID, identificador):
    return await recargarPrompt(ID, identificador)

async def recargarPromptID4(identificador):
    #Esto solo va a funcionar si identificador es un nombre
    prompt = f"Eres el asistente personal de {identificador}. Cuando la conversacion inicie, saludalo por su nombre"
    return prompt