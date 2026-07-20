from sqlalchemy import func

from models import VerbalAutopsy


def get_dashboard_statistics():
    """
    Generate summary statistics for the dashboard.

    Returns:
        dict
    """

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
        func.max(
            VerbalAutopsy.interview_year
        )
    ).scalar()

    top_states = (
        VerbalAutopsy.query.with_entities(
            VerbalAutopsy.state_name,
            func.count(VerbalAutopsy.id)
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
            if state
        ],

        "top_causes": [
            {
                "cause": cause,
                "count": count
            }
            for cause, count in top_causes
            if cause
        ],

        "yearly_trend": [
            {
                "year": year,
                "count": count
            }
            for year, count in yearly_trend
        ]

    }


def db_count_distinct(column):
    """
    Count distinct non-null values.
    """

    return (
        VerbalAutopsy.query.with_entities(column)
        .filter(column.isnot(None))
        .distinct()
        .count()
    )