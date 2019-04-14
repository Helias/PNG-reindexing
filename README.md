# PNG-reindexing
PNG reindexing a university project for the course Multimedia.

This project consist into implement this concept: *[A Fast Palette Reordering Technique Based on GPU-Optimized Genetic Algorithms](https://ieeexplore.ieee.org/document/8451221/authors#authors)*

This project use AntColony algorithm based on [this](https://github.com/trevlovett/Python-Ant-Colony-TSP-Solver) implementation.

## Requirements

To run this project you need **Python3** and the following packages:
- pypng
- numpy
- scipy
- image

You can install the packages dependencies through:

```
$ pip3 install -r requirements.txt
```

Use just "pip" if you have python3 as default instead of python2.

## Usage

This project provides the following commands:

```
$ python3 main.py -r
```

The `-r` (run) parameter generate a new image img1.png of 8x8 pixels with random palette and colors and img2.png with a ordered palette.


```
$ python3 main.py -i path/file_name.png
```

The `-i` (input) parameter get a png image as input and generate the same image as img2.png with a new palette ordered and with the reindexed colors.

If the picture has more than 256 colors, it can't create a palette following the PNG standard, so, optionally it can reduce the colors of the image to 256 with the parameter `-f` (force).

```
$ python3 main.py -i path/file_name.png -f
```

---

The `-l` (log) parameter is optional, if used it generates a file `palette_stats.txt` that show the pixels indexed, palette and the best order of palette (about old unordered palette and new image with ordered palette).
Is recommended to use this parameter only with small images.

## Credits

- [Helias (Stefano Borzì)](https://github.com/Helias)
