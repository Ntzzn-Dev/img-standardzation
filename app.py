import gradio as gr
from rembg import remove
from PIL import Image
import io
import requests

def process_image(url):
    try:
        # Baixa imagem
        response = requests.get(url)
        img = Image.open(io.BytesIO(response.content)).convert("RGBA")

        # Remove fundo corretamente
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes = img_bytes.getvalue()
        result_bytes = remove(img_bytes)
        img_no_bg = Image.open(io.BytesIO(result_bytes)).convert("RGBA")

        # Transforma em quadrado
        w, h = img_no_bg.size
        max_side = max(w, h)
        square_img = Image.new("RGBA", (max_side, max_side), (0, 0, 0, 0))
        square_img.paste(img_no_bg, ((max_side - w)//2, (max_side - h)//2), img_no_bg)

        # Crop transparência
        bbox = square_img.getbbox()
        if bbox:
            square_img = square_img.crop(bbox)

        # Converte para PNG bytes para Gradio
        final_bytes = io.BytesIO()
        square_img.save(final_bytes, format="PNG")
        final_bytes.seek(0)

        original_bytes = io.BytesIO()
        img.save(original_bytes, format="PNG")
        original_bytes.seek(0)

        return original_bytes, final_bytes
    except Exception as e:
        return None, None

demo = gr.Interface(
    fn=process_image,
    inputs=gr.Textbox(label="Cole a URL da imagem"),
    outputs=[
        gr.Image(type="file", label="Imagem Original"),
        gr.Image(type="file", label="Imagem Processada")
    ]
)

if __name__ == "__main__":
    demo.launch()
