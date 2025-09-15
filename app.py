import gradio as gr
from rembg import remove
from PIL import Image, ImageEnhance, ImageFilter
import io
import requests

def process_image(url, file, margin_x, margin_y, enhance_quality):
    try:
        # Baixa imagem
        if file is not None:
            img = Image.open(file).convert("RGBA")
        else:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
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
with gr.Blocks() as demo:
    gr.Markdown("## Processador de Imagens")
    
    with gr.Row():
        img_input = gr.File(label="Escolha uma imagem", height=89)
        url_input = gr.Textbox(label="Cole a URL da imagem")

    with gr.Row():
        enhance_checkbox = gr.Checkbox(label="Melhorar Qualidade (leve)", value=True)

    with gr.Row():
        margin_x = gr.Slider(0, 500, step=1, value=40, label="Margem Horizontal")
        margin_y = gr.Slider(0, 500, step=1, value=40, label="Margem Vertical")
    
    with gr.Row():
        original_img = gr.Image(label="Imagem Original", type="pil", show_share_button=False)
        processed_img = gr.Image(label="Imagem Processada", type="pil", format="png", show_share_button=False)
    
    with gr.Row():
        process_button = gr.Button("Baixar PNG")
        process_button.click(fn=None,
                            inputs=[processed_img],
                            outputs=[],
                            js="""
                                (img) => {
                                    // Cria um elemento <canvas> temporário
                                    let image = new Image();
                                    image.src = img;
                                    image.onload = function() {
                                        let canvas = document.createElement('canvas');
                                        canvas.width = image.width;
                                        canvas.height = image.height;
                                        let ctx = canvas.getContext('2d');
                                        ctx.drawImage(image, 0, 0);

                                        // Converte para PNG
                                        let newData = canvas.toDataURL('image/png');

                                        // Cria link para baixar
                                        let a = document.createElement('a');
                                        a.href = newData;
                                        a.download = "convertida.jpg";
                                        a.click();
                                    };
                                }
                                """)
        bmp_button = gr.Button("Baixar BMP")
        bmp_button.click(
            fn=None,
            inputs=[processed_img],
            outputs=[],
            js="""
                (img) => {
                    let image = new Image();
                    image.src = img;
                    image.onload = function() {
                        let blob = pngImageToBmpBlob(image);

                        let a = document.createElement('a');
                        a.href = URL.createObjectURL(blob);
                        a.download = "convertida.bmp";
                        a.click();
                    };

                    function pngImageToBmpBlob(img) {
                        const width = img.naturalWidth;
                        const height = img.naturalHeight;

                        const canvas = document.createElement('canvas');
                        canvas.width = width;
                        canvas.height = height;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0);
                        const imageData = ctx.getImageData(0, 0, width, height);
                        const rgba = imageData.data;

                        const rowSizeNoPad = width * 3;
                        const padding = (4 - (rowSizeNoPad % 4)) % 4;
                        const rowSizePadded = rowSizeNoPad + padding;
                        const pixelDataSize = rowSizePadded * height;
                        const fileHeaderSize = 14;
                        const dibHeaderSize = 40;
                        const pixelDataOffset = fileHeaderSize + dibHeaderSize;
                        const fileSize = pixelDataOffset + pixelDataSize;

                        const buffer = new ArrayBuffer(fileSize);
                        const view = new DataView(buffer);
                        let offset = 0;

                        // FILE HEADER
                        view.setUint8(offset++, 0x42); // 'B'
                        view.setUint8(offset++, 0x4D); // 'M'
                        view.setUint32(offset, fileSize, true); offset += 4;
                        view.setUint16(offset, 0, true); offset += 2;
                        view.setUint16(offset, 0, true); offset += 2;
                        view.setUint32(offset, pixelDataOffset, true); offset += 4;

                        // DIB HEADER
                        view.setUint32(offset, dibHeaderSize, true); offset += 4;
                        view.setInt32(offset, width, true); offset += 4;
                        view.setInt32(offset, height, true); offset += 4;
                        view.setUint16(offset, 1, true); offset += 2;
                        view.setUint16(offset, 24, true); offset += 2;
                        view.setUint32(offset, 0, true); offset += 4;
                        view.setUint32(offset, pixelDataSize, true); offset += 4;
                        view.setInt32(offset, 2835, true); offset += 4;
                        view.setInt32(offset, 2835, true); offset += 4;
                        view.setUint32(offset, 0, true); offset += 4;
                        view.setUint32(offset, 0, true); offset += 4;

                        // PIXELS (bottom-up)
                        let pixelOffset = pixelDataOffset;
                        for (let row = height - 1; row >= 0; row--) {
                            let rowStart = row * width * 4;
                            for (let x = 0; x < width; x++) {
                                const i = rowStart + x * 4;
                                const r = rgba[i];
                                const g = rgba[i + 1];
                                const b = rgba[i + 2];
                                view.setUint8(pixelOffset++, b);
                                view.setUint8(pixelOffset++, g);
                                view.setUint8(pixelOffset++, r);
                            }
                            for (let p = 0; p < padding; p++) {
                                view.setUint8(pixelOffset++, 0);
                            }
                        }

                        return new Blob([buffer], { type: 'image/bmp' });
                    }
                }
            """
        )
        
    process_button = gr.Button("Processar Imagem")
    process_button.click(process_image, 
                         inputs=[url_input, img_input, margin_x, margin_y, enhance_checkbox],
                         outputs=[original_img, processed_img])          

if __name__ == "__main__":
    demo.launch()
