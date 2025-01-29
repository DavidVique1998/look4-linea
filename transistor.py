from dotenv import load_dotenv
import os
load_dotenv()  # Carga variables desde el archivo .env

from models import *
from fastapi.responses import StreamingResponse
from modulos.grafoChats.grafoChat import GrafoChat 
import recopilador
from fastapi import FastAPI, HTTPException, Depends, Body, Request  
from pydantic import BaseModel
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
import json
from usersTTL import ttl_users
import requests
from PyPDF2 import PdfReader
from pprint import pprint
import re
import asyncio
import random
import uvicorn


grafoChats = GrafoChat.grafoChats

app = FastAPI()



origins = ["http://127.0.0.1:5500", 
           "http://0.0.0.0:8000",
           "http://localhost:3000",
           "http://localhost:3001",
           "http://192.168.100.92:5500"]  # Adjust as per your CORS needs

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los dominios
    allow_methods=["*"],   # Permitir todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],   # Permitir todos los encabezados
    allow_credentials=True # Permitir credenciales (si es necesario)
)


openai = OpenAI()

api_keys = [
    "c5435fd0-hrry-4617-krpn-9ffb829e7513",
    "ec9bcba1-tfwk-9799-rslv-378aae060441",
    "94705224-bhvg-4745-mac7-f15c455858f4"
]

api_key_header = APIKeyHeader(name='Psico-API-Key')


def numero_aleatorio_positivo_negativo(n):
    # Genera un número aleatorio entre 1 y n
    numero = random.randint(1, n)
    
    # Decide aleatoriamente si el número será positivo o negativo
    if random.choice([True, False]):
        return numero
    else:
        return -numero
    

def contar_paginas_pdf(url):
    try:
        # Descargar el archivo
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error si la descarga falla
        
        # Guardar el archivo temporalmente
        with open("temp_document.pdf", "wb") as temp_file:
            temp_file.write(response.content)
        
        # Leer el documento con PyPDF2
        reader = PdfReader("temp_document.pdf")
        num_paginas = len(reader.pages)
        
        # Eliminar el archivo temporal (opcional)
        import os
        os.remove("temp_document.pdf")
        
        return num_paginas
    except Exception as e:
        return f"Error al procesar el documento: {e}"

async def updateMessagesWithSystem(identificador, systemMsg):
    identificador += "@s.whatsapp.net"
    messages = await ttl_users.get_user_key(identificador, "messages")
    if messages == None:
        messages = await get_messages(identificador)
    messages.append({"role":"system", "content":systemMsg})
    return messages
    

def delete_chat(chat_id):
    url = f"https://gate.whapi.cloud/chats/{chat_id}"
    token = "orL40u4yiReW6m0NmDTJdMemLNQpWqfA"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 200:
        print(f"Chat {chat_id} eliminado correctamente.")
    else:
        print(f"Error al eliminar el chat {chat_id}: {response.status_code} - {response.text}")


async def procesarComando(mensaje):
    chat_ID_for_admin = '120363376341151112@g.us'


    textUser = mensaje.get('text', None)
    if textUser == None:
        return
    mensajeUsr = textUser.get('body', None)

    if mensajeUsr == None:
        return

    contexto = mensaje.get('context', None)
    if contexto == None:
        enviar_mensaje_whatsapp(chat_ID_for_admin, "Por favor, para ejecutar un comando debes responder al mensaje.")
        return
    msgCitado = contexto.get('quoted_content', None)
    if msgCitado == None:
        return 
    msgComando = msgCitado.get('body', None)
    if msgComando == None:
        return
    print(msgComando)

    # Expresión regular para encontrar el texto entre []
    patron = r'\[([^]]+)\]'

