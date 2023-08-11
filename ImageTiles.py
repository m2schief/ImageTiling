from PIL import Image
import numpy as np
from scipy.optimize import linear_sum_assignment
import math
from colorspacious import cspace_converter
import random

labConvert = cspace_converter('sRGB255', 'CIELab')

class Tile:
    def __init__(self, dimensions, pixels, position):
        self._dimensions = dimensions
        self._pixels = pixels
        self._position = position

        reds, greens, blues = zip(*pixels)
        self.averageColour = (np.average(reds), np.average(greens), np.average(blues))
        self.averageLAB = labConvert(self.averageColour)

    def getDimensions(self):
        return self._dimensions

    def getPixels(self):
        return self._pixels
    
    def tileDistance(self, otherTile):
        return round(math.dist(self.averageLAB, otherTile.averageLAB), 3)
        #return round(math.dist(self.averageColour, otherTile.averageColour), 3)
    
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
                tile = self.tiles[tileY * self.xTileCount + tileX]
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
        #ensure images have identical tile dimensions and near aspect ratios
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



def TileSwapping(im1name, im2name, dimensions):
    im1 = Image.open('./sample_images/' + im1name)
    im2 = Image.open('./sample_images/' + im2name)

    tileIm1 = TiledImage(im1, dimensions[0], dimensions[1])
    tileIm2 = TiledImage(im2, dimensions[0], dimensions[1])

    tileIm1.replaceTiles(tileIm2.constructImage(tileIm1))
    tileIm1.generateImageFromTiles()

    tileIm1.image.save('./generated_images/' + im2name.split('.')[0] + '_from_' + im1name.split('.')[0] + '.jpg')
    tileIm2.image.save('./generated_images/' + im1name.split('.')[0] + '_from_' + im2name.split('.')[0] + '.jpg')



TileSwapping('monaLisa.jpg', 'skullGogh.jpg', (36, 54))