import logging

from flask_restx import Namespace, Resource, fields, marshal
from sqlalchemy import select
from awesoon.constants import SUCCESS_MESSAGE

from awesoon.model.schema import Session
from awesoon.model.schema.shop import Prompt

logger = logging.getLogger(__name__)

api = Namespace("prompt", "prompt endpoint")

prompt_model = api.model(
    "prompt",
    {
        "prompt": fields.String(
            description="prompt to be used"
        ),
    },
)
prompt_parser = api.parser()
prompt_parser.add_argument("prompt", type=str, default=None, location="json")


@api.route("")
class PromptTemplate(Resource):
    @api.marshal_with(prompt_model)
    def get(self):
        with Session() as session:
            query = select(Prompt)
            prompt = session.scalars(query).first()
            marshalled_prompt = marshal(prompt, prompt_model)
        return marshalled_prompt, 200

    @api.expect(prompt_model, validate=True)
    def put(self):
        data = prompt_parser.parse_args()
        with Session() as session:
            query = select(Prompt)
            prompt = session.scalars(query).first()
            if prompt:
                prompt.prompt = data["prompt"]
            else:
                prompt = Prompt(prompt=data["prompt"])
            session.add(prompt)
            session.commit()
            return SUCCESS_MESSAGE, 200
