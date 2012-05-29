
from artpacker.saver import Saver

class PNGSaver(Saver):
    def __init__(self, output_path, filename_prefix):
        Saver.__init__(self, 'png', output_path, filename_prefix)

    def save_file(self, image, filename):
        image.save(filename, optimize=True)