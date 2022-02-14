# Blender 3.1 | Linux | Python 3.10
#
# To execute the script you need to have the
# two 'csv' Files: PARTITION.csv and GROUPES.csv.
# Change the path under DATA IMPORT/MANIPULATION
# accordingly. Furthermore you need to have the 
# following Python libraries installed: Pandas,
# Random, Math, Numpy, Mathutils, Time.
# Please note that this script is tested for
# Blender 3.1 and Python 3.10 if any error occurs
# please try installing blender 3.1.
# Once the script is executed you can play the
# animation by clicking on play in the timeline.


### IMPORT LIBRARIES


import bpy
import pandas
import random
import math
import numpy
from mathutils import Vector
import time


### DATA IMPORT/MANIPULATION


partition_table = pandas.read_csv(
    "/home/sinasta/Documents/MASTER/1sem/AIM/PHASE II/CSV/PARTITION.csv"
)  # import the general csv file (change to new CSV path)
group_table = pandas.read_csv(
    "/home/sinasta/Documents/MASTER/1sem/AIM/PHASE II/CSV/GROUPES.csv"
)  # import the group csv file (change to new CSV path)

t_max = 5  # map values to fit in cube
t_min = -5

partition_table.loc[:, ["HEIGHT", "SIZE", "% OF INFO"]] -= partition_table.loc[
    :, ["HEIGHT", "SIZE", "% OF INFO"]
].min()
partition_table.loc[:, ["HEIGHT", "SIZE", "% OF INFO"]] /= (
    partition_table.loc[:, ["HEIGHT", "SIZE", "% OF INFO"]].max()
    - partition_table.loc[:, ["HEIGHT", "SIZE", "% OF INFO"]].min()
)
partition_table.loc[:, ["HEIGHT", "SIZE", "% OF INFO"]] *= t_max - t_min
partition_table.loc[:, ["HEIGHT", "SIZE", "% OF INFO"]] += t_min


### VARIABLES

start_time = time.time()
random.seed()
total_group_amount = len(partition_table)
total_amount_of_symbols = len(group_table.columns) - 2
start_frame = bpy.context.scene.frame_start
end_frame = bpy.context.scene.frame_end


### LISTS


list_of_symbols = list(group_table)[2:]  # get list of symbols
list_of_group_relations = partition_table["RELATION"].tolist()


### UTILITY FUNCTIONS


def clean_terminal():
    for i in range(20):
        print(" ")


def unhide_all():
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.data.objects:
        obj.hide_viewport = False
        obj.hide_render = False
        obj.hide_set(False)
        obj.hide_select = False


def clean():
    unhide_all()
    bpy.ops.object.select_all(action="SELECT")  # clean the viewport
    bpy.ops.object.delete(use_global=False)
    bpy.ops.outliner.orphans_purge()
    for c in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.unlink(c)
    for c in bpy.data.collections:
        if not c.users:
            bpy.data.collections.remove(c)


def scene_setup():
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = get_group_end_time(18) * 30
    bpy.context.scene.render.resolution_y = 2248
    bpy.context.scene.render.resolution_x = 4000
    bpy.context.scene.render.filepath = "/home/sinasta/Documents/MASTER/1sem/AIM/PHASE II/Render/"  # change for render output directory


def map_values(value, old_min, old_max, new_min, new_max):
    old_span = old_max - old_min
    new_span = new_max - new_min
    value_scaled = (value - old_min) / (old_span)
    return new_min + (value_scaled * new_span)


def show_on_second():
    bpy.context.object.hide_viewport = True
    bpy.context.object.hide_render = True
    bpy.context.object.keyframe_insert(
        data_path="hide_viewport", frame=bpy.context.scene.frame_current - 1
    )
    bpy.context.object.keyframe_insert(
        data_path="hide_render", frame=bpy.context.scene.frame_current - 1
    )
    bpy.context.object.hide_viewport = False
    bpy.context.object.hide_render = False
    bpy.context.object.keyframe_insert(
        data_path="hide_viewport", frame=bpy.context.scene.frame_current
    )
    bpy.context.object.keyframe_insert(
        data_path="hide_render", frame=bpy.context.scene.frame_current
    )
    bpy.context.object.hide_viewport = True
    bpy.context.object.hide_render = True
    bpy.context.object.keyframe_insert(
        data_path="hide_viewport", frame=bpy.context.scene.frame_current + 30
    )
    bpy.context.object.keyframe_insert(
        data_path="hide_render", frame=bpy.context.scene.frame_current + 30
    )


def frame_to_second():
    return int(bpy.context.scene.frame_current / 30)


def convert_to_second(frame):
    return int(frame / 30)


### GET FUNCTIONS (RETURNS)


def get_origin_vector(
    group_number,
):  # get origin vector per group (size, % of info, height)
    three_value_table = partition_table.loc[
        group_number, ["SIZE", "% OF INFO", "HEIGHT"]
    ]
    return three_value_table.values.tolist()


def get_origin_vector_list():  # get list of origin vectors per group (size, % of info, height)
    origin_vector_list = []

    for i in range(total_group_amount):
        origin_vector_list.append(get_origin_vector(i))
    return origin_vector_list


def get_group_start_time(group_number):  # get starttime per group
    return int(partition_table.loc[group_number, ["START TIME"]][0])


def get_active_groups_per_time(time):  # get active groups per second
    group_numbers = []

    for i in range(total_group_amount):
        if time >= get_group_start_time(i) and time <= get_group_end_time(i):
            group_numbers.append(i)

    if len(group_numbers) == 0:
        group_numbers.append("no group")
    return group_numbers


def get_group_duration(group_number):  # get duration per group in seconds
    return group_table.loc[group_table["GROUP"] == group_number + 1].shape[0] - 1


def get_group_end_time(group_number):  # get ending second per group
    return get_group_start_time(group_number) + get_group_duration(group_number)


def get_relative_time(group_number, time):  # count relative time per group
    relative_time = 0

    if time >= get_group_start_time(group_number) and time <= get_group_end_time(
        group_number
    ):
        relative_time = time - get_group_start_time(group_number) + 1
    else:
        relative_time = "not active"
    return relative_time


def get_group_height_value(
    group_number, second, symbol
):  # get individual height value per symbol and second
    individual_group_table = group_table.loc[group_table["GROUP"] == group_number + 1]
    individual_values_per_second = individual_group_table.loc[
        individual_group_table["TIME"] == second
    ]
    height_value = int(individual_values_per_second.iloc[:, symbol + 2].tolist()[0])
    return height_value


def get_group_amount_value(
    group_number, second, symbol
):  # get individual amount value per symbol and second
    individual_group_table = group_table.loc[group_table["GROUP"] == group_number + 1]
    individual_values_per_second = individual_group_table.loc[
        individual_group_table["TIME"] == second
    ]
    amount_value = round(
        abs(individual_values_per_second.iloc[:, symbol + 2].tolist()[0]) % 1 * 10
    )
    return amount_value


def get_active_values_and_groups_per_time_and_symbol(
    time, symbol
):  # get list of active groups, amount and height values per time
    height_values = []
    amount_values = []
    active_group_list = get_active_groups_per_time(time)

    if active_group_list[0] != "no group":
        for i in range(len(active_group_list)):
            active_group = active_group_list[i]
            relative_time = get_relative_time(active_group, time)
            height_value = get_group_height_value(active_group, relative_time, symbol)
            height_values.append(height_value)
            amount_value = get_group_amount_value(active_group, relative_time, symbol)
            amount_values.append(amount_value)
    else:
        height_values.append("no group"), amount_values.append("no group")
    return active_group_list, height_values, amount_values


def get_symbols_per_time(
    time,
):  # get all symbols (even blanks) per time divided by groups
    list_of_symbols_amount = []
    list_of_symbols_height = []
    for i in range(total_amount_of_symbols):
        (
            active_group_list,
            amount_values,
            height_values,
        ) = get_active_values_and_groups_per_time_and_symbol(time, i)
        list_of_symbols_amount.append(amount_values)
        list_of_symbols_height.append(height_values)
    return active_group_list, list_of_symbols_amount, list_of_symbols_height


def get_frame_cube_coordinates_list():
    frame = bpy.data.objects["Frame"]
    coordinates = [(frame.matrix_world @ points.co) for points in frame.data.vertices]
    plein_coordinates = [points.to_tuple() for points in coordinates]
    coordinates_list = []
    for i in range(len(plein_coordinates)):
        coordinates_list.append(list(plein_coordinates[i]))
    return coordinates_list


### GENERATOR FUNCTIONS


def new_collection(name):
    def find_layer_collection_recursive(find, col):
        for c in col.children:
            if c.collection == find:
                return c
        return None

    my_collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(my_collection)
    found = find_layer_collection_recursive(
        my_collection, bpy.context.view_layer.layer_collection
    )
    if found:
        bpy.context.view_layer.active_layer_collection = found


def generate_frame_cube():
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.mesh.primitive_cube_add(
        size=1, rotation=(0, 0, 0), scale=(10, 10, 10)
    )  # create frame cube
    bpy.context.object.name = "Frame"
    bpy.context.object.display_type = "WIRE"
    bpy.data.objects["Frame"].hide_render = True


def generate_spheres_at_origins():
    bpy.ops.object.select_all(action="DESELECT")
    for i in range(total_group_amount):
        vector_list = get_origin_vector(i)
        origin_vector = vector_list[:-1] + [vector_list[2]]
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=(list_of_group_relations[i] / 8),
            location=(origin_vector),
            scale=(1, 1, 1),
        )
        bpy.context.object.name = "origin_group_" + str(i)
        bpy.ops.object.modifier_add(type="SUBSURF")
        bpy.context.object.modifiers["Subdivision"].levels = 0
        bpy.context.object.modifiers["Subdivision"].render_levels = 0
        bpy.ops.object.modifier_add(type="WIREFRAME")
        bpy.context.object.modifiers["Wireframe"].thickness = 0.08
        bpy.context.object.modifiers["Wireframe"].use_replace = False
        bpy.context.object.modifiers["Wireframe"].use_even_offset = False

        bpy.context.object.hide_viewport = True
        bpy.context.object.hide_render = True
        bpy.context.object.keyframe_insert(data_path="hide_viewport", frame=0)
        bpy.context.object.keyframe_insert(data_path="hide_render", frame=0)

        bpy.context.object.hide_viewport = False
        bpy.context.object.hide_render = False
        bpy.context.object.scale = (1, 1, 1)
        bpy.context.object.keyframe_insert(
            data_path="hide_viewport", frame=get_group_start_time(i) * 30
        )
        bpy.context.object.keyframe_insert(
            data_path="hide_render", frame=get_group_start_time(i) * 30
        )
        bpy.context.object.keyframe_insert(
            data_path="scale", frame=get_group_start_time(i) * 30
        )

        bpy.context.object.hide_viewport = True
        bpy.context.object.hide_render = True
        duration = 1 + get_group_duration(i) / 40
        bpy.context.object.scale = (duration, duration, duration)

        bpy.context.object.keyframe_insert(
            data_path="hide_viewport", frame=get_group_end_time(i) * 30
        )
        bpy.context.object.keyframe_insert(
            data_path="hide_render", frame=get_group_end_time(i) * 30
        )
        bpy.context.object.keyframe_insert(
            data_path="scale", frame=get_group_end_time(i) * 30
        )


def animate_origins():
    for i in range(int(bpy.context.scene.frame_end / 30)):
        level = transform_treble_key_symbol(i)
        transparency = transform_bass_key_symbol(i)
        print(
            "  ", round(((i + 1) / int(bpy.context.scene.frame_end / 30)) * 100, 1), "%"
        )
        if level == 0:
            for j in range(19):
                bpy.data.objects["origin_group_" + str(j)].modifiers[
                    "Subdivision"
                ].levels = 1
                bpy.data.objects["origin_group_" + str(j)].modifiers[
                    "Subdivision"
                ].render_levels = 1
                bpy.data.objects["origin_group_" + str(j)].modifiers[
                    "Subdivision"
                ].keyframe_insert(data_path="levels", frame=i * 30)
                bpy.data.objects["origin_group_" + str(j)].modifiers[
                    "Subdivision"
                ].keyframe_insert(data_path="render_levels", frame=i * 30)
        if level > 0:
            for j in range(19):
                bpy.data.objects["origin_group_" + str(j)].modifiers[
                    "Subdivision"
                ].levels = 0
                bpy.data.objects["origin_group_" + str(j)].modifiers[
                    "Subdivision"
                ].render_levels = 0
                bpy.data.objects["origin_group_" + str(j)].modifiers[
                    "Subdivision"
                ].keyframe_insert(data_path="levels", frame=i * 30)
                bpy.data.objects["origin_group_" + str(j)].modifiers[
                    "Subdivision"
                ].keyframe_insert(data_path="render_levels", frame=i * 30)
        if transparency == 0:
            for o in range(19):
                bpy.data.objects["origin_group_" + str(o)].modifiers[
                    "Wireframe"
                ].use_replace = False
                bpy.data.objects["origin_group_" + str(o)].modifiers[
                    "Wireframe"
                ].keyframe_insert(data_path="use_replace", frame=i * 30)
        if transparency > 0:
            for p in range(19):
                bpy.data.objects["origin_group_" + str(p)].modifiers[
                    "Wireframe"
                ].use_replace = True
                bpy.data.objects["origin_group_" + str(p)].modifiers[
                    "Wireframe"
                ].keyframe_insert(data_path="use_replace", frame=i * 30)


def generate_group_wire():
    bpy.ops.object.select_all(action="DESELECT")
    origin_list = get_origin_vector_list()
    frame_list = get_frame_cube_coordinates_list()
    origin_list.extend(frame_list)
    group_wire = bpy.data.curves.new("group_wire", "CURVE")  # make a new curve
    group_wire.dimensions = "3D"
    group_wire.bevel_depth = 0.16
    group_wire.bevel_resolution = 10

    group_wire_spline = group_wire.splines.new(
        type="NURBS"
    )  # make a new spline in that curve

    group_wire_spline.points.add(len(origin_list) - 1)  # a spline point for each point
    group_wire.splines[0].use_cyclic_u = True
    group_wire.splines[0].order_u = 2
    group_wire.splines[0].resolution_u = 45

    for p, new_point in zip(
        group_wire_spline.points, origin_list
    ):  # assign the point coordinates to the spline points
        p.co = new_point + [1.0]

    group_wire_object = bpy.data.objects.new(
        "group_wire", group_wire
    )  # make a new object with the curve
    bpy.context.scene.collection.objects.link(group_wire_object)

    group_wire = bpy.context.scene.objects["group_wire"]
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = group_wire
    group_wire.select_set(True)

    bpy.ops.object.modifier_add(type="BUILD")
    bpy.context.object.modifiers["Build"].frame_duration = bpy.context.scene.frame_end


def animate_group_wire():
    for i in range(int(bpy.context.scene.frame_end / 30)):
        marcato = transform_marcato_symbol(i)
        diminuendo = transform_diminuendo_symbol(i)
        print(
            "  ", round(((i + 1) / int(bpy.context.scene.frame_end / 30)) * 100, 1), "%"
        )
        if marcato:
            present_size = bpy.data.curves["group_wire"].bevel_depth
            bpy.data.curves["group_wire"].bevel_depth = present_size + 0.04
            bpy.data.curves["group_wire"].keyframe_insert(
                data_path="bevel_depth", frame=i * 30
            )
            bpy.data.curves["group_wire"].bevel_depth = present_size
        elif diminuendo:
            bpy.data.curves["group_wire"].bevel_depth = (
                bpy.data.curves["group_wire"].bevel_depth - 0.002
            )
            bpy.data.curves["group_wire"].keyframe_insert(
                data_path="bevel_depth", frame=i * 30
            )
        else:
            bpy.data.curves["group_wire"].keyframe_insert(
                data_path="bevel_depth", frame=i * 30
            )


def generate_trimetric_cam():
    cam_data = bpy.data.cameras.new("trimetric_camera")
    cam = bpy.data.objects.new("trimetric_camera", cam_data)

    bpy.data.collections[
        bpy.context.view_layer.active_layer_collection.collection.name
    ].objects.link(cam)
    bpy.context.scene.camera = cam

    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 31.7
    cam.location = Vector((8, -13, 6.5))
    cam.rotation_euler = (math.radians(67), 0.0, math.radians(34))

def animate_camera():
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    bpy.data.objects["Empty"].name = "Camera_rotation"
    bpy.data.objects["Camera_rotation"].keyframe_insert(
        data_path="rotation_euler", frame=0
    )
    bpy.data.objects["Camera_rotation"].rotation_euler[2] = math.radians(180)
    bpy.data.objects["Camera_rotation"].keyframe_insert(
        data_path="rotation_euler", frame= get_group_end_time(18) * 30
    )
    bpy.data.objects['trimetric_camera'].parent = bpy.data.objects['Camera_rotation']
    
    

def generate_horizontal_symbol():
    amount = 4
    vertex_weight = 1
    x1, x2, x3, x4, y1, y2, y3, y4 = -15, -5, 5, 15, 15, 5, -5, -15
    low_left = 0
    high_left = 0
    low_right = 0
    high_right = 0
    points = [
        Vector((x1, y1, random.uniform(low_left, high_left), vertex_weight)),
        Vector((x1, y2, random.uniform(low_left, high_left), vertex_weight)),
        Vector((x1, y3, random.uniform(low_left, high_left), vertex_weight)),
        Vector((x1, y4, random.uniform(low_left, high_left), vertex_weight)),
        Vector((x2, y1, random.uniform(low_left, high_left), vertex_weight)),
        Vector((x2, y2, random.uniform(low_left, high_left), vertex_weight)),
        Vector((x2, y3, random.uniform(low_left, high_left), vertex_weight)),
        Vector((x2, y4, random.uniform(low_left, high_left), vertex_weight)),
        Vector((x3, y1, random.uniform(low_right, high_right), vertex_weight)),
        Vector((x3, y2, random.uniform(low_right, high_right), vertex_weight)),
        Vector((x3, y3, random.uniform(low_right, high_right), vertex_weight)),
        Vector((x3, y4, random.uniform(low_right, high_right), vertex_weight)),
        Vector((x4, y1, random.uniform(low_right, high_right), vertex_weight)),
        Vector((x4, y2, random.uniform(low_right, high_right), vertex_weight)),
        Vector((x4, y3, random.uniform(low_right, high_right), vertex_weight)),
        Vector((x4, y4, random.uniform(low_right, high_right), vertex_weight)),
    ]

    for y in range(amount):
        surface_data = bpy.data.curves.new("horizontal_" + str(y), "SURFACE")

        for f in range(0, len(points), 4):
            spline = surface_data.splines.new(type="NURBS")
            spline.points.add(3)
            for p, new_co in zip(spline.points, points[f : f + 4]):
                p.co = new_co

        horizontal_surface = bpy.data.objects.new("horizontal_" + str(y), surface_data)
        bpy.data.collections[
            bpy.context.view_layer.active_layer_collection.collection.name
        ].objects.link(horizontal_surface)
        splines = horizontal_surface.data.splines

        for s in splines:
            for p in s.points:
                p.select = True

        bpy.context.view_layer.objects.active = horizontal_surface
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.curve.make_segment()
        bpy.ops.object.mode_set(mode="OBJECT")

        horizontal = bpy.context.scene.objects["horizontal_" + str(y)]
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = horizontal
        horizontal.select_set(True)
        bpy.context.object.data.resolution_v = 10
        bpy.context.object.data.resolution_u = 10

        bpy.ops.object.mode_set(mode="EDIT")

        for i in range(len(bpy.data.curves["horizontal_" + str(y)].splines[0].points)):
            bpy.ops.curve.select_all(action="DESELECT")
            bpy.data.curves["horizontal_" + str(y)].splines[0].points[i].select = True
            bpy.ops.object.hook_add_newob()
            bpy.data.objects["Empty"].name = "empty_" + str(y) + "_" + str(i)
        bpy.ops.object.mode_set(mode="OBJECT")

        bpy.ops.object.empty_add(
            type="PLAIN_AXES", align="WORLD", location=(0, 0, 0), scale=(1, 1, 1)
        )
        position = bpy.context.selected_objects[0]
        position.name = "position_" + str(y)
        bpy.ops.object.select_all(action="DESELECT")
        for o in range(16):
            bpy.data.objects["empty_" + str(y) + "_" + str(o)].select_set(True)
        bpy.data.objects["position_" + str(y)].select_set(True)
        bpy.ops.object.parent_set(type="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")

        bpy.context.view_layer.objects.active = bpy.data.objects["horizontal_" + str(y)]
        bpy.ops.object.modifier_add(type="SOLIDIFY")
        bpy.context.object.modifiers["Solidify"].thickness = 0.15
        bpy.ops.object.modifier_add(type="ARRAY")
        bpy.context.object.modifiers["Array"].count = 1
        bpy.context.object.modifiers["Array"].relative_offset_displace[0] = 0


def animate_horizontals():
    symbol = 0
    for i in range(int(bpy.context.scene.frame_end / 30)):
        list_of_symbols = get_symbols_per_time(i)
        print(
            "  ", round(((i + 1) / int(bpy.context.scene.frame_end / 30)) * 100, 1), "%"
        )
        if (
            list_of_symbols[1][0][0] != "no group"
            and sum(list_of_symbols[1][symbol]) != 0
        ):
            slur_down = transform_slur_down_symbol(i)
            slur_up = transform_slur_up_symbol(i)
            slur = (slur_up - slur_down) / 1.8
            legato = transform_legato_symbol(i) * 2
            turn = 0
            turns = []
            for y, element in enumerate(list_of_symbols[1][symbol]):
                if element != 0:
                    height = map_values(element, -5, 13, -4, 4)
                    amount = list_of_symbols[2][symbol][y]
                    bpy.data.objects["position_" + str(turn)].location[2] = height
                    bpy.data.objects["position_" + str(turn)].keyframe_insert(
                        data_path="location", frame=i * 30
                    )
                    bpy.data.objects["horizontal_" + str(turn)].modifiers[
                        "Array"
                    ].count = amount
                    bpy.data.objects["horizontal_" + str(turn)].modifiers[
                        "Array"
                    ].use_relative_offset = False
                    bpy.data.objects["horizontal_" + str(turn)].modifiers[
                        "Array"
                    ].use_constant_offset = True
                    bpy.data.objects["horizontal_" + str(turn)].modifiers[
                        "Array"
                    ].constant_offset_displace[0] = 0
                    if amount == 1:
                        bpy.data.objects["horizontal_" + str(turn)].modifiers[
                            "Array"
                        ].constant_offset_displace[2] = 0
                    elif amount == 2:
                        bpy.data.objects["horizontal_" + str(turn)].modifiers[
                            "Array"
                        ].constant_offset_displace[2] = -0.8
                    elif amount == 3:
                        bpy.data.objects["horizontal_" + str(turn)].modifiers[
                            "Array"
                        ].constant_offset_displace[2] = -0.5
                    bpy.data.objects["horizontal_" + str(turn)].modifiers[
                        "Array"
                    ].keyframe_insert(data_path="count", frame=i * 30)
                    bpy.data.objects["horizontal_" + str(turn)].modifiers[
                        "Array"
                    ].keyframe_insert(
                        data_path="constant_offset_displace", frame=i * 30
                    )

                    bpy.data.objects["horizontal_" + str(turn)].hide_viewport = False
                    bpy.data.objects["horizontal_" + str(turn)].hide_render = False
                    bpy.data.objects["horizontal_" + str(turn)].keyframe_insert(
                        data_path="hide_viewport", frame=i * 30
                    )
                    for z in range(16):
                        for z in [0, 1, 2, 3, 4, 7]:
                            base_location = bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(z)
                            ].location[2]
                            bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(z)
                            ].location[2] = (
                                random.uniform(-1 - legato, 1 - legato) - slur
                            )
                            bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(z)
                            ].keyframe_insert(data_path="location", frame=i * 30)
                            bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(z)
                            ].location[2] = base_location
                            bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(z)
                            ].keyframe_insert(data_path="location", frame=i * 30 + 30)
                        for p in [5, 6]:
                            base_location = bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(p)
                            ].location[2]
                            bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(p)
                            ].location[2] = (
                                random.uniform(-1 + legato, 1 + legato) - slur
                            )
                            bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(p)
                            ].keyframe_insert(data_path="location", frame=i * 30)
                            bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(p)
                            ].location[2] = base_location
                            bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(p)
                            ].keyframe_insert(data_path="location", frame=i * 30 + 30)
                        for o in [8, 11, 12, 13, 14, 15]:
                            base_location = bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(o)
                            ].location[2]
                            bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(o)
                            ].location[2] = (
                                random.uniform(-1 - legato, 1 - legato) + slur
                            )
                            bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(o)
                            ].keyframe_insert(data_path="location", frame=i * 30)
                            bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(o)
                            ].location[2] = base_location
                            bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(o)
                            ].keyframe_insert(data_path="location", frame=i * 30 + 30)
                        for b in [9, 10]:
                            base_location = bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(b)
                            ].location[2]
                            bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(b)
                            ].location[2] = (
                                random.uniform(-1 + legato, 1 + legato) + slur
                            )
                            bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(b)
                            ].keyframe_insert(data_path="location", frame=i * 30)
                            bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(b)
                            ].location[2] = base_location
                            bpy.data.objects[
                                "empty_" + str(turn) + "_" + str(b)
                            ].keyframe_insert(data_path="location", frame=i * 30 + 30)

                    turns.append(turn)
                    turn = turn + 1

            for v in range(4):
                if v not in turns:
                    bpy.data.objects["horizontal_" + str(v)].hide_viewport = True
                    bpy.data.objects["horizontal_" + str(v)].hide_render = True
                    bpy.data.objects["horizontal_" + str(v)].keyframe_insert(
                        data_path="hide_viewport", frame=i * 30
                    )

        else:
            for q in range(4):
                bpy.data.objects["horizontal_" + str(q)].hide_viewport = True
                bpy.data.objects["horizontal_" + str(q)].hide_render = True
                bpy.data.objects["horizontal_" + str(q)].keyframe_insert(
                    data_path="hide_viewport", frame=i * 30
                )


def generate_vertical_symbol():
    symbol = 1
    list_of_symbols = get_symbols_per_time(frame_to_second())
    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        for i, element in enumerate(list_of_symbols[1][symbol]):
            if element != 0:
                height = element
                amount = list_of_symbols[2][symbol][i]
                rotation_degree = map_values(height, -10, 8, -20, 20)
                thickness = amount / 3
                bpy.ops.mesh.primitive_cube_add(
                    size=2,
                    enter_editmode=False,
                    align="WORLD",
                    location=(random.uniform(-4, 4), random.uniform(-4, 4), 0),
                    rotation=(
                        random.uniform(-1, 1) * rotation_degree * math.pi / 180,
                        random.uniform(-1, 1) * rotation_degree * math.pi / 180,
                        random.uniform(-1, 1) * rotation_degree * math.pi / 180,
                    ),
                    scale=(thickness, thickness, 7),
                )
                bpy.context.object.name = "vertical"
                show_on_second()


def generate_note_symbol(negate, scale_up, scale_down, multiply_2, multiply_3, bevel):
    symbol = 4
    second = frame_to_second()
    list_of_symbols = get_symbols_per_time(second)
    if negate:
        scale_up = 1
        scale_down = 1
    if multiply_2 or multiply_3:
        if multiply_3 == False:
            factor = 2
        elif multiply_2 == False:
            factor = 3
        else:
            factor = 4
    else:
        factor = 1

    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        for i in range(factor):
            for j, element in enumerate(list_of_symbols[1][symbol]):
                if element != 0:
                    height_unmapped = element
                    amount = list_of_symbols[2][symbol][j]
                    height = map_values(height_unmapped, -11, 15, -4, 4)
                    for k in range(amount * 2):
                        bpy.ops.mesh.primitive_cube_add(
                            size=1,
                            enter_editmode=False,
                            align="WORLD",
                            location=(
                                random.uniform(-4, 4),
                                random.uniform(-4, 4),
                                height + random.uniform(-1, 1),
                            ),
                            rotation=(
                                math.radians(random.uniform(-45, 45)),
                                math.radians(random.uniform(-45, 45)),
                                math.radians(random.uniform(-45, 45)),
                            ),
                            scale=(
                                random.uniform(1, 2.5) * scale_up * scale_down,
                                random.uniform(1, 2.5) * scale_up * scale_down,
                                random.uniform(1, 2.5) * scale_up * scale_down,
                            ),
                        )
                        bpy.context.object.name = (
                            "note_"
                            + str(second)
                            + "_"
                            + str(i)
                            + "_"
                            + str(j)
                            + "_"
                            + str(k)
                        )
                        if bevel:
                            bpy.ops.object.modifier_add(type="BEVEL")
                            bpy.context.object.modifiers[
                                "Bevel"
                            ].offset_type = "PERCENT"
                            bpy.context.object.modifiers["Bevel"].width_pct = 40
                        show_on_second()


def generate_number_one_symbol():
    symbol = 14
    list_of_symbols = get_symbols_per_time(frame_to_second())
    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        for i, element in enumerate(list_of_symbols[1][symbol]):
            if element != 0:
                height = element
                amount = list_of_symbols[2][symbol][i]
                rotation_degree = map_values(height, -6, 11, -20, 20)
                thickness = amount / 3
                bpy.ops.mesh.primitive_cube_add(
                    size=2,
                    enter_editmode=False,
                    align="WORLD",
                    location=(0, random.uniform(-4, 4), random.uniform(-4, 4)),
                    rotation=(
                        random.uniform(-1, 1) * rotation_degree * math.pi / 180,
                        random.uniform(-1, 1) * rotation_degree * math.pi / 180,
                        random.uniform(-1, 1) * rotation_degree * math.pi / 180,
                    ),
                    scale=(7, thickness, thickness),
                )
                bpy.context.object.name = "number_one"
                show_on_second()


def generate_number_two_symbol():
    symbol = 15
    list_of_symbols = get_symbols_per_time(frame_to_second())
    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        for i, element in enumerate(list_of_symbols[1][symbol]):
            if element != 0:
                height = element
                amount = list_of_symbols[2][symbol][i]
                rotation_degree = map_values(height, -2, -1, -20, 20)
                thickness = amount / 3
                for i in range(2):
                    rotation_degree = height
                    thickness = amount / 2
                    bpy.ops.mesh.primitive_cube_add(
                        size=2,
                        enter_editmode=False,
                        align="WORLD",
                        location=(0, random.uniform(-4, 4), random.uniform(-4, 4)),
                        rotation=(
                            random.uniform(-1, 1) * rotation_degree * math.pi / 180,
                            random.uniform(-1, 1) * rotation_degree * math.pi / 180,
                            random.uniform(-1, 1) * rotation_degree * math.pi / 180,
                        ),
                        scale=(7, thickness, thickness),
                    )
                    bpy.context.object.name = "number_two"
                    show_on_second()


def generate_circle_symbol():
    symbol = 2
    list_of_symbols = get_symbols_per_time(frame_to_second())
    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        for i, element in enumerate(list_of_symbols[1][symbol]):
            if element != 0:
                height_unmapped = element
                amount = list_of_symbols[2][symbol][i]
                height = map_values(height_unmapped, -10, 21, -4.5, 4.5)
                bpy.ops.mesh.primitive_cylinder_add(
                    vertices=60,
                    end_fill_type="NOTHING",
                    radius=(2.5 + random.uniform(0, 4)),
                    depth=random.uniform(0.5, 1),
                    enter_editmode=False,
                    align="WORLD",
                    location=(random.uniform(-4, 4), random.uniform(-4, 4), height),
                    rotation=(
                        math.radians(random.uniform(-45, 45)),
                        math.radians(random.uniform(-45, 45)),
                        math.radians(random.uniform(-45, 45)),
                    ),
                    scale=(1, 1, 1),
                )
                bpy.ops.object.modifier_add(type="SIMPLE_DEFORM")
                bpy.context.object.modifiers["SimpleDeform"].deform_axis = "Z"
                bpy.context.object.modifiers["SimpleDeform"].angle = math.radians(
                    50 + 30 * amount
                )
                bpy.ops.object.modifier_add(type="WIREFRAME")
                bpy.context.object.modifiers["Wireframe"].thickness = 0.1
                bpy.context.object.modifiers["Wireframe"].use_boundary = True
                bpy.context.object.modifiers["Wireframe"].use_even_offset = True
                bpy.context.object.name = (
                    "circle_" + str(frame_to_second()) + "_" + str(i)
                )
                bpy.data.objects[
                    "circle_" + str(frame_to_second()) + "_" + str(i)
                ].modifiers["SimpleDeform"].keyframe_insert(
                    data_path="angle", frame=frame_to_second() * 30 + 30
                )
                bpy.data.objects[
                    "circle_" + str(frame_to_second()) + "_" + str(i)
                ].keyframe_insert(data_path="scale", frame=frame_to_second() * 30 + 20)
                bpy.data.objects[
                    "circle_" + str(frame_to_second()) + "_" + str(i)
                ].scale[0] = 0.5
                bpy.data.objects[
                    "circle_" + str(frame_to_second()) + "_" + str(i)
                ].scale[1] = 0.5
                bpy.data.objects[
                    "circle_" + str(frame_to_second()) + "_" + str(i)
                ].keyframe_insert(data_path="scale", frame=frame_to_second() * 30)
                bpy.data.objects[
                    "circle_" + str(frame_to_second()) + "_" + str(i)
                ].modifiers["SimpleDeform"].angle = 0
                bpy.data.objects[
                    "circle_" + str(frame_to_second()) + "_" + str(i)
                ].modifiers["SimpleDeform"].keyframe_insert(
                    data_path="angle", frame=frame_to_second() * 30
                )
                show_on_second()


### TRANSFORMATOR FUNCTIONS


def transform_legato_symbol(second):
    symbol = 3
    list_of_symbols = get_symbols_per_time(second)
    amount_list = []
    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        for i, element in enumerate(list_of_symbols[2][symbol]):
            if element != 0:
                amount = element
                amount_list.append(amount)
    else:
        amount_list.append(0)
    return sum(amount_list)


def transform_slur_up_symbol(second):
    symbol = 5
    list_of_symbols = get_symbols_per_time(second)
    amount_list = []
    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        for i, element in enumerate(list_of_symbols[2][symbol]):
            if element != 0:
                amount = element
                amount_list.append(amount)
    else:
        amount_list.append(0)
    return sum(amount_list)


def transform_slur_down_symbol(second):
    symbol = 6
    list_of_symbols = get_symbols_per_time(second)
    amount_list = []
    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        for i, element in enumerate(list_of_symbols[2][symbol]):
            if element != 0:
                amount = element
                amount_list.append(amount)
    else:
        amount_list.append(0)
    return sum(amount_list)


def transform_bass_key_symbol(second):
    symbol = 7
    list_of_symbols = get_symbols_per_time(second)
    height_list = []
    amount_list = []
    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        for i, element in enumerate(list_of_symbols[2][symbol]):
            if element != 0:
                amount_list.append(element)
    else:
        amount_list.append(0)
    return sum(amount_list)


def transform_treble_key_symbol(second):
    symbol = 8
    list_of_symbols = get_symbols_per_time(second)
    height_list = []
    amount_list = []
    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        for i, element in enumerate(list_of_symbols[2][symbol]):
            if element != 0:
                amount_list.append(element)
    else:
        amount_list.append(0)
    return sum(amount_list)


def transform_sharp_symbol():
    symbol = 9
    list_of_symbols = get_symbols_per_time(frame_to_second())
    result_list = []
    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        for i, element in enumerate(list_of_symbols[1][symbol]):
            if element != 0:
                height = map_values(element, -5, 7, 1.1, 2.3)
                amount = list_of_symbols[2][symbol][i]
                result_list.append(height)
    else:
        result_list.append(1)
    return sum(result_list) / len(result_list)


def transform_flat_symbol():
    symbol = 10
    list_of_symbols = get_symbols_per_time(frame_to_second())
    result_list = []
    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        for i, element in enumerate(list_of_symbols[1][symbol]):
            if element != 0:
                height = map_values(element, -10, 8, 1, 5)
                amount = list_of_symbols[2][symbol][i]
                result_list.append((1 - height / 10) / (amount / 10 + 1))
    else:
        result_list.append(1)
    return sum(result_list) / len(result_list)


def transform_marcato_symbol(second):
    symbol = 11
    list_of_symbols = get_symbols_per_time(second)
    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        result = True
    else:
        result = False
    return result


def transform_natural_symbol():
    symbol = 12
    list_of_symbols = get_symbols_per_time(frame_to_second())
    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        result = True
    else:
        result = False
    return result


def transform_diminuendo_symbol(second):
    symbol = 13
    list_of_symbols = get_symbols_per_time(second)
    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        result = True
    else:
        result = False
    return result


def transform_staccato_symbol():
    symbol = 16
    list_of_symbols = get_symbols_per_time(frame_to_second())
    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        result = True
    else:
        result = False
    return result


def transform_sullarco_symbol():
    symbol = 17
    list_of_symbols = get_symbols_per_time(frame_to_second())
    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        result = True
    else:
        result = False
    return result


def transform_upper_mordent_symbol():
    symbol = 18
    list_of_symbols = get_symbols_per_time(frame_to_second())
    if list_of_symbols[1][0][0] != "no group" and sum(list_of_symbols[1][symbol]) != 0:
        result = True
    else:
        result = False
    return result


### GENERATION


clean_terminal()
print("cleaning up ...", end=" ")
clean()
print("preparing the scene ...")
scene_setup()
print("  done")
print("starting generation")
print("")

print("generating Camera ...")
new_collection("Cameras")
generate_trimetric_cam()
animate_camera()
print("  done")
print("generating Cube ...")
new_collection("Frame")
generate_frame_cube()
print("  done")
print("generating Wire ...")
generate_group_wire()
print(" animating Wire ...")
animate_group_wire()
print("  done")
print("generating Origins ...")
new_collection("Origins")
generate_spheres_at_origins()
print(" animating Origins ...")
animate_origins()
print("  done")
print("generating Horizontals ...")
new_collection("Horizontals")
generate_horizontal_symbol()
print(" animating Horizontals ...")
animate_horizontals()
print("  done")
print("")

end = get_group_end_time(18)

for i in range(end):
    bpy.context.scene.frame_set(i * 30)
    print(
        "generating Collection for Second: " + str(i),
        " / " + str(end),
    )
    print("")
    new_collection("Second_" + str(i))
    print("   generating Verticals for Second: " + str(i), "...")
    generate_vertical_symbol()
    print("     done")
    print("   generating Notes for Second: " + str(i), "...")
    generate_note_symbol(
        transform_natural_symbol(),
        transform_sharp_symbol(),
        transform_flat_symbol(),
        transform_sullarco_symbol(),
        transform_upper_mordent_symbol(),
        transform_staccato_symbol(),
    )
    print("     done")
    print("   generating Number One for Second: " + str(i), "...")
    generate_number_one_symbol()
    print("     done")
    print("   generating Number Two for Second: " + str(i), "...")
    generate_number_two_symbol()
    print("     done")
    print("   generating Circles for Second: " + str(i), "...")
    generate_circle_symbol()
    print("     done")
    print("")

print("")
print("execution successfull")
print("execution took: ", round((time.time() - start_time) / 60.0, 2), " minutes")