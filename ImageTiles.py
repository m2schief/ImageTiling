from PIL import Image
import numpy as np
from scipy.optimize import linear_sum_assignment
import math
import random

class Tile:
    def __init__(self, dimensions, pixels, position):
        self._dimensions = dimensions
        self._pixels = pixels
        self._position = position

        reds, greens, blues = zip(*pixels)
        self._averageColour = (np.average(reds), np.average(greens), np.average(blues))

    def getDimensions(self):
        return self._dimensions

    def getPixels(self):
        return self._pixels
    
    def getAverageColour(self):
        return self._averageColour
    
    def tileDistance(self, otherTile):
        return round(math.dist(self._averageColour, otherTile.getAverageColour()), 3)
    
    def updatePosition(self, newPosition):
        self._position = newPosition

    def getAsImage(self):
        tileIm = Image.new('RGB', self._dimensions)
        tileIm.putdata(self._pixels)
        return tileIm
    
    def show(self):
        self.getAsImage().show()



class TiledImage:
    def __init__(self, im, xTileCount, yTileCount):
        self.image = CroppedImageForTiling(im, xTileCount, yTileCount)

        self.xTileCount, self.yTileCount = xTileCount, yTileCount
        self.imWidth, self.imHeight = self.image.size
        self.tileWidth = self.imWidth // xTileCount
        self.tileHeight = self.imHeight // yTileCount

        self.tiles = self.extractTilesFromImage()
    
    def extractTilesFromImage(self):
        imData = list(self.image.getdata())
        dimensions = (self.tileWidth, self.tileHeight)
        madeTiles = []

        for tileY in range(self.yTileCount):
            for tileX in range(self.xTileCount):
                tilePosition = (tileX, tileY)

                left = tileX * self.tileWidth
                right = left + self.tileWidth
                top = tileY * self.tileHeight
                bottom = top + self.tileHeight
                newTileAsImage = self.image.crop((left, top, right, bottom))
                tilePixels = list(newTileAsImage.getdata())

                newTile = Tile(dimensions, tilePixels, tilePosition)
                madeTiles.append(newTile)

        return madeTiles
    
    def generateImageFromTiles(self):
        updatedImage = Image.new('RGB', (self.imWidth, self.imHeight))

        for tileY in range(self.yTileCount):
            for tileX in range(self.xTileCount):
                tile = self.tiles[tileY * self.yTileCount + tileX]
                left = tileX * self.tileWidth
                top = tileY * self.tileHeight

                updatedImage.paste(tile.getAsImage(), (left, top))


        self.image = updatedImage
    
    def shuffleTiles(self):
        random.shuffle(self.tiles)
    
    def show(self):
        self.image.show()
    
    def replaceTiles(self, newTiles):
        #ensure dimensions remain intact
        self.tiles = newTiles

    def constructImage(self, tileImage2):
        #ensure images have identical total image and tile dimensions
        otherImageTiles = tileImage2.tiles

        #create cost matrix
        costMatrix = []
        for ourTile in self.tiles:
            ourTileCost = []
            for otherTile in otherImageTiles:
                ourTileCost.append(ourTile.tileDistance(otherTile))
            costMatrix.append(ourTileCost)
        costMatrix = np.array(costMatrix)

        #use the hungarian algorithm for an ideal matching O(n^3) 
        rowind, colind = linear_sum_assignment(costMatrix)

        #arrange our tiles according to the cost matrix
        size = self.xTileCount * self.yTileCount
        sortedTiles = [-1] * size
        alternateTiles = [-1] * size
        for i in range(size):
            sortedTiles[colind[i]] = self.tiles[i]
            alternateTiles[i] = otherImageTiles[colind[i]]

        self.tiles = sortedTiles
        self.generateImageFromTiles()

        return alternateTiles




def CroppedImageForTiling(im, xTileCount, yTileCount):
    width, height = im.size

    newWidth = (width // xTileCount) * xTileCount
    newHeight = (height // yTileCount) * yTileCount

    croppedImage = im.crop((0, 0, newWidth, newHeight))
    return croppedImage



monaLisa = Image.open('./sample_images/mona_lisa.jpg')
tiledLisa = TiledImage(monaLisa, 50, 50)

vanGogh = Image.open('./sample_images/skeleton_gogh.jpg')
tiledGogh = TiledImage(vanGogh, 50, 50)

tiledGogh.replaceTiles(tiledLisa.constructImage(tiledGogh))
tiledGogh.generateImageFromTiles()
tiledLisa.image.save('./generated_images/Skeleton_from_MonaLisa.bmp')
tiledGogh.image.save('./generated_images/MonaLisa_from_Skeleton.bmp')