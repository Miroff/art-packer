
import Image
import os

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
            self.child = [None, None]
            self.child[0] = PackNode((self.area[0] + area.width, self.area[1], self.area[2], self.area[1] + area.height))
            self.child[1] = PackNode((self.area[0], self.area[1] + area.height, self.area[2], self.area[3]))
            return PackNode((self.area[0], self.area[1], self.area[0] + area.width, self.area[1] + area.height))

class SimplePacker():
    def __init__(self, max_width, max_height, output_path):
        self.max_width =  max_width
        self.max_height = max_height
        self.output_path = output_path

    def pack(self, images, output_filename):
        source_images = sorted(images, key=lambda item: item['area'], reverse=True)

        output_size = self.adjust_max_size(source_images)

        output_image = Image.new('RGBA', output_size, (0xff, 0xff, 0xff, 1))
        tree = PackNode(output_size)

        missed_images = []
        area = 0
        actual_size = (0, 0, 0, 0)
        metadata = {}
        for image in source_images:
            position = tree.insert(image['size'])
            if position is None:
                missed_images.append(image)
            else:
                output_image.paste(image['image'], position.area)
                area += image['area']
                actual_size = (0, 0, max(actual_size[2], position.area[2]), max(actual_size[3], position.area[3]))
                metadata[image['path']] = {
                    'coordinates': position.area,
                    'sprite': output_filename,
                    }

        sheet_filename = os.path.join(self.output_path, output_filename)
        output_image.crop(actual_size).save(sheet_filename)

        return metadata, missed_images, area, actual_size[2] * actual_size[3], os.path.getsize(sheet_filename)

    def adjust_max_size(self, images):
        #The largest image must fit the sprite sheet
        max_width = max(self.max_width, max(map(lambda a: a['width'], images)))
        max_height = max(self.max_height, max(map(lambda a: a['height'], images)))
        return max_width, max_height
