# -*- coding: utf-8 -*-
#
# Copyright (c), 2016-2019, SISSA (International School for Advanced Studies).
# All rights reserved.
# This file is distributed under the terms of the MIT License.
# See the file 'LICENSE' in the root directory of the present
# distribution, or http://opensource.org/licenses/MIT.
#
# @author Davide Brunato <brunato@sissa.it>
#
"""
This module contains classes for XML Schema wildcards.
"""
from __future__ import unicode_literals

from ..exceptions import XMLSchemaValueError
from ..qnames import XSD_ANY, XSD_ANY_ATTRIBUTE, XSD_OPEN_CONTENT, XSD_DEFAULT_OPEN_CONTENT
from ..helpers import get_namespace
from ..namespaces import XSI_NAMESPACE
from ..xpath import XMLSchemaProxy, ElementPathMixin

from .exceptions import XMLSchemaNotBuiltError
from .xsdbase import ValidationMixin, XsdComponent, ParticleMixin


class XsdWildcard(XsdComponent, ValidationMixin):
    names = ()
    namespace = ('##any',)
    not_namespace = ()
    not_qname = ()
    process_contents = 'strict'

    def __init__(self, elem, schema, parent):
        if parent is None:
            raise XMLSchemaValueError("'parent' attribute is None but %r cannot be global!" % self)
        super(XsdWildcard, self).__init__(elem, schema, parent)

    def __repr__(self):
        if self.namespace:
            return '%s(namespace=%r, process_contents=%r)' % (
                self.__class__.__name__, self.namespace, self.process_contents
            )
        else:
            return '%s(not_namespace=%r, process_contents=%r)' % (
                self.__class__.__name__, self.not_namespace, self.process_contents
            )

    def _parse(self):
        super(XsdWildcard, self)._parse()

        # Parse namespace and processContents
        namespace = self.elem.get('namespace', '##any').strip()
        if namespace == '##any':
            pass
        elif namespace == '##other':
            self.namespace = [namespace]
        elif namespace == '##local':
            self.namespace = ['']
        elif namespace == '##targetNamespace':
            self.namespace = [self.target_namespace]
        else:
            self.namespace = []
            for ns in namespace.split():
                if ns == '##local':
                    self.namespace.append('')
                elif ns == '##targetNamespace':
                    self.namespace.append(self.target_namespace)
                elif ns.startswith('##'):
                    self.parse_error("wrong value %r in 'namespace' attribute" % ns)
                else:
                    self.namespace.append(ns)

        process_contents = self.elem.get('processContents', 'strict')
        if process_contents == 'strict':
            pass
        elif process_contents not in ('lax', 'skip'):
            self.parse_error("wrong value %r for 'processContents' attribute" % self.process_contents)
        else:
            self.process_contents = process_contents

    def _parse_not_constraints(self):
        if 'notNamespace' not in self.elem.attrib:
            pass
        elif 'namespace' in self.elem.attrib:
            self.parse_error("'namespace' and 'notNamespace' attributes are mutually exclusive")
        else:
            self.namespace = []
            self.not_namespace = []
            for ns in self.elem.attrib['notNamespace'].strip().split():
                if ns == '##local':
                    self.not_namespace.append('')
                elif ns == '##targetNamespace':
                    self.not_namespace.append(self.target_namespace)
                elif ns.startswith('##'):
                    self.parse_error("wrong value %r in 'notNamespace' attribute" % ns)
                else:
                    self.not_namespace.append(ns)

        # Parse notQName attribute
        if 'notQName' not in self.elem.attrib:
            return

        not_qname = self.elem.attrib['notQName'].strip().split()

        if isinstance(self, XsdAnyAttribute) and \
                not all(not s.startswith('##') or s == '##defined' for s in not_qname) or \
                not all(not s.startswith('##') or s in {'##defined', '##definedSibling'} for s in not_qname):
            self.parse_error("wrong value for 'notQName' attribute")
            return

        try:
            names = [x if x.startswith('##') else self.schema.resolve_qname(x, False)
                     for x in not_qname]
        except KeyError as err:
            self.parse_error("unmapped QName in 'notQName' attribute: %s" % str(err))
            return
        except ValueError as err:
            self.parse_error("wrong QName format in 'notQName' attribute: %s" % str(err))
            return

        if self.not_namespace:
            if any(not x.startswith('##') for x in names) and \
                    all(get_namespace(x) in self.not_namespace for x in names if not x.startswith('##')):
                self.parse_error("the namespace of each QName in notQName is allowed by notNamespace")
        elif any(not self.is_namespace_allowed(get_namespace(x)) for x in names if not x.startswith('##')):
            self.parse_error("names in notQName must be in namespaces that are allowed")

        self.not_qname = names

    def _load_namespace(self, namespace):
        if namespace in self.schema.maps.namespaces:
            return

        for url in self.schema.get_locations(namespace):
            try:
                schema = self.schema.import_schema(namespace, url, base_url=self.schema.base_url)
                if schema is not None:
                    try:
                        schema.maps.build()
                    except XMLSchemaNotBuiltError:
                        # Namespace build fails: remove unbuilt schemas and the url hint
                        schema.maps.clear(remove_schemas=True, only_unbuilt=True)
                        self.schema.locations[namespace].remove(url)
                    else:
                        break
            except (OSError, IOError):
                pass

    @property
    def built(self):
        return True

    def is_matching(self, name, default_namespace=None, group=None):
        if name is None:
            return False
        elif not name or name[0] == '{':
            return self.is_namespace_allowed(get_namespace(name))
        elif default_namespace is None:
            return self.is_namespace_allowed('')
        else:
            return self.is_namespace_allowed(default_namespace)

    def is_namespace_allowed(self, namespace):
        if self.not_namespace:
            return namespace not in self.not_namespace
        elif self.namespace[0] == '##any' or namespace == XSI_NAMESPACE:
            return True
        elif self.namespace[0] == '##other':
            return namespace and namespace != self.target_namespace
        else:
            return namespace in self.namespace

    def deny_namespaces(self, namespaces):
        if self.not_namespace:
            return all(x in self.not_namespace for x in namespaces)
        elif '##any' in self.namespace:
            return False
        elif '##other' in self.namespace:
            return all(x == self.target_namespace for x in namespaces)
        else:
            return all(x not in self.namespace for x in namespaces)

    def deny_qnames(self, names):
        if self.not_namespace:
            return all(x in self.not_qname or get_namespace(x) in self.not_namespace for x in names)
        elif '##any' in self.namespace:
            return all(x in self.not_qname for x in names)
        elif '##other' in self.namespace:
            return all(x in self.not_qname or get_namespace(x) == self.target_namespace for x in names)
        else:
            return all(x in self.not_qname or get_namespace(x) not in self.namespace for x in names)

    def is_restriction(self, other, check_occurs=True):
        if check_occurs and isinstance(self, ParticleMixin) and not self.has_occurs_restriction(other):
            return False
        elif not isinstance(other, type(self)):
            return False
        elif other.process_contents == 'strict' and self.process_contents != 'strict':
            return False
        elif other.process_contents == 'lax' and self.process_contents == 'skip':
            return False

        if not self.not_qname and not other.not_qname:
            pass
        elif '##defined' in other.not_qname and '##defined' not in self.not_qname:
            return False
        elif '##definedSibling' in other.not_qname and '##definedSibling' not in self.not_qname:
            return False
        elif other.not_qname:
            if not self.deny_qnames(x for x in other.not_qname if not x.startswith('##')):
                return False
        elif any(not other.is_namespace_allowed(get_namespace(x)) for x in self.not_qname if not x.startswith('##')):
            return False

        if self.not_namespace:
            if other.not_namespace:
                return all(ns in self.not_namespace for ns in other.not_namespace)
            elif '##any' in other.namespace:
                return True
            elif '##other' in other.namespace:
                return '' in self.not_namespace and other.target_namespace in self.not_namespace
            else:
                return False
        elif other.not_namespace:
            if '##any' in self.namespace:
                return False
            elif '##other' in self.namespace:
                return set(other.not_namespace).issubset({'', other.target_namespace})
            else:
                return all(ns not in other.not_namespace for ns in self.namespace)

        if self.namespace == other.namespace:
            return True
        elif '##any' in other.namespace:
            return True
        elif '##any' in self.namespace or '##other' in self.namespace:
            return False
        elif '##other' in other.namespace:
            return other.target_namespace not in self.namespace and '' not in self.namespace
        else:
            return all(ns in other.namespace for ns in self.namespace)

    def extend(self, other):
        """Extends the XSD wildcard to include the namespace of another XSD wildcard."""
        if self.not_namespace:
            if other.not_namespace:
                self.not_namespace = [ns for ns in self.not_namespace if ns in other.not_namespace]
            elif other.namespace == '##any':
                self.not_namespace = ()
            elif other.namespace != '##other':
                self.not_namespace = [ns for ns in self.not_namespace if ns not in other.namespace]
            elif other.target_namespace in self.not_namespace:
                self.not_namespace = ['', other.target_namespace] if other.target_namespace else ['']
            else:
                self.not_namespace = ()

            if not self.not_namespace:
                self.namespace = ['##any']
            return

        elif other.not_namespace:
            if self.namespace == '##any':
                return
            elif self.namespace != '##other':
                self.not_namespace = [ns for ns in other.not_namespace if ns not in self.namespace]
            elif self.target_namespace in other.not_namespace:
                self.not_namespace = ['', self.target_namespace] if self.target_namespace else ['']
            else:
                self.not_namespace = ()

            if not self.not_namespace:
                self.namespace = ['##any']
            return

        if '##any' in self.namespace or self.namespace == other.namespace:
            return
        elif '##any' in other.namespace:
            self.namespace = ['##any']
            return
        elif '##other' in other.namespace:
            w1, w2 = other, self
        elif '##other' in self.namespace:
            w1, w2 = self, other
        else:
            self.namespace.extend(ns for ns in other.namespace if ns not in self.namespace)
            return

        if w2.not_namespace:
            self.not_namespace = [ns for ns in w2.not_namespace]
            if w1.target_namespace not in self.not_namespace:
                self.not_namespace.append(w1.target_namespace)
            self.namespace = []
        elif w1.target_namespace in w2.namespace and '' in w2.namespace:
            self.namespace = ['##any']
        elif '' not in w2.namespace and w1.target_namespace == w2.target_namespace:
            self.namespace = ['##other']
        elif self.xsd_version == '1.0':
            msg = "not expressible wildcard namespace union: {!r} V {!r}:"
            raise XMLSchemaValueError(msg.format(other.namespace, self.namespace))
        else:
            self.namespace = []
            self.not_namespace = ['', w1.target_namespace] if w1.target_namespace else ['']

    def iter_decode(self, source, validation='lax', **kwargs):
        raise NotImplementedError

    def iter_encode(self, obj, validation='lax', **kwargs):
        raise NotImplementedError


