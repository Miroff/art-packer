
from artpacker import create_sprite_sheet
from optparse import OptionParser

def main():
    parser = OptionParser(usage="%prog [options]")

    parser.add_option("-i", "--input-path",
        dest="input",
        help="Path to image folder, required")

    parser.add_option("-o", "--output-path",
        dest="output",
        default=".",
        help="Path to output folder. Default '.'")

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
        print "--input-path, --prefix-js, and --output-js parameters are required"
        raise SystemExit

    print "Compressing images to sprite sheets"
    create_sprite_sheet(options.input, options.output, (options.width, options.height), options.output_js, options.prefix_js)
