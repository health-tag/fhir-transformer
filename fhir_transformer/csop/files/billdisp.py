from dataclasses import dataclass, field

import xmltodict
from charset_normalizer import from_path


@dataclass
class DispensingItemDetailRow:
    disp_id: str
    product_cat: str
    local_drug_id: str
    standard_drug_id: str
    dfs: str
    package_size: str
    instruction_code: str
    instruction_text: str
    quantity: str
    # 'prd_code': item_split[14],
    # 'multiple_disp': item_split[17],
    # 'supply_for': item_split[18],


@dataclass
class DispensingItemRow:
    """
    dictionary of DispensingId:str,DispensingItem (DispensingItem.items:DispensingItemDetail is already related with DispensingItem)
    """
    disp_status: str
    license_id: str
    disp_date: str
    presc_date: str
    inv_no: str
    disp_id: str
    provider_id: str
    details: list[DispensingItemDetailRow] = field(default_factory=list[DispensingItemDetailRow])


def open_bill_disp_xml(file_path):
    """
    :param file_path:
    :return: dictionary of DispensingId:str,DispensingItem (DispensingItem.items:DispensingItemDetail is already related with DispensingItem)
    """
    with open(file_path, encoding=from_path(file_path).best().first().encoding) as xml_file:
        xml_dict = xmltodict.parse(xml_file.read())
        Dispensing_items = dict[str, DispensingItemRow]()
        Dispensing_rows = xml_dict['ClaimRec']['Dispensing'].split('\n')
        DispensedItems_rows = xml_dict['ClaimRec']['DispensedItems'].split('\n')
        for item in Dispensing_rows:
            columns = item.split('|')
            dispensing_item = DispensingItemRow(
                provider_id=columns[0],
                disp_id=columns[1],
                inv_no=columns[2],
                presc_date=columns[5],
                disp_date=columns[6],
                license_id=columns[7],
                disp_status=columns[15],
                # practitioner=license_mapping[columns[7][0]],
            )
            Dispensing_items[dispensing_item.disp_id] = dispensing_item

        for item in DispensedItems_rows:
            columns = item.split('|')
            dispensing_item_detail = DispensingItemDetailRow(
                disp_id=columns[0],
                product_cat=columns[1],
                local_drug_id=columns[2],
                standard_drug_id=columns[3],
                dfs=columns[5],
                package_size=columns[6],
                instruction_code=columns[7],
                instruction_text=columns[8],
                quantity=columns[9],
                # 'prd_code': columns[14],
                # 'multiple_disp': columns[17],
                # 'supply_for': columns[18],
            )
            Dispensing_items[dispensing_item_detail.disp_id].details.append(dispensing_item_detail)
        return Dispensing_items
