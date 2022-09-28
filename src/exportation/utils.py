from xml.dom.minidom import parseString
import xml.etree.ElementTree as ET
import shapely.wkt
import numpy as np
import math
import os

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

def get_patch_origin(patch_coords):
    x = [p[0] for p in patch_coords]
    y = [p[1] for p in patch_coords]
    return (int(min(x)), int(min(y)))

def fix_borders(x_min, x_max, y_min, y_max, patch_size, point_class):
    aux = {
        "x_min":x_min,
        "x_max":x_max,
        "y_min":patch_size - y_min + 1,
        "y_max":patch_size - y_max + 1
    }
    for key, value in aux.items():
        if value > int(patch_size - 1):
            aux[key] = int(patch_size - 1)
        elif value < 0:
            aux[key] = 0
    return (aux["x_min"], aux["x_max"], aux["y_min"], aux["y_max"], point_class)

def create_pascal_xml(boxes, output_path, folder, patch_filename, patch_size):
    #input_path_base_xml = 'base.xml'
    input_path_base_xml = f'<annotation><folder>{folder}</folder>-<path>{output_path}</path>-<filename>{patch_filename}</filename>-<source><annotation>CellsIA Viewer</annotation></source>-<size><width>{patch_size}</width><height>{patch_size}</height><depth>3</depth></size>-<object><name>0</name>-<bndbox><xmin>786</xmin><ymin>654</ymin><xmax>837</xmax><ymax>715</ymax></bndbox></object></annotation>'
    poligonos = boxes
    dom = parseString(input_path_base_xml)
    dom_aux = parseString(input_path_base_xml)
    #     object_dom_aux = dom.getElementsByTagName('object')[0]
    dom_filename = dom.getElementsByTagName('filename')[0]
    dom_width = dom.getElementsByTagName('width')[0]
    dom_height = dom.getElementsByTagName('height')[0]
    dom_depth = dom.getElementsByTagName('depth')[0]
    for num_pol, box in enumerate(boxes):
        if len(box) == 5:
            name = box[4]
        else:
            name = ''
        x = []
        y = []
        xmin = box[0]
        xmax = box[1]
        ymin = box[2]
        ymax = box[3]
        if num_pol == 0:      
            dom_xmin = dom.getElementsByTagName('object')[0].getElementsByTagName('xmin')[0]
            dom_ymin = dom.getElementsByTagName('object')[0].getElementsByTagName('ymin')[0]
            dom_xmax = dom.getElementsByTagName('object')[0].getElementsByTagName('xmax')[0]
            dom_ymax = dom.getElementsByTagName('object')[0].getElementsByTagName('ymax')[0]
            dom_name = dom.getElementsByTagName('object')[0].getElementsByTagName('name')[0]
            dom_xmin.firstChild.data = xmin
            dom_xmax.firstChild.data = xmax
            dom_ymin.firstChild.data = ymin
            dom_ymax.firstChild.data = ymax
            dom_name.firstChild.data = name
        else:
            object_dom_aux = dom_aux.getElementsByTagName('object')[0].cloneNode(deep=True)      
            dom_xmin = object_dom_aux.getElementsByTagName('xmin')[0]
            dom_ymin = object_dom_aux.getElementsByTagName('ymin')[0]
            dom_xmax = object_dom_aux.getElementsByTagName('xmax')[0]
            dom_ymax = object_dom_aux.getElementsByTagName('ymax')[0]
            dom_name = object_dom_aux.getElementsByTagName('name')[0]
            dom_xmin.firstChild.data = xmin
            dom_xmax.firstChild.data = xmax
            dom_ymin.firstChild.data = ymin
            dom_ymax.firstChild.data = ymax
            dom_name.firstChild.data = name
            dom.firstChild.appendChild(object_dom_aux)
    myxml = open(output_path, 'w+')
    myxml.write(dom.toprettyxml())
    myxml.close()

def _convert(size, box):
    dw = 1./(size[0])
    dh = 1./(size[1])
    x = (box[0] + box[1])/2.0 - 1
    y = (box[2] + box[3])/2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

def create_coco_from_pascal(image_no_ext, working_path):
    in_file = open(os.path.join(working_path, f"{image_no_ext}.xml"))
    out_file = open(os.path.join(working_path, f"{image_no_ext}.txt"), "w")
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    for obj in root.iter('object'):
        cls = obj.find('name').text
        # cls_id = str(int(cls)-1)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = _convert((w,h), b)
        out_file.write(str(cls) + " " + " ".join([str(a) for a in bb]) + '\n')

def box_size_parser(str_box_size):
    str_sizes = str_box_size.split("|")
    sizes = [s.split(",") for s in str_sizes]
    output_sizes = {}
    for s in sizes:
        output_sizes[s[0]] = int(s[1])
    return output_sizes

    
