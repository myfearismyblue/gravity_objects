TIME_REFRESH = 1  # in ms
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
CANVAS_BACKGROUND_COLOR = 'white'
G = 6.6743 * 10 ** (-11)  # Gravitational constant m**3 * kg**(-1) * s**(-2)

EARTH_MASS = 5.9722 * 10 ** 24  # in kg
EARTH_DENSITY = 5515.3  # kg * m**(-3)
EARTH_RADIUS = 6.3781 * 10 ** 6  # in meters

RADIUS_PROPORTION_FACTOR = 0.1 * EARTH_RADIUS  # each pixels is RADIUS_PROPORTION_FACTOR of earth's radius at canvas
DISTANCE_FACTOR = 1 * EARTH_RADIUS  # each pixel is DISTANCE_FACTOR earth's radius at canvas
TIME_FACTOR = 1000 / TIME_REFRESH

PLANET_RADIUS = 1 * EARTH_RADIUS
PLANET_DENSITY = 1 * EARTH_DENSITY
PLANET_COLOR = 'blue'

STENCIL_COLOR = '#BBFFFF'


