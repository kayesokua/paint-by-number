from PIL import Image, ImageDraw, ImageFont

class PaintSwatch:
    def __init__(self, paint_map):
        self.paint_map = paint_map
        self.swatch_size, self.padding, self.font_size = 200, 10, 16
        self.num_colors = len(paint_map)
        self.num_cols = 6
        self.num_rows = (self.num_colors + self.num_cols - 1) // self.num_cols
        self.swatch_width = self.num_cols * (self.swatch_size + self.padding) + self.padding
        self.swatch_height = self.num_rows * (self.swatch_size + self.padding + self.font_size) + self.padding
        self.swatch = Image.new('RGB', (self.swatch_width, self.swatch_height), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.swatch)
        self.font = ImageFont.truetype("static/fonts/arial.ttf", self.font_size)

    def create_swatch(self, filename=None):
        def create_paint_swatch_element(index, paint_map_item, position_func):
            color_name, color_rgb = paint_map_item
            x, y = position_func(index)

            self.draw.rectangle((x, y, x+self.swatch_size, y+self.swatch_size), fill=color_rgb)

            text_x = x + self.swatch_size/2
            text_y = y + self.swatch_size + self.padding/2
            text = f"{color_name}\nRGB: {color_rgb}"
            self.draw.text((text_x, text_y), text, font=self.font, fill=(0, 0, 0), anchor="mm")

        def swatch_position(index):
            row = index // self.num_cols
            col = index % self.num_cols
            x = col * (self.swatch_size + self.padding) + self.padding
            y = row * (self.swatch_size + self.padding + self.font_size) + self.padding
            return x, y

        for i, paint_map_item in enumerate(self.paint_map.items()):
            create_paint_swatch_element(i, paint_map_item, swatch_position)

        if filename:
            self.swatch.save(filename)
        return self.swatch