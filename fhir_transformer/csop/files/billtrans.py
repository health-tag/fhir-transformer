from dataclasses import dataclass


@dataclass
class BillTransItem:
    station: str
    inv_no: str
    hn: str
    member_number: str
    pid: str
    name: str
    pay_plan: str


@dataclass
class BillTransXML:
    hospital_code: str
    hospital_name: str
    bill_trans_items_dict: dict[str, BillTransItem] #Invoice Number, BillTransItem
