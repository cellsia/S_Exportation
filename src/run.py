import cytomine
import logging
import sys

from exportation.exportation_job import ExportationJob


__version__ = "v1.5.0" 


if __name__ == "__main__":
    
    logging.debug(f"Command: {sys.argv}")
    
    with cytomine.CytomineJob.from_cli(sys.argv) as cyto_job:

        exportation = ExportationJob()
        exportation.set_version(__version__)
        exportation.launch(cyto_job, cyto_job.parameters)