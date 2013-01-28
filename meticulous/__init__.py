import sys

class SchemaBase(object):
	"""SchemaBase - Base class for all schema definition classes.
		Extend on this and implement the following methods, to implement your own special schema types.
		Parameters:
			optional - Specifies whether a particular schema element is optional in the data.
	"""
	def __init__(self, optional):
		self.optional = optional

	def is_optional(self):
		return self.optional

	def self_check(self, fqn, errors):
		"""self_check - Implement this, to validate that an instance of a schema class is valid.
			returns: True  - Schema element and subordinate schema elements are all valid.
					 False - Schema element  or one or more subordinate schema elements are invalid.
			"""
		errors.append("{}: self_check() must be implemented for SchemaBase derived classes.".format(self.__class__.__name__))
		return False
	
	def valid_type(self, data, errors):
		"""valid_type - Implement this, to validate that a python data structure(representative of JSON) is of the correct type.
			returns: True  - Data element has the right type according to the schema element.
					 False - Data element has the wrong type according to the schema element.
			"""
		errors.append("{}: valid_type() must be implemented for SchemaBase derived classes.".format(self.__class__.__name__))
		return False
	
	def validate(self, fqn, data, errors):
		"""validate - Implement this, to validate that a python data structure(representative of JSON) is comprehensively correct.
			returns: True  - Data element and subordinate data elements are all valid.
					 False - Data element  or one or more subordinate data elements are invalid.
			"""
		errors.append("{}: validate() must be implemented for SchemaBase derived classes.".format(self.__class__.__name__))
		return False

class SchemaAny(SchemaBase):
	"""SchemaAny - Schema type that matches any data types.
		This should be used only sparingly. It represents the case where there is an application level interpretation of some
		sub-data structure of the message which may not be validated using this module.
		Parameters:
			optional - Whether the Any element is optional in the containing structure (dict or list).
		"""
	def __init__(self, optional=False):
		SchemaBase.__init__(self, optional)
	def self_check(self, fqn, errors):
		return True
	def valid_type(self, data):
		return True
	def validate(self, fqn, json_any, errors):
		#print(self.__class__.__name__+" - "+fqn+": result=True")
		return True

class SchemaStr(SchemaBase):
	"""SchemaStr - Validates a data structure member that is supposed to be a string.
		Parameters:
			minlen   - minimum length of string. Target data string must be >= this length.
					   You can not specify this as a negative value.
				  	   minlen must <= maxlen. 
			maxlen   - maximum length of string. Target data string must be <= this length.
			optional - Whether the string element is optional in the containing structure (dict or list).
			valid    - None or a list of valid string values.
	"""
	def __init__(self, minlen=0, maxlen=None, optional=False, valid=None):
		SchemaBase.__init__(self, optional)
		self.minlen = minlen
		self.maxlen = maxlen
		self.valid  = valid

	def self_check(self, fqn, errors):
		result = True
		if not isinstance(self.minlen, int) or self.minlen < 0:
			errors.append("{}({}): minlen({}) must be Integer(and >= 0). Default=0.".format(self.__class__.__name__, fqn, repr(self.minlen)))
			result = False
		if self.maxlen is not None:
			if not isinstance(self.maxlen, int):
				errors.append("{}({}): maxlen({}) must be Integer or None".format(self.__class__.__name__, fqn, repr(self.maxlen)))
				result = False
			elif isinstance(self.minlen, int):
				if self.minlen > self.maxlen:
					errors.append("{}({}): maxlen({}) must be >= minlen({}) or None".format(self.__class__.__name__, fqn, self.maxlen, self.minlen))
					result = False
		if self.valid is not None:
			if not isinstance(self.valid, list):
				errors.append("{}({}): valid param must be None or a list. Got {}".format(self.__class__.__name__, fqn, repr(self.valid)))
				result = False
			else:
				if len(self.valid) == 0:
					errors.append("{}({}): Valid list may not be empty.".format(self.__class__.__name__, fqn))
					result = False
				else:
					for v in self.valid:
						if not isinstance(v, str):
							errors.append("{}({}): element({}) of valid list must be of type string.".format(self.__class__.__name__, fqn, repr(v)))
							result = False
		return result

	def valid_type(self, json_str):
		return isinstance(json_str, str)

	def validate(self, fqn, json_str, errors):
		result = True
		if not self.valid_type(json_str):
			errors.append("{}({}): Expected 'str', got {}".format(self.__class__.__name__, fqn, repr(json_str)))
			result = False
		elif len(json_str) < self.minlen:
			errors.append("{}({}): String({}) shorter than minlen({}).".format(self.__class__.__name__, fqn, json_str, self.minlen))
			result = False
		elif self.maxlen is not None and len(json_str) > self.maxlen:
			errors.append("{}({}): String({}) longer than maxlen({}).".format(self.__class__.__name__, fqn, json_str, self.maxlen))
			result = False
		if result and self.valid is not None:
			if not json_str in self.valid:
				errors.append("{}({}): Integer({}) not in valid list({}).".format(self.__class__.__name__, fqn, json_str, self.valid))
				result = False
		#print(self.__class__.__name__+" - "+fqn+": result=",result)
		return result
			