class XsdAnyElement(XsdWildcard, ParticleMixin, ElementPathMixin):
    """
    Class for XSD 1.0 *any* wildcards.

    ..  <any
          id = ID
          maxOccurs = (nonNegativeInteger | unbounded)  : 1
          minOccurs = nonNegativeInteger : 1
          namespace = ((##any | ##other) | List of (anyURI | (##targetNamespace | ##local)) )  : ##any
          processContents = (lax | skip | strict) : strict
          {any attributes with non-schema namespace . . .}>
          Content: (annotation?)
        </any>
    """
    _ADMITTED_TAGS = {XSD_ANY}

    def __repr__(self):
        if self.namespace:
            return '%s(namespace=%r, process_contents=%r, occurs=%r)' % (
                self.__class__.__name__, self.namespace, self.process_contents, self.occurs
            )
        else:
            return '%s(not_namespace=%r, process_contents=%r, occurs=%r)' % (
                self.__class__.__name__, self.not_namespace, self.process_contents, self.occurs
            )

    def _parse(self):
        super(XsdAnyElement, self)._parse()
        self._parse_particle(self.elem)
        self.xpath_proxy = XMLSchemaProxy(self.schema, self)

    def is_emptiable(self):
        return self.min_occurs == 0 or self.process_contents != 'strict'

    def matched_element(self, name, default_namespace=None, group=None):
        if self.is_matching(name, default_namespace, group):
            try:
                if name[0] != '{' and default_namespace:
                    return self.maps.lookup_element('{%s}%s' % (default_namespace, name))
                else:
                    return self.maps.lookup_element(name)
            except LookupError:
                pass

    def __iter__(self):
        return iter(())

    def iter(self, tag=None):
        return iter(())

    def iterchildren(self, tag=None):
        return iter(())

    @staticmethod
    def iter_substitutes():
        return iter(())

    def iter_decode(self, elem, validation='lax', **kwargs):
        if self.process_contents == 'skip':
            return

        namespace = get_namespace(elem.tag)
        if self.is_namespace_allowed(namespace):
            self._load_namespace(namespace)
            try:
                xsd_element = self.maps.lookup_element(elem.tag)
            except LookupError:
                if kwargs.get('drop_results'):
                    # Validation-only mode: use anyType for decode a complex element.
                    yield self.any_type.decode(elem) if len(elem) > 0 else elem.text
                elif self.process_contents == 'strict' and validation != 'skip':
                    reason = "element %r not found." % elem.tag
                    yield self.validation_error(validation, reason, elem, **kwargs)
            else:
                for result in xsd_element.iter_decode(elem, validation, **kwargs):
                    yield result
        elif validation != 'skip':
            reason = "element %r not allowed here." % elem.tag
            yield self.validation_error(validation, reason, elem, **kwargs)

    def iter_encode(self, obj, validation='lax', **kwargs):
        if self.process_contents == 'skip':
            return

        name, value = obj
        namespace = get_namespace(name)
        if self.is_namespace_allowed(namespace):
            self._load_namespace(namespace)
            try:
                xsd_element = self.maps.lookup_element(name)
            except LookupError:
                if self.process_contents == 'strict' and validation != 'skip':
                    reason = "element %r not found." % name
                    yield self.validation_error(validation, reason, **kwargs)
            else:
                for result in xsd_element.iter_encode(value, validation, **kwargs):
                    yield result
        elif validation != 'skip':
            reason = "element %r not allowed here." % name
            yield self.validation_error(validation, reason, value, **kwargs)

    def is_overlap(self, other):
        if not isinstance(other, XsdAnyElement):
            return other.is_overlap(self)
        elif self.not_namespace:
            if other.not_namespace:
                return True
            elif '##any' in other.namespace:
                return True
            elif '##other' in other.namespace:
                return True
            else:
                return any(ns not in self.not_namespace for ns in other.namespace)
        elif other.not_namespace:
            if '##any' in self.namespace:
                return True
            elif '##other' in self.namespace:
                return True
            else:
                return any(ns not in other.not_namespace for ns in self.namespace)
        elif self.namespace == other.namespace:
            return True
        elif '##any' in self.namespace or '##any' in other.namespace:
            return True
        elif '##other' in self.namespace:
            return any(ns and ns != self.target_namespace for ns in other.namespace)
        elif '##other' in other.namespace:
            return any(ns and ns != other.target_namespace for ns in self.namespace)
        else:
            return any(ns in self.namespace for ns in other.namespace)

    def is_consistent(self, other):
        return True


