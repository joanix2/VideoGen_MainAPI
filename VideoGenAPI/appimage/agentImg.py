import numpy as np
from PIL import Image

class RandomImageGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image = None
        self.prompt = ""

    def generate(self):
        # Générez une image aléatoire avec des valeurs de pixel aléatoires
        random_pixels = np.random.randint(0, 256, (self.height, self.width, 3), dtype=np.uint8)

        # Créez une image PIL à partir du tableau de pixels aléatoires
        self.image = Image.fromarray(random_pixels)

        return self.image
    
    def save(self, path):
        if self.image:
            self.image.save(path)

