from job import Job
import logging


class ExportationJob(Job):

    def __init__(bash):
        super().__init__()

    def run(self, job, project, params) -> None:

        logging.info("----- Variables de entrada -----")
        logging.info(f"Job: {job}")
        logging.info(f"Project: {project}")
        logging.info(f"Params: {params}")

        pass  