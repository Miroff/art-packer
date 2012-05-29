import Image
import os

class Saver():
    def __init__(self, extension, output_path, filename_prefix):
        self.output_path = output_path
        self.filename_prefix = filename_prefix
        self.last_index = 0
        self.extension = extension

        if self.filename_prefix and not self.filename_prefix.endswith("-"):
            self.filename_prefix += "-"


    def next_filename(self):
        self.last_index += 1
        return "%s%d.%s" % (self.filename_prefix, self.last_index, self.extension)

    def save(self, sprite_sheet):
        result = Image.new('RGBA', sprite_sheet.size, (0xff, 0xff, 0xff, 1))

        for image, position in sprite_sheet:
            result.paste(image, position)

        sprite_sheet.filename = self.next_filename()

        self.save_file(result, sprite_sheet.filename)

        sprite_sheet.filesize = os.path.getsize(sprite_sheet.filename)

    def save_file(self, image, filename):
        raise "This method should be overridden in inherited classes"
