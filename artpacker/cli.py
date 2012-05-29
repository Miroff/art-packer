
import os
from artpacker import ArtPacker
from optparse import OptionParser

from metadata.json import JSONMetadataSaver
from metadata.dummy import DummyMetadataSaver
from packer.simple import SimplePacker
from saver.png import PNGSaver
from saver.jpeg import JPEGSaver

AVAILABLE_FORMATS = ('png', 'jpg')

def main():
    parser = OptionParser(usage="%prog [options]")

    parser.add_option("-i", "--input-path",
        dest="input",
        help="Path to image folder, required")

    parser.add_option("-o", "--output-path",
        dest="output",
        default=".",
        help="Path to output folder. Default '.'")

    parser.add_option("--metadata-format",
        dest="metadata_format",
        default="json",
        help="Metadata file format. Should be one of 'json', 'dummy'. Default 'json'")

    parser.add_option("--metadata-filename",
        dest="metadata_filename",
        help="Metadata file name")

    parser.add_option("--sprite-sheet-prefix",
        dest="prefix",
        default='',
        help="Prefix of sprite sheet file names.")

    parser.add_option("--width",
        dest="width", default=1024, type="int",
        help="Sprite sheet image width. Default 1024")

    parser.add_option("--height",
        dest="height", default=1024, type="int",
        help="Sprite sheet image height. Default 1024")

    parser.add_option("--padding",
        dest="padding", default=0, type="int",
        help="Padding between images in the sprite sheet")

    parser.add_option("--duplicates-threshold",
        dest="duplicates_threshold", default=None, type="float",
        help="Threshold for automatic duplicates filtering. Reasonable values are from 0 to 25. 0 is exact match")

    parser.add_option("--input-regex",
        dest="input_regex", default=None,
        help="Regular expression for filtering input files")

    names = ", ".join(map(lambda a: "'%s'" % a, AVAILABLE_FORMATS))
    parser.add_option("--output-format",
        dest="output_format", default='png',
        help="Output files format. Should be one of %s" % names)

    parser.add_option("--jpeg-quality",
        dest="jpeg_quality", default='85', type="int",
        help="Quality of JPEG file. Reasonable values 70-100")

    parser.add_option("--jpeg-progressive",
        action='store_true',
        dest="jpeg_progressive", default='False',
        help="Produce progressive JPEG file")

    parser.add_option("-q", "--quiet",
        action='store_false',
        dest="verbose", default=True,
        help="Don't print status messages to stdout")

    (options, args) = parser.parse_args()

    if not options.input:
        print "--input-path parameter is required"
        raise SystemExit

    if options.output_format not in AVAILABLE_FORMATS:
        print "--output-format %s is not supported" % options.output_format
        raise SystemExit


    packer = SimplePacker(
        max_width=options.width,
        max_height=options.height)

    ArtPacker(
        input_path=options.input,
        metadata_saver=get_metadata_saver(options),
        image_saver=get_image_saver(options),
        input_regex=options.input_regex,
        resource_packer=packer,
        padding=options.padding,
        duplicates_threshold=options.duplicates_threshold,
        verbose=options.verbose).generate()

def get_image_saver(options):
    if options.output_format == 'jpg':
        return JPEGSaver(
            output_path=options.output,
            filename_prefix=options.prefix,
            progressive=options.jpeg_progressive,
            quality=options.jpeg_quality)
    elif options.output_format == 'png':
        return PNGSaver(
            output_path=options.output,
            filename_prefix=options.prefix)

def get_metadata_saver(options):
    if options.metadata_format == 'json':
        if options.metadata_filename:
            metadata_filename = options.metadata_filename
        elif options.prefix:
            metadata_filename = options.prefix + '.json'
        else:
            metadata_filename = 'metadata.json'
        return JSONMetadataSaver(os.path.join(options.output, metadata_filename))
    else:
        return DummyMetadataSaver()