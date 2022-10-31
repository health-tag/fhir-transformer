from dataclasses import dataclass


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


@dataclass()
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
    details = list[DispensingItemDetailRow]()