class XsdAnyAttribute(XsdWildcard):
    """
    Class for XSD 1.0 *anyAttribute* wildcards.

    ..  <anyAttribute
          id = ID
          namespace = ((##any | ##other) | List of (anyURI | (##targetNamespace | ##local)) )
          processContents = (lax | skip | strict) : strict
          {any attributes with non-schema namespace . . .}>
          Content: (annotation?)
        </anyAttribute>
    """
    _ADMITTED_TAGS = {XSD_ANY_ATTRIBUTE}

    def iter_decode(self, attribute, validation='lax', **kwargs):
        if self.process_contents == 'skip':
            return

        name, value = attribute
        namespace = get_namespace(name)
        if self.is_namespace_allowed(namespace):
            self._load_namespace(namespace)
            try:
                xsd_attribute = self.maps.lookup_attribute(name)
            except LookupError:
                if kwargs.get('drop_results'):
                    # Validation-only mode: returns the value if a decoder is not found.
                    yield value
                elif self.process_contents == 'strict' and validation != 'skip':
                    reason = "attribute %r not found." % name
                    yield self.validation_error(validation, reason, attribute, **kwargs)
            else:
                for result in xsd_attribute.iter_decode(value, validation, **kwargs):
                    yield result
        elif validation != 'skip':
            reason = "attribute %r not allowed." % name
            yield self.validation_error(validation, reason, attribute, **kwargs)

    def iter_encode(self, attribute, validation='lax', **kwargs):
        if self.process_contents == 'skip':
            return

        name, value = attribute
        namespace = get_namespace(name)
        if self.is_namespace_allowed(namespace):
            self._load_namespace(namespace)
            try:
                xsd_attribute = self.maps.lookup_attribute(name)
            except LookupError:
                if self.process_contents == 'strict' and validation != 'skip':
                    reason = "attribute %r not found." % name
                    yield self.validation_error(validation, reason, attribute, **kwargs)
            else:
                for result in xsd_attribute.iter_encode(value, validation, **kwargs):
                    yield result
        elif validation != 'skip':
            reason = "attribute %r not allowed." % name
            yield self.validation_error(validation, reason, attribute, **kwargs)


