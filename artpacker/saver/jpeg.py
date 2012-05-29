
import ImageFile
from artpacker.saver import Saver

class JPEGSaver(Saver):
    def __init__(self, output_path, filename_prefix, progressive=False, quality=85):
        Saver.__init__(self, 'jpg', output_path, filename_prefix)
        self.progressive = progressive
        self.quality = quality
        self.output_path = output_path

    def save_file(self, image, filename):
        #Increase buffer to allow large images processing
        ImageFile.MAXBLOCK = image.size[0] * image.size[1]
        image.save(filename, 'JPEG', quality=self.quality, optimize=True, progressive=self.progressive)
