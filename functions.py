import sys
import traceback
import png
import struct
import numpy as np
import ntpath
from random import randint
from scipy.spatial.distance import euclidean
from PIL import Image

# Ant Colony
from ant_colony_algorithm.antcolony import AntColony
from ant_colony_algorithm.antgraph import AntGraph


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

# Write the image
def write_image(img_name, pixels_idx, palette):
    width = len(pixels_idx[0])
    height = len(pixels_idx)

    f = open(img_name, 'wb')
    w = png.Writer(width, height, palette=palette)
    w.write(f, pixels_idx)
    f.close()

def generate_new_image(img_name):
    colors = [
        [255,0,0],
        [0,255,0],
        [0,0,255],
        [255,255,0],
        [128,0,0],
        [0,128,0],
        [0,0,128],
        [128,128,0]
    ]

    palette = [tuple(x) for x in colors]

    pixels_idx = []
    for i in range(len(colors)):
        row = []
        for j in range(len(colors)):
            row.append(randint(0, len(colors)-1))
        pixels_idx.append(tuple(row))

    write_image(img_name, pixels_idx, palette)

# calculate co-occurences matrix (M)
def matrix_co_occurences(matrix, palette):
    occ = {}

    for i in range(len(palette)):
        for j in range(len(palette)):
            occ[str(i)+"_"+str(j)]=0

    for i in range(len(matrix)):
        for j in range(len(matrix[i])-1):
            occ[str(matrix[i][j])+"_"+str(matrix[i][j+1])]+=1

    return occ

# calculate space color distance (T)
def space_color_distance(palette):
    distances = {}

    for i in range(len(palette)-1):
        distance = euclidean(palette[i], palette[i+1])
        distances[str(i)+"_"+str(i+1)] = distance
        distances[str(i+1)+"_"+str(i)] = distance

    return distances

# calculate weights (distance matrix) (W)
def calculate_weights(m, t, matrix, len_palette):

    print(t)

    #init matrix with 1 values to avoid divide by 0
    matrix_distances = [[1 for j in range(len_palette)] for i in range(len_palette)]

    for i in range(len_palette):
        for j in range(len_palette):
            key = str(i)+"_"+str(j)

            if i == j:
                matrix_distances[i][j] = 0
            elif m[key] != 0 and key in t:
                matrix_distances[i][j] += round(t[key] + 1/m[key],2)
            elif m[key] != 0 and not key in t:
                matrix_distances[i][j] += round(0 + 1/m[key],2)
            elif m[key] == 0 and key in t:
                matrix_distances[i][j] += round(t[key], 2)

    # for i in range(len(matrix_distances)):
    #     text = ""
    #     for j in range(len(matrix_distances[j])):
    #         text += str(matrix_distances[i][j])+"\t"
    #     print(text)
    # exit(0)

    return matrix_distances

# Applying Ant Colony to palette
def apply_ant_colony(palette, cost_mat):
    num_nodes = len(palette)

    if num_nodes <= 10:
        num_ants = 20
        num_iterations = 12
        num_repetitions = 1
    else:
        num_ants = 28
        num_iterations = 20
        num_repetitions = 1

    if num_nodes < len(cost_mat):
        cost_mat = cost_mat[0:num_nodes]
        for i in range(0, num_nodes):
            cost_mat[i] = cost_mat[i][0:num_nodes]

    try:
        graph = AntGraph(num_nodes, cost_mat, logs=False)
        best_path_vec = None
        best_path_cost = sys.maxsize
        for i in range(0, num_repetitions):
            graph.reset_tau()
            ant_colony = AntColony(graph, num_ants, num_iterations, logs=False)
            ant_colony.start()
            if ant_colony.best_path_cost < best_path_cost:
                best_path_vec = ant_colony.best_path_vec
                best_path_cost = ant_colony.best_path_cost

        # print ("------------------------------------------------------------")
        # print ("                     Results                                ")
        # print ("------------------------------------------------------------")
        # print ("Best path = %s" % (best_path_vec,))
        # print ("Best path cost = %s" % (best_path_cost,))

    except Exception as e:
        print ("exception: " + str(e))
        traceback.print_exc()

    return best_path_vec


def convert_palette(best_path_vec, palette, pixels_idx):

    # make new palette
    new_palette = []
    for i in range(len(palette)):
        new_palette.append(palette[best_path_vec[i]])

    # update colors pixels
    k_v = {}
    for i in best_path_vec:
        k_v[best_path_vec[i]] = i

    new_pixels_idx = []
    for i in range(len(pixels_idx)):
        t = []
        for j in range(len(pixels_idx[0])):
            t.append(k_v[pixels_idx[i][j]])
        new_pixels_idx.append(tuple(t))

    return new_palette, new_pixels_idx

def generate_palette_indexed_pixels(img_name, force=None):
    im = Image.open(img_name)
    [width, height] = im.size

    p_colors = im.getdata() # this is not only for PNG
    p_colors = list(p_colors)

    palette = list(set(p_colors)) # remove duplicates from p_colors

    if len(palette) > 256:
        if not force:
            print("This image has more than 256 colors, use the parameter -f to force the PNG format for palette")
            exit(0)
        else:
            im = im.convert("RGB")
            im = im.convert('P', palette=Image.ADAPTIVE) # colors=256 as default

            p_colors = list(im.getdata()) # this is not only for PNG
            palette = list(im.palette.palette) # remove duplicates from palette

            N = 3
            palette = [tuple(palette[n:n+N]) for n in range(0, len(palette), N)]

            pixels_idx = []
            for i in range(height):
                pixels_idx.append([])
                for j in range(width):
                    idx = (i*width)+j
                    pixels_idx[i].append( p_colors[idx] )
    else:
        k_v = dict() # make new dict key-value for pixels indexing

        for i in range(len(palette)):
            k_v[palette[i]] = i

        pixels_idx = []
        for i in range(height):
            pixels_idx.append([])
            for j in range(width):
                idx = (i*width)+j
                pixels_idx[i].append( k_v[p_colors[idx]] )

    return pixels_idx, palette

def write_palette_data(old_palette, new_palette, old_pixels, new_pixels, best_idx):

    text = "old palette:\n[ "
    for i in range(len(old_palette)):
        text += str(old_palette[i])+" "

    text +="]\n\n new palette:\n[ "
    for i in range(len(new_palette)):
        text += str(new_palette[i])+" "
    text+="]\n"

    text +="\n\n old pixels indexed:\n[\n"
    for i in range(len(old_pixels)):
        for j in range(len(old_pixels[0])):
            text += " "+str(old_pixels[i][j])
        text+="\n"
    text+="]\n"

    text +="\n new pixels indexed:\n[\n"
    for i in range(len(new_pixels)):
        for j in range(len(new_pixels[0])):
            text += " "+str(new_pixels[i][j])
        text+="\n"
    text+="]\n"

    text+="\n new index order:\n[ "
    for i in range(len(best_idx)):
        text+= str(best_idx[i])+" "
    text+="]\n"

    f = open("palette_stats.txt", "w+")
    f.write(text)
    f.close()
