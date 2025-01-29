from openai import AsyncOpenAI
from models import *
from usersTTL import ttl_users
import json
import modulos.grafoChats.promptsDinamicas as promptsDinamicas
import re
import numpy as np


async def eliminarDecoraciones(texto):
    patrones = ['f{',  '}', '{f', '**', '### ', '###', '"', "'", '{', 'extit']
    for patron in patrones:
        texto = texto.replace(patron, '')
    return texto


async def reemplazarIniciosLatex(texto):
    # Reemplazar los inicios de expresiones LaTeX comunes por "$"
    inicios = [r"\(", r"\)", r"\[", r"\]", "$$"]
    
    for expression in inicios:
        texto = texto.replace(expression, "$")
    
    patronesTextuales = ['**', '### ', '###', '"']

    for patron in patronesTextuales:
        texto = texto.replace(patron, "")
        
    return texto 


async def limpiar_json(arguments):
    # Función para limpiar el JSON antes de intentar decodificarlo
    try:
        # Intentamos decodificar el JSON para verificar su validez
        json.loads(arguments)
        return arguments
    except json.JSONDecodeError as e:
        # Limpiamos el JSON de caracteres no válidos
        print(f"Error decoding JSON at position {e.pos}: {e.msg}")
        print(f"Invalid JSON segment: {arguments[e.pos-20:e.pos+20]}")
        # Aquí se puede implementar una limpieza más específica
        cleaned_arguments = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', arguments)
        return cleaned_arguments



client = AsyncOpenAI()  # Use your OpenAI API key


class GrafoChat:
    grafoChats = {}
    def __init__(self, id, available_functions, lista_de_tools, prompt, tienePromptDinamica=False, paralelo=False, policia = False, parallel_calls = True, temperature = 1, top_p = 1):
        self.id = id
        self.available_functions = available_functions
        self.lista_de_tools = lista_de_tools
        self.prompt = prompt
        self.tienePromptDinamica = tienePromptDinamica
        self.paralelo = paralelo
        self.policia = policia
        self.parallel_calls = parallel_calls
        self.temperature = temperature
        self.top_p = top_p

        GrafoChat.grafoChats[id] = self
        
        

    async def set_prompt(self, identificador):

        if (self.tienePromptDinamica):
            new_prompt = await promptsDinamicas.getPromptDinamica(self.id, identificador)
            await self.update_prompt(new_prompt)
        await ttl_users.update_lista_de_mensajes(identificador, "messages", {"role":"system", "content":self.prompt})
        


    async def update_prompt(self, nueva_prompt):
        self.prompt = nueva_prompt

    async def run_conversation(self, identificador):
        print("RUN CORRRE")

        userChatID = await ttl_users.get_user_key_DEEP_COPY(identificador, "chatID")
        if userChatID != self.id and self.paralelo == False:
            print(f"DISONANCIA  desde {self.id} a {userChatID} ")
            return await GrafoChat.grafoChats[userChatID].run_conversation(identificador)
            
        
        else:
            
            await self.set_prompt(identificador)

            messages = await ttl_users.get_user_key(identificador, "messages")
            

            if (self.lista_de_tools != None and self.available_functions != None):

                tools = self.lista_de_tools
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    temperature=self.temperature,
                    top_p= self.top_p,
                    messages=messages,
                    tools=tools,
                    tool_choice= "auto",
                    parallel_tool_calls = self.parallel_calls
                )
                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls
                if tool_calls:

                    await ttl_users.append_to_user_list(identificador, "messages", response_message)
                    for tool_call in tool_calls:
                        function_name = tool_call.function.name
                        function_to_call = self.available_functions[function_name]
                        arguments = await limpiar_json(tool_call.function.arguments)
                        try:
                            function_args = json.loads(arguments)
                            function_args.update({"identificador": identificador})
                        
                        except json.JSONDecodeError as e:
                            print(f"Error decoding cleaned JSON at position {e.pos}: {e.msg}")
                            raise
                        #print(f"ARGS: {function_args}")
                        function_response = await function_to_call(**function_args)
                        print(function_response)
                        function_response = await eliminarDecoraciones(function_response)

                        registroDeLlamada = {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": function_response,
                            }
                        
                        await ttl_users.append_to_user_list(identificador, "messages", registroDeLlamada)
                    messages = await ttl_users.get_user_key(identificador, "messages")
                    second_response = await client.chat.completions.create(
                        model="gpt-4o-mini",
                        temperature=self.temperature,
                        top_p= self.top_p,
                        messages=messages,
                    )  
                    userChatID = await ttl_users.get_user_key_DEEP_COPY(identificador, "chatID") 
                    #print(f"USER CHAT ID: {userChatID}")
                    if userChatID != self.id and self.paralelo == False:
                        print(f"DISONANCIA desde {self.id} a {userChatID} ")

                        return await GrafoChat.grafoChats[userChatID].run_conversation(identificador)   
                    else:    
                        if self.policia == True  :
                            return None, -1
                        
                        respuestaARegresar = second_response.choices[0].message.content
                        await ttl_users.append_to_user_list(identificador, "messages", {"role":"assistant", "content":respuestaARegresar})
                        return respuestaARegresar, userChatID
                if self.policia == True:
                    return None, -1
                
                respuestaARegresar = response_message.content

                respuestaARegresar = await eliminarDecoraciones(respuestaARegresar)


                await ttl_users.append_to_user_list(identificador, "messages", {"role":"assistant", "content":respuestaARegresar})
                
                return respuestaARegresar, userChatID
            else:
                if self.policia == True:
                    return None, -1
                response = await client.chat.completions.create(
                temperature=self.temperature,
                top_p= self.top_p,
                model="gpt-4o-mini", 
                messages=messages
                )
                respuestaARegresar = response.choices[0].message.content

                respuestaARegresar = await eliminarDecoraciones(respuestaARegresar)

                await ttl_users.append_to_user_list(identificador, "messages", {"role":"assistant", "content":respuestaARegresar})
                return  respuestaARegresar, userChatID
            

async def get_embedding(text, model="text-embedding-3-small"):
    embedding_response = await client.embeddings.create(input=[text], model=model)
    return embedding_response.data[0].embedding


async def cos_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

async def getProbability(input, expectedInput):
    vector_input = await get_embedding(input)
    vector_expected = await get_embedding(expectedInput)
    result = await cos_sim(vector_expected, vector_input)
    return result
