# version
__version__ = "1.1.0"

# python
import json
import logging
import os
from shapely.geometry import Polygon
import shutil
import sys

# cytomine
import cytomine
from cytomine.models.annotation import Annotation, AnnotationCollection
from cytomine.models.image import ImageInstance
from cytomine.models.software import Job, JobCollection, JobData, JobDataCollection
from cytomine.models.user import UserCollection, UserJob, UserJobCollection

# constantes
PATCH_SIZE = [1024, 2048, 4096]


# ------------------------------ Support functions ------------------------------

# Obtención de la geometría de un polígono
def process_polygon(polygon):
    pol = list(polygon.exterior.coords)
    return pol

# Obtención de la geometría de un punto
def process_point(point):
    punto = list(point.coords)
    return punto

# Función para distinguir polígonos o puntos (anotacion) dentro de otros (parche)
def estar_dentro(parche, anotacion):
    try:
        anotacion_pol = Polygon(process_polygon(anotacion.location))
        anotacion_geo = []
        for i in range(0,len(anotacion_pol)):
            anotacion_geo.append(Point(anotacion_pol[i]))
    except:
        anotacion_geo = Point(process_point(anotacion.location))
    for j in anotacion_geo:
        if parche.contains(j):
            return anotacion
            break
        else:
            continue

# ------------------------------ Step functions ------------------------------

#STEP 0: buscar anotaciones en general
# Función que recoge la inforamción de todas las anotaciones manuales
def get_anotaciones_general(params):
    user_jobs = UserCollection().fetch_with_filter("project", params.cytomine_id_project)
    ids = [user_job.id for user_job in user_jobs]
    
    general_annots = AnnotationCollection()
    general_annots.project = params.cytomine_id_project
    general_annots.image = params.image_to_analyze
    general_annots.users = ids
    
    general_annots.showWKT = True
    general_annots.showMeta = True
    general_annots.showGIS = True
    general_annots.showTerm = True
    
    general_annots.fetch()
        
    return general_annots

# STEP 1: buscar parches
# Función que recoge las coordenadas de los parches (anotaciones manuales con un tamaño determinado -> PATCH_SIZE)
def get_parches(anotaciones_general):
    parches = []
    for anot_gen in anotaciones_general:
        perimetro = Polygon(process_polygon(anot_gen.location)).length
        for size in PATCH_SIZE:
            if perimetro == size*4:
                parches.append(Polygon(process_polygon(anot_gen.location)))
    return parches

# STEP 2: recuperar detecciones de dentro de los parches
# Función que recoge la inforamción de las detecciones subidas por el algoritmo de IA de dentro del parche
def get_detecciones_dentro(parche, params):
    user_jobs = UserJobCollection().fetch_with_filter("project", params.cytomine_id_project)
    ids = [user_job.id for user_job in user_jobs]
    
    detecciones = AnnotationCollection()
    detecciones.project = params.cytomine_id_project
    detecciones.image = params.image_to_analyze
    detecciones.users = ids
    
    detecciones.showWKT = True
    detecciones.showTerm = True
    detecciones.showMeta = True
    detecciones.showGIS = True
    
    detecciones.fetch()
    
    detecciones_dentro = []
    for deteccion in detecciones:
        detecciones_dentro.append(estar_dentro(parche, deteccion))
    
    return detecciones_dentro

# STEP 3: buscar anotaciones manuales dentro de los parches
# Función que recoge la información de las anotaciones manuales de dentro del parche
def get_anotaciones_dentro(anotaciones_general, parche, params):
    anotaciones_dentro = []
    
    for anotacion in anotaciones_general:
        anotaciones_dentro.append(estar_dentro(parche, anotacion))
    
    return anotaciones_dentro


# ------------------------------ Main function ------------------------------
def run(cyto_job, parameters):
    logging.info("----- test software v%s -----", __version__)
    logging.info("Entering run(cyto_job=%s, parameters=%s)", cyto_job, parameters)

    job = cyto_job.job
    project = cyto_job.project

    # I create a working directory that I will delete at the end of this run
    working_path = os.path.join("tmp", str(job.id))
    if not os.path.exists(working_path):
        logging.info("Creating working directory: %s", working_path)
        os.makedirs(working_path)

    try:
        #STEP 0: anotaciones en general
        general_annotations = get_anotaciones_general(parameters)
        
        # STEP 1: parches
        parches = get_parches(general_annotations)
        
        # STEPS 2, 3: detecciones y anotaciones manuales
        # Creación de un diccionario que va a contener la información solicitada
        diccionario = {}
        
        for parche in parches:
            detecciones = get_detecciones_dentro(parche, parameters)
            anotaciones = get_anotaciones_dentro(general_annotations, parche, parameters)
            diccionario[parche]={"Detecciones": detecciones,"Anotaciones": anotaciones}
        
              
        output_path = os.path.join(working_path, "output.json")
        f = open(output_path,"w+")
        json.dump(diccionario, f)
        f.close()

        #I save a file generated by this run into a "job data" that will be available in the UI. 
        job_data = JobData(job.id, "Generated File", "output.json").save()
        job_data.upload(output_path)

    finally:
        logging.info("Deleting folder %s", working_path)
        shutil.rmtree(working_path, ignore_errors=True)
        logging.debug("Leaving run()")


if __name__ == "__main__":
    logging.debug("Command: %s", sys.argv)

    with cytomine.CytomineJob.from_cli(sys.argv) as cyto_job:
        run(cyto_job, cyto_job.parameters)


