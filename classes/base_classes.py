    class BaseColorPalette:
        def __init__(self):
            self.paint_map = {}

        def get_paint_map(self):
            return self.paint_map

        def create_swatch(self, filename=None):
            pass

    class GouacheColorPalette(BaseColorPalette):
        def __init__(self):
            super().__init__()
            self.paint_map = {
            }

    class WatercolorPalette(BaseColorPalette):
        def __init__(self):
            super().__init__()
            self.paint_map = {
            }