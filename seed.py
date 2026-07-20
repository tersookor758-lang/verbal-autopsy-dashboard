from app import app
from extensions import db
from models import VerbalAutopsy


sample_records = [

    VerbalAutopsy(
        patientid="PAT001",
        state_name="Benue",
        lga_name="Makurdi",
        facility_name="General Hospital Makurdi",
        datim_code="NG001",
        age=45,
        sex="Male",
        cause_of_death="Stroke",
        cause_list=1,
        icd10="I64",
        interviewer_name="John Doe",
        interview_year=2025,
        interview_month="July",
        interview_day=10,
        interview_time="10:30 AM"
    ),


    VerbalAutopsy(
        patientid="PAT002",
        state_name="Abuja",
        lga_name="Bwari",
        facility_name="PHC Bwari",
        datim_code="NG002",
        age=30,
        sex="Female",
        cause_of_death="Malaria",
        cause_list=2,
        icd10="B54",
        interviewer_name="Jane Smith",
        interview_year=2025,
        interview_month="June",
        interview_day=22,
        interview_time="09:15 AM"
    )

]


with app.app_context():

    db.session.add_all(sample_records)

    db.session.commit()


    print("Sample records added successfully")