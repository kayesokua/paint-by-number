from PIL import Image
import numpy as np

class BaseImageProcessor:
    def __init__(self, image_path):
        self.image_path = image_path

    def process_image(self):
        pass

class ImageResizer(BaseImageProcessor):
    def __init__(self, image_path):
        super().__init__(image_path)

    def process_image(self):
        """
        Resize the image to be 25% of its original size
        """
        with Image.open(self.image_path) as img:
            original_width, original_height = img.size
            new_width = int(original_width * 0.25)
            new_height = int(original_height * 0.25)
            resized_image = img.resize((new_width, new_height), Image.ANTIALIAS)
            resized_image_array = np.array(resized_image)
        return resized_image_array

class ImageToGrayscale(BaseImageProcessor):
    def process_image(self):
        """
        Convert RGB image to grayscale = 0.2989 * R + 0.5870 * G + 0.1140 * B
        """
        image = Image.open(self.image_path)
        image_array = np.array(image)
        grayscale_array = np.dot(image_array[..., :3], [0.2989, 0.5870, 0.1140])
        grayscale_image = Image.fromarray(np.uint8(grayscale_array))
        return grayscale_image

class ImageColorQuantized(BaseImageProcessor):
    def __init__(self, image_path, paint_map):
        super().__init__(image_path)
        self.paint_map = paint_map

    def map_rgb_to_custom_paint(self, rgb):
        rgb_array = np.array(rgb)
        distances = np.sqrt(np.sum((np.array(list(self.paint_map.values())) - rgb_array)**2, axis=1))
        closest_index = np.argmin(distances)
        paint_name = list(self.paint_map.keys())[closest_index]
        return paint_name, np.array(self.paint_map[paint_name])

    def process_image(self):
        with Image.open(self.image_path) as img:
            img_array = np.array(img)
            h, w, _ = img_array.shape
            new_h = int(h * 0.25)
            new_w = int(w * 0.25)
            img_resized = img.resize((new_w, new_h), Image.ANTIALIAS)
            resized_img_array = np.array(img_resized)

        custom_guide = np.zeros_like(resized_img_array)
        used_paints = {}
        for i in range(new_h):
            for j in range(new_w):
                paint_name, paint_color = self.map_rgb_to_custom_paint(resized_img_array[i, j])
                custom_guide[i, j] = paint_color
                if paint_name:
                    key = paint_name
                    used_paints[key] = used_paints.get(key, 0) + 1

        return custom_guide, used_paints