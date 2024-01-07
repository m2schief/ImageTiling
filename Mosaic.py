from PIL import Image, ImageDraw
import numpy as np
import random

class Mosaic:
    """
    """

    class Tile():
        """
        """

        def __init__(self, image, position=(0, 0)):
            self._image = image.convert('RGBA')
            self._size = image.size
            self._position = position

            # boolean mask for tile shape. Stored as Image
            self._mask = Image.new('1', self._size, color=1)

            self._av_pixel = (0, 0, 0)
            self._av_updated = False
        
        def set_mask(self, new_mask):
            self._mask = new_mask
            self._apply_mask()
        
        def _apply_mask(self):
            # call every time mask/image updated
            self._image.putalpha(self._mask)
            self._av_updated = False
        
        def get_average_color(self):
            if (not self._av_updated):
                # find the average pixel
                pixel_values = np.array(self._image)
                alpha_mask = (pixel_values[:, :, 3] == 255) # indicates opaque

                self._av_pixel = np.mean(pixel_values[alpha_mask, :3], axis=0).astype(np.uint8)
                self._av_updated = True

            return self._av_pixel
        
        def set_average_color(self):
            average_color = self.get_average_color()
            self._image.paste(tuple(average_color), (0, 0, self._size[0], self._size[1]))
            self._apply_mask()
        
        def set_circle(self):
            width, height = self._size
            center_x, center_y = width // 2, height // 2
            radius = min(self._size) // 2

            self._mask = Image.new('1', self._size, color=0)
            self._av_updated = False

            draw = ImageDraw.Draw(self._mask)
            draw.ellipse((center_x - radius, center_y - radius, 
                          center_x + radius, center_y + radius), fill = 1)
            
            self._apply_mask()
        
        def set_image(self, new_image, update_size=False):
            if (not update_size): # default: retain tile size
                resized_image = new_image.resize(self._size)
                self._image = resized_image
            else: # tile takes on new size
                self._image = new_image
                self._size = new_image.size
                self._mask = self._mask.resize(self._size)
            self._apply_mask()
        
    
    def __init__(self, image):
        self._image = image.convert('RGBA') # with alpha layer (necessary?)
        self._size = image.size

        self.tiles = [Mosaic.Tile(self._image)] # default 1 tile
    
    def tile_rectangular(self, xTileCount, yTileCount, resize=False):
        self.tiles = []

        if (resize): 
            newWidth = round(self._size[0] / xTileCount) * xTileCount
            newHeight = round(self._size[1] / yTileCount) * yTileCount
            self._image = self._image.resize((newWidth, newHeight))
            self._size = (newWidth, newHeight)

        # residual pixels batched into last tiles (could be much larger than others)
        residX = self._size[0] % xTileCount
        residY = self._size[1] % yTileCount

        tileWidth = self._size[0] // xTileCount
        tileHeight = self._size[1] // yTileCount

        for tileY in range(yTileCount):
            for tileX in range(xTileCount):

                # crop requires 4 pixel coordinates:
                left, top = (tileX * tileWidth, tileY * tileHeight) # tile pos
                right, bottom = (left + tileWidth, top + tileHeight)
                if (tileX == xTileCount - 1): right += residX
                if (tileY == yTileCount - 1): bottom += residY

                tileIm = self._image.crop((left, top, right, bottom))
                self.tiles.append(Mosaic.Tile(tileIm, (left, top)))
    
    def emplace_tile(self, tile):
        self._image.paste(tile._image, tile._position)

    def set_tiles(self):
        self._image = Image.new('RGBA', self._size, (0, 0, 0, 0))
        for tile in self.tiles:
            self.emplace_tile(tile)

    def solid_tiles(self):
        for tile in self.tiles:
            tile.set_average_color()
        self.set_tiles()
    
    def round_tiles(self):
        for tile in self.tiles:
            tile.set_circle()
        self.set_tiles()

    def shuffle_tiles(self):
        tile_positions = [tile._position for tile in self.tiles]
        random.shuffle(tile_positions)

        for tile, new_position in zip(self.tiles, tile_positions):
            tile._position = new_position

        self.set_tiles()
    
    def arrange_tiles(self):
        # prioritize 'tile._position' close to image center
        center_x, center_y = self._size[0] // 2, self._size[1] // 2

        # tile distances found together
        tile_positions = np.array([tile._position for tile in self.tiles])
        tile_distances = np.linalg.norm(tile_positions - np.array([center_x, center_y]), axis=1)

        # zip and sort by distances. reassign
        self.tiles = [tile for _, tile in sorted(zip(tile_distances, self.tiles), key=lambda x: x[0])]
    
    def set_tile_images(self, tile_images):
        replace_n = min(len(tile_images), len(self.tiles))

        for i in range(replace_n):
            self.tiles[i].set_image(tile_images[i])
        self.set_tiles()

    def show(self):
        self._image.show()
    
    def save_image(self, fp, format=None, **params):
        self._image.save(fp, format, **params)

''' next problem: paste outside of dimensions (crop tile) (no-throw guarantee) '''

