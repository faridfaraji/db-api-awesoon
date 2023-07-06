from flask_restx import inputs


def add_date_search_params(parser):
    parser.add_argument(
        "start_datetime",
        type=inputs.datetime_from_iso8601,
        required=False,
        help="Start date for filtering requested conversations",
    )
    parser.add_argument(
        "end_datetime",
        type=inputs.datetime_from_iso8601,
        required=False,
        help="End date for filtering requested conversations",
    )
    return parser
