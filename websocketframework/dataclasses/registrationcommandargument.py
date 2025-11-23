#!/bin/python

import types
import typeguard
import logging
import attrs

logger = logging.getLogger(__name__)

@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False)
class RegistrationCommandArgument:
	_argument:str = attrs.field(validator=attrs.validators.instance_of(str))
	_type: type|types.GenericAlias|types.UnionType = attrs.field(validator=attrs.validators.or_(attrs.validators.instance_of(type), attrs.validators.instance_of(types.GenericAlias), attrs.validators.instance_of(types.UnionType)))
	_has_default: bool = attrs.field(validator=attrs.validators.instance_of(bool))
