import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

class ImageConverter:
    def __init__(self, input_image_path, selected_paint, sample):
        self.input_image_path = input_image_path
        self.paint_map = selected_paint
        self.sample = True
        self.custom_guide = None
        self.used_paints = None
        self.custom_sketch = None
        self.custom_sketch_numbers = None
        self.custom_swatch = None

    def map_rgb_to_custom_paint(self, rgb):
        rgb_array = np.array(rgb)
        distances = np.sqrt(np.sum((np.array(list(self.paint_map.values())) - rgb_array)**2, axis=1))
        closest_index = np.argmin(distances)
        paint_name = list(self.paint_map.keys())[closest_index]
        return paint_name, np.array(self.paint_map[paint_name])

    def convert_image_to_paint(self):
        image = cv2.imread(self.input_image_path)
        h, w, _ = image.shape

        if self.sample:
            h = int(h * 0.25)
            w = int(w * 0.25)
            image = cv2.resize(image, (w, h), interpolation=cv2.INTER_AREA)

        custom_guide = np.zeros_like(image)
        used_paints = {}
        for i in range(h):
            for j in range(w):
                paint_name, paint_color = self.map_rgb_to_custom_paint(image[i, j])
                custom_guide[i, j] = paint_color
                if paint_name:
                    key = paint_name
                    used_paints[key] = used_paints.get(key, 0) + 1

        self.custom_guide = custom_guide
        self.used_paints = used_paints
        return custom_guide, used_paints

    def generate_sketches(self):
        gray = cv2.cvtColor(self.custom_guide, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        sketch = cv2.bitwise_not(edges)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.3
        font_thickness = 1
        sketch_numbers = np.full_like(self.custom_guide, 255)

        for x in range(0, self.custom_guide.shape[0], 10):
            for y in range(0, self.custom_guide.shape[1], 10):
                color, _ = self.map_rgb_to_custom_paint(self.custom_guide[x, y])
                color_label = list(self.paint_map.keys()).index(color)
                cv2.putText(sketch_numbers, str(color_label + 1), (y, x), font, font_scale, (128, 128, 128), font_thickness, cv2.LINE_AA)

        self.custom_sketch = sketch
        self.custom_sketch_numbers = sketch_numbers

        return sketch, sketch_numbers

    def generate_legend(self):
        swatch_size, padding, font_size = 200, 10, 16
        num_colors = len(self.used_paints)
        num_cols = 6
        num_rows = (num_colors + num_cols - 1) // num_cols

        swatch_width = num_cols * (swatch_size + padding) + padding
        swatch_height = num_rows * (swatch_size + padding + font_size) + padding

        swatch = Image.new('RGB', (swatch_width, swatch_height), (255, 255, 255))
        draw = ImageDraw.Draw(swatch)
        font = ImageFont.truetype("static/fonts/arial.ttf", font_size)

        total_usage = sum(self.used_paints.values())

        for i, color_name in enumerate(self.used_paints):
            color_rgb = self.paint_map[color_name]
            color_usage = self.used_paints[color_name]
            usage_percentage = (color_usage / total_usage) * 100
            row = i // num_cols
            col = i % num_cols
            x = col * (swatch_size + padding) + padding
            y = row * (swatch_size + padding + font_size) + padding
            draw.rectangle((x, y, x+swatch_size, y+swatch_size), fill=color_rgb)
            text_x = x + swatch_size/2
            text_y = y + swatch_size/2
            text = f"{color_name}\nRGB: {color_rgb}\nUsage: {usage_percentage:.0f}%"
            draw.text((text_x, text_y), text, font=font, fill=(0, 0, 0), anchor="mm")
        self.custom_swatch = swatch
        return swatch