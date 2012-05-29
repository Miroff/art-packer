import ImageChops
import os
import Image
import re
from math import sqrt

class ArtPacker():
    def __init__(self, input_path, output_size, metadata_saver, resource_packer, resource_prefix=None, padding=0, duplicates_threshold=None, input_regex=None, output_format='png', verbose=False):
        self.input_path = input_path
        self.output_size = output_size
        self.metadata_saver = metadata_saver
        self.resource_packer = resource_packer
        self.resource_prefix = resource_prefix
        self.verbose = verbose
        self.padding = padding
        self.input_regex = input_regex
        self.output_format = output_format
        self.duplicates_threshold = duplicates_threshold

        if self.resource_prefix and not self.resource_prefix.endswith("-"):
            self.resource_prefix += "-"

    def generate(self):
        if self.verbose:
            print "Reading image resources"

        images, duplicates = self.read_sprites()

        if not images:
            if self.verbose:
                print "No images was found"
            raise SystemExit


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
            filename = "%s%d.%s" % (self.resource_prefix, last_sprite_sheet, self.output_format)
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

        for image in duplicates:
            metadata[image['path']] = metadata[image['duplicate_of']]

        self.metadata_saver.save({'spriteshhets': sprite_sheets, 'sprites': metadata})
        if self.verbose:
            total_overhead = 100.0 - (100.0 * total_used_area / total_sheet_area)
            print "Done!"
            print "Total %d images was packed to %d sprite-sheets with pixel overhead of %.2f%%" % (len(metadata), len(sprite_sheets), total_overhead)
            print "Total size of unpacked resources is %.2f Mb" % (source_filesize / 1024.0 / 1024.0)
            print "Total size of sprite sheets is %.2f Mb" % (total_filesize / 1024.0 / 1024.0)

    def read_sprites(self):
        images = []

        for dirname, dirnames, filenames in os.walk(self.input_path):
            for filename in filenames:
                if self.input_regex and not re.match(self.input_regex, filename):
                    continue

                file_path = os.path.join(dirname, filename)

                try:
                    image = Image.open(file_path)
                except Exception, e:
                    continue

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
            return images, []

        result = []
        duplicates = []
        for image in images:
            is_duplicate = False
            for candidate in result:
                if image_match(candidate['image'], image['image'], self.duplicates_threshold):
                    is_duplicate = True
                    break
            if not is_duplicate:
                result.append(image)
            else:
                del image['image']
                image['duplicate_of'] = candidate['path']
                duplicates.append(image)

        return result, duplicates

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

    return rms <= threshold
