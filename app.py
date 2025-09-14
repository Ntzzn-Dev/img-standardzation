import gradio as gr
from rembg import remove
from PIL import Image, ImageEnhance, ImageFilter
import io
import requests

def process_image(url, margin_x, margin_y, enhance_quality):
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

        # Melhorar qualidade levemente
        if enhance_quality:
            final_img = final_img.filter(ImageFilter.SHARPEN)
            final_img = ImageEnhance.Contrast(final_img).enhance(1.2)

        return img, final_img

    except Exception as e:
        return None, None

# Interface Gradio com sliders e checkbox
demo = gr.Interface(
    fn=process_image,
    inputs=[
        gr.Textbox(label="Cole a URL da imagem"),
        gr.Slider(minimum=0, maximum=500, step=1, label="Margem Horizontal"),
        gr.Slider(minimum=0, maximum=500, step=1, label="Margem Vertical"),
        gr.Checkbox(label="Melhorar Qualidade (leve)")
    ],
    outputs=[
        gr.Image(type="pil", label="Imagem Original"),
        gr.Image(type="pil", label="Imagem Processada com Margens")
    ]
)

if __name__ == "__main__":
    demo.launch()
