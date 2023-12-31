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
        
        def set_mask(self, new_mask):
            self._mask = new_mask
        
        def _apply_mask(self):
            # call every time mask updated
            self._image.putalpha(self._mask)
        
        def find_average_color(self):
            pixel_values = np.array(self._image)

            alpha_mask = (pixel_values[:, :, 3] == 255) # indicates opaque
            self._av_pixel = np.mean(pixel_values[alpha_mask, :3], axis=0).astype(np.uint8)
            return self._av_pixel
        
        def set_average_color(self):
            average_color = self.find_average_color()
            self._image.paste(tuple(average_color), (0, 0, self._size[0], self._size[1]))
            self._apply_mask()
        
        def set_circle(self):
            width, height = self._size
            center_x, center_y = width // 2, height // 2
            radius = min(self._size) // 2

            self._mask = Image.new('1', self._size, color=0)
            draw = ImageDraw.Draw(self._mask)
            draw.ellipse((center_x - radius, center_y - radius, 
                          center_x + radius, center_y + radius), fill = 1)
            
            self._apply_mask()
        
    
    def __init__(self, image):
        self._image = image.convert('RGBA') # with alpha layer (necessary?)
        self._size = image.size

        self._tiles = [Mosaic.Tile(self._image)] # default 1 tile
        self._tile_positions = [(0, 0)]
    
    def tile_rectangular(self, xTileCount, yTileCount, resize=False):
        self._tiles = []

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
                self._tiles.append(Mosaic.Tile(tileIm, (left, top)))
    
    def emplace_tile(self, tile):
        self._image.paste(tile._image, tile._position)

    def set_tiles(self):
        self._image = Image.new('RGBA', self._size, (0, 0, 0, 0))
        for tile in self._tiles:
            self.emplace_tile(tile)

    def solid_tiles(self):
        for tile in self._tiles:
            tile.set_average_color()
        self.set_tiles()
    
    def round_tiles(self):
        for tile in self._tiles:
            tile.set_circle()
        self.set_tiles()

    def shuffle_tiles(self):
        tile_positions = [tile._position for tile in self._tiles]
        random.shuffle(tile_positions)

        for tile, new_position in zip(self._tiles, tile_positions):
            tile._position = new_position

        self.set_tiles()

    def show(self):
        self._image.show()
    
    def save_image(self, fp, format=None, **params):
        self._image.save(fp, format, **params)

