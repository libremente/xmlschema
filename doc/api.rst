API Documentation
=================

.. _document-level-api:

Document level API
------------------

.. autofunction:: xmlschema.validate
.. autofunction:: xmlschema.to_dict
.. autofunction:: xmlschema.to_json
.. autofunction:: xmlschema.from_json


.. _schema-level-api:

Schema level API
----------------

.. class:: xmlschema.XMLSchema10
.. class:: xmlschema.XMLSchema11

    The classes for XSD v1.0 and v1.1 schema instances. They are both generated by the
    meta-class :class:`XMLSchemaMeta` and take the same API of :class:`XMLSchemaBase`.

.. autoclass:: xmlschema.XMLSchema

.. autoclass:: xmlschema.XMLSchemaBase

    .. autoattribute:: root
    .. automethod:: get_text
    .. autoattribute:: url

    .. autoattribute:: tag
    .. autoattribute:: id
    .. autoattribute:: version

    .. autoattribute:: schema_location
    .. autoattribute:: no_namespace_schema_location
    .. autoattribute:: target_prefix
    .. autoattribute:: default_namespace
    .. autoattribute:: base_url
    .. autoattribute:: builtin_types
    .. autoattribute:: root_elements

    .. automethod:: create_meta_schema
    .. automethod:: create_schema
    .. automethod:: create_any_content_group
    .. automethod:: create_any_attribute_group

    .. automethod:: get_locations
    .. automethod:: include_schema
    .. automethod:: import_schema
    .. automethod:: resolve_qname
    .. automethod:: iter_globals
    .. automethod:: iter_components

    .. automethod:: check_schema
    .. automethod:: build
    .. automethod:: clear
    .. autoattribute:: built
    .. autoattribute:: validation_attempted
    .. autoattribute:: validity
    .. autoattribute:: all_errors

    .. automethod:: get_converter
    .. automethod:: validate
    .. automethod:: is_valid
    .. automethod:: iter_errors
    .. automethod:: decode

    .. _schema-iter_decode:

    .. automethod:: iter_decode
    .. automethod:: encode

    .. _schema-iter_encode:

    .. automethod:: iter_encode


XSD global maps API
-------------------

.. autoclass:: xmlschema.XsdGlobals
    :members: copy, register, iter_schemas, iter_globals, lookup_notation, lookup_type,
        lookup_attribute, lookup_attribute_group, lookup_group, lookup_element, lookup,
        clear, build, unbuilt, check


.. _xml-schema-converters-api:

XML Schema converters
---------------------

The base class `XMLSchemaConverter` is used for defining generic converters.
The subclasses implement some of the most used `conventions for converting XML
to JSON data <http://wiki.open311.org/JSON_and_XML_Conversion/>`_.

.. autoclass:: xmlschema.converters.ElementData

.. autoclass:: xmlschema.XMLSchemaConverter

    .. autoattribute:: lossy
    .. autoattribute:: lossless
    .. autoattribute:: losslessly

    .. automethod:: copy
    .. automethod:: map_attributes
    .. automethod:: map_content
    .. automethod:: etree_element
    .. automethod:: element_decode
    .. automethod:: element_encode

    .. automethod:: map_qname
    .. automethod:: unmap_qname

.. autoclass:: xmlschema.UnorderedConverter

.. autoclass:: xmlschema.ParkerConverter

.. autoclass:: xmlschema.BadgerFishConverter

.. autoclass:: xmlschema.AbderaConverter

.. autoclass:: xmlschema.JsonMLConverter


.. _resource-access-api:

Resource access API
-------------------

.. autoclass:: xmlschema.XMLResource

    .. autoattribute:: root
    .. autoattribute:: document
    .. autoattribute:: text
    .. autoattribute:: url
    .. autoattribute:: base_url
    .. autoattribute:: namespace

    .. automethod:: copy
    .. automethod:: tostring
    .. automethod:: open
    .. automethod:: load
    .. automethod:: is_lazy
    .. automethod:: is_loaded
    .. automethod:: iter
    .. automethod:: iter_location_hints
    .. automethod:: get_namespaces
    .. automethod:: get_locations

    .. automethod:: defusing
    .. automethod:: parse
    .. automethod:: iterparse
    .. automethod:: fromstring


.. autofunction:: xmlschema.fetch_resource
.. autofunction:: xmlschema.fetch_schema
.. autofunction:: xmlschema.fetch_schema_locations
.. autofunction:: xmlschema.load_xml_resource
.. autofunction:: xmlschema.normalize_url




XSD components API
------------------

.. note::
    For XSD components only methods included in the following documentation are considered
    part of the stable API, the others are considered internals that can be changed without
    forewarning.

XSD elements
^^^^^^^^^^^^
.. autoclass:: xmlschema.validators.Xsd11Element
.. autoclass:: xmlschema.validators.XsdElement

XSD attributes
^^^^^^^^^^^^^^
.. autoclass:: xmlschema.validators.Xsd11Attribute
.. autoclass:: xmlschema.validators.XsdAttribute

XSD types
^^^^^^^^^
.. autoclass:: xmlschema.validators.XsdType
    :members: is_simple, is_complex, is_atomic, is_empty, is_emptiable, has_simple_content,
        has_mixed_content, is_element_only
