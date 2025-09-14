import gradio as gr
from rembg import remove
from PIL import Image
import io
import requests

def process_image(url):
    try:
        # Baixa a imagem da URL
        response = requests.get(url)
        img = Image.open(io.BytesIO(response.content)).convert("RGBA")

        # Remove fundo
        img_no_bg = Image.open(io.BytesIO(remove(img.tobytes(), alpha_matting=True))).convert("RGBA")

        # Transforma em quadrado (centraliza com transparência)
        w, h = img_no_bg.size
        max_side = max(w, h)
        square_img = Image.new("RGBA", (max_side, max_side), (0, 0, 0, 0))
        square_img.paste(img_no_bg, ((max_side - w)//2, (max_side - h)//2), img_no_bg)

        # Corta transparência
        bbox = square_img.getbbox()
        if bbox:
            square_img = square_img.crop(bbox)

        return square_img
    except Exception as e:
        return f"Erro: {str(e)}"

demo = gr.Interface(
    fn=process_image,
    inputs=gr.Textbox(label="Cole a URL da imagem"),
    outputs=gr.Image(type="pil", label="Resultado")
)

if __name__ == "__main__":
    demo.launch()
