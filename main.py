from functions import *
import argparse

parser = argparse.ArgumentParser(description='PNG palette reordering tool')
parser.add_argument("-i", "--input",      action="store",       dest="inp",   help="Take a sample image and reindex it", type=str)
parser.add_argument("-r", "--run",        action="store_true",                help="Generate a new image img1.png and reindex it making img2.png")
parser.add_argument("-l", "--log",        action="store_true",                help="Generate file palette_stats.txt with all pixels indexed and palette (old and new)")
parser.add_argument("-f", "--force",      action="store_true",                help="Force to reduce the colors of the image to 256 and generating a new image PNG and the same with a ordered palette")
args = parser.parse_args()

def reindexing(img_name=None):

    # if img_name is None generate new image
    if img_name is None:
        img_name = "img1.png"
        generate_new_image(img_name)
        print ("Generated img1.png")

    if args.inp and "png" not in args.inp:
        print ("The file is not a PNG image, converting into PNG...")

        pixs, _palette = generate_palette_indexed_pixels(img_name, args.force)
        write_image("img_1.png", pixs, _palette)
        source = png.Reader("img_1.png")
        width, height, pixels, metadata = source.read()
    else:
        source = png.Reader(img_name)
        width, height, pixels, metadata = source.read()

        if "palette" not in metadata:
            print("This image has no palette, generating palette...")

            pixs, _palette = generate_palette_indexed_pixels(img_name, args.force)
            write_image("img_1.png", pixs, _palette)
            source = png.Reader("img_1.png")
            width, height, pixels, metadata = source.read()

    # converting pixels hex bytearray into integer
    pixels_idx = []
    for s in pixels:
        pixels_idx.append([x for x in s])

    M = matrix_co_occurences(pixels_idx, metadata["palette"])
    T = space_color_distance(metadata["palette"])
    W = calculate_weights(M, T, pixels_idx, len(metadata["palette"]))

    best_path_vec = apply_ant_colony(metadata["palette"], W)

    new_palette, new_pixels_idx = convert_palette(best_path_vec, metadata["palette"], pixels_idx)

    write_image("img2.png", new_pixels_idx, new_palette)

    print (path_leaf(img_name)+" reindexed, check img2.png!")

    if args.log:
        write_palette_data(metadata["palette"], new_palette, pixels_idx, new_pixels_idx, best_path_vec)
        print ("Written old palette and new palette in palette_stats.txt")

if args.run:
    reindexing()

if args.inp:
    reindexing(args.inp)