# Buscar todas las coincidencias
    resultados = re.findall(patron, msgComando)
    print(resultados)
    if len(resultados) == 0:
        enviar_mensaje_whatsapp(chat_ID_for_admin, "El mensaje al que se respondió no corresponde a un mensaje de comando.")
        return
    accion = resultados[0]
    if accion == "CONECTAR":
        await ttl_users.add_or_update_user(resultados[1], {"desconectado": False, "chatID":8})
        enviar_mensaje_whatsapp(chat_ID_for_admin, f"El número {resultados[1]} se ha conectado exitosamente")
    if accion == "TRANSFERENCIA/ASSESMENT":
        if mensajeUsr == '1':
            userMesgs = await updateMessagesWithSystem(resultados[1], "La transferencia del usuario ha sido validada.")
            response = await grafoChatsAPI({"messages":userMesgs, "identificador":resultados[1], "chatID":15})
            enviar_mensaje_whatsapp(resultados[1], response['response'])
            enviar_mensaje_whatsapp(chat_ID_for_admin, f"Se le ha indicado al cliente {resultados[1]} que su transferencia ha sido validada.")
        if mensajeUsr == '2':
            userMesgs = await updateMessagesWithSystem(resultados[1], "La transferencia del usuario no ha sido reconocida, que porfavor la verifique y la reenvíe.")
            response = await grafoChatsAPI({"messages":userMesgs, "identificador":resultados[1], "chatID":15})
            enviar_mensaje_whatsapp(resultados[1], response['response'])
            enviar_mensaje_whatsapp(chat_ID_for_admin, f"Se le ha indicado al cliente {resultados[1]} que su transferencia no ha sido reconocida, que porfavor la verifique y la reenvíe.  ")
    if accion == "TRANSFERENCIA/TRADUCCIONES":
        if mensajeUsr == '1':
            userMesgs = await updateMessagesWithSystem(resultados[1], "La transferencia del usuario ha sido validada.")
            response = await grafoChatsAPI({"messages":userMesgs, "identificador":resultados[1], "chatID":13})
            enviar_mensaje_whatsapp(resultados[1], response['response'])
            enviar_mensaje_whatsapp(chat_ID_for_admin, f"Se le ha indicado al cliente {resultados[1]} que su transferencia ha sido validada.")
        if mensajeUsr == '2':
            userMesgs = await updateMessagesWithSystem(resultados[1], "La transferencia del usuario no ha sido reconocida, que porfavor la verifique y la reenvíe.")
            response = await grafoChatsAPI({"messages":userMesgs, "identificador":resultados[1], "chatID":13})
            enviar_mensaje_whatsapp(resultados[1], response['response'])
            enviar_mensaje_whatsapp(chat_ID_for_admin, f"Se le ha indicado al cliente {resultados[1]} que su transferencia no ha sido reconocida, que porfavor la verifique y la reenvíe.  ")


        print(mensajeUsr)
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



def enviar_documento_whatsapp(to, media):
    # URL del endpoint para enviar documentos
    url = "https://gate.whapi.cloud/messages/document"
    
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
        "media": media,
    }
    
    # Realizar la solicitud POST
    response = requests.post(url, json=payload, headers=headers)
    
    # Verificar la respuesta
    if response.status_code == 200:
        print("Documento enviado con éxito!")
        print("Respuesta:", response.json())
    else:
        print("Error al enviar el documento.")
        print("Código de estado:", response.status_code)
        print("Respuesta:", response.text)

def get_api_key(api_key: str = Depends(api_key_header)) -> str:
    if api_key in api_keys:
        return api_key
    else:
        raise HTTPException(
            status_code=HTTPException.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )


async def get_messages(chat_id, count=20, offset=None, time_from=None, time_to=None, normal_types=None, author=None, from_me=None, sort=None):
    url = f"https://gate.whapi.cloud/messages/list/{chat_id}"
    headers = {
        "Authorization": "Bearer orL40u4yiReW6m0NmDTJdMemLNQpWqfA",
        "Content-Type": "application/json"
    }
    params = {
        "count": count,
        "offset": offset,
        "time_from": time_from,
        "time_to": time_to,
        "normal_types": normal_types,
        "author": author,
        "from_me": from_me,
        "sort": sort
    }
    
    # Removiendo parámetros que sean None
    params = {key: value for key, value in params.items() if value is not None}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        print("LA OBTENCION DE MENSAJES FUE EXITOSA")
        mensajesOpenAI = [{}]
        response = response.json()
        mensajesWhatsApp = response['messages']
        
        mensajesWhatsApp.reverse()
        print(mensajesWhatsApp)
        for mensaje in mensajesWhatsApp:
            role = ''
            content = ''
            if mensaje['from_me'] == False:
                role = 'user'
            else:
                role = 'assistant'
            
            textContainer = mensaje.get('text', None)
            if textContainer != None:
                content = textContainer.get('body', "")
            if content != '':
                mensajesOpenAI.append({"role": role, "content": content})


            imageContainer = mensaje.get("image", None)
            if imageContainer != None:
                link = imageContainer.get('link', None)
                caption = imageContainer.get('caption', None)
                content = []
                if caption != None:
                    imgtext = {
            "type": "text",
            "text": caption
        }           
                    content.append(imgtext)

                if link != None:
                    img = {
            "type": "image_url",
            "image_url": {
            "url": link,
            "detail": "high"
            }
                    }
                    content.append(img)
                mensajesOpenAI.append({"role":"user", "content": content})
                content = f"El link de la imagen previa es {link}"
                mensajesOpenAI.append({"role":"system", "content":content})
            document = mensaje.get('document', None) 
            if document != None:
                link = document.get('link', None)
                if link != None:
                    paginas = contar_paginas_pdf(link)
                    content = f"El usuario adjunto un documento de {paginas} paginas. Este es el link del documento previo {link}"
                    mensajesOpenAI.append({"role":"system", "content":content})

        print(mensajesOpenAI)
            
        


        return mensajesOpenAI
    else:
        return {"error": response.status_code, "message": response.text}
    


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


