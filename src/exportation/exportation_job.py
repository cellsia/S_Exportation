from exportation.annotation_handler import AnnotationHandler
from exportation.output_formatter import OutputFormatter
from exportation.file_manager import FileManager
from exportation.job import BaseJob
from cytomine.models import Job


class ExportationJob(BaseJob):

    def __init__(self):
        super().__init__()
        self.annotation_handler = None
        self.output_formatter = None
        self.file_manager = None

    def run(self, job, project, params) -> None:

        print("----- Running Exportation -----")
        if params.image_to_analyze:
            job.update(progres = 0, status = Job.RUNNING, statusComment = "Fetching annotations and patches")
            self.annotation_handler = AnnotationHandler()
            self.annotation_handler.get_patches(project.id, params.image_to_analyze)
            self.annotation_handler.get_points(project.id, params.image_to_analyze)
            self.annotation_handler.verbose()
            self.annotation_handler.distribute_points()
            template = self.annotation_handler.template
            
            job.update(progres = 50, status = Job.RUNNING, statusComment = "Formatting the output")
            self.output_formatter = OutputFormatter()
            self.output_formatter.set_template(template)
            self.output_formatter.format(project, params)
            formatted_template = self.output_formatter.template
            
            del self.annotation_handler
            del self.output_formatter
            del template

            job.update(progres = 75, status = Job.RUNNING, statusComment = "Uploading results file")
            self.file_manager = FileManager()
            self.file_manager.set_template(formatted_template)
            self.file_manager.data_to_json(self.working_path, job, project.id, params.offset)

            job.update(progres = 100, status = Job.TERMINATED, statusComment = "Exportation done!")
        
        else:
            job.update(progres = 0, status = Job.RUNNING, statusComment = "Fetching annotations and patches")
            self.annotation_handler = AnnotationHandler()
            self.annotation_handler.get_patches(project.id, [])
            self.annotation_handler.get_points(project.id, [])
            self.annotation_handler.verbose()
            self.annotation_handler.distribute_points()
            template = self.annotation_handler.template

            job.update(progres = 50, status = Job.RUNNING, statusComment = "Formatting the output")
            self.output_formatter = OutputFormatter()
            self.output_formatter.set_template(template)
            self.output_formatter.format(project, params)
            formatted_template = self.output_formatter.template

            del annotation_handler
            del output_formatter
            del template

            job.update(progres = 75, status = Job.RUNNING, statusComment = "Uploading results file")
            self.file_manager = FileManager()
            self.file_manager.set_template(formatted_template)
            self.file_manager.data_to_json(self.working_path, job, project.id, params.offset)

            job.update(progres = 100, status = Job.TERMINATED, statusComment = "Exportation done!")

        
        



        
        
        