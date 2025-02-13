from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def add_watermark(input_path, output_path, text="Protected by As Shejan"):
    """Adds a semi-transparent watermark to an image."""
    image = Image.open(input_path).convert("RGBA")

    # Create a transparent overlay for watermark
    watermark = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark)

    # Load a font (ensure you have a valid .ttf font file)
    font_path = "arial.ttf"  # Change if needed
    try:
        font = ImageFont.truetype(font_path, size=int(image.width * 0.05))
    except IOError:
        font = ImageFont.load_default()

    # Calculate text size using textbbox()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Set watermark position diagonally
    position = (image.width // 4, image.height // 2)

    # Apply semi-transparent text
    draw.text(position, text, fill=(255, 255, 255, 128), font=font)

    # Merge watermark with image
    watermarked_image = Image.alpha_composite(image, watermark).convert("RGB")
    watermarked_image.save(output_path, "JPEG")

@app.route("/", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":
        if "image" not in request.files:
            return "No file uploaded", 400

        file = request.files["image"]
        if file.filename == "":
            return "No selected file", 400

        # Save original image
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        # Add watermark
        watermarked_path = os.path.join(app.config["UPLOAD_FOLDER"], "watermarked_" + file.filename)
        add_watermark(filepath, watermarked_path)

        return redirect(url_for("view_image", filename="watermarked_" + file.filename))

    return render_template("index.html")

@app.route("/uploads/<filename>")
def view_image(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.run(debug=True)
