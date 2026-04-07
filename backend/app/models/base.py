from pydantic import BeforeValidator, ConfigDict
from typing import Annotated
from bson import ObjectId

# Standard Pydantic v2 helper for MongoDB ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]
