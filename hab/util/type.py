from collections.abc import Iterable, Mapping
import six

def is_mapping(data):
	return isinstance(data, Mapping)

def is_string(data):
    return isinstance(data, six.string_types)

def is_iterable(data):
	return not is_string(data) and isinstance(data, Iterable)