.. autoclass:: xmlschema.validators.Xsd11ComplexType
.. autoclass:: xmlschema.validators.XsdComplexType
.. autoclass:: xmlschema.validators.XsdSimpleType
.. autoclass:: xmlschema.validators.XsdAtomicBuiltin
.. autoclass:: xmlschema.validators.XsdList
.. autoclass:: xmlschema.validators.Xsd11Union
.. autoclass:: xmlschema.validators.XsdUnion
.. autoclass:: xmlschema.validators.Xsd11AtomicRestriction
.. autoclass:: xmlschema.validators.XsdAtomicRestriction

Attribute and model groups
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: xmlschema.validators.XsdAttributeGroup
.. autoclass:: xmlschema.validators.Xsd11Group
.. autoclass:: xmlschema.validators.XsdGroup

Wildcards
^^^^^^^^^
.. autoclass:: xmlschema.validators.Xsd11AnyElement
.. autoclass:: xmlschema.validators.XsdAnyElement
.. autoclass:: xmlschema.validators.Xsd11AnyAttribute
.. autoclass:: xmlschema.validators.XsdAnyAttribute
.. autoclass:: xmlschema.validators.XsdOpenContent
.. autoclass:: xmlschema.validators.XsdDefaultOpenContent

Identity constraints
^^^^^^^^^^^^^^^^^^^^
.. autoclass:: xmlschema.validators.XsdIdentity
.. autoclass:: xmlschema.validators.XsdSelector
.. autoclass:: xmlschema.validators.XsdFieldSelector
.. autoclass:: xmlschema.validators.Xsd11Unique
.. autoclass:: xmlschema.validators.XsdUnique
.. autoclass:: xmlschema.validators.Xsd11Key
.. autoclass:: xmlschema.validators.XsdKey
.. autoclass:: xmlschema.validators.Xsd11Keyref
.. autoclass:: xmlschema.validators.XsdKeyref

Facets
^^^^^^
.. autoclass:: xmlschema.validators.XsdFacet
.. autoclass:: xmlschema.validators.XsdWhiteSpaceFacet
.. autoclass:: xmlschema.validators.XsdLengthFacet
.. autoclass:: xmlschema.validators.XsdMinLengthFacet
.. autoclass:: xmlschema.validators.XsdMaxLengthFacet
.. autoclass:: xmlschema.validators.XsdMinInclusiveFacet
.. autoclass:: xmlschema.validators.XsdMinExclusiveFacet
.. autoclass:: xmlschema.validators.XsdMaxInclusiveFacet
.. autoclass:: xmlschema.validators.XsdMaxExclusiveFacet
.. autoclass:: xmlschema.validators.XsdTotalDigitsFacet
.. autoclass:: xmlschema.validators.XsdFractionDigitsFacet
.. autoclass:: xmlschema.validators.XsdExplicitTimezoneFacet
.. autoclass:: xmlschema.validators.XsdAssertionFacet
.. autoclass:: xmlschema.validators.XsdEnumerationFacets
.. autoclass:: xmlschema.validators.XsdPatternFacets

Other XSD components
^^^^^^^^^^^^^^^^^^^^
.. autoclass:: xmlschema.validators.XsdAssert
.. autoclass:: xmlschema.validators.XsdAlternative
.. autoclass:: xmlschema.validators.XsdNotation
.. autoclass:: xmlschema.validators.XsdAnnotation

XSD Validation API
^^^^^^^^^^^^^^^^^^
This API is implemented for XSD schemas, elements, attributes, types, attribute
groups and model groups.

.. autoclass:: xmlschema.validators.ValidationMixin

    .. automethod:: is_valid
    .. automethod:: validate
    .. automethod:: decode
    .. automethod:: iter_decode
    .. automethod:: iter_encode
    .. automethod:: iter_errors
    .. automethod:: encode
    .. automethod:: iter_encode

ElementTree and XPath API
^^^^^^^^^^^^^^^^^^^^^^^^^
This API is implemented for XSD schemas, elements and complexType's assertions.

.. autoclass:: xmlschema.ElementPathMixin

    .. autoattribute:: tag
    .. autoattribute:: attrib
    .. automethod:: get
    .. automethod:: iter
    .. automethod:: iterchildren
    .. automethod:: find
    .. automethod:: findall
    .. automethod:: iterfind


.. _errors-and-exceptions:

Errors and exceptions
---------------------

.. autoexception:: xmlschema.XMLSchemaException
.. autoexception:: xmlschema.XMLSchemaRegexError

.. autoexception:: xmlschema.XMLSchemaValidatorError
.. autoexception:: xmlschema.XMLSchemaNotBuiltError
.. autoexception:: xmlschema.XMLSchemaParseError
.. autoexception:: xmlschema.XMLSchemaModelError
.. autoexception:: xmlschema.XMLSchemaModelDepthError
.. autoexception:: xmlschema.XMLSchemaValidationError
.. autoexception:: xmlschema.XMLSchemaDecodeError
.. autoexception:: xmlschema.XMLSchemaEncodeError
.. autoexception:: xmlschema.XMLSchemaChildrenValidationError

.. autoexception:: xmlschema.XMLSchemaIncludeWarning
.. autoexception:: xmlschema.XMLSchemaImportWarning
.. autoexception:: xmlschema.XMLSchemaTypeTableWarning
