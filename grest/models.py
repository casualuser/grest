# -*- coding: utf8 -*-
#
# Copyright (C) 2018 Mostafa Moradian <mostafamoradian0@gmail.com>
#
# This file is part of grest.
#
# grest is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# grest is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with grest.  If not, see <http://www.gnu.org/licenses/>.
#

from webargs import fields
from neomodel import (relationship_manager, Property, StringProperty,
                      DateTimeProperty, DateProperty, EmailProperty,
                      BooleanProperty, ArrayProperty, IntegerProperty,
                      UniqueIdProperty, JSONProperty)


class NodeAndRelationHelper(object):
    __validation_rules__ = {}

    def __init__(self):
        super(self.__class__, self)
        self.__validation_rules__ = self.validation_rules

    def to_dict(self):
        name = 0
        properties = [p[name] for p in self.defined_properties().items()]
        blocked_properties = ["id",
                              "password",
                              "current_otp",
                              "validation_rules"]

        if hasattr(self, "__filtered_fields__"):
            blocked_properties.extend(self.__filtered_fields__)

        removable_keys = set()
        for prop in properties:
            # remove null key/values
            if getattr(self, prop) is None:
                removable_keys.add(prop)

            # remove display functions for choices
            # if prop.startswith("get_") and prop.endswith("_display"):
            #     removable_keys.add(prop)

            # remove relations for now!!!
            if isinstance(getattr(self, prop), relationship_manager.RelationshipManager):
                removable_keys.add(prop)

            # remove blocked properties, e.g. password, id, ...
            if prop in blocked_properties:
                removable_keys.add(prop)

        for key in removable_keys:
            properties.remove(key)

        result = {key: getattr(self, key) for key in properties}

        return result

    @property
    def validation_rules(self):
        """
        if the user has defined validation rules,
        return that, otherwise construct a set of
        predefined rules and return it.

        All internal GRest methods should use this property.
        """

        if len(self.__validation_rules__) > 0:
            # there is a set of user-defined validation rules
            return self.__validation_rules__

        model_types = [
            StringProperty, DateTimeProperty, DateProperty,
            EmailProperty, BooleanProperty, UniqueIdProperty,
            ArrayProperty, IntegerProperty, JSONProperty
        ]

        model_mapping = {
            IntegerProperty: fields.Int,
            StringProperty: fields.Str,
            BooleanProperty: fields.Bool,
            DateTimeProperty: fields.DateTime,
            DateProperty: fields.Date,
            EmailProperty: fields.Email,
            ArrayProperty: fields.List,
            JSONProperty: fields.Dict,
            UniqueIdProperty: fields.UUID
        }

        name = 0
        value = 1

        for field in self.defined_properties().items():
            if field[name] not in self.__validation_rules__:
                if type(field[value]) in model_types:
                    if isinstance(field[value], ArrayProperty):
                        if field[value].unique_index:
                            # what it contains: Array of *String*
                            container = model_mapping[
                                type(field[value].unique_index)]
                        else:
                            # defaults to Raw for untyped ArrayProperty
                            container = fields.Raw

                        self.__validation_rules__[field[name]] = model_mapping[
                            type(field[value])](container,
                                                required=field[value].required)
                    else:
                        self.__validation_rules__[field[name]] = model_mapping[
                            type(field[value])](required=field[value].required)

        return self.__validation_rules__


class Node(NodeAndRelationHelper):
    pass


class Relation(NodeAndRelationHelper):
    pass
