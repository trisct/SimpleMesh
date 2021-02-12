import trimesh
import argparse
import math

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', type=str, required=True)
parser.add_argument('-o', '--output', type=str, required=True)
parser.add_argument('-n', '--normalize', type=float)
parser.add_argument('-r', '--rotate', nargs=2)

def as_mesh(scene_or_mesh):
    """
    Convert a possible scene to a mesh.

    If conversion occurs, the returned mesh has only vertex and face data.
    """
    if isinstance(scene_or_mesh, trimesh.Scene):
        print('[HERE: In simplemesh.as_mesh] This is a Scene...Something may go wrong.')
        if len(scene_or_mesh.geometry) == 0:
            mesh = None  # empty scene
        else:
            # we lose texture information here
            mesh = trimesh.util.concatenate(
                tuple(trimesh.Trimesh(vertices=g.vertices, faces=g.faces)
                    for g in scene_or_mesh.geometry.values()))
    else:
        assert(isinstance(scene_or_mesh, trimesh.Trimesh))
        mesh = scene_or_mesh
    return mesh

pi = math.pi
opt = parser.parse_args()

mesh = trimesh.load_mesh(opt.input)
mesh = as_mesh(mesh)


if opt.normalize is not None:
    print('[HERE: In smplmesh] --normalize specified, target bounding box is [-%.4f, %.4f]' % (opt.normalize, opt.normalize))

    bbox_max = mesh.vertices.max(axis=0)
    bbox_min = mesh.vertices.min(axis=0)
    bbox_cent = .5 * (bbox_max + bbox_min)

    axis_extent = bbox_max - bbox_min
    max_extent = axis_extent.max()

    scale_transfm = trimesh.transformations.scale_matrix(factor=2*opt.normalize/max_extent)
    trans_transfm = trimesh.transformations.translation_matrix(direction=-bbox_cent)

    mesh.apply_transform(trans_transfm)
    mesh.apply_transform(scale_transfm)

if opt.rotate is not None:
    opt.rotate[1] = eval(opt.rotate[1])
    
    print('[HERE: In smplmesh] --rotate specified, will rotate %.4f degrees around the %s axis' % (opt.rotate[1], opt.rotate[0]))

    if opt.rotate[0] == 'x':
        direction = [1,0,0]
    elif opt.rotate[0] == 'y':
        direction = [0,1,0]
    elif opt.rotate[0] == 'z':
        direction = [0,0,1]
    else:
        print('Invalid rotation axis')
        opt.rotate[1] = 0.

    rot_transfm = trimesh.transformations.rotation_matrix(
        angle=opt.rotate[1]*pi/180,
        direction=direction,
        point=[0,0,0])
    mesh.apply_transform(rot_transfm)

mesh.export(opt.output)
