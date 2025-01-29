var conversations = {}; 
// Definición de la base URL para la API de FastAPI
const URL_BASE = "http://127.0.0.1:8000/procesoLineal";

// Prompt de entrenamiento para configurar el contexto de la conversación
const training_prompt = `
Eres Emilio Einstein, una mezcla entre un matemático puro y Albert
`;

const training_prompt_1 = `
Eres Emilio, un entrenador Fitness
`;
const training_prompt_2 = `
Eres Emilio un experto en alimentación deportiva.
`;



document.addEventListener('DOMContentLoaded', function () {
    cargarChat('1',training_prompt);
    cargarChat('2',training_prompt_1);
    cargarChat('3',training_prompt_2);
    cargarChat('4',training_prompt);
    cargarChat('5',training_prompt);
    cargarChat('6',training_prompt);

});



