import shapely.wkt
import math

get_annot_geometry = lambda annot:shapely.wkt.loads(annot.location)

def get_distances(polygon):
    poly_points = list(polygon.exterior.coords)
    aux_poly_points = zip(poly_points, poly_points[1:])
    distances = list(map(lambda p:int(math.dist(p[0],p[1])), aux_poly_points))
    return distances

def is_polygon(annotation) -> bool:
    annot_geometry = get_annot_geometry(annotation)
    return annot_geometry.geom_type == "Polygon"

def is_point(annotation) -> bool:
    annot_geometry = get_annot_geometry(annotation)
    return annot_geometry.geom_type == "Point"

def is_patch(polygon) -> bool:
    poly_geometry = get_annot_geometry(polygon)
    distances = get_distances(poly_geometry)
    return all(d%256==0 for d in distances)

def get_patch_sizes(patches):
    sizes = {}
    for patch in patches:
        poly_geometry = get_annot_geometry(patch)
        distances = get_distances(poly_geometry)
        patch_size = distances[0]
        if not patch_size in sizes.keys():
            sizes[patch_size] = 0
        sizes[patch_size] += 1
    return sizes