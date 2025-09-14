import gradio as gr
from rembg import remove
from PIL import Image
import io
import requests

def process_image(url, margin_x, margin_y):
    try:
        # Baixa imagem
        response = requests.get(url)
        img = Image.open(io.BytesIO(response.content)).convert("RGBA")

        # Remove fundo
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes = img_bytes.getvalue()
        result_bytes = remove(img_bytes)
        img_no_bg = Image.open(io.BytesIO(result_bytes)).convert("RGBA")

        # Transformar em quadrado
        w, h = img_no_bg.size
        max_side = max(w, h)
        square_img = Image.new("RGBA", (max_side, max_side), (0, 0, 0, 0))
        square_img.paste(img_no_bg, ((max_side - w)//2, (max_side - h)//2), img_no_bg)

        # Crop transparência
        bbox = square_img.getbbox()
        if bbox:
            square_img = square_img.crop(bbox)

        # Adiciona margens
        final_w = square_img.width + 2 * margin_x
        final_h = square_img.height + 2 * margin_y
        final_img = Image.new("RGBA", (final_w, final_h), (0, 0, 0, 0))
        final_img.paste(square_img, (margin_x, margin_y), square_img)

        # Converte para bytes para Gradio
        final_bytes = io.BytesIO()
        final_img.save(final_bytes, format="PNG")
        final_bytes.seek(0)

        original_bytes = io.BytesIO()
        img.save(original_bytes, format="PNG")
        original_bytes.seek(0)

        return original_bytes, final_bytes
    except Exception as e:
        return None, None

# Interface Gradio com sliders
demo = gr.Interface(
    fn=process_image,
    inputs=[
        gr.Textbox(label="Cole a URL da imagem"),
        gr.Slider(minimum=0, maximum=500, step=1, label="Margem Horizontal"),
        gr.Slider(minimum=0, maximum=500, step=1, label="Margem Vertical")
    ],
    outputs=[
        gr.Image(type="file", label="Imagem Original"),
        gr.Image(type="file", label="Imagem Processada com Margens")
    ]
)

if __name__ == "__main__":
    demo.launch()
