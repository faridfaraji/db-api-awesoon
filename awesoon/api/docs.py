
import sys

from flask_restx import Namespace, Resource, marshal

from awesoon.api.model.docs import add_docs_parser, doc
from awesoon.constants import SUCCESS_MESSAGE
from awesoon.core.database.docs import delete_doc, get_doc_by_id, update_doc
from awesoon.core.exceptions import DocNotFoundError
from awesoon.model.schema import Session
from awesoon.model.schema.doc import ADA_TOKEN_COUNT

api = Namespace("docs", "This namespace is responsible for updating and deleting docs")

doc_parser = api.parser()
add_docs_parser(doc_parser)

doc_model = api.model("doc", doc)


@api.route("/<doc_id>")
class SingleDoc(Resource):
    @api.marshal_with(doc_model)
    def get(self, doc_id):
        with Session() as session:
            try:
                doc = get_doc_by_id(session, doc_id)
                return marshal(doc, doc_model), 200
            except DocNotFoundError:
                api.abort(400, "doc not found")
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)

    @api.expect(doc_model)
    def put(self, doc_id):
        with Session() as session:
            try:
                doc_data = doc_parser.parse_args()
                embedding = doc_data["embedding"]
                if len(embedding) != ADA_TOKEN_COUNT:
                    api.abort(400, f"Wrong embedding dimension, should be length {ADA_TOKEN_COUNT}")
                update_doc(session, doc_data, doc_id)
                session.commit()
                return SUCCESS_MESSAGE, 200
            except DocNotFoundError:
                api.abort(400, "doc not found")
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)

    def delete(self, doc_id):
        with Session() as session:
            try:
                delete_doc(session, doc_id)
                session.commit()
                return SUCCESS_MESSAGE, 200
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)
