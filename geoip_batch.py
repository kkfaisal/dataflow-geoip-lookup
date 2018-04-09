"""
Redading data from Bigquery table and find location based on ip present in input data and write it to bigquery table
Dataflow used in batch mode.

Input table : 'event_id': STRING, 'ip': STRING, 'date_time':TIMESTAMP

Output table : 'event_id': STRING, 'ip': STRING, 'date_time':TIMESTAMP,'Country':STRING

"""

from __future__ import absolute_import
import logging
import apache_beam as beam
from google.cloud import bigquery
from google.cloud.bigquery import SchemaField

class GeoIpFn(beam.DoFn):
    gi = None
    def process(self, element):
        if self.gi is None:    
            from resources.loader import load_geoip
            self.gi = load_geoip()
            
        tablerow = element
        
        client_ip = tablerow.get("ip")
        try:
            if client_ip:
                # country = self.gi.country_code_by_addr(client_ip)
                country = self.gi.city(client_ip).city.name
                tablerow["geoIpCountry"] = country
        except:
            print "not found"
            
        yield tablerow  

def schemaConvert(schemaFields):
    return ",".join(["%s:%s" % (f.name, f.field_type) for f in schemaFields])


def run(projectId, src_dataset, src_tablename, dest_dataset, dest_tablename, gcs_location_prefix, jobname):
    
    from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions, StandardOptions, SetupOptions, WorkerOptions
    
    dataset = bigquery.Client(project=projectId).dataset(src_dataset)
    src_table = dataset.table(src_tablename)
    src_table.reload()
    dest_schema = src_table.schema
    dest_schema.append(SchemaField('geoIpCountry', 'STRING'))
    
    options = PipelineOptions()
    google_cloud_options = options.view_as(GoogleCloudOptions)
    google_cloud_options.project = projectId
    google_cloud_options.job_name = jobname
    google_cloud_options.region='europe-west1'
    google_cloud_options.staging_location = gcs_location_prefix + 'staging'
    google_cloud_options.temp_location = gcs_location_prefix + 'temp'
    
    worker_options = options.view_as(WorkerOptions)
    worker_options.max_num_workers = 50
    worker_options.machine_type = "n1-standard-4" # https://cloud.google.com/compute/docs/machine-types
    worker_options.autoscaling_algorithm = "THROUGHPUT_BASED" #"NONE"
    
    setup_options = options.view_as(SetupOptions) 
    setup_options.setup_file = "./setup.py"
    setup_options.save_main_session = False 
    
    options.view_as(StandardOptions).runner ='DirectRunner' #'DataflowRunner'
    options.view_as(StandardOptions).streaming = False

    with beam.Pipeline(options=options) as p:
        rows = (p | 'ReadBQ' >> beam.io.Read(beam.io.BigQuerySource(table=src_tablename, dataset=src_dataset))
                  | 'Enrich GeoIP' >> beam.ParDo(GeoIpFn())
                )

        rows | 'WriteBQ' >> beam.io.Write(
                beam.io.BigQuerySink(
                table = dest_tablename,
                dataset= dest_dataset,
                schema=schemaConvert(dest_schema),
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE))

if __name__ == '__main__':

    logging.getLogger().setLevel(logging.INFO)

    projectId = ''
    src_dataset = ''
    src_tablename = ''
    dest_dataset = ''
    dest_tablename = ''
    gcs_location_prefix = ''
    jobname = ''
    run(projectId, src_dataset, src_tablename, dest_dataset, dest_tablename, gcs_location_prefix, jobname)

