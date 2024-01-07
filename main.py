from Mosaic import *
from scipy.optimize import linear_sum_assignment # hungarian matching algorithm
import math

def TileSwapping(im1, im2, tile_dimensions):
    # match dimensions
    im2 = im2.resize(im1.size)
    
    m1 = Mosaic(im1)
    m2 = Mosaic(im2)

    m1.tile_rectangular(tile_dimensions[0], tile_dimensions[1], resize=True)
    m2.tile_rectangular(tile_dimensions[0], tile_dimensions[1], resize=True)
    num_tiles = tile_dimensions[0] * tile_dimensions[1]

    # create cost matrix

    cost_matrix = []
    # properly set all tile colours
    m1_colours = [m1_tile.get_average_color() for m1_tile in m1._tiles]
    m2_colours = [m2_tile.get_average_color() for m2_tile in m2._tiles]

    # Create the cost matrix using list comprehensions and numpy
    cost_matrix = np.array([[math.dist(tile1, tile2) for tile2 in m2_colours] for tile1 in m1_colours])

    # Use the Hungarian algorithm for an ideal matching O(n^3)
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    # Set tile positions according to the cost matrix
    for i in range(num_tiles):
        (
            m1._tiles[i]._position,
            m2._tiles[col_ind[i]]._position
        ) = (
            m2._tiles[col_ind[i]]._position,
            m1._tiles[i]._position
        )
    
    # Emplace tiles
    m1.set_tiles()
    m2.set_tiles()
    return m1, m2


def main():
    im1 = Image.open('./sample_images/monaLisa.jpg')
    im2 = Image.open('./sample_images/skullGogh.jpg')

    m1, m2 = TileSwapping(im1, im2, (36, 54))

    m1.save_image('./generated_images/skullGogh_from_monaLisa.png')
    m2.save_image('./generated_images/monaLisa_from_skullGogh.png')

    # for monaLisa shuffled
    m_shuffle = Mosaic(im1)
    m_shuffle.tile_rectangular(5, 5)
    m_shuffle.shuffle_tiles()
    m_shuffle.save_image('./generated_images/MonaLisa_Shuffled.png')

if __name__ == "__main__":
    main()
