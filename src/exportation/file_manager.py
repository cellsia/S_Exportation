from cytomine.models.image import ImageInstanceCollection
from cytomine.models.software import JobData
from exportation.utils import create_pascal_xml, create_coco_from_pascal, box_size_parser
import json
import os

class FileManager():

    def __init__(self):
        self.template = None
        self.output_file = None

    def set_template(self, template: dict) -> None:
        self.template = template

    def set_output_file(self, output_file: str) -> None:
        self.output_file = output_file

    def generate_files(self, working_path: str, job, project_id: int, offset: int, add_job_data = True) -> None:
        offset = box_size_parser(offset)
        if self.output_file == "json":
            self._data_to_json(working_path, job, project_id, offset, add_job_data)
        elif self.output_file == "pascal":
            self._data_to_pascal(working_path, job, project_id, offset, add_job_data)
        elif self.output_file == "coco":
            self._data_to_coco(working_path, job, project_id, offset, add_job_data)

    def _data_to_json(self, working_path: str, job, project_id: int, offset: int, add_job_data = True) -> None:
        patches = self.template["patches"]
        cter = offset
        for patch in patches:
            image_id = patch["image"]
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
            if classes:
                classes_str = "-".join(classes)
            else:
                classes_str = "empty"
            patch_data = patch["inside_points"]
            output_path = os.path.join(working_path, f"{classes_str}-{cter}.json")
            f = open(output_path,"w+")
            json.dump(patch_data, f)
            f.close()
            if add_job_data:
                job_data = JobData(job.id, "patch", f"{classes_str}-{cter}.jpg").save()
                job_data.upload(dest_path)
                job_data = JobData(job.id, "patch-data", f"{classes_str}-{cter}.json").save()
                job_data.upload(output_path)
    
    def _data_to_pascal(self, working_path: str, job, project_id: int, offset: int, add_job_data = True) -> None:
        patches = self.template["patches"]
        cter = offset
        for patch in patches:
            image_id = patch["image"]
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
            classes = patch["classes"]
            if classes:
                classes_str = "-".join(classes)
            else:
                classes_str = "empty"
            dest_path = os.path.join(working_path, f"{classes_str}-{cter}.jpg")
            image.window(x_aux, y_aux, patch_size, patch_size, dest_pattern=dest_path)
            patch_data = patch["inside_points"]
            output_path = os.path.join(working_path, f"{classes_str}-{cter}.xml")
            xml_patch_data = create_pascal_xml(patch_data, output_path, working_path, f"{classes_str}-{cter}.jpg", patch["patch_size"])
            if add_job_data:
                job_data = JobData(job.id, "patch", f"{classes_str}-{cter}.jpg").save()
                job_data.upload(dest_path)
                job_data = JobData(job.id, "patch-data", f"{classes_str}-{cter}.xml").save()
                job_data.upload(output_path)

    def _data_to_coco(self, working_path: str, job, project_id: int, offset: int, add_job_data = True) -> None:
        self._data_to_pascal(working_path, job, project_id, offset, False)
        images = [f for f in os.listdir(working_path) if f.endswith("jpg")]
        for image in images:
            image_path = os.path.join(working_path, image)
            image_no_ext = os.path.splitext(image)[0]
            create_coco_from_pascal(image_no_ext, working_path)
            if add_job_data:
                job_data = JobData(job.id, "patch", image).save()
                job_data.upload(image_path)
                job_data = JobData(job.id, "patch-data", f"{image_no_ext}.txt").save()
                job_data.upload(os.path.join(working_path, f"{image_no_ext}.txt"))