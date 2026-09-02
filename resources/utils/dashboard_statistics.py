from sqlalchemy import func

from models import VerbalAutopsy


def get_dashboard_statistics():
    total_records = VerbalAutopsy.query.count()

    total_states = db_count_distinct(
        VerbalAutopsy.state_name
    )

    total_lgas = db_count_distinct(
        VerbalAutopsy.lga_name
    )

    total_facilities = db_count_distinct(
        VerbalAutopsy.facility_name
    )

    male_count = VerbalAutopsy.query.filter(
        func.lower(VerbalAutopsy.sex) == "male"
    ).count()

    female_count = VerbalAutopsy.query.filter(
        func.lower(VerbalAutopsy.sex) == "female"
    ).count()

    latest_year = VerbalAutopsy.query.with_entities(
        func.max(VerbalAutopsy.interview_year)
    ).scalar()

    top_states = (
        VerbalAutopsy.query.with_entities(
            VerbalAutopsy.state_name,
            func.count(VerbalAutopsy.id)
        )
        .filter(
            VerbalAutopsy.state_name.isnot(None)
        )
        .filter(
            func.trim(VerbalAutopsy.state_name) != ""
        )
        .group_by(
            VerbalAutopsy.state_name
        )
        .order_by(
            func.count(VerbalAutopsy.id).desc()
        )
        .limit(5)
        .all()
    )

    top_causes = (
        VerbalAutopsy.query.with_entities(
            VerbalAutopsy.cause_of_death,
            func.count(VerbalAutopsy.id)
        )
        .filter(
            VerbalAutopsy.cause_of_death.isnot(None)
        )
        .filter(
            func.trim(VerbalAutopsy.cause_of_death) != ""
        )
        .group_by(
            VerbalAutopsy.cause_of_death
        )
        .order_by(
            func.count(VerbalAutopsy.id).desc()
        )
        .limit(5)
        .all()
    )

    yearly_trend = (
        VerbalAutopsy.query.with_entities(
            VerbalAutopsy.interview_year,
            func.count(VerbalAutopsy.id)
        )
        .filter(
            VerbalAutopsy.interview_year.isnot(None)
        )
        .group_by(
            VerbalAutopsy.interview_year
        )
        .order_by(
            VerbalAutopsy.interview_year
        )
        .all()
    )

    return {
        "total_records": total_records,
        "total_states": total_states,
        "total_lgas": total_lgas,
        "total_facilities": total_facilities,
        "male_count": male_count,
        "female_count": female_count,
        "latest_year": latest_year,

        "top_states": [
            {
                "state": state,
                "count": count
            }
            for state, count in top_states
        ],

        "top_causes": [
            {
                "cause": cause,
                "count": count
            }
            for cause, count in top_causes
        ],

        "yearly_trend": [
            {
                "year": year,
                "count": count
            }
            for year, count in yearly_trend
        ]
    }


def get_state_analytics(state_name):
    state_name = (state_name or "").strip()

    if not state_name:
        return {
            "state": "",
            "observed_records": 0,
            "reporting_facilities": 0,
            "reporting_lgas": 0,
            "top_cause": None,
            "top_cause_percentage": 0,
            "male": 0,
            "female": 0,
            "latest_year": None
        }

    state_filter = func.lower(
        func.trim(VerbalAutopsy.state_name)
    ) == state_name.lower()

    observed_records = (
        VerbalAutopsy.query
        .filter(state_filter)
        .count()
    )

    if observed_records == 0:
        return {
            "state": state_name,
            "observed_records": 0,
            "reporting_facilities": 0,
            "reporting_lgas": 0,
            "top_cause": None,
            "top_cause_percentage": 0,
            "male": 0,
            "female": 0,
            "latest_year": None
        }

    reporting_facilities = (
        VerbalAutopsy.query
        .with_entities(
            VerbalAutopsy.facility_name
        )
        .filter(state_filter)
        .filter(
            VerbalAutopsy.facility_name.isnot(None)
        )
        .filter(
            func.trim(VerbalAutopsy.facility_name) != ""
        )
        .distinct()
        .count()
    )

    reporting_lgas = (
        VerbalAutopsy.query
        .with_entities(
            VerbalAutopsy.lga_name
        )
        .filter(state_filter)
        .filter(
            VerbalAutopsy.lga_name.isnot(None)
        )
        .filter(
            func.trim(VerbalAutopsy.lga_name) != ""
        )
        .distinct()
        .count()
    )

    top_cause_result = (
        VerbalAutopsy.query
        .with_entities(
            VerbalAutopsy.cause_of_death,
            func.count(VerbalAutopsy.id)
        )
        .filter(state_filter)
        .filter(
            VerbalAutopsy.cause_of_death.isnot(None)
        )
        .filter(
            func.trim(VerbalAutopsy.cause_of_death) != ""
        )
        .group_by(
            VerbalAutopsy.cause_of_death
        )
        .order_by(
            func.count(VerbalAutopsy.id).desc()
        )
        .first()
    )

    top_cause = None
    top_cause_percentage = 0

    if top_cause_result:
        cause_name, cause_count = top_cause_result

        top_cause = cause_name

        top_cause_percentage = round(
            (cause_count / observed_records) * 100,
            1
        )

    male = (
        VerbalAutopsy.query
        .filter(state_filter)
        .filter(
            func.lower(
                func.trim(VerbalAutopsy.sex)
            ) == "male"
        )
        .count()
    )

    female = (
        VerbalAutopsy.query
        .filter(state_filter)
        .filter(
            func.lower(
                func.trim(VerbalAutopsy.sex)
            ) == "female"
        )
        .count()
    )

    latest_year = (
        VerbalAutopsy.query
        .with_entities(
            func.max(VerbalAutopsy.interview_year)
        )
        .filter(state_filter)
        .scalar()
    )

    return {
        "state": state_name,
        "observed_records": observed_records,
        "reporting_facilities": reporting_facilities,
        "reporting_lgas": reporting_lgas,
        "top_cause": top_cause,
        "top_cause_percentage": top_cause_percentage,
        "male": male,
        "female": female,
        "latest_year": latest_year
    }


def db_count_distinct(column):
    return (
        VerbalAutopsy.query
        .with_entities(column)
        .filter(
            column.isnot(None)
        )
        .filter(
            func.trim(column) != ""
        )
        .distinct()
        .count()
    )