class Paddle:
    def __init__(self, x_position, z_position, width, height):
        self._position = {'x': x_position, 'y': 0, 'z': z_position}
        self.width = width
        self.height = height
    
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, new_position):
        ## TODO: make sure position can't be set out of playing field
        if 'x' in new_position:
            self._position['x'] = new_position['x']
        if 'z' in new_position:
            self._position['z'] = new_position['z']

    @property
    def x(self):
        return self._position['x']

    @x.setter
    def x(self, value):
        ## TODO: make sure position can't be set out of playing field
        self._position['x'] = value

    @property
    def z(self):
        return self._position['z']

    @z.setter
    def z(self, value):
        ## TODO: make sure position can't be set out of playing field
        self._position['z'] = value
    
    def move(self, delta_z):
        ## TODO: make sure paddle doesn't move out of bounds
        self._position['z'] += delta_z

class Player:
    def __init__(self, id, x_position, z_position, width, height):
        self.id = id
        self.paddle = Paddle(x_position, z_position, width, height)
        self.score = 0
    
    @property
    def score(self):
        return self._score
    
    @score.setter
    def score(self, new_score):
        self._score = new_score

    def move_paddle(self, delta_z):
        self.paddle.move(delta_z)

    def update_score(self):
        self._score += 1


