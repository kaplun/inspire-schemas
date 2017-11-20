# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Signatures builder class and related code."""

from __future__ import absolute_import, division, print_function

import re

import six
from inspire_utils.name import normalize_name
from isbn import ISBN

import idutils


# Matches INSPIRE BAIs
RE_BAI = re.compile(r'^((\w|\-|\')+\.)+\d+$')


class SignatureBuilder(object):
    """Class used for building JSON signatures objects given simple properties.

    Use this when:
        * Converting from MARC to Literature
        * Pushing a record from Holdingpen

    We wrote this in a non-pythonic non-generic way so it's extensible to any
    format a signature field might take.
    """

    def __init__(self, signature=None):
        """Initializes a signature.

        Initializes a signature to be used within a Literature record.
        """
        if signature is None:
            signature = {}
        self.obj = signature

    def _ensure_field(self, field_name, value):
        if value:
            self.obj.setdefault(field_name, value)

    def _ensure_list_field(self, field_name, value):
        if value:
            self.obj.setdefault(field_name, [])
            if value not in self.obj[field_name]:
                self.obj[field_name].append(value)

    def add_affiliation(self, value, curated_relation=None, record=None):
        """Add an affiliation.
        """
        if value:
            affiliation = {
                'value': value
            }
            if record:
                affiliation['record'] = record
            if curated_relation is not None:
                affiliation['curated_relation'] = curated_relation
            self._ensure_list_field('affiliations', affiliation)

    def add_alternative_name(self, alternative_name):
        self._ensure_list_field('alternative_names', alternative_name)

    def add_credit_role(self, credit_role):
        self._ensure_list_field('credit_roles', credit_role)

    def add_email(self, email):
        self._ensure_list_field('emails', email)

    def set_full_name(self, full_name):
        self._ensure_field('full_name', full_name)

    def _guess_schema(self, uid):
        schema = None
        if RE_BAI.match(uid):
            schema = 'INSPIRE BAI'
        elif idutils.is_orcid(uid):
            schema = 'ORCID'
            value = idutils.normalize_orcid(uid)
        elif RE_INSPIRE_ID.match(uid):
            schema = 'INSPIRE ID'
        return schema


    def add_uid(self, uid, schema=None):
        if not uid:
            return
        if schema is None:
            schema = _guess_schema(uid)
        self._ensure_field('ids', [])
        elem = {'value': uid}
        if schema:
            elem['schema'] = schema
        self.obj['ids'].append(elem)

    def set_uid(self, uid, schema=None):
        if schema is None:
            schema = _guess_schema(uid)
        if schema:
            self.obj['ids'] = filter(lambda uid: uid.get('schema') != schema, self.obj['ids'])
        self.add_uid(uid, schema)

    def set_bai(self, bai):
        self.set_uid(uid, 'INSPIRE BAI')

    def set_orcid(self, orcid):
        self.set_uid(uid, 'ORCID')

    def add_inspire_role(self, inspire_role):
        self._ensure_list_field('inspire_roles', inspire_role)

    def add_raw_affiliation(self, raw_affiliation):
        self._ensure_list_field('raw_affiliations', raw_affiliation)

    def set_record(self, record):
        self.obj['record'] = record
        self._ensure_field('curated_relation', False)

    def curate(self):
        self.obj['curated_relation'] = True
