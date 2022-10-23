from dataclasses import dataclass


@dataclass
class OpdCsvItem:
    """
    Constructor arguments:
    :param sequence: SEQ
    :param hospital_number: HN
    :param clinic_number: CLINIC
    :param visit_date: DATEOPD
    :param visit_time: TIMEOPD
    """
    sequence: str = None
    """ SEQ """
    hospital_number: str = None
    """ HN """
    clinic_number: str = None
    """ CLINIC """
    visit_date: str = None
    """ DATEOPD """
    visit_time: str = None
    """ TIMEOPD """

#hn|clinic|dateopd|timeopd|seq|uuc