import os
import Image

class ArtPacker():
    def __init__(self, input_path, output_size, metadata_saver, resource_packer, resource_prefix, verbose=False):
        self.input_path = input_path
        self.output_size = output_size
        self.metadata_saver = metadata_saver
        self.resource_packer = resource_packer
        self.resource_prefix = resource_prefix
        self.verbose = verbose

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

                #TODO: Crop to transparent
                #TODO: Detect duplicates
                #TODO: Add padding
                images.append({
                    'image': image,
                    'path': os.path.relpath(file_path, self.input_path),
                    'size': image.size,
                    'area': image.size[0] * image.size[1],
                    'width': image.size[0],
                    'height': image.size[1],
                    'filesize': os.path.getsize(file_path)
                })
        return images
    
#    def pack_sprites(self, source_images, output_size, output_filename, sprite_sheet):