class SchemaInt(SchemaBase):
	"""SchemaInt - Validates a data structure member that is supposed to be an integer.
		Parameters:
			minval   - minimum value of integer. Target data value must be >= this value.
					   minval must be <= maxval.
			maxval   - maximum value of integer. Target data value must be <= this value.
			optional - Whether the integer element is optional in the containing structure (dict or list).
			valid    - None or a list of valid integer values.
	"""
	def __init__(self, minval=None, maxval=None, optional=False, valid=None):
		SchemaBase.__init__(self, optional)
		self.minval = minval
		self.maxval = maxval
		self.valid  = valid
		
	def self_check(self, fqn, errors):
		result = True
		if self.minval is not None:
			if not isinstance(self.minval, int):
				errors.append("{}({}): minval({}) must be Integer.".format(self.__class__.__name__, fqn, repr(self.minval)))
				result = False
		if self.maxval is not None:
			if not isinstance(self.maxval, int):
				errors.append("{}({}): maxval({}) must be Integer or None".format(self.__class__.__name__, fqn, repr(self.maxval)))
				result = False
			elif isinstance(self.minval, int):
				if self.minval > self.maxval:
					errors.append("{}({}): maxval({}) must be >= minval({}) or None".format(self.__class__.__name__, fqn, self.maxval, self.minval))
					result = False
		if self.valid is not None:
			if not isinstance(self.valid, list):
				errors.append("{}({}): valid param must be None or a list. Got {}".format(self.__class__.__name__, fqn, repr(self.valid)))
				result = False
			else:
				if len(self.valid) == 0:
					errors.append("{}({}): Valid list may not be empty.".format(self.__class__.__name__, fqn))
					result = False
				else:
					for v in self.valid:
						if not isinstance(v, int):
							errors.append("{}({}): element({}) of valid list must be of type integer.".format(self.__class__.__name__, fqn, repr(v)))
							result = False
		return result

	def valid_type(self, json_int):
		return isinstance(json_int, int)

	def validate(self, fqn, json_int, errors):
		result = True
		if not self.valid_type(json_int):
			errors.append("{}({}): Expected 'int', got {}".format(self.__class__.__name__, fqn, repr(json_int)))
			result = False
		elif self.minval is not None and json_int < self.minval:
			errors.append("{}({}): Integer({}) less than minval({}).".format(self.__class__.__name__, fqn, json_int, self.minval))
			result = False
		elif self.maxval is not None and json_int > self.maxval:
			errors.append("{}({}): Integer({}) greater than maxval({}).".format(self.__class__.__name__, fqn, json_int, self.maxval))
			result = False
		if result and self.valid is not None:
			if not json_int in self.valid:
				errors.append("{}({}): Integer({}) not in valid list({}).".format(self.__class__.__name__, fqn, json_int, self.valid))
				result = False
		#print(self.__class__.__name__+" - "+fqn+": result=",result)
		return result
	
