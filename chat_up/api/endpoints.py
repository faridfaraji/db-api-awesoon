import sys

from flask import request
from flask_restx import Namespace, Resource, fields

ns = Namespace(
    "endpoints", "This namespace is resposible for your cookie recipes.")

model = ns.model(
    "model",
    {
        "butter": fields.String(description='amount of butter', required=True),
        "sugar": fields.String(),
        "egg": fields.String(),
        "flour": fields.String(),
        "chocolate_chips": fields.String()
    },
)

@ns.route("/compute_recipe")
class ComputeCookieRecipe(Resource):
    @ns.expect(model, validate=True)
    def post(self):
        """
        Compute cookie recipe.
        """

        try:
            input_data = request.get_json()
            return {"recipe": input_data}

        except Exception as e:
            print(e, file=sys.stderr)
            ns.abort(500)
