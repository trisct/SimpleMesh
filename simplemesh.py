import trimesh
import argparse
import math
import einops

def get_bbox_mesh(mesh):
    bbox_max = mesh.vertices.max(axis=0)
    bbox_min = mesh.vertices.min(axis=0)

    return bbox_max, bbox_min
    
def get_bbox_scene(scene):
    bbox_maxs = []
    bbox_mins = []
    
    for mesh in scene.geometry.values():
        bbox_max, bbox_min = get_bbox_mesh(mesh)
        
        bbox_maxs.append(bbox_max)
        bbox_mins.append(bbox_min)
            
    bbox_maxs = einops.rearrange(bbox_maxs, 'n c -> n c')
    bbox_mins = einops.rearrange(bbox_mins, 'n c -> n c')

    bbox_max = bbox_maxs.max(axis=0)
    bbox_min = bbox_mins.max(axis=0)

    return bbox_max, bbox_min




parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', type=str, required=True)
parser.add_argument('-o', '--output', type=str)
parser.add_argument('-n', '--normalize', type=float)
parser.add_argument('-r', '--rotate', nargs=2)
parser.add_argument('--skip_textures', action='store_true')

pi = math.pi
opt = parser.parse_args()

#skip_textures = True if opt.skip_textures else False

mesh = trimesh.load(opt.input)#, skip_textures=skip_textures)

if opt.normalize is not None:
    print('[HERE: In smplmesh] --normalize specified, target bounding box is [-%.4f, %.4f]' % (opt.normalize, opt.normalize))

    bbox_min, bbox_max = mesh.bounds
    bbox_cent = .5 * (bbox_min + bbox_max)

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

if opt.output is None:
    opt.output = opt.input[:-4] + '_aalnormed.obj'

#mesh.show()
mesh.export(opt.output)
