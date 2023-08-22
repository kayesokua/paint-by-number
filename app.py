import os
from flask import Flask, render_template, request, send_from_directory
from classes.paint import PaintSwatch
from classes.converter import ImageConverter
from pathlib import Path
from data.custom import gouache
from werkzeug.datastructures import FileStorage
import cv2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data/user/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    selected_paint = gouache
    swatch = PaintSwatch(selected_paint)
    swatch.create_swatch('static/images/palette/gouache.png')

    if request.method == 'POST':
        file = request.files['input_image']
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        filename_no_ext = Path(filename).stem
        input_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        custom_art = ImageConverter(input_image_path, gouache, True)
        custom_guide, used_paints = custom_art.convert_image_to_paint()
        custom_sketch, custom_sketch_numbers = custom_art.generate_sketches()
        custom_swatch = custom_art.generate_legend()

        custom_sketch_filename = f'data/user/generated/{filename_no_ext}_lineart.png'
        custom_sketch_numbers_filename = f'data/user/generated/{filename_no_ext}_lineart_numbers.png'
        custom_paint_guide_filename = f'data/user/generated/{filename_no_ext}_matched.png'
        custom_swatch_filename = f'data/user/generated/{filename_no_ext}_swatch.png'

        cv2.imwrite(custom_sketch_filename, custom_sketch)
        cv2.imwrite(custom_sketch_numbers_filename, custom_sketch_numbers)
        cv2.imwrite(custom_paint_guide_filename, custom_guide)
        custom_swatch.save(custom_swatch_filename)

        return render_template('result.html', filename=filename_no_ext, original=filename)
    return render_template('index.html')

@app.route('/data/user/generated/<path:filename>')
def get_generated_image(filename):
    return send_from_directory('data/user/generated', filename)

@app.route('/data/user/uploads/<path:filename>')
def get_upload_image(filename):
    return send_from_directory('data/user/uploads', filename)

if __name__ == '__main__':
    app.run(debug=True)