class Xsd11AnyElement(XsdAnyElement):
    """
    Class for XSD 1.1 *any* declarations.

    ..  <any
          id = ID
          maxOccurs = (nonNegativeInteger | unbounded)  : 1
          minOccurs = nonNegativeInteger : 1
          namespace = ((##any | ##other) | List of (anyURI | (##targetNamespace | ##local)) )
          notNamespace = List of (anyURI | (##targetNamespace | ##local))
          notQName = List of (QName | (##defined | ##definedSibling))
          processContents = (lax | skip | strict) : strict
          {any attributes with non-schema namespace . . .}>
          Content: (annotation?)
        </any>
    """
    def _parse(self):
        super(Xsd11AnyElement, self)._parse()
        self._parse_not_constraints()

    def is_matching(self, name, default_namespace=None, group=None):
        if name is None:
            return False
        elif not name or name[0] == '{':
            namespace = get_namespace(name)
        elif default_namespace is None:
            namespace = ''
        else:
            name = '{%s}%s' % (default_namespace, name)
            namespace = default_namespace

        if '##defined' in self.not_qname and name in self.maps.elements:
            if self.maps.elements[name].schema is self.schema:
                return False
        if group and '##definedSibling' in self.not_qname:
            if any(e is not self and e.match(name, default_namespace) for e in group.iter_elements()):
                return False
        return name not in self.not_qname and self.is_namespace_allowed(namespace)

    def is_consistent(self, other):
        if isinstance(other, XsdAnyElement) or self.process_contents == 'skip':
            return True
        xsd_element = self.matched_element(other.name, other.default_namespace)
        return xsd_element is None or other.is_consistent(xsd_element, False)


