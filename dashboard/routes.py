
from pathlib import Path
import json

from flask import render_template, request
from flask_login import login_required

from dashboard import dashboard_bp
from models import VerbalAutopsy

from resources.utils.dashboard_statistics import (
    get_dashboard_statistics
)


BASE_DIR = Path(__file__).resolve().parent.parent

STATES_FILE = BASE_DIR / "resources" / "raw" / "states.json"
LGAS_FILE = BASE_DIR / "resources" / "raw" / "lgas.json"


def load_states():
    with open(STATES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def load_lgas():
    with open(LGAS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_dashboard_data():

    query = VerbalAutopsy.query

    state = request.args.get(
        "state",
        ""
    ).strip()

    lga = request.args.get(
        "lga",
        ""
    ).strip()

    facility = request.args.get(
        "facility",
        ""
    ).strip()

    cause = request.args.get(
        "cause",
        ""
    ).strip()

    sex = request.args.get(
        "sex",
        ""
    ).strip()

    year = request.args.get(
        "year",
        ""
    ).strip()

    patient = request.args.get(
        "patient",
        ""
    ).strip()


    if state:

        query = query.filter(
            VerbalAutopsy.state_name == state
        )


    if lga:

        query = query.filter(
            VerbalAutopsy.lga_name == lga
        )


    if facility:

        query = query.filter(
            VerbalAutopsy.facility_name == facility
        )


    if cause:

        query = query.filter(
            VerbalAutopsy.cause_of_death == cause
        )


    if sex:

        query = query.filter(
            VerbalAutopsy.sex == sex
        )


    if year:

        query = query.filter(
            VerbalAutopsy.interview_year == int(year)
        )


    if patient:

        query = query.filter(
            VerbalAutopsy.patientid.contains(patient)
        )


    page = request.args.get(
        "page",
        1,
        type=int
    )


    pagination = query.order_by(
        VerbalAutopsy.id.desc()
    ).paginate(
        page=page,
        per_page=20,
        error_out=False
    )


    records = pagination.items


    states = load_states()

    all_lgas = load_lgas()


    if state:

        lgas = all_lgas.get(
            state,
            []
        )

    else:

        lgas = []


    facilities = [

        facility[0]

        for facility in VerbalAutopsy.query.with_entities(
            VerbalAutopsy.facility_name
        ).distinct().order_by(
            VerbalAutopsy.facility_name
        ).all()

        if facility[0]

    ]


    causes = [

        cause[0]

        for cause in VerbalAutopsy.query.with_entities(
            VerbalAutopsy.cause_of_death
        ).distinct().order_by(
            VerbalAutopsy.cause_of_death
        ).all()

        if cause[0]

    ]


    years = [

        year[0]

        for year in VerbalAutopsy.query.with_entities(
            VerbalAutopsy.interview_year
        ).distinct().order_by(
            VerbalAutopsy.interview_year.desc()
        ).all()

        if year[0]

    ]


    statistics = get_dashboard_statistics()


    return {

        "records": records,

        "pagination": pagination,

        "states": states,

        "lgas": lgas,

        "all_lgas": all_lgas,

        "facilities": facilities,

        "causes": causes,

        "years": years,

        "statistics": statistics

    }


@dashboard_bp.route("/")
@login_required
def index():

    data = get_dashboard_data()

    return render_template(
        "index.html",
        **data
    )


@dashboard_bp.route("/records")
@login_required
def records():

    data = get_dashboard_data()

    return render_template(
        "records.html",
        **data
    )


@dashboard_bp.route("/analytics")
@login_required
def analytics():

    statistics = get_dashboard_statistics()

    return render_template(
        "Analytics.html",
        statistics=statistics
    )


@dashboard_bp.route("/reports")
@login_required
def reports():

    return render_template(
        "reports.html"
    )

