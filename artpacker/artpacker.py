import ImageChops
import os
import Image
from math import sqrt

class ArtPacker():
    def __init__(self, input_path, output_size, metadata_saver, resource_packer, resource_prefix=None, padding=0, duplicates_threshold=None, verbose=False):
        self.input_path = input_path
        self.output_size = output_size
        self.metadata_saver = metadata_saver
        self.resource_packer = resource_packer
        self.resource_prefix = resource_prefix
        self.verbose = verbose
        self.padding = padding
        self.duplicates_threshold = duplicates_threshold

        if self.resource_prefix and not self.resource_prefix.endswith("-"):
            self.resource_prefix += "-"

    def generate(self):
        if self.verbose:
            print "Reading image resources"

        images = self.read_sprites()

        if self.verbose:
            print "Packing %d images to sprite-sheets" % len(images)

        source_filesize = reduce(lambda total, image: image['filesize'] + total, images, 0)

        last_sprite_sheet = 1
        #Some statistics
        total_used_area = 0
        total_sheet_area = 0
        total_filesize = 0

        metadata = {}
        sprite_sheets = []

        while images:
            filename = "%s%d.png" % (self.resource_prefix, last_sprite_sheet)
            sprite_metadata, images, used_area, sheet_area, sheet_filesize = self.resource_packer.pack(images, filename)

            total_used_area += used_area
            total_sheet_area += sheet_area
            total_filesize += sheet_filesize
            last_sprite_sheet += 1
            sprite_sheets.append(filename)
            metadata.update(sprite_metadata)
            if self.verbose:
                overhead = 100.0 - (100.0 * used_area / sheet_area)
                print "%s %d images was packed with pixel overhead of %.2f%%" % (filename, len(sprite_metadata), overhead)

        self.metadata_saver.save({'spriteshhets': sprite_sheets, 'sprites': metadata})
        if self.verbose:
            total_overhead = 100.0 - (100.0 * total_used_area / total_sheet_area)
            byte_overhead = ((total_filesize - source_filesize) / 1024.0 / 1024.0)
            byte_overhead_percent = 100.0 - (100.0 * source_filesize / total_filesize)
            print "Done!"
            print "Total %d images was packed to %d sprite-sheets with pixel overhead of %.2f%%" % (len(metadata), len(sprite_sheets), total_overhead)
            print "Bytes overhead is %.2f%% (%.2f Mb of %.2f Mb)" % (byte_overhead_percent, byte_overhead, total_filesize / 1024.0 / 1024.0)

    def read_sprites(self):
        images = []

        for dirname, dirnames, filenames in os.walk(self.input_path):
            for filename in filenames:
                extension = os.path.splitext(filename)[1]
                if extension.lower() not in ('.png', '.jpg', '.jpeg', '.gif', '.bmp'):
                    continue

                file_path = os.path.join(dirname, filename)
                image = Image.open(file_path)

                #Crop by alpha channel if any
                if 'A' in image.getbands():
                    bbox = image.split()[image.getbands().index('A')].getbbox()
                else:
                    bbox = image.getbbox()

                #check Image is not empty
                if not bbox:
                    continue

                #Crop image to non-transparent area
                image = image.crop(bbox)

                #Add padding to the image
                image = self.add_padding(image)

                images.append({
                    'image': image,
                    'path': os.path.relpath(file_path, self.input_path),
                    'size': image.size,
                    'area': image.size[0] * image.size[1],
                    'width': image.size[0],
                    'height': image.size[1],
                    'filesize': os.path.getsize(file_path)
                })

        return self.filter_duplicates(images)

    def add_padding(self, image):
        if self.padding <= 0:
            return image

        #We use this hand-written code because ImageOps.expand doesn't add transparent background
        width = self.padding + image.size[0] + self.padding
        height = self.padding + image.size[1] + self.padding
        result = Image.new("RGBA", (width, height), (0xff, 0xff, 0xff, 1))
        result.paste(image, (self.padding, self.padding))
        return result

    def filter_duplicates(self, images):
        if self.duplicates_threshold is None:
            return images

        result = []
        for image in images:
            is_duplicate = False
            for candidate in result:
                if image_match(candidate['image'], image['image'], self.duplicates_threshold):
                    is_duplicate = True
                    break
            if not is_duplicate:
                result.append(image)
        return result

def image_match(image_a, image_b, threshold):
    if image_a.size != image_b.size or image_a.getbands() != image_b.getbands():
        return False

    rms = []
    for band_a, band_b in zip(image_a.split(), image_b.split()):
        hist = ImageChops.difference(band_a, band_b).histogram()
        squares = (value * (i ** 2.0) for i, value in enumerate(hist))
        area = image_a.size[0] * image_a.size[1]
        rms.append(sqrt(sum(squares) / area))

    rms = sqrt(reduce(lambda score, rms: rms ** 2 + score, rms, 0))

    return rms < threshold