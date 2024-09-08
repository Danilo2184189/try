import google.generativeai as genai
import logging
import requests
import json
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from telegram.ext import ContextTypes

# Cargar variables desde el archivo .env
load_dotenv()

# Obtener las variables de entorno
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PAGE_ID = os.getenv("NOTION_PAGE_ID")

# Configura los logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configura la API Key de Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Inicializa el modelo de Gemini 1.5 Flash
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# URL de la API de Notion
NOTION_API_URL = f"https://api.notion.com/v1/blocks/{PAGE_ID}/children"

# Encabezados para la solicitud a Notion
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Función para agregar múltiples ideas como checklist a la página de Notion
def agregar_ideas_notion(ideas):
    children_blocks = [
        {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": idea.strip()
                        }
                    }
                ],
                "checked": False
            }
        }
        for idea in ideas  # Crea un bloque 'to_do' por cada idea
    ]
    
    data = {
        "children": children_blocks
    }
    
    response = requests.patch(NOTION_API_URL, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        logger.info("Ideas guardadas como checklist en Notion con éxito.")
    else:
        logger.error(f"Error al guardar las ideas en Notion: {response.status_code} - {response.text}")

# Función para procesar el audio y extraer ideas principales
async def procesar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    logger.info(f"Procesando audio enviado por el usuario con ID: {user_id}")

    audio_file = None

    # Verifica si el mensaje contiene un archivo de audio o un mensaje de voz
    if update.message.audio:
        logger.info("El usuario ha enviado un archivo de audio.")
        audio_file = await update.message.audio.get_file()
    elif update.message.voice:
        logger.info("El usuario ha enviado un mensaje de voz.")
        audio_file = await update.message.voice.get_file()
    else:
        logger.error("No se recibió un archivo de audio ni un mensaje de voz.")
        await update.message.reply_text("Por favor, envía un archivo de audio o un mensaje de voz.")
        return

    try:
        logger.info("Enviando el archivo de audio a Gemini para su procesamiento directamente...")

        # Obtener los bytes del archivo de audio
        audio_bytes = bytes(await audio_file.download_as_bytearray())  # Conversión a bytes

        # Crea el nuevo prompt para extraer ideas
        prompt = """Tu tarea es escuchar el audio proporcionado y extraer las ideas principales. 
        Organiza cada idea separada por una coma siguiendo el formato indicado.
        
        [IDEA1], [IDEA2], [IDEA3], etc.
        Ejemplo de respuesta:
        Innovación tecnológica con enfoque en IA, Sostenibilidad, Productividad"""

        # Enviar el archivo a Gemini
        response = model.generate_content([
            prompt,
            {
                "mime_type": "audio/mp3",  # Cambiar a mime_type adecuado según el archivo
                "data": audio_bytes
            }
        ], safety_settings={
            'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'block_none',
            'HARM_CATEGORY_HATE_SPEECH': 'block_none',
            'HARM_CATEGORY_HARASSMENT': 'block_none',
            'HARM_CATEGORY_DANGEROUS_CONTENT': 'block_none'
        })

        # Procesa las ideas extraídas
        ideas = response.text.split(',')
        logger.info(f"Ideas extraídas: {ideas}")

        # Agregar las ideas extraídas a Notion
        agregar_ideas_notion(ideas)

        # Envía la respuesta al chat de Telegram
        await update.message.reply_text(f"Ideas principales extraídas y enviadas a Notion: {', '.join(ideas)}")

    except Exception as e:
        logger.error(f"Error al procesar el archivo de audio con Gemini: {e}")
        await update.message.reply_text(f"Ocurrió un error al procesar el archivo de audio con Gemini.")

# Función principal para iniciar el bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Manejador de mensajes de audio y voz
    app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, procesar_audio))

    # Iniciar el bot
    logger.info("El bot ha iniciado correctamente.")
    app.run_polling()

if __name__ == '__main__':
    main()
