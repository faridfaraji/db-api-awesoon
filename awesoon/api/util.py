from flask_restx import inputs
from datetime import datetime, timedelta


def add_date_search_params(parser):
    parser.add_argument(
        "start_datetime",
        type=inputs.datetime_from_iso8601,
        required=False,
        default=lambda: datetime.utcnow() - timedelta(days=1),
        help="Start date for filtering requested conversations",
    )
    parser.add_argument(
        "end_datetime",
        type=inputs.datetime_from_iso8601,
        required=False,
        default=lambda: datetime.utcnow(),
        help="End date for filtering requested conversations",
    )
    return parser
