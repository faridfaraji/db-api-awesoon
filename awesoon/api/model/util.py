from flask_restx import inputs
from datetime import datetime, timedelta


def add_date_search_params(parser):
    parser.add_argument(
        "start_datetime",
        type=inputs.datetime_from_iso8601,
        default=(datetime.utcnow()-timedelta(days=1)).isoformat(),
        required=False,
        help="Start date for filtering requested conversations",
        location="values",
    )
    parser.add_argument(
        "end_datetime",
        type=inputs.datetime_from_iso8601,
        required=False,
        default=datetime.utcnow().isoformat(),
        help="End date for filtering requested conversations",
        location="values",
    )
    return parser


def add_paginator(parser):
    parser.add_argument(
        "offset",
        type=int,
        default=0,
        required=False,
        help="page number",
        location="values",
    )
    parser.add_argument(
        "limit",
        type=int,
        required=False,
        default=1000,
        help="limit number of results",
        location="values",
    )
    return parser
