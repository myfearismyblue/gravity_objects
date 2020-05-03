import tkinter as tk
from math import pi, tan, atan, sin, cos
from global_vars import *


def main():
    global root, canvas

    root = tk.Tk()
    root.geometry(str(CANVAS_WIDTH) + 'x' + str(CANVAS_HEIGHT))
    canvas = tk.Canvas(root, background=CANVAS_BACKGROUND_COLOR)
    canvas.focus_set()
    canvas.bind('<Key>', lambda event: key_and_mouse_handler(event, gravity))
    canvas.bind('<Button-1>', lambda event: key_and_mouse_handler(event, gravity))
    canvas.bind('<Button-3>', lambda event: key_and_mouse_handler(event, gravity))
    canvas.bind('<Motion>', lambda event: key_and_mouse_handler(event, gravity))
    gravity = init_objects()
    canvas.pack(fill=tk.BOTH, expand=1)
    tick(gravity)
    root.mainloop()


def init_objects():
    """Init some object before ticking loop"""
    gravity = Gravity()
    return gravity


def tick(gravity):
    """Moves and reshows everything on canvas."""
    gravity.update()
    for object_ in gravity.objects_list:
        object_.show()
    root.after(TIME_REFRESH, tick, gravity)


def key_and_mouse_handler(event, gravity):
    """FIXME: Add description here"""
    if str(event.type) == 'KeyPress':
        if event.keysym == 'space':
            gravity.del_all_objects()
    elif str(event.type) == 'ButtonPress':
        if event.num == 1:
            planet = Planet(event.x * DISTANCE_FACTOR, event.y * DISTANCE_FACTOR,
                            0, 0, PLANET_DENSITY, PLANET_RADIUS, PLANET_COLOR)
            gravity.add_object_to_list(planet)

        elif event.num == 3:
            planet = Planet(event.x * DISTANCE_FACTOR, event.y * DISTANCE_FACTOR,
                            0, 0, 1 * PLANET_DENSITY, 2 * PLANET_RADIUS, 'red')
            gravity.add_object_to_list(planet)
    elif str(event.type) == 'Motion':
        pass


class Planet:
    """Any gravitating object"""

    def __init__(self, x, y, dx, dy, density, r, color):
        self.x, self.y, self.dx, self.dy, self.density, self.r, self.color = x, y, dx, dy, density, r, color
        self.mass = self.density * 4. / 3. * pi * self.r ** 3.

        self.id = False
        self.visual_r = self.r / RADIUS_PROPORTION_FACTOR
        self.visual_x = self.x / DISTANCE_FACTOR
        self.visual_y = self.y / DISTANCE_FACTOR
        self.counter = 0    # counter to show trajectory

    def delete_from_canvas(self):
        if self.id:
            canvas.delete(self.id)
            self.id = False

    def _calculate_visual_params(self):
        self.visual_r = self.r / RADIUS_PROPORTION_FACTOR
        self.visual_x = self.x / DISTANCE_FACTOR
        self.visual_y = self.y / DISTANCE_FACTOR

    def show(self):
        """Shows on canvas"""
        self._calculate_visual_params()
        self._show_trajectory()
        if self.id:  # check, if it has been drawn
            canvas.coords(self.id,  # if so, then redraw coords
                          self.visual_x - self.visual_r,
                          self.visual_y - self.visual_r,
                          self.visual_x + self.visual_r,
                          self.visual_y + self.visual_r
                          )

        else:  # if it hasn't been drawn, then draw
            self.id = canvas.create_oval(self.visual_x - self.visual_r,
                                         self.visual_y - self.visual_r,
                                         self.visual_x + self.visual_r,
                                         self.visual_y + self.visual_r,
                                         fill=self.color
                                         )


    def _show_trajectory(self):
        if self.id:
            self.counter += 1
            if self.counter % 50 == 0:
                self.counter = 0
                canvas.create_oval(self.visual_x, self.visual_y, self.visual_x, self.visual_y, fill='black')


class Gravity:
    """Changes x, y, dx, dy of all objects at canvas calculating forces between objects"""

    def __init__(self):
        self.objects_list = []

    def add_object_to_list(self, object_):
        self.objects_list.append(object_)

    def get_objects_list(self):
        return self.objects_list

    def del_all_objects(self):
        for object_ in self.objects_list:
            object_.delete_from_canvas()
        canvas.delete('all')
        self.objects_list = []

    def _get_object_params(self, object_):
        """Returns parameters of the object in order:
        mass, x, y"""
        return object_.mass, object_.x, object_.y

    def _set_objects_params(self, object_, force_x, force_y):
        object_.dx = object_.dx + TIME_FACTOR * force_x / object_.mass
        object_.dy = object_.dy + TIME_FACTOR * force_y / object_.mass
        object_.x += TIME_FACTOR * object_.dx
        object_.y += TIME_FACTOR * object_.dy

    def _calculate_gravity(self, object_2, object_1):
        """Gets two objects with masses, xs, ys
        :returns Projections of the gravity force on 0x and 0y axis for first and second objects"""

        def _calculate_angle(x0, y0, x1, y1):
            """Counts angle in radians between vector (x0, y0)(x1, y1) and horizontal axis (CW) in canvas
            coordinate system
                :returns  0 if x0 == y0 == x1 == y1 == 0
                          [0.. +3.14] if vector points down
                          (-3.14.. 0] if vector points up
            """
            if x0 == y0 == x1 == y1 == 0:
                return 0

            if x1 - x0 > 0:  # pointing to the right semi-plane
                angle = atan((y1 - y0) / (x1 - x0))
            elif x1 - x0 < 0 and y1 - y0 >= 0:  # adding pi if pointing to the left-bottom quart
                angle = pi + atan((y1 - y0) / (x1 - x0))
            elif x1 - x0 < 0 and y1 - y0 < 0:  # subtract pi if pointing to the left-upper quart
                angle = -pi + atan((y1 - y0) / (x1 - x0))
            else:  # zerodevision handle
                if y1 - y0 > 0:  # pointing down
                    angle = pi / 2
                else:  # pointing up
                    angle = -pi / 2

            return angle

        m1, x1, y1 = self._get_object_params(object_1)
        m2, x2, y2 = self._get_object_params(object_2)
        R = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        F = G * m1 * m2 / R ** 2
        angle = _calculate_angle(x1, y1, x2, y2)
        Fx1 = F * cos(angle)
        Fy1 = F * sin(angle)
        Fy2, Fx2 = -Fy1, -Fx1  # vectors are exactly opposite
        return Fx2, Fy2, Fx1, Fy1

    def update(self):
        for i in range(0, len(self.objects_list)):
            object_1 = self.objects_list[i]
            for j in range(i + 1, len(self.objects_list)):
                object_2 = self.objects_list[j]
                force_x2, force_y2, force_x1, force_y1 = self._calculate_gravity(object_2, object_1)
                self._set_objects_params(object_2, force_x2, force_y2)
                self._set_objects_params(object_1, force_x1, force_y1)


if __name__ == '__main__':
    main()
