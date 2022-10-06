import os
from dotenv import load_dotenv
load_dotenv()

hospital_blockchain_address = os.getenv('HOSPITAL_BLOCK_CHAIN_ADDRESS')
hospital_name_43folders = os.getenv('HOSPITAL_NAME_FOR_43FOLDERS')

base_fhir_url = os.getenv('FHIR_SERVER_URL')

headers = {
    'apikey': ''
}
max_patient_per_cycle = 1000
