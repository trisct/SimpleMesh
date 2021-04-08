import trimesh
import argparse
import math
import einops


parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', type=str, required=True)
parser.add_argument('-I', '--info', action='store_true')
parser.add_argument('-r', '--rotate', nargs='+')
parser.add_argument('-n', '--normalize', type=float)
parser.add_argument('-o', '--output', nargs='?', const=True)

pi = math.pi
args = parser.parse_args()

#skip_textures = True if opt.skip_textures else False

def display_info(mesh):
    print('[In simplemesh] --info specified, displaying object info...')
    print(f'| Object type: {mesh}')
    print(f'| Object bbox:\n{mesh.bounds}')


def normalize_by_bbox_(mesh, bound):
    """
    Normalizes the mesh to [-bound, bound]^3.

    Note that this is in-place.
    """
    print(f'[In simplemesh] --normalize specified, target bounding box is [-{bound:.4f}, {bound:.4f}]')

    bbox_min, bbox_max = mesh.bounds
    bbox_cent = .5 * (bbox_min + bbox_max)

    axis_extent = bbox_max - bbox_min
    max_extent = axis_extent.max()

    scale_transfm = trimesh.transformations.scale_matrix(factor=2*bound/max_extent)
    trans_transfm = trimesh.transformations.translation_matrix(direction=-bbox_cent)

    mesh.apply_transform(trans_transfm)
    mesh.apply_transform(scale_transfm)

def rotate_by_deg_(mesh, axis, deg):
    if axis == 'x':
        direction = [1,0,0]
    elif axis == 'y':
        direction = [0,1,0]
    elif axis == 'z':
        direction = [0,0,1]
    else:
        print(f'[In simplemesh] --rotate specified, but with invalid rotation axis: {axis}')
        return
        
    print(f'[In simplemesh] --rotate specified, will rotate {deg:.4f} degrees around the {axis} axis')

    rot_transfm = trimesh.transformations.rotation_matrix(
        angle=deg*pi/180,
        direction=direction,
        point=[0,0,0])
    mesh.apply_transform(rot_transfm)

def export(mesh, in_name, out_name):
    if out_name == True:
        out_name = in_name[:-4] + '_processed.obj'
    print(f'[In simplemesh] --output specified, will output to {out_name}')
    mesh.export(out_name)

if __name__ == '__main__':
    mesh = trimesh.load(args.input)#, skip_textures=skip_textures)
    
    if args.info:
        display_info(mesh)
    
    if args.rotate is not None:
        i = 0
        while i < len(args.rotate):
            axis = args.rotate[i]
            deg = eval(args.rotate[i+1])
            rotate_by_deg_(mesh, axis, deg)
            i = i + 2
        del i, axis, deg

    if args.normalize is not None:
        bound = args.normalize
        normalize_by_bbox_(mesh, bound)
        del bound

    if args.output is not None:
        in_name = args.input
        out_name = args.output
        export(mesh, in_name, out_name)

