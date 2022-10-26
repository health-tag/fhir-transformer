import os
from dotenv import load_dotenv

load_dotenv(".env")

hospital_blockchain_address = os.getenv('HOSPITAL_BLOCK_CHAIN_ADDRESS')
hospital_name_43folders = os.getenv('HOSPITAL_NAME_FOR_43FOLDERS')
file_uploader_server_url = os.getenv('FILE_UPLOADER_SERVER_URL')
base_fhir_url = os.getenv('FHIR_SERVER_URL')

headers = {
    'apikey': ''
}
max_patient_per_cycle = 5000
