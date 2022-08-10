from cytomine.models.image import ImageInstanceCollection
from cytomine.models.software import JobData
import json
import os

class FileManager():

    def __init__(self):
        self.template = None

    def set_template(self, template: dict) -> None:
        self.template = template

    def data_to_json(self, working_path: str, job, project_id: int, offset: int) -> None:
        image_id = self.template["image_id"]
        patches = self.template["patches"]
        cter = offset
        for patch in patches:
            cter += 1
            patch_coords = patch["patch_coords"]
            patch_size = patch["patch_size"]
            imageinstancecol = ImageInstanceCollection().fetch_with_filter(key="project", value=project_id)
            image = [i for i in imageinstancecol if i.id == image_id][0]
            p0 = patch_coords[0]
            x = int(p0[0])
            y = int(p0[1])
            x_aux = x
            y_aux = image.height - y
            dest_path = os.path.join(working_path, f"patch-{cter}.jpg")
            image.window(x_aux, y_aux, patch_size, patch_size, dest_pattern=dest_path)
            classes = patch["classes"]
            classes_str = "-".join(classes)
            job_data = JobData(job.id, "patch", f"{classes_str}-{cter}.jpg").save()
            job_data.upload(dest_path)
            patch_data = patch["inside_points"]
            output_path = os.path.join(working_path, f"{classes_str}-{cter}.json")
            f = open(output_path,"w+")
            json.dump(patch_data, f)
            f.close()
            job_data = JobData(job.id, "patch-data", f"{classes_str}-{cter}.json").save()
            job_data.upload(output_path)