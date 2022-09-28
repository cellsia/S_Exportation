from cytomine.models.image import ImageInstanceCollection
from exportation.utils import get_patch_origin, fix_borders, box_size_parser
from cytomine.models import TermCollection



class OutputFormatter():

    def __init__(self):
        self.template = None
        self.output_file = None
        self.default_box_size = 50

    def _fetch_image_info(self, project_id: int, image_id: int) -> None:
        if image_id:
            image_instances = ImageInstanceCollection().fetch_with_filter("project", project_id)
            filtered_image_instances_iterable = filter(lambda i:i.id == image_id, image_instances)
            image = list(filtered_image_instances_iterable)[0]
            self.template["image_id"] = image.id
            self.template["image_name"] = image.originalFilename

    def _get_term_name(self, term_id: int, project_id: int) -> str:
        termcollection = TermCollection().fetch_with_filter("project", project_id)
        term_iterator = filter(lambda t:t.id==term_id, termcollection)
        term = list(term_iterator)[0]
        return term.name

    def _group_points_by_class(self, points, project_id: int) -> dict:
        points_by_class = {}
        for p in points:
            if p.term:
                term_name = self._get_term_name(p.term[0], project_id)
                if not term_name in points_by_class:
                    points_by_class[term_name] = []
                points_by_class[term_name].append((int(p.x), int(p.y)))
            else:
                if not "no_term" in points_by_class.keys():
                    points_by_class = {"no_term": []}
                points_by_class["no_term"].append((int(p.x), int(p.y)))
        return points_by_class

    def _format_patch(self, key: int, patch, project_id: int) -> dict:
        patch["patch_id"] = key
        patch["inside_points_len"] = len(patch["inside_points"])
        points = patch["inside_points"]
        patch["inside_points"] = self._group_points_by_class(points, project_id)
        patch["classes"] = list(patch["inside_points"].keys())
        return patch

    def _format_patches(self, project_id: int) -> None:
        patches = self.template["patches"]
        self.template["patches"] = []
        for key, patch in patches.items():
            self.template["patches"].append(self._format_patch(key, patch, project_id))

    def _format_boxes(self, box_sizes: int) -> None:
        patches = self.template["patches"]
        for patch in patches:
            all_points = []
            patch_coords = patch["patch_coords"]
            origin = get_patch_origin(patch_coords)
            patch_size = patch["patch_size"]
            for point_class, points in patch["inside_points"].items():
                for p in points:
                    if point_class in box_sizes.keys():
                        box_size = box_sizes[point_class]
                    else:
                        box_size = self.default_box_size
                    x_min = int((p[0] - (box_size / 2)) - origin[0])
                    x_max = int((p[0] + (box_size / 2)) - origin[0])
                    y_min = int((p[1] + (box_size / 2)) - origin[1])                   
                    y_max = int((p[1] - (box_size / 2)) - origin[1])                   
                    box = fix_borders(x_min, x_max, y_min, y_max, patch_size, point_class)
                    all_points.append(box)
            patch["inside_points"] = all_points
                    
    def set_template(self, template: dict) -> None:
        self.template = template

    def set_output_file(self, output_file: str) -> None:
        self.output_file = output_file

    def format(self, project, params) -> None:
        if self.output_file in ["json", "pascal", "coco"]:    
            self._fetch_image_info(project.id, params.image_to_analyze)
            self._format_patches(project.id)
            self._format_boxes(box_size_parser(params.box_size))