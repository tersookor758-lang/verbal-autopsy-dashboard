import re
from datetime import datetime

from resources.utils.location_normalizer import (
    normalize_state,
    normalize_lga,
    state_exists,
    lga_exists
)


VALID_SEX = {
    "Male",
    "Female"
}


MONTHS = {
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
}


ICD10_PATTERN = r"^[A-TV-Z][0-9]{2}(\.[A-Z0-9]{1,4})?$"



def validate_state(state_name):

    if not state_name:
        return False, "State is required"


    state_name = normalize_state(
        state_name
    )


    if not state_exists(state_name):

        return False, "Invalid State"


    return True, state_name




def validate_lga(state_name, lga_name):

    if not lga_name:

        return False, "LGA is required"


    state_name = normalize_state(
        state_name
    )


    lga_name = normalize_lga(
        state_name,
        lga_name
    )


    if not lga_exists(
        state_name,
        lga_name
    ):

        return False, "LGA does not belong to selected state"


    return True, lga_name




def validate_age(age):

    if age in [
        None,
        ""
    ]:

        return True, None


    try:

        age = int(age)


    except (
        ValueError,
        TypeError
    ):

        return False, "Age must be a whole number"



    if age < 0:

        return False, "Age cannot be negative"



    if age > 130:

        return False, "Age is unrealistically high"



    return True, age




def validate_sex(sex):

    if not sex:

        return False, "Sex is required"



    sex = str(sex).strip().title()



    if sex not in VALID_SEX:

        return False, "Sex must be Male or Female"



    return True, sex




def validate_patientid(patientid):

    if not patientid:

        return False, "Patient ID is required"



    patientid = str(
        patientid
    ).strip()



    return True, patientid




def validate_datim(datim_code):

    if not datim_code:

        return False, "DATIM Code is required"



    datim_code = str(
        datim_code
    ).strip().upper()



    return True, datim_code




def validate_icd10(icd10):

    if not icd10:

        return True, None



    icd10 = str(
        icd10
    ).strip().upper()



    if not re.match(
        ICD10_PATTERN,
        icd10
    ):

        return False, "Invalid ICD-10 Code"



    return True, icd10




def validate_interview_date(year, month, day):

    current_year = datetime.now().year


    if year:

        try:

            year = int(year)


        except (
            ValueError,
            TypeError
        ):

            return False, "Interview year must be a number"



        if year < 2000 or year > current_year + 1:

            return False, "Interview year is out of range"



    if month:

        month = str(
            month
        ).strip().title()



        if month not in MONTHS:

            return False, "Invalid interview month"



    if day:

        try:

            day = int(day)


        except (
            ValueError,
            TypeError
        ):

            return False, "Interview day must be a number"



        if day < 1 or day > 31:

            return False, "Interview day is out of range"



    return True, {

        "year": year,

        "month": month if month else None,

        "day": day

    }




def validate_record(record):

    errors = []


    state_valid, state_result = validate_state(
        record.get("state_name")
    )


    if not state_valid:

        errors.append(state_result)



    lga_valid, lga_result = validate_lga(
        record.get("state_name"),
        record.get("lga_name")
    )


    if not lga_valid:

        errors.append(lga_result)



    patient_valid, patient_result = validate_patientid(
        record.get("patientid")
    )


    if not patient_valid:

        errors.append(patient_result)



    datim_valid, datim_result = validate_datim(
        record.get("datim_code")
    )


    if not datim_valid:

        errors.append(datim_result)



    age_valid, age_result = validate_age(
        record.get("age")
    )


    if not age_valid:

        errors.append(age_result)



    sex_valid, sex_result = validate_sex(
        record.get("sex")
    )


    if not sex_valid:

        errors.append(sex_result)



    icd_valid, icd_result = validate_icd10(
        record.get("icd10")
    )


    if not icd_valid:

        errors.append(icd_result)



    date_valid, date_result = validate_interview_date(
        record.get("interview_year"),
        record.get("interview_month"),
        record.get("interview_day")
    )


    if not date_valid:

        errors.append(date_result)



    return errors