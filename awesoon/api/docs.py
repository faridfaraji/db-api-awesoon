
import sys
from flask_restx import Namespace, Resource, marshal
from awesoon.api.util import add_docs_search_params
from awesoon.api.model.docs import doc, docs_parser
from awesoon.core.database.docs import get_doc_by_id
from awesoon.model.schema import Session

ns = Namespace("docs", "This namespace is resposible for updating and deleting docs")

get_doc_parser = ns.parser()
get_doc_parser = add_docs_search_params(get_doc_parser)

doc_parser = ns.parser()
docs_parser(doc_parser)

doc_model = ns.model("doc", doc)


@ns.route("/<doc_id>")
class SingleDoc(Resource):
    @ns.expect(get_doc_parser)
    def get(self, doc_id):
        with Session() as session:
            try:
                doc = get_doc_by_id(session, doc_id)
                return marshal(doc, doc_model), 200
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)

    @ns.expect(doc_model)
    def put(self, doc_id):
        with Session() as session:
            try:
                doc_data = doc_parser.parse_args()
                embedding = doc_data["embedding"]
                if len(embedding) != 2:
                    return 400, "Wrong embedding dimension, should be length 1536"
                update_doc(session, doc_data)
                session.commit()
                return {"message": "SUCCESS"}, 200
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)

    @ns.expect(doc_model)
    def delete(self, doc_id):
        with Session() as session:
            try:
                doc_data = doc_parser.parse_args()
                embedding = doc_data["embedding"]
                if len(embedding) != 2:
                    return 400, "Wrong embedding dimension, should be length 1536"
                delete_doc(session, doc_data)
                session.commit()
                return {"message": "SUCCESS"}, 200
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)