@app.get('/')
async def index():
    return {'message': 'API is Up and Running!'}


@app.post("/policia")
async def grafoChatsAPI(input_data: ChatInput):
    print(input_data)

    datosUser = {"messages": input_data['messages'], "chatID": input_data['chatID']}

    idt = input_data['chatID']
    user = input_data['identificador']
   
    await ttl_users.add_or_update_user(user, datosUser)

    if input_data['chatID'] in [13, 12, 11]:
       responseFake, chatIdFake = await GrafoChat.grafoChats[14].run_conversation(user)

    
    response, chatId = await grafoChats[idt].run_conversation(user)
    return { "response": response , "chatID":chatId}

async def waitAndRespond(identificador, ultimoMensaje):
    print("iniciado")
    numero = 30 + numero_aleatorio_positivo_negativo(20)
    await asyncio.sleep(numero)
    chatID = await ttl_users.get_user_key(identificador, "chatID")
    if chatID == None:
        chatID = 9
    print("FUNCIONANDO")
    mensajes = await get_messages(ultimoMensaje['chat_id'])
    print(mensajes)
    response = await grafoChatsAPI({"messages":mensajes, "identificador":identificador, "chatID":chatID})
    respuesta = response['response']  
    await enviar_mensaje_whatsapp(identificador, respuesta)

@app.post("/messages")
async def postMessage(request: Request):
    body = await request.json()
    numberRootID = "593992722256"
    print(body)
    mensaje = body['messages']
    ultimoMensaje = mensaje[0]

    chat_ID_for_admin = '120363376341151112@g.us'
    identificador = ultimoMensaje['from']
    
    if ultimoMensaje['chat_id'] == chat_ID_for_admin and ultimoMensaje['source'] != 'api' and ultimoMensaje['source'] != 'system':
        print("Ejecutando comando")
        await procesarComando(ultimoMensaje)

    if ultimoMensaje['from'] == numberRootID and ultimoMensaje['source'] != 'api' and ultimoMensaje['source'] != 'system' and ultimoMensaje['chat_id'] != chat_ID_for_admin:
        
        chatIDWHO =ultimoMensaje['chat_id']
        chatIDWHO = chatIDWHO.replace("@s.whatsapp.net", "")

        mensaje= f"""ACCION: [CONECTAR] \nQUIEN: [{chatIDWHO}]\n\nPor favor, responde a este mensaje para conectar el bot con este número.
        """

        enviar_mensaje_whatsapp(chat_ID_for_admin, mensaje)
        timer = await ttl_users.get_user_key(chatIDWHO, "timer")

        if timer != None:
            timer.cancel()

        await ttl_users.add_or_update_user(chatIDWHO, {"desconectado": True})
    
    try:
        textContainer = ultimoMensaje.get('text', None)
        if textContainer != None:
            content = textContainer.get('body', "")
            if content != '':
                if content == 'cocoloco':
                    print("COCOLOCO")
                    delete_chat(ultimoMensaje['chat_id'])
                    await ttl_users.add_or_update_user(identificador,{"messages": None, "chatID": 9})
                    return {"message": "Success deleting"} 
            
        print("xd")
        
        if ultimoMensaje['from_me'] != True  and ultimoMensaje['source'] != 'system' and ultimoMensaje['chat_id'] != chat_ID_for_admin: 
            desconexion = await ttl_users.get_user_key(identificador, "desconectado")
            if desconexion == True:
                print("DESONECCTADO")
                return {"message": "Success, desconectado"}
            else:
                timer = await ttl_users.get_user_key(identificador, "timer")
                if timer == None:
                    
                    await ttl_users.add_or_update_user(identificador, {"timer":asyncio.create_task(waitAndRespond(identificador, ultimoMensaje))})
                else:
                    timer.cancel()
                    print("cancelado")
                    await ttl_users.add_or_update_user(identificador, {"timer":asyncio.create_task(waitAndRespond(identificador, ultimoMensaje))})

    except Exception as e:
        print(e)
    return {"message": "Success"}

@app.get("/test")
async def test_endpoint():
    return {"status": "success", "message": "¡Tu API en Vercel funciona correctamente!"}
        

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)