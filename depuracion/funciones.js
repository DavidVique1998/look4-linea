function handleFormSubmit(event,chat_id) {
    event.preventDefault();
    sendMessage(chat_id);
}


function inicializarChat(chat_id) {
    console.log("Inicializando eventos del chat...");

    const promptForm = findElementByClassAndDataChatNumber('chat-form', chat_id);
    console.log("Formulario encontrado:", promptForm);
    if (promptForm) {
        promptForm.addEventListener("submit", handleFormSubmit);

        // Prevenir que el formulario se envíe con la tecla Enter, pero llamar a sendMessage directamente
        promptForm.addEventListener("keydown", function(event) {
            if (event.key === "Enter") {
                event.preventDefault(); // Prevenir el comportamiento predeterminado de la tecla Enter
                sendMessage(chat_id); // Llamar a la función de enviar mensaje
            }
        });
    } else {
        console.error("El formulario 'promptForm' no se encontró en el DOM.");
    }

    const clearButton = document.querySelector('.btn-clear');
    console.log("Botón de limpieza encontrado:", clearButton);
    if (clearButton) {
        clearButton.addEventListener("click", () => resetConversation(chat_id));
    } else {
        console.error("El botón 'btn-clear' no se encontró en el DOM.");
    }
}

function cargarChat(id, training_prompt) {
    // URL del contenido HTML a cargar dinámicamente
    const url = `chat-container-${id}.html`
    var chat_id = id

    // Puedes colocar el resto de tu código JavaScript aquí
    // Inicializamos la historia de conversación para este chat_id específico
    conversations[chat_id] = [
    { role: "system", content: training_prompt }
    ];  
    // Selecciona el contenedor donde cargar el contenido
    const chatContainer = findElementByClassAndDataChatNumber('chat-box', chat_id);

    // Usar fetch para cargar el contenido HTML desde la URL
    fetch(url)
        .then(response => response.text())
        .then(html => {
            // Inserta el HTML en el contenedor
            chatContainer.innerHTML = html;

            // Encuentra todos los elementos dentro del contenedor y agrega el atributo data-chat-number
            addDataChatNumber(chatContainer, chat_id);

            inicializarChat(chat_id); // Se confirma que esta línea se ejecuta con el mensaje de consola.
            // Inicializar la conversación al cargar la página
            // Esperamos a que el DOM se cargue completamente
            // Ejemplo de uso
            const foundElement = findElementByClassAndDataChatNumber('chat-messages', chat_id);
            if (foundElement) {
                console.log('Elemento encontrado:', foundElement);
            } else {
                console.log('Elemento no encontrado.');
            }
            renderConversationHistory(chat_id);
        })
        .catch(error => console.error('Error al cargar el chat:', error));
}

// Función para agregar el atributo data-chat-number a todos los elementos dentro del contenedor
function addDataChatNumber(container, chat_id) {
    // Selecciona todos los elementos dentro del contenedor
    const elements = container.querySelectorAll('*');

    // Agrega el atributo data-chat-number a cada elemento
    elements.forEach(element => {
        element.setAttribute('data-chat-number', chat_id);
    });
}






// Función para renderizar el historial de la conversación en la interfaz
function renderConversationHistory(chat_id) {

    let conversationElement = findElementByClassAndDataChatNumber('chat-messages', chat_id);
    if (conversationElement) {
        // Limpiar la conversación actual y añadir los nuevos mensajes aquí
        conversationElement.innerHTML = ''; // Ahora seguro de que conversationElement no es null.
        // Añadir mensajes...
    } else {
        console.error("El elemento 'apiResponse' no se encontró en el DOM.");
    }
    


    conversations[chat_id].filter(message => message.role !== "system" && message.role !== "tool" && message.function_call === undefined && message.tool_calls === undefined).forEach(message => {
        let messageElement = document.createElement("div");
        messageElement.classList.add('message-bubble');
        messageElement.classList.add(message.role === "user" ? "user" : "assistant");

        if (message.content.startsWith("escribiendo")) {
            messageElement.classList.add("writing");
        }

        messageElement.innerText = message.content;
        conversationElement.appendChild(messageElement);
    });

    let lastMessageElement = conversationElement.lastChild;
}

// Función para resetear la conversación
function resetConversation(chat_id) {
    findElementByClassAndDataChatNumber('form-control', chat_id).value = '';
    findElementByClassAndDataChatNumber('chat-messages', chat_id).innerHTML = ''; // Limpiar la visualización de la conversación
    conversations[chat_id] = [{ role: "system", content: training_prompt }]; // Reiniciar con el prompt de entrenamiento
    renderConversationHistory(chat_id);
}




chatIDFuncional = 9;
// Función para enviar mensajes
function sendMessage(chat_id) {
    let userPrompt = findElementByClassAndDataChatNumber('form-control', chat_id).value.trim();
    if (userPrompt === '') return; // No enviar mensajes vacíos

    conversations[chat_id].push({ role: "user", content: userPrompt });
    renderConversationHistory(chat_id);

    let dots = "";
    let writingIndex = conversations[chat_id].length; // Índice para la burbuja "escribiendo..."
    conversations[chat_id].push({ role: "assistant", content: `escribiendo${dots}` });
    renderConversationHistory(chat_id);

    let writingInterval = setInterval(() => {
        dots = dots.length < 3 ? dots + "." : "";
        conversations[chat_id][writingIndex] = { role: "assistant", content: `escribiendo${dots}` };
        renderConversationHistory(chat_id);
    }, 500); // Actualiza cada 500 ms

    findElementByClassAndDataChatNumber('form-control', chat_id).value = '';

    let dictTemas = {
        1.01: 5, 1.02: 5, 1.03: 5, 1.04: 5
    }
    let dataToSend = {
        messages: conversations[chat_id].slice(0, -1), // Excluir "escribiendo..."
        "chatID": chatIDFuncional,
        "identificador": "Enrique"
    };

    fetch(URL_BASE, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'Psico-API-Key': '94705224-bhvg-4745-mac7-f15c455858f4'
        },
        body: JSON.stringify(dataToSend)
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(writingInterval); // Detener el intervalo de "escribiendo..."
        conversations[chat_id].splice(writingIndex, 1); // Eliminar "escribiendo..."
        let lastMessages = data.messages
        let ultimoMensaje = lastMessages[lastMessages.length - 1];
        if (!conversations[chat_id].find(m => m.content === ultimoMensaje)) {
            conversations[chat_id] = lastMessages
            console.log(conversations[chat_id])
        }
        chatIDFuncional = data.chatID;
        renderConversationHistory(chat_id);
    })  
    .catch((error) => {
        clearInterval(writingInterval); // Detener el intervalo de "escribiendo..." en caso de error
        console.error('Error:', error);
        // Remover la burbuja "escribiendo..." y mostrar error
        conversations[chat_id].splice(writingIndex, 1); // Eliminar "escribiendo..."
        conversations[chat_id].push({ role: "assistant", content: `Error: ${error}` });
        renderConversationHistory(chat_id);
    });
}

function findElementByClassAndDataChatNumber(className, dataChatNumber) {
    // Construye el selector combinando la clase y el atributo data-chat-number
    const selector = `.${className}[data-chat-number="${dataChatNumber}"]`;
    
    // Utiliza querySelector para buscar el elemento en el documento
    const element = document.querySelector(selector);
    
    // Retorna el elemento encontrado o null si no se encuentra ninguno
    return element;
}