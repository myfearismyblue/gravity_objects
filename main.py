import tkinter as tk
from math import pi, tan, atan, sin, cos
from global_vars import *
from collections import deque


def main():
    global root, canvas

    root = tk.Tk()
    root.geometry(str(CANVAS_WIDTH) + 'x' + str(CANVAS_HEIGHT))
    canvas = tk.Canvas(root, background=CANVAS_BACKGROUND_COLOR)
    canvas.focus_set()
    canvas.bind('<Key>', lambda event: key_and_mouse_handler(event, gravity, planet_stencil))
    canvas.bind('<KeyRelease>', lambda event: key_and_mouse_handler(event, gravity, planet_stencil))
    canvas.bind('<Button-1>', lambda event: key_and_mouse_handler(event, gravity, planet_stencil))
    canvas.bind('<Alt-Button-1>', lambda event: key_and_mouse_handler(event, gravity, planet_stencil))
    canvas.bind('<Button-3>', lambda event: key_and_mouse_handler(event, gravity, planet_stencil))
    canvas.bind('<Motion>', lambda event: key_and_mouse_handler(event, gravity, planet_stencil))
    canvas.bind('<MouseWheel>', lambda event: key_and_mouse_handler(event, gravity, planet_stencil))
    gravity, planet_stencil = init_objects()
    canvas.pack(fill=tk.BOTH, expand=1)
    tick(gravity, planet_stencil)
    root.mainloop()

def stub_handler(event, gravity, panet_stancil):
    print(event)

def init_objects():
    """Init some object before ticking loop"""
    gravity = Gravity()
    planet_stencil = PlanetStencil()
    return gravity, planet_stencil


def tick(gravity, planet_stencil):
    """Moves and reshows everything on canvas."""
    gravity.update()
    for object_ in gravity.get_objects_list():
        object_.show()
    root.after(TIME_REFRESH, tick, gravity, planet_stencil)


def key_and_mouse_handler(event, gravity, planet_stencil):
    """Handles key-presses and mouse events"""
    if str(event.type) == 'KeyPress':
        if event.keysym == 'space':
            # On space press clear the canvas
            gravity.del_all_objects()
            planet_stencil.show()
        elif event.keysym == 'Shift_L':
            planet_stencil.show()
    elif str(event.type) == 'KeyRelease':
        if event.keysym == 'Shift_L':
            planet_stencil.delete()

    elif str(event.type) == 'ButtonPress':
        if event.num == 1:
            # In left click
            if event.state == 131080:
                # Left Alt pressed
                planet = Planet(planet_stencil.visual_x * DISTANCE_FACTOR, planet_stencil.visual_y * DISTANCE_FACTOR,
                                0, 0, PLANET_DENSITY, planet_stencil.visual_r * RADIUS_PROPORTION_FACTOR,
                                PLANET_IMMOVABLE_COLOR, movable=False)
                gravity.add_object_to_list(planet)
            else:
                planet = Planet(planet_stencil.visual_x * DISTANCE_FACTOR, planet_stencil.visual_y * DISTANCE_FACTOR,
                                0, 0, PLANET_DENSITY, planet_stencil.visual_r * RADIUS_PROPORTION_FACTOR, PLANET_COLOR)
                gravity.add_object_to_list(planet)
        elif event.num == 3:
            # On right-click delete planet on a distance less then stencil radius
            sten_x, sten_y, sten_r = planet_stencil.get_canvas_coords()
            for object_ in gravity.get_objects_list():
                obj_x, obj_y, _ = object_.get_object_canvas_coords()
                if (obj_x - sten_x) ** 2 + (obj_y - sten_y) ** 2 <= sten_r ** 2:
                    object_.delete_from_canvas()
                    gravity.del_object(object_)

    elif str(event.type) == 'Motion':
        planet_stencil.set_canvas_coords(event.x, event.y, planet_stencil.visual_r)
        planet_stencil.show()

    elif str(event.type) == 'MouseWheel':
        # Increase stencil radius
        if event.delta >= 0:
            planet_stencil.visual_r += 2
            planet_stencil.show()
        else:
            if planet_stencil.visual_r > 2:
                planet_stencil.visual_r += -2
                planet_stencil.show()


