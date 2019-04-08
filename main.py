from functions import *
import argparse

parser = argparse.ArgumentParser(description='car model recognition')

parser.add_argument("-i", "--input",      action="store",       dest="inp",   help="Take a sample image and reindex it", type=str)
parser.add_argument("-r", "--run",        action="store_true",                help="Generate a new image and ")

args = parser.parse_args()

def reindexing(img_name=None):

    sys.argv = "" # remove parameters for ant colony classes

    # if img_name is None generate new image
    if img_name is None:
        img_name = "img1.png"
        generate_new_image(img_name)
        print ("Generated img1.png")

    source = png.Reader(img_name)
    width, height, pixels, metadata = source.read()

    if "palette" not in metadata:
        print("This image has no palette")
        exit(0)

    # converting pixels hex bytearray into integer
    pixels_idx = []
    for s in pixels:
        pixels_idx.append([x for x in s])

    M = matrix_co_occurences(pixels_idx, metadata["palette"])
    T = space_color_distance(metadata["palette"])
    W = calculate_weights(M, T, pixels_idx)

    best_path_vec = apply_ant_colony(metadata["palette"], W)

    new_palette, new_pixels_idx = convert_palette(best_path_vec, metadata["palette"], pixels_idx)

    write_image("img2.png", new_pixels_idx, new_palette)

    print (path_leaf(img_name)+" reindexed, check img2.png!")

if args.run:
    reindexing()

if args.inp:
    reindexing(args.inp)