class Xsd11AnyAttribute(XsdAnyAttribute):
    """
    Class for XSD 1.1 *anyAttribute* declarations.

    ..  <anyAttribute
          id = ID
          namespace = ((##any | ##other) | List of (anyURI | (##targetNamespace | ##local)) )
          notNamespace = List of (anyURI | (##targetNamespace | ##local))
          notQName = List of (QName | ##defined)
          processContents = (lax | skip | strict) : strict
          {any attributes with non-schema namespace . . .}>
          Content: (annotation?)
        </anyAttribute>
    """
    def _parse(self):
        super(Xsd11AnyAttribute, self)._parse()
        self._parse_not_constraints()

    def is_matching(self, name, default_namespace=None, group=None):
        if name is None:
            return False
        elif not name or name[0] == '{':
            namespace = get_namespace(name)
        elif default_namespace is None:
            namespace = ''
        else:
            name = '{%s}%s' % (default_namespace, name)
            namespace = default_namespace

        if '##defined' in self.not_qname and name in self.maps.attributes:
            if self.maps.attributes[name].schema is self.schema:
                return False
        return name not in self.not_qname and self.is_namespace_allowed(namespace)


class XsdOpenContent(XsdComponent):
    """
    Class for XSD 1.1 *openContent* model definitions.

    ..  <openContent
          id = ID
          mode = (none | interleave | suffix) : interleave
          {any attributes with non-schema namespace . . .}>
          Content: (annotation?), (any?)
        </openContent>
    """
    _ADMITTED_TAGS = {XSD_OPEN_CONTENT}
    mode = 'interleave'
    any_element = None

    def __init__(self, elem, schema, parent):
        super(XsdOpenContent, self).__init__(elem, schema, parent)

    def __repr__(self):
        return '%s(mode=%r)' % (self.__class__.__name__, self.mode)

    def _parse(self):
        super(XsdOpenContent, self)._parse()
        try:
            self.mode = self.elem.attrib['mode']
        except KeyError:
            pass
        else:
            if self.mode not in {'none', 'interleave', 'suffix'}:
                self.parse_error("wrong value %r for 'mode' attribute." % self.mode)

        child = self._parse_child_component(self.elem)
        if self.mode == 'none':
            if child is not None and child.tag == XSD_ANY:
                self.parse_error("an openContent with mode='none' must not has an <xs:any> child declaration")
        elif child is None or child.tag != XSD_ANY:
            self.parse_error("an <xs:any> child declaration is required")
        else:
            any_element = Xsd11AnyElement(child, self.schema, self)
            any_element.min_occurs = 0
            any_element.max_occurs = None
            self.any_element = any_element

    @property
    def built(self):
        return True

    def is_restriction(self, other):
        if self.mode == 'none' or other is None or other.mode == 'none':
            return True
        elif self.mode == 'interleave' and other.mode == 'suffix':
            return False
        else:
            return self.any_element.is_restriction(other.any_element)


class XsdDefaultOpenContent(XsdOpenContent):
    """
    Class for XSD 1.1 *defaultOpenContent* model definitions.

    ..  <defaultOpenContent
          appliesToEmpty = boolean : false
          id = ID
          mode = (interleave | suffix) : interleave
          {any attributes with non-schema namespace . . .}>
          Content: (annotation?, any)
        </defaultOpenContent>
    """
    _ADMITTED_TAGS = {XSD_DEFAULT_OPEN_CONTENT}
    applies_to_empty = False

    def __init__(self, elem, schema):
        super(XsdOpenContent, self).__init__(elem, schema)

    def _parse(self):
        super(XsdDefaultOpenContent, self)._parse()
        if self.parent is not None:
            self.parse_error("defaultOpenContent must be a child of the schema")
        if self.mode == 'none':
            self.parse_error("the attribute 'mode' of a defaultOpenContent cannot be 'none'")
        if self._parse_child_component(self.elem) is None:
            self.parse_error("a defaultOpenContent declaration cannot be empty")

        if self._parse_boolean_attribute('appliesToEmpty'):
            self.applies_to_empty = True