class Planet:
    """Any gravitating object"""

    def __init__(self, x, y, dx, dy, density, r, color, movable=True):
        self.x, self.y, self.dx, self.dy, self.density, self.r, self.color = x, y, dx, dy, density, r, color
        self.mass = self.density * 4. / 3. * pi * self.r ** 3.
        self.movable = movable
        self.id = False
        self.counter = 0  # counter to show trajectory
        self.trajectory_queue = deque()

    def delete_from_canvas(self):
        if self.id:
            canvas.delete(self.id)
            for point in self.trajectory_queue:
                canvas.delete(point)
            self.trajectory_queue = deque()
            self.id = False

    def _calculate_visual_params(self):
        visual_r = self.r / RADIUS_PROPORTION_FACTOR
        visual_x = self.x / DISTANCE_FACTOR
        visual_y = self.y / DISTANCE_FACTOR
        return visual_x, visual_y, visual_r

    def show(self):
        """Shows on canvas"""
        visual_x, visual_y, visual_r = self._calculate_visual_params()
        self._show_trajectory()
        if self.id:  # check, if it has been drawn
            canvas.coords(self.id,  # if so, then redraw coords
                          visual_x - visual_r,
                          visual_y - visual_r,
                          visual_x + visual_r,
                          visual_y + visual_r
                          )

        else:  # if it hasn't been drawn, then draw
            self.id = canvas.create_oval(visual_x - visual_r,
                                         visual_y - visual_r,
                                         visual_x + visual_r,
                                         visual_y + visual_r,
                                         fill=self.color
                                         )

    def get_object_params(self):
        """Returns mass, x, y of an object"""
        return self.mass, self.x, self.y

    def get_object_canvas_coords(self):
        return self.x / DISTANCE_FACTOR, self.y / DISTANCE_FACTOR, self.r / RADIUS_PROPORTION_FACTOR

    def _show_trajectory(self):
        if self.id:
            self.counter += 1
            if self.counter % 50 == 0:
                self.counter = 0
                visual_x, visual_y, visual_r = self._calculate_visual_params()
                self.trajectory_queue.append(
                    canvas.create_oval(visual_x, visual_y,
                                       visual_x, visual_y, fill=TRAJECTORY_COLOR))
                if len(self.trajectory_queue) >= TRAJECTORY_LENGTH:
                    canvas.delete(self.trajectory_queue.popleft())


class PlanetStencil:
    def __init__(self, visual_x=0, visual_y=0, visual_r=1):
        self.id = False
        self.visual_r = visual_r
        self.visual_x = visual_x
        self.visual_y = visual_y
        self.color = STENCIL_COLOR

    def set_canvas_coords(self, visual_x, visual_y, visual_r):
        """Sets x, y, r on canvas """
        self.visual_y = visual_y
        self.visual_x = visual_x
        self.visual_r = visual_r

    def get_canvas_coords(self):
        return self.visual_x, self.visual_y, self.visual_r

    def show(self):
        if self.id:  # check, if it has been drawn
            canvas.coords(self.id,  # if so, then redraw coords
                          self.visual_x - self.visual_r,
                          self.visual_y - self.visual_r,
                          self.visual_x + self.visual_r,
                          self.visual_y + self.visual_r,
                          )

        else:  # if it hasn't been drawn, then draw
            self.id = canvas.create_oval(self.visual_x - self.visual_r,
                                         self.visual_y - self.visual_r,
                                         self.visual_x + self.visual_r,
                                         self.visual_y + self.visual_r,
                                         fill=self.color,
                                         )

    def delete(self):
        canvas.delete(self.id)
        self.id = False


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

    def del_object(self, object_):
        for i in range(0, len(self.objects_list)):
            if object_.id == self.objects_list[i].id:
                canvas.delete(self.objects_list[i].id)
                self.objects_list.pop(i)

    def _get_object_params(self, object_):
        """Returns parameters of the object in order:
        mass, x, y"""
        return object_.mass, object_.x, object_.y

    def _set_objects_velocity(self, object_, force_x, force_y):
        if object_.movable:
            object_.dx = object_.dx + TIME_FACTOR * force_x / object_.mass
            object_.dy = object_.dy + TIME_FACTOR * force_y / object_.mass
        else:
            object_.dx = 0
            object_.dy = 0

    def _move_object(self, object_):
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
            for j in list(range(0, i)) + list(range(i + 1, len(self.objects_list))):
                object_2 = self.objects_list[j]
                force_x2, force_y2, force_x1, force_y1 = self._calculate_gravity(object_2, object_1)
                self._set_objects_velocity(object_2, force_x2, force_y2)
        for object_ in self.objects_list:
            self._move_object(object_)


if __name__ == '__main__':
    main()
