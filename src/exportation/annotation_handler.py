from importlib.resources import path
from cytomine.models.annotation import AnnotationCollection
from exportation.utils import is_polygon, is_patch, is_point, get_patch_sizes, get_annot_geometry, get_distances
from exportation.templates import all_patches_template, patch_template

class AnnotationHandler():

    def __init__(self):
        self.patches = None
        self.points = None
        self.template = None
        self.patch_points = None

    def _fetch_image_annotations(self, project_id: int, image_id: int, reviewed = False) -> AnnotationCollection():
        annotations = AnnotationCollection()
        annotations.project = project_id
        annotations.image = image_id
        annotations.reviewed = reviewed
        annotations.showWKT = True
        annotations.showMeta = True
        annotations.showGIS = True
        annotations.showTerm = True
        annotations.fetch()
        return annotations

    def _generate_all_patches_template(self) -> None:
        self.template = all_patches_template
        self.template["image_patches_len"] = len(self.patches)
        self.template["image_patches_len_per_size"] = get_patch_sizes(self.patches)
        self.template["image_points_len"] = len(self.points)

    def _iterate_points(self) -> None:
        self.patch_points = {}
        for patch in self.patches:
            self.patch_points[patch.id] = patch_template.copy()
            self.patch_points[patch.id]["patch_id"] = patch.id
            poly = get_annot_geometry(patch)
            distances = get_distances(poly)
            self.patch_points[patch.id]["patch_size"] = distances[0]
            self.patch_points[patch.id]["patch_coords"] = list(poly.exterior.coords)
            self.patch_points[patch.id]["inside_points"] = []
            self.patch_points[patch.id]["inside_points_len"] = 0
            self.patch_points[patch.id]["image"] = patch.image
            for p in self.points:
                point = get_annot_geometry(p)
                if poly.contains(point):
                    self.patch_points[patch.id]["inside_points_len"] += 1
                    self.patch_points[patch.id]["inside_points"].append(p)
        self.template["patches"] = self.patch_points     

    def get_patches(self, project_id: int, image_id: int) -> None:
        user_annotations = self._fetch_image_annotations(project_id, image_id, reviewed = True)
        polygons_iterator = filter(is_polygon, user_annotations)
        polygons = list(polygons_iterator)
        patches_iterator = filter(is_patch, polygons)
        patches = list(patches_iterator)
        self.patches = patches

    def get_points(self, project_id: int, image_id: int) -> None:
        user_annotations = self._fetch_image_annotations(project_id, image_id)
        points_iterator = filter(is_point, user_annotations)
        points = list(points_iterator)
        self.points = points

    def verbose(self) -> None:
        verbose_info = f"""----- Verbose Info -----
        Image Patches: {len(self.patches)}
        Image Point Annotations: {len(self.points)}"""
        print(verbose_info)

    def distribute_points(self) -> None:
        self._generate_all_patches_template()
        self._iterate_points()    