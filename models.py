from pydantic import BaseModel
from typing import List, Optional, Dict, Union, Any

# Definir el modelo para la función llamada por el tool call
class Function(BaseModel):
    arguments: str
    name: str
    class Config:
        arbitrary_types_allowed = True
        

# Definir el modelo para cada tool call
class ChatCompletionMessageToolCall(BaseModel):
    id: str
    function: Function
    type: str
    class Config:
        arbitrary_types_allowed = True
        
# Actualizar ChatCompletionMessage para usar estos modelos
class ChatCompletionMessage(BaseModel):
    content: Optional[str] = None
    role: str
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: List[ChatCompletionMessageToolCall]
    class Config:
        arbitrary_types_allowed = True
        

class ChatMessage(BaseModel):
    role: str
    content: str
    tool_call_id: str = None
    name: str = None

class ChatInput(BaseModel):
    messages: List[Union[ChatMessage, ChatCompletionMessage]] = []
    chatID: int
    identificador: str