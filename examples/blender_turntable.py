# Render a part (STL) as a clean studio still, or a turntable animation, with no window.
#
# Still image:
#   blender --background --factory-startup --python examples/blender_turntable.py -- out/plate.stl
# Turntable (36 frames, then stitch with ffmpeg if you have it):
#   blender --background --factory-startup --python examples/blender_turntable.py -- out/plate.stl --frames 36
#
# Output goes next to the STL: <name>.png, or <name>_0001.png ... for a turntable.
import bpy, sys, os, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if not argv:
    sys.exit("give an STL path after --")
stl = os.path.abspath(argv[0])
frames = int(argv[argv.index("--frames") + 1]) if "--frames" in argv else 1
samples = int(argv[argv.index("--samples") + 1]) if "--samples" in argv else 64
stem = os.path.splitext(stl)[0]

# Start empty.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Import. CAD exports are in millimetres; Blender thinks in metres, so scale down.
bpy.ops.wm.stl_import(filepath=stl)
part = bpy.context.selected_objects[0]
part.scale = (0.001, 0.001, 0.001)
bpy.context.view_layer.update()
bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
part.location = (0, 0, 0)
bpy.context.view_layer.update()
corners = [part.matrix_world @ Vector(c) for c in part.bound_box]
size = max((max(c[i] for c in corners) - min(c[i] for c in corners)) for i in range(3))
zmin = min(c.z for c in corners)
bpy.ops.object.shade_auto_smooth()

# Brushed metal material.
mat = bpy.data.materials.new("metal"); mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.75, 0.76, 0.78, 1)
bsdf.inputs["Metallic"].default_value = 1.0
bsdf.inputs["Roughness"].default_value = 0.3
part.data.materials.append(mat)

# Turntable pivot: the part rotates, camera and lights stay put.
pivot = bpy.data.objects.new("pivot", None); scene.collection.objects.link(pivot)
part.parent = pivot

# Floor.
bpy.ops.mesh.primitive_plane_add(size=size * 40, location=(0, 0, zmin))
floor = bpy.context.object
fm = bpy.data.materials.new("floor"); fm.use_nodes = True
fb = fm.node_tree.nodes["Principled BSDF"]
fb.inputs["Base Color"].default_value = (0.55, 0.55, 0.55, 1)
fb.inputs["Roughness"].default_value = 0.6
floor.data.materials.append(fm)

# Lights: one big soft key, one fill, plus a light grey world.
def area(name, loc, power, sz):
    d = bpy.data.lights.new(name, "AREA"); d.energy = power; d.size = sz
    o = bpy.data.objects.new(name, d); scene.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
area("key", (size * 1.5, -size * 1.5, size * 2.5), 400 * size ** 2, size * 2)
area("fill", (-size * 2, -size * 0.5, size * 1.2), 120 * size ** 2, size * 3)
world = bpy.data.worlds.new("w"); scene.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.8, 0.8, 0.8, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.4

# Camera, three-quarter view, framed to the part.
cam_data = bpy.data.cameras.new("cam"); cam_data.lens = 85
cam = bpy.data.objects.new("cam", cam_data); scene.collection.objects.link(cam); scene.camera = cam
cam.location = (size * 1.9, -size * 2.6, size * 1.8)
cam.rotation_euler = (Vector((0, 0, 0)) - cam.location).to_track_quat("-Z", "Y").to_euler()

# Render settings. Cycles works without a GPU or a display; try the GPU, fall back to CPU.
scene.render.engine = "CYCLES"
scene.cycles.samples = samples
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1600, 1200
scene.render.film_transparent = False
device = "CPU"
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for kind in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
        try:
            prefs.compute_device_type = kind
        except TypeError:
            continue
        prefs.refresh_devices()
        gpus = [d for d in prefs.devices if d.type == kind]
        if gpus:
            for d in prefs.devices:
                d.use = d.type == kind
            scene.cycles.device = "GPU"; device = f"GPU ({kind})"
            break
except Exception as e:
    print("GPU setup skipped:", e)
print("Rendering on", device)

if frames <= 1:
    scene.render.filepath = stem + ".png"
    bpy.ops.render.render(write_still=True)
    print("OK still:", scene.render.filepath)
else:
    scene.frame_start, scene.frame_end = 1, frames
    pivot.rotation_euler = (0, 0, 0); pivot.keyframe_insert("rotation_euler", frame=1)
    pivot.rotation_euler = (0, 0, 2 * math.pi * frames / (frames + 1)); pivot.keyframe_insert("rotation_euler", frame=frames)
    for fc in pivot.animation_data.action.fcurves if hasattr(pivot.animation_data.action, "fcurves") else []:
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"
    scene.render.filepath = stem + "_"
    bpy.ops.render.render(animation=True)
    print(f"OK turntable: {frames} frames at {stem}_####.png")
