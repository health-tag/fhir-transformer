from dataclasses import dataclass


@dataclass
class InsCsvItem:
    hospital_number: str
    citizen_id: str
    insurance: str
    sequence: str

# hn|inscl|subtype|cid|datein|dateexp|hospmain|hospsub|govcode|govname|permitno|docno|ownrpid|ownname|an|seq|subinscl|relinscl|htype
