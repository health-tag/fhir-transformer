from charset_normalizer import from_path
import xmltodict
from fhir_transformer.csop.holder.billtrans import BillTransItem, BillTransXML
from fhir_transformer.csop.holder.billdisp import DispensingItemDetailRow, DispensingItemRow


def _get_file_encoding(file_path):
    return from_path(file_path).best().first().encoding
    # with open(file_path, encoding="utf-8") as xml_file_for_encoding_check:
    #    first_line = xml_file_for_encoding_check.readline()
    #    encoding = re.search('encoding="(.*)"', first_line).group(1)
    #    if encoding == "windows-874":
    #        encoding = "cp874"
    #    return encoding


def open_bill_trans_xml(file_path: str):
    """
    :param file_path:
    :return: dictionary of InvoiceNumber:str,BillTransItem
    """
    with open(file_path, encoding=_get_file_encoding(file_path)) as xml_file:
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


def open_bill_disp_xml(file_path: str):
    """
    :param file_path:
    :return: dictionary of DispensingId:str,DispensingItem (DispensingItem.items:DispensingItemDetail is already related with DispensingItem)
    """
    with open(file_path, encoding=_get_file_encoding(file_path)) as xml_file:
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
            matched_dispensing_item = Dispensing_items[dispensing_item_detail.disp_id].details
            matched_dispensing_item.append(dispensing_item_detail)
        return Dispensing_items
