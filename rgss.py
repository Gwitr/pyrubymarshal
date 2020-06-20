import numpy as np

class Color():

    def __init__(self, r, g, b, a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def __repr__(self):
        return "Color(%f, %f, %f, %f)" % (self.r, self.g, self.b, self.a)

    @staticmethod
    def readDouble(x):
        return np.frombuffer(x[:8], "<f8")[0]

    @classmethod
    def load(cls, m, x, symbols, objcache):
        # print(x[:100])
        # print(x[:(4 * 8)])
        # print("====")
        i = 1
        
        r = cls.readDouble(x[i:])
        i += 8

        g = cls.readDouble(x[i:])
        i += 8

        b = cls.readDouble(x[i:])
        i += 8

        a = cls.readDouble(x[i:])
        i += 8

        res = cls(r, g, b, a)

        objcache.append(res)
        return res, i

class Tone(Color):

    def __repr__(self):
        return "Tone(%f, %f, %f, %f)" % (self.r, self.g, self.b, self.a)

class Table():

    def __new__(*__, **_):
        raise TypeError("This class cannot be instantiated")

    @staticmethod
    def readInt32(x):
        return np.frombuffer(x[:4], "<i4")

    @classmethod
    def load(cls, m, x, symbols, objcache):
        i = 3   #  ??????? The dissasembly doesn't mention that anywhere but the first 3 bytes are garbage
        
        dim = int(cls.readInt32(x[i:]))
        i += 4
        
        xs = int(cls.readInt32(x[i:]))
        i += 4
        ys = int(cls.readInt32(x[i:]))
        i += 4
        zs = int(cls.readInt32(x[i:]))
        i += 4

        size = int(cls.readInt32(x[i:]))  # size broke
        i += 4

        res = x[i:(i + size * 2)]
        i += size * 2

        # res = cls(xs, ys, zs, res)

        res = np.ndarray((xs, ys, zs), buffer=res, dtype=np.int16, order='F')
        
        return res, i

RGSS_PARSERS = {"Table": Table, "Color": Color, "Tone": Tone}
