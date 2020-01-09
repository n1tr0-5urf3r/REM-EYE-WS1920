class Node:

    def __init__(self, x, y, neighbors=None, image=None):
        self.x = x
        self.y = y
        self.neighbors = neighbors
        if image is None:
            self.image = []
        else:
            self.image = image
        self.color = (0,128,255)
