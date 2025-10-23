import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image, ImageOps
import numpy as np
from streamlit_drawable_canvas import st_canvas
from io import BytesIO

# --- 0. CSS para la Estética "Biblioteca Antigua/Pergamino" ---
def inject_library_css():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@400;700&family=Cutive+Mono&display=swap');
            
            /* Colores Base: Sepia Library */
            :root {
                --color-text-dark: #473B2C;  /* Tinta de pluma */
                --color-parchment: #FCF5E5;  /* Color Pergamino */
                --color-wood: #8B4513;       /* Marrón Madera */
                --color-accent: #B8860B;     /* Dorado Antiguo */
            }

            /* Fondo General (Simula textura de papel o pergamino) */
            .stApp {
                background-color: var(--color-parchment);
                color: var(--color-text-dark);
                font-family: 'Roboto Slab', serif; /* Fuente clásica con serifa */
            }
            
            /* Títulos y Encabezados */
            h1, h2, h3, h4 {
                font-family: 'Roboto Slab', serif;
                color: var(--color-wood);
                text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.1);
            }
            
            /* Input de API Key (Caja de Seguridad) */
            .stTextInput label {
                font-family: 'Cutive Mono', monospace; /* Monospace para códigos */
                color: var(--color-text-dark);
            }

            /* Botón de Análisis (Sello de Cera) */
            .stButton > button {
                background-color: var(--color-accent);
                color: white;
                border: 2px solid var(--color-wood);
                border-radius: 5px;
                padding: 10px 20px;
                box-shadow: 3px 3px 0px rgba(71, 59, 44, 0.5);
                transition: all 0.2s;
                font-family: 'Roboto Slab', serif;
                font-weight: bold;
            }
            .stButton > button:hover {
                background-color: var(--color-wood);
                box-shadow: 1px 1px 0px rgba(0, 0, 0, 0.3);
                transform: translateY(2px);
            }

            /* Contenedor principal de resultados/descripción (Caja de texto de la biblioteca) */
            .stMarkdown, .stAlert {
                border-radius: 8px;
                border: 1px solid var(--color-wood);
                background-color: #F8F0D7; /* Tono de pergamino más oscuro para contraste */
                padding: 15px;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
            }
            
            /* Barra lateral (Estantería) */
            .css-1d3s3aw, .st-emotion-cache-1d3s3aw { 
                background-color: #D3B88C; /* Tono de madera claro */
                border-right: 5px solid var(--color-wood);
            }

            /* Estilo del Canvas (Marco) */
            .main .block-container .st-emotion-cache-1ft911z, 
            .main .block-container .st-emotion-cache-1cpxdwv {
                border: 5px solid var(--color-wood); 
                box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.2);
                padding: 0;
                border-radius: 0; 
            }
        </style>
    """, unsafe_allow_html=True)

# --- Función de Codificación Robusta (Sin guardar archivos) ---
def image_to_base64(image):
    """Convierte un objeto PIL Image a una cadena Base64 (formato PNG)."""
    buffered = BytesIO()
    # Guardar el objeto Image (RGBA) en el buffer como PNG
    image.save(buffered, format="PNG") 
    encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return encoded_image

# --- Configuración de Streamlit y UI ---
st.set_page_config(page_title='Archivo de Bocetos Olvidados', page_icon='📜')
inject_library_css() # Inyectar el CSS
st.title('📜 El Archivo de Bocetos Olvidados')

with st.sidebar:
    st.subheader("📚 Bibliotecario Digital:")
    st.markdown("""
        **Nuestra Misión:** Cada boceto es un artefacto histórico. Nuestro **Archivista Digital** (GPT-4o-mini) usa Visión Computacional para desentrañar su significado y catalogarlo.
    """)
st.subheader("🖋️ Desempolva tu Pergamino y Dibuja")

# --- Panel de API Key ---
ke = st.text_input('🔑 Llave de la Bóveda (OpenAI API Key)')
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

# --- Canvas de Dibujo (El Pergamino) ---
drawing_mode = "freedraw"
# stroke_width se mantiene en el sidebar para interacción
stroke_width = st.sidebar.slider('Grosor de la Pluma (Ancho de línea)', 1, 30, 5) 
stroke_color = "#473B2C"  # Tinta de pluma (Marrón oscuro)
bg_color = '#FFFFFF' # Fondo del pergamino

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.0)", 
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

# --- Botón de Análisis (Sello de Aprobación) ---
analyze_button = st.button("Sellar y Catalogar Artefacto", type="primary")

# --- Lógica de Llamada a la API de OpenAI (Funcionalidad Preservada) ---
if analyze_button:
    if not api_key:
        st.error("Por favor, ingresa tu Llave de la Bóveda (API key) para que el Archivista Digital pueda comenzar.")
    elif canvas_result.image_data is None:
        st.warning("Por favor, dibuja el artefacto olvidado en el pergamino antes de intentar catalogarlo.")
    else:
        # Verificar si se ha dibujado algo significativo (canal alfa > 0)
        input_numpy_array = np.array(canvas_result.image_data)
        non_transparent_pixels = (input_numpy_array[:, :, 3] > 0).sum()
        
        if non_transparent_pixels < 50:
            st.warning("El boceto es demasiado tenue. Nuestro archivista necesita trazos más audaces para identificar este artefacto.")
            
        else:
            with st.spinner("⏳ Clasificando y desentrañando la historia del artefacto con el Archivista Digital..."):
                
                # 1. Convertir datos del Canvas (RGBA array) a imagen PIL
                input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
                
                # 2. Codificar la imagen en base64 (usando BytesIO para evitar archivos)
                base64_image = image_to_base64(input_image)
                
                # Prompt mejorado con la narrativa de biblioteca
                prompt_text = "Actúa como un Archivista Histórico digital. Describe en español de forma breve el boceto que ves, identificando el objeto o concepto principal que el usuario intentó dibujar. Luego, asigna un 'Título de Catálogo' de no más de 5 palabras."
                
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
                        # Añadir un emoji de libro o pergamino al inicio de la respuesta
                        full_response = "📜 **Reporte del Archivista:**\n\n" + response.choices[0].message.content
                        message_placeholder.markdown(full_response)
                        
                    # Final update to placeholder
                    message_placeholder.markdown(full_response)
                    
                except openai.APIError as e:
                    st.error(f"Error del Servidor de Archivos (API de OpenAI): Código {e.status_code}. Por favor, verifica tu clave o el estado de tu cuenta.")
                except Exception as e:
                    st.error(f"Ocurrió un error inesperado en el Archivo: {e}")
