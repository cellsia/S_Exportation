import logging
import shutil
import os


class BaseJob():

    def __init__(self):
        self.version = None
        self.working_path = None
        self.job = None
        self.project = None
        self.parameters = None

    def set_version(self, str_version: str) -> None:
        self.version = str_version

    def _create_working_path(self) -> None:
        self.working_path = os.path.join("tmp", str(self.job.id))
        if not os.path.exists(self.working_path):
            logging.info(f"Creating working directory: {self.working_path}")
            os.makedirs(self.working_path)

    def _destroy(self) -> None:
        logging.info(f"Deleting folder {self.working_path}")
        shutil.rmtree(self.working_path, ignore_errors=True)
        logging.debug("Leaving run()")

    def run(self) -> None:
        pass

    def launch(self, cyto_job, parameters) -> None:
        
        logging.info("----- test software v%s -----", self.version)
        logging.info("Entering run(cyto_job=%s, parameters=%s)", cyto_job, parameters)

        self.job = cyto_job.job
        self.project = cyto_job.project
        self.parameters = parameters

        self._create_working_path()
        self.run(self.job, self.project, self.parameters)
        self._destroy()