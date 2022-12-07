from dataclasses import dataclass

import xmltodict
from charset_normalizer import from_path


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


def open_bill_trans_xml(file_path):
    """
    :param file_path:
    :return: dictionary of InvoiceNumber:str,BillTransItem
    """
    with open(file_path, encoding=from_path(file_path).best().first().encoding) as xml_file:
        xml_dict = xmltodict.parse(xml_file.read())
        bill_trans_items = dict()
        hospital_code = xml_dict['ClaimRec']['Header']['HCODE']
        hospital_name = xml_dict['ClaimRec']['Header']['HNAME']
        BILLTRAN_rows = xml_dict['ClaimRec']['BILLTRAN'].split('\n')
        #BillItems_rows = xml_dict['ClaimRec']['BillItems'].split('\n')
        for item in BILLTRAN_rows:
            columns = item.split('|')
            bill_trans_item = BillTransItem(
                station=columns[0],
                inv_no=columns[4],
                hn=columns[6],
                member_number=columns[7],
                pid=columns[12],
                name=columns[13],
                pay_plan=columns[15],
            )
            bill_trans_items[bill_trans_item.inv_no] = bill_trans_item
        return BillTransXML(hospital_code, hospital_name, bill_trans_items)
