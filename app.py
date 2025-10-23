import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image, ImageOps
import numpy as np
from streamlit_drawable_canvas import st_canvas
from io import BytesIO

# --- Función de Codificación Robusta (Sin guardar archivos) ---
def image_to_base64(image):
    """Convierte un objeto PIL Image a una cadena Base64 (formato PNG)."""
    buffered = BytesIO()
    # Guardar el objeto Image (RGBA) en el buffer como PNG
    image.save(buffered, format="PNG") 
    encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return encoded_image

# --- Configuración de Streamlit y UI ---
st.set_page_config(page_title='Tablero Inteligente', page_icon='🎨')
st.title('🎨 Tablero Inteligente: Reconocimiento de Bocetos')

with st.sidebar:
    st.subheader("Acerca de:")
    st.markdown("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto usando modelos de Visión (OpenAI GPT-4o-mini).")
st.subheader("Dibuja el boceto en el panel y presiona el botón para analizarlo.")

# --- Panel de API Key ---
ke = st.text_input('🔑 Ingresa tu Clave (OpenAI API Key)')
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

# --- Canvas de Dibujo ---
drawing_mode = "freedraw"
# stroke_width se mantiene en el sidebar para interacción
stroke_width = st.sidebar.slider('Selecciona el ancho de línea', 1, 30, 5) 
stroke_color = "#000000"  
bg_color = '#FFFFFF'

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.0)",  # Fondo transparente para el dibujo
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

# --- Botón de Análisis ---
analyze_button = st.button("Analiza la imagen", type="primary")

# --- Lógica de Llamada a la API de OpenAI ---
if analyze_button:
    if not api_key:
        st.warning("Por favor, ingresa tu API key de OpenAI para iniciar el análisis.")
    elif canvas_result.image_data is None:
        st.warning("Por favor, dibuja algo en el tablero antes de presionar 'Analiza la imagen'.")
    else:
        # Verificar si se ha dibujado algo significativo (canal alfa > 0)
        input_numpy_array = np.array(canvas_result.image_data)
        non_transparent_pixels = (input_numpy_array[:, :, 3] > 0).sum()
        
        if non_transparent_pixels < 50:
            st.warning("Tu boceto está muy claro, ¿seguro que dibujaste algo? Intenta con trazos más fuertes.")
            
        else:
            with st.spinner("Analizando la inteligencia de tu boceto con GPT-4o-mini..."):
                
                # 1. Convertir datos del Canvas (RGBA array) a imagen PIL
                input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
                
                # 2. Codificar la imagen en base64 (usando BytesIO para evitar archivos)
                base64_image = image_to_base64(input_image)
                
                prompt_text = "Describe en español y de forma breve el boceto que ves, identificando los objetos principales que el usuario intentó dibujar."
                
                # Inicializar el cliente de OpenAI
                client = OpenAI(api_key=api_key)

                # Crear el payload
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ]
            
                try:
                    full_response = ""
                    message_placeholder = st.empty()
                    
                    # Llamada al modelo de visión
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        max_tokens=500,
                    )
                    
                    if response.choices and response.choices[0].message.content is not None:
                        full_response += response.choices[0].message.content
                        message_placeholder.markdown(full_response)
                        
                    # Final update to placeholder
                    message_placeholder.markdown(full_response)
                    
                except openai.APIError as e:
                    # Capturar errores comunes de la API (ej. clave inválida, límites)
                    st.error(f"Error de la API de OpenAI: {e.status_code}. Por favor, verifica tu clave o los límites de uso.")
                except Exception as e:
                    st.error(f"Ocurrió un error inesperado: {e}")