class SchemaList(SchemaBase, list):
	"""SchemaList - Validates a data structure member that is supposed to be a list.
			e.g. SchemaList([SchemaStr()])	defines a JSON list with any number of members that must be a strings.
		Parameters:
			[list] - SchemaList is also derived from base Python list class.
					 It may be constructed as per any list, but it is expected that it will be constructed with a list of
					 other SchemaBase derived objects, defining the valid members of the list. 
			minlen - minimum length of list. Target data list must be >= this length.
					 You can not specify this as a negative value.
					 minlen must <= maxlen. 
			maxlen - maximum length of list. Target data list must be <= this length.
		"""
	def __init__(self, list_param=[], minlen=0, maxlen=None, optional=False):
		list.__init__(self, list_param)
		SchemaBase.__init__(self, optional)
		self.minlen = minlen
		self.maxlen = maxlen

	def self_check(self, fqn, errors):
		result = True
		if len(self) == 0:	# Default Empty SchemaList to allow SchemaAny  
			self.append(SchemaAny())
		if not isinstance(self.minlen, int) or self.minlen < 0:
			errors.append("{}({}): minlen({}) must be Integer(and >= 0). Default=0.".format(self.__class__.__name__, fqn, repr(self.minlen)))
			result = False

		# Validate length parameters for list
		if self.maxlen is not None:
			if not isinstance(self.maxlen, int):
				errors.append("{}({}): maxlen({}) must be Integer or None".format(self.__class__.__name__, fqn, repr(self.maxlen)))
				result = False
			elif isinstance(self.minlen, int):
				if self.minlen > self.maxlen:
					errors.append("{}({}): maxlen({}) must be >= minlen({}) or None".format(self.__class__.__name__, fqn, self.maxlen, self.minlen))
					result = False			
		
		# Validate schema list members.
		for seq, schema_type in enumerate(self):
			elem_fqn = '.'.join([fqn, str(seq)])
			if not isinstance(schema_type, SchemaBase):
				errors.append("{}({}): Member({}) must be derived from SchemaBase".format(self.__class__.__name__, elem_fqn, repr(schema_type)))
				result = False
				continue
			if not schema_type.self_check(elem_fqn, errors):
				result = False
		return result
	
	def valid_type(self, json_list):
		return isinstance(json_list, list)

	def validate(self, fqn, json_list, errors):
		result = True
		if not self.valid_type(json_list):
			errors.append("{}({}): Expected 'list', got {}".format(self.__class__.__name__, fqn, repr(json_list)))
			result = False
		else:
			# Impose length restrictions
			if len(json_list) < self.minlen:
				errors.append("{}({}): List({}) shorter than minlen({}).".format(self.__class__.__name__, fqn, json_list, self.minlen))
				result = False
			elif self.maxlen is not None and len(json_list) > self.maxlen:
				errors.append("{}({}): List({}) longer than maxlen({}).".format(self.__class__.__name__, fqn, json_list, self.maxlen))
				result = False
			
			# Check each element of the json list
			for seq, json_elem in enumerate(json_list):
				elem_fqn = fqn + '[' + str(seq) + ']'	# Express fqn with [0] index notation.
				for schema_type in self:				# Each element matched against the first item in the schema list that allows its type.
					if schema_type.valid_type(json_elem):
						result = schema_type.validate(elem_fqn, json_elem, errors) and result
						break	# 1st match does validation, ignore others.
				else:	# None matched.
					errors.append("{}({}): Expected one of {}, got {}".format(self.__class__.__name__, elem_fqn, repr(self), json_elem))
					result = False
		#print(self.__class__.__name__+" - "+fqn+": result=",result)
		return result
		
class SchemaDict(SchemaBase, dict):
	"""SchemaDict - Validates a data structure member that is supposed to be a dict.
			SchemaDict is also expected to be the top level schema class for any message validation schema.
			e.g. SchemaDict({'a': SchemaStr(),}) defines a JSON dictt with a single member named 'a' that must be a string.
		Parameters:
			{dict} - SchemaDict is also derived from base Python dict class.
					 It may be constructed as per any dict, but it is expected that it will be constructed with a dict of
					 other SchemaBase derived objects, defining the valid members of the dict.
		"""
	def __init__(self, dict_param={}, optional=False):
		dict.__init__(self, dict_param)
		SchemaBase.__init__(self, optional)

	def self_check(self, fqn, errors):
		result = True
		for name, schema_type in self.items():
			elem_fqn = '.'.join([fqn, name])
			if not isinstance(schema_type, SchemaBase):
				errors.append("{}({}): Member({}) must be derived from SchemaBase".format(self.__class__.__name__, elem_fqn, repr(schema_type)))
				result = False
				continue
			if not schema_type.self_check(elem_fqn, errors):
				result = False
		return result

	def valid_type(self, json_dict):
		return isinstance(json_dict, dict)
	
	def validate(self, fqn, json_dict, errors):
		result = True
		if not self.valid_type(json_dict):
			errors.append("{}({}): Expected 'dict', got {}".format(self.__class__.__name__, fqn, repr(json_dict)))
			result = False
		else:
			# Check each element of the json dict data present.
			for name, json_elem in json_dict.items():
				if name not in self:
					errors.append("{}({}): Unexpected element ({}={})".format(self.__class__.__name__, fqn, name, json_elem))
					result = False
					continue
				elem_fqn = '.'.join([fqn, name])	# Extend fqn to next dot depth.
				result = self[name].validate(elem_fqn, json_elem, errors) and result
			
			# Reverse check, that all schema elements are present in the data
			for name, schema_type in self.items():
				if name not in json_dict and not schema_type.is_optional():
					errors.append("{}({}): Expected element ({}) missing".format(self.__class__.__name__, fqn, name))
					result = False
		#print(self.__class__.__name__+" - "+fqn+": result=",result)
		return result
