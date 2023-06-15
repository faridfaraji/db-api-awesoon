from flask_restx import inputs


def add_docs_search_params(parser):
    parser.add_argument(
        "show_embedding",
        type=inputs.boolean,
        required=False,
        default=False,
        location="values"
    )
    return parser
