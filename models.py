from extensions import db


class VerbalAutopsy(db.Model):
    __tablename__ = "verbal_autopsy"

    id = db.Column(db.Integer, primary_key=True)

    patientid = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    state_name = db.Column(
        db.String(100),
        nullable=True
    )

    lga_name = db.Column(
        db.String(100),
        nullable=True
    )

    facility_name = db.Column(
        db.String(100),
        nullable=True
    )

    datim_code = db.Column(
        db.String(100),
        nullable=False
    )

    age = db.Column(
        db.Integer,
        nullable=True
    )

    sex = db.Column(
        db.String(50),
        nullable=True
    )

    cause_of_death = db.Column(
        db.String(200),
        nullable=True
    )

    cause_list = db.Column(
        db.Integer,
        nullable=True
    )

    icd10 = db.Column(
        db.String(50),
        nullable=True
    )

    interviewer_name = db.Column(
        db.String(200),
        nullable=True
    )

    interview_year = db.Column(
        db.Integer,
        nullable=True
    )

    interview_month = db.Column(
        db.String(100),
        nullable=True
    )

    interview_day = db.Column(
        db.Integer,
        nullable=True
    )

    interview_time = db.Column(
        db.String(100),
        nullable=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "patientid": self.patientid,
            "state_name": self.state_name,
            "lga_name": self.lga_name,
            "facility_name": self.facility_name,
            "datim_code": self.datim_code,
            "age": self.age,
            "sex": self.sex,
            "cause_of_death": self.cause_of_death,
            "cause_list": self.cause_list,
            "icd10": self.icd10,
            "interviewer_name": self.interviewer_name,
            "interview_year": self.interview_year,
            "interview_month": self.interview_month,
            "interview_day": self.interview_day,
            "interview_time": self.interview_time
        }

    def __repr__(self):
        return f"<VerbalAutopsy {self.patientid}>"