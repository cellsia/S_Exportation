from exportation.annotation_handler import AnnotationHandler
from exportation.output_formatter import OutputFormatter
from exportation.file_manager import FileManager
from cytomine.models.project import Project
from cytomine import Cytomine

HOST = ""
PUBLIC_KEY = ""
PRIVATE_KEY = ""
PROJECT_ID = ""
BOX_SIZE = 0
WORKING_PATH =""
OFFSET = 0

class Params():
    def __init__(self, image_to_analyze, box_size):
        self.image_to_analyze = image_to_analyze
        self.box_size = box_size

def run():
    annotation_handler = AnnotationHandler()
    annotation_handler.get_patches(PROJECT_ID, [])
    annotation_handler.get_points(PROJECT_ID, [])
    annotation_handler.verbose()
    annotation_handler.distribute_points()
    template = annotation_handler.template
    output_formatter = OutputFormatter()
    output_formatter.set_template(template)
    project = Project().fetch(PROJECT_ID)
    params = Params(None, BOX_SIZE)
    output_formatter.format(project, params)
    formatted_template = output_formatter.template
    del annotation_handler
    del output_formatter
    del template
    file_manager = FileManager()
    file_manager.set_template(formatted_template)
    file_manager.data_to_json(WORKING_PATH, None, PROJECT_ID, OFFSET, add_job_data=False)


with Cytomine(HOST, PUBLIC_KEY, PRIVATE_KEY, verbose = False) as cytomine:
    run()