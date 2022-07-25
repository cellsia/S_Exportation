from cytomine.models.software import JobData
import json
import os

class FileManager():

    def __init__(self):
        self.template = None

    def set_template(self, template: dict) -> None:
        self.template = template

    def data_to_json(self, working_path: str, job) -> None:
        output_path = os.path.join(working_path, "patch_points.json")
        f = open(output_path,"w+")
        json.dump(self.template, f)
        f.close()

        job_data = JobData(job.id, "patch_points", "patch_points.json").save()
        job_data.upload(output_path)