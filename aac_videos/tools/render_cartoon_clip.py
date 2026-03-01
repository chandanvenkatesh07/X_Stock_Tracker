#!/usr/bin/env python3
"""
Run with:
blender -b -P render_cartoon_clip.py -- --phrase "Yes" --out /tmp/yes.mp4 --gender male --action yes
"""
import argparse
import math
import bpy


def parse_args():
    import sys
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    p = argparse.ArgumentParser()
    p.add_argument("--phrase", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--gender", choices=["male", "female"], default="male")
    p.add_argument("--action", default="neutral")
    return p.parse_args(argv)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def make_mat(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 0.6
    return mat


def add_character(gender="male"):
    skin = make_mat("Skin", (0.96, 0.78, 0.62))
    cloth_color = (0.22, 0.52, 0.95) if gender == "male" else (0.92, 0.38, 0.66)
    cloth = make_mat("Cloth", cloth_color)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.23, location=(0, 0, 1.45))
    head = bpy.context.object
    head.name = "Head"
    head.data.materials.append(skin)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.55, location=(0, 0, 1.0))
    body = bpy.context.object
    body.name = "Body"
    body.data.materials.append(cloth)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.35, location=(-0.32, 0, 1.07))
    arm_l = bpy.context.object
    arm_l.rotation_euler[1] = math.radians(90)
    arm_l.data.materials.append(skin)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.35, location=(0.32, 0, 1.07))
    arm_r = bpy.context.object
    arm_r.rotation_euler[1] = math.radians(90)
    arm_r.data.materials.append(skin)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.45, location=(-0.11, 0, 0.55))
    leg_l = bpy.context.object
    leg_l.data.materials.append(cloth)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.45, location=(0.11, 0, 0.55))
    leg_r = bpy.context.object
    leg_r.data.materials.append(cloth)

    # parent all to body
    for obj in [head, arm_l, arm_r, leg_l, leg_r]:
        obj.parent = body

    return body, head, arm_l, arm_r


def add_environment(phrase):
    # Floor
    mat_floor = make_mat("Floor", (0.9, 0.95, 1.0))
    bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0.3))
    floor = bpy.context.object
    floor.data.materials.append(mat_floor)

    # soft backdrop wall
    mat_wall = make_mat("Wall", (0.82, 0.92, 1.0))
    bpy.ops.mesh.primitive_plane_add(size=6, location=(0, -1.5, 2.0))
    wall = bpy.context.object
    wall.rotation_euler[0] = math.radians(90)
    wall.data.materials.append(mat_wall)

    bpy.ops.object.light_add(type="AREA", location=(1.2, -0.7, 3.2))
    key = bpy.context.object
    key.data.energy = 900

    bpy.ops.object.light_add(type="AREA", location=(-1.0, -0.4, 2.8))
    fill = bpy.context.object
    fill.data.energy = 400

    bpy.ops.object.camera_add(location=(0, -2.15, 1.25), rotation=(math.radians(80), 0, 0))
    cam = bpy.context.object
    bpy.context.scene.camera = cam

    # 3D text title above character
    bpy.ops.object.text_add(location=(0, -0.1, 2.25), rotation=(math.radians(90), 0, 0))
    txt = bpy.context.object
    txt.data.body = phrase
    txt.data.align_x = 'CENTER'
    txt.data.size = 0.18


def kf(obj, frame, **kwargs):
    for k, v in kwargs.items():
        setattr(obj, k, v)
        obj.keyframe_insert(data_path=k, frame=frame)


def animate(action, body, head, arm_l, arm_r):
    # baseline subtle bounce
    kf(body, 1, location=(0, 0, 1.0))
    kf(body, 36, location=(0, 0, 1.03))
    kf(body, 72, location=(0, 0, 1.0))
    kf(body, 108, location=(0, 0, 1.03))
    kf(body, 144, location=(0, 0, 1.0))

    if action == "yes":
        for f, ang in [(30, -10), (45, 10), (60, -10), (75, 10), (90, 0)]:
            head.rotation_euler = (math.radians(ang), 0, 0)
            head.keyframe_insert(data_path="rotation_euler", frame=f)
        arm_r.rotation_euler = (0, math.radians(90), math.radians(-40))
        arm_r.keyframe_insert(data_path="rotation_euler", frame=70)
    elif action == "no":
        for f, ang in [(30, -16), (45, 16), (60, -16), (75, 16), (90, 0)]:
            head.rotation_euler = (0, 0, math.radians(ang))
            head.keyframe_insert(data_path="rotation_euler", frame=f)
    elif action == "hello" or action == "goodbye":
        for f, ang in [(24, -20), (36, 30), (48, -20), (60, 30), (72, 0)]:
            arm_r.rotation_euler = (0, math.radians(90), math.radians(ang))
            arm_r.keyframe_insert(data_path="rotation_euler", frame=f)
    elif action == "stop":
        arm_r.rotation_euler = (0, math.radians(90), math.radians(85))
        arm_r.keyframe_insert(data_path="rotation_euler", frame=50)
    elif action == "help":
        arm_r.rotation_euler = (0, math.radians(90), math.radians(-85))
        arm_r.keyframe_insert(data_path="rotation_euler", frame=50)
    elif action == "love":
        arm_l.rotation_euler = (0, math.radians(90), math.radians(50))
        arm_r.rotation_euler = (0, math.radians(90), math.radians(-50))
        arm_l.keyframe_insert(data_path="rotation_euler", frame=58)
        arm_r.keyframe_insert(data_path="rotation_euler", frame=58)
    else:
        # neutral gesture: slight open arms
        arm_l.rotation_euler = (0, math.radians(90), math.radians(20))
        arm_r.rotation_euler = (0, math.radians(90), math.radians(-20))
        arm_l.keyframe_insert(data_path="rotation_euler", frame=50)
        arm_r.keyframe_insert(data_path="rotation_euler", frame=50)


def action_for_phrase(phrase):
    p = phrase.lower().strip()
    if p == "yes":
        return "yes"
    if p == "no":
        return "no"
    if p == "hello":
        return "hello"
    if p == "goodbye":
        return "goodbye"
    if p == "stop":
        return "stop"
    if p == "i need help":
        return "help"
    if p == "i love you":
        return "love"
    return "neutral"


def configure_render(out_path):
    s = bpy.context.scene
    s.render.engine = 'BLENDER_EEVEE'
    s.eevee.taa_render_samples = 16
    s.render.resolution_x = 1080
    s.render.resolution_y = 1920
    s.render.fps = 24
    s.frame_start = 1
    s.frame_end = 144  # 6 sec
    s.render.image_settings.file_format = 'FFMPEG'
    s.render.ffmpeg.format = 'MPEG4'
    s.render.ffmpeg.codec = 'H264'
    s.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    s.render.ffmpeg.ffmpeg_preset = 'GOOD'
    s.render.filepath = out_path


def main():
    args = parse_args()
    clear_scene()
    body, head, arm_l, arm_r = add_character(args.gender)
    add_environment(args.phrase)
    action = args.action if args.action and args.action != "auto" else action_for_phrase(args.phrase)
    animate(action, body, head, arm_l, arm_r)
    configure_render(args.out)
    bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()
