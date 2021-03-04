from marshmallow import Schema, fields
from marshmallow.validate import Length, Range


class UserSchema(Schema):
    name = fields.Str(required=True, validate=Length(max=50))
    surname = fields.Str(required=True, validate=Length(max=50))
    identity_number = fields.Int(required=True, validate=Range(min=1))


class IDSchema(Schema):
    identity_number = fields.Int(required=True, validate=Range(min=1))