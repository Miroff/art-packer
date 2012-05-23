#!/usr/bin/python

import os
import Image

class PackNode(object):
    """
    Creates an area which can recursively pack other areas of smaller sizes into itself.
    """
    def __init__(self, area):
        #if tuple contains two elements, assume they are width and height, and origin is (0,0)
        if len(area) == 2:
            area = (0, 0, area[0], area[1])
        self.area = area

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, str(self.area))

    def get_width(self):
        return self.area[2] - self.area[0]

    width = property(fget=get_width)

    def get_height(self):
        return self.area[3] - self.area[1]

    height = property(fget=get_height)

    def insert(self, area):
        if hasattr(self, 'child'):
            a = self.child[0].insert(area)

            if a is None: 
                return self.child[1].insert(area)

            return a

        area = PackNode(area)
        if area.width <= self.width and area.height <= self.height:
            self.child = [None,None]
            self.child[0] = PackNode((self.area[0] + area.width, self.area[1], self.area[2], self.area[1] + area.height))
            self.child[1] = PackNode((self.area[0], self.area[1] + area.height, self.area[2], self.area[3]))
            return PackNode((self.area[0], self.area[1], self.area[0] + area.width, self.area[1] + area.height))

def create_sprite_sheet(input_path, output_path, output_size, metadata_filename, metadata_prefix):
    images = read_sprites(input_path, output_path)

    i = 0
    sum_used_area = 0
    sum_sheet_area = 0
    metadata = {}
    sprite_sheets = []

    while images:
        filename = "sprite_sheet_%s_%d.png" % (metadata_prefix, i)
        sprite_metadata, images, used_area, sheet_area = pack_sprites(images, output_size, os.path.join(output_path, filename), filename)

        sum_used_area += used_area
        sum_sheet_area += sheet_area
        i += 1
        sprite_sheets.append(filename)
        metadata.update(sprite_metadata)
        print "%s overhead: %.2f%%" % (filename, 100.0 - (100.0 * used_area / sheet_area))
    
    save_metadata(metadata, sprite_sheets, metadata_filename, metadata_prefix)
    print "Total overhead: %.2f%%" % (100.0 - (100.0 * sum_used_area / sum_sheet_area))

def save_metadata(metadata, sprite_sheets, output_filename, prefix):
    rows = []
    for path, md in metadata.items():
        coords = ", ".join(map(str, md['coordinates']))
        rows.append("    '%s': {'coordinates': [%s], 'sprite': '%s'}" % (path, coords, md['sprite']))

    sprite_sheets = ", ".join(map(lambda s: "'%s'" % s, sprite_sheets))
    with open(output_filename, 'w') as fh:
        fh.write("""/* This file was automatically generated and shouldn't be changed manually */
{
    'sprite_sheets_%s': [%s],
    'sprites_%s': {
        %s
    }
}""" % (prefix, sprite_sheets, prefix, ",\n        ".join(rows)))

def read_sprites(input_path, output_path):
    images = []

    for dirname, dirnames, filenames in os.walk(input_path):
        for filename in filenames:
            extension = os.path.splitext(filename)[1]
            if extension.lower() not in ('.png', '.jpg', '.jpeg', '.gif', '.bmp') :
                continue

            file_path = os.path.join(dirname, filename)
            image = Image.open(file_path)

            images.append({
                'image': image,
                'path': os.path.relpath(file_path, input_path),
                'size': image.size,
                'area': image.size[0] * image.size[1],
                'width': image.size[0],
                'height': image.size[1],
            })
    return images
    
def pack_sprites(source_images, output_size, output_filename, sprite_sheet):
    source_images = sorted(source_images, key=lambda item: item['area'], reverse=True)

    #The largest image must fit the sprite sheet
    max_width = max(output_size[0], max(map(lambda a: a['width'], source_images)))
    max_height = max(output_size[1], max(map(lambda a: a['height'], source_images)))
    output_size = (max_width, max_height)

    output_image = Image.new('RGBA', output_size, (0xff, 0, 0xff, 1))
    tree = PackNode(output_size)

    missed_images = []
    area = 0
    actual_size = (0, 0, 0, 0)
    sprites = {}
    for image in source_images:
        position = tree.insert(image['size'])
        if position is None: 
            missed_images.append(image)
        else:
            output_image.paste(image['image'], position.area)
            area += image['area']
            actual_size = (0, 0, max(actual_size[2], position.area[2]), max(actual_size[3], position.area[3]))
            sprites[image['path']] = {
                'coordinates': position.area,
                'sprite': sprite_sheet,
            }
    
    output_image.crop(actual_size).save(output_filename)

    return (sprites, missed_images, area, actual_size[2] * actual_size[3])

if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser(usage="%prog [options]")

    parser.add_option("-i", "--input-path",
        dest="input",
        help="Path to image folder, required")

    parser.add_option("-o", "--output-path",
        dest="output",
        help="Path to output folder, required")

    parser.add_option("--output-js",
        dest="output_js",
        help="Name of output JS metadata file, required")

    parser.add_option("--prefix-js",
        dest="prefix_js",
        help="Prefix of JS namespace in the metadata file, required")

    parser.add_option("--width",
        dest="width", default=1024, type="int",
        help="Sprite sheet image width")

    parser.add_option("--height",
        dest="height", default=1024, type="int",
        help="Sprite sheet image height")

    (options, args) = parser.parse_args()

    if not options.input or not options.output or not options.output_js or not options.prefix_js:
        print "--input-path, --output-path, --prefix-js, and --output-js parameters are required"
        raise SystemExit

    print "Compressing images to sprite sheets"
    create_sprite_sheet(options.input, options.output, (options.width, options.height), options.output_js, options.prefix_js)
