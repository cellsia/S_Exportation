from cytomine.models.image import ImageInstanceCollection
from exportation.utils import get_annot_geometry
from cytomine.models import TermCollection



class OutputFormatter():

    def __init__(self):
        self.template = None

    def _fetch_image_info(self, project_id: int, image_id: int) -> None:
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
        return patch

    def _format_patches(self, project_id: int) -> None:
        patches = self.template["patches"]
        self.template["patches"] = []
        for key, patch in patches.items():
            self.template["patches"].append(self._format_patch(key, patch, project_id))

    def set_template(self, template: dict) -> None:
        self.template = template

    def format(self, project, params) -> None:
        self._fetch_image_info(project.id, params.image_to_analyze)
        self._format_patches(project.id)