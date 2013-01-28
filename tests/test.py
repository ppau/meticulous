# TODO: port to pyunit or nosetest

from meticulous import *

if __name__ == "__main__":

	def validate_schema(schema, schema_name):
		errors = []
		schema_valid = schema.self_check(schema_name, errors)
		if not schema_valid:
			print('validate_schema:', schema_name, " is invalid:", file=sys.stderr)
			for error in errors:
				print("   ", error, file=sys.stderr)
		else:
			print('validate_schema:', schema_name, " is valid.", file=sys.stderr)

	def validate_json_data(json_data, json_data_name, schema, schema_name):
		errors = []
		json_valid = schema.validate(json_data_name, json_data, errors)
		if not json_valid:
			print('validate_json_data(using',schema_name,'):', json_data_name, "is invalid:", file=sys.stderr)
			for error in errors:
				print("   ", error, file=sys.stderr)
		else:
			print('validate_json_data(using',schema_name,'):', json_data_name, "is valid.", file=sys.stderr)
	
	# Define and validate a valid schema.
	valid_schema = SchemaDict({
		'a1': SchemaList([							# SchemaList of types allowed in SchemaList. Construct with []
			SchemaStr(maxlen=32), 
			SchemaInt(minval=10, maxval=42)
		]),
		'a2': SchemaStr(minlen=10),
		'a3': SchemaStr(maxlen=10),
		'a4': SchemaInt(),							# Any integer
		'a5': SchemaDict({
			'b1': SchemaInt(minval=0),				# Any maxval >= minval
			'b2': SchemaInt(maxval=42),				# Any minval <= maxval
			'b3': SchemaInt(minval=-1, maxval=42),
			'b4': SchemaList(),  					# Defaults to SchemaList of Any
			'b5': SchemaList([						# SchemaList of schemas allowed in list
				SchemaDict({
					'c1': SchemaInt(),
					'c2': SchemaStr(),
				}),
			]),
			'b6': SchemaList([
				SchemaInt(), 
			], minlen=2, maxlen=3),
		}),
		'a6': SchemaInt(optional=True),				# Optional member. If it's there, must be int.
		'a7': SchemaStr(valid=["abc", "123"]),		# Valid string  values list
		'a8': SchemaInt(valid=[1,2,3]),				# Valid integer values list
	})
	validate_schema(valid_schema, "valid_schema")

	# Define and validate an invalid schema.
	class non_schema:
		pass
	invalid_schema = SchemaDict({
		'a1': non_schema(),							# Invalid - Non schema member
		'a2': SchemaStr(minlen='a', maxlen='z'),	# Invalid - min/maxlen types.
		'a3': SchemaStr(maxlen=-1),					# Invalid - Max string length < 0
		'a4': SchemaInt(minval='a', maxval='z'),	# Invalid - min/maxval types.
		'a5': SchemaDict({
			'b1': non_schema(),						# Invalid - Non scheme member in sub-Dict
			'b2': SchemaInt(maxval=42),				# Any minval <= maxval
			'b3': SchemaInt(minval=-1, maxval=42),
			'b4': SchemaList(),  					# Defaults to SchemaList of Any
			'b5': SchemaList([						# SchemaList of schemas allowed in list
				non_schema(),						# Invalid - Non schema member in list
			]),
			'b6': SchemaList([						# Invalid - Negative list minlen
				SchemaInt(), 
			], minlen=-1, maxlen=3),
			'b7': SchemaList([						# Invalid - maxlen <= minlen
				SchemaInt(), 
			], minlen=3, maxlen=1),
			'b8': SchemaList([], 
						minlen='a', maxlen='z'), 	# Invalid - minlen, maxlen types.
		}),
		'a7': SchemaStr(valid=non_schema),			# Invalid - should be list
		'a8': SchemaStr(valid=[]),					# Invalid - valid list can't be empty
		'a9': SchemaStr(valid=[1,2]),				# Invalid - valid list types must match schema type.
		'a10': SchemaInt(valid=non_schema),			# Invalid - should be list
		'a11': SchemaInt(valid=[]),					# Invalid - valid list can't be empty
		'a12': SchemaInt(valid=["abc",]),			# Invalid - valid list types must match schema type.
	})
	validate_schema(invalid_schema, "invalid_schema")
	
	# Define and validate valid JSON data against valid schema.
	valid_json_data = {
		'a1': ["abc", 11, 12, "def"],
		'a2': "Andrew Downing",
		'a3': "Short",
		'a4': 42,
		'a5': {
			'b1': 1,
			'b2': 42,
			'b3': -1,
			'b4': ['abc', 'its', 'easy', 'as', 1,2,3],
			'b5': [ 
				{'c1': 1, 'c2': 'abc'},
				{'c1': 2, 'c2': 'def'},
				{'c1': 3, 'c2': 'ghi'},
			],
			'b6': [1,2,3],
		},
		# 'a6': 42,		# Optional and excluded.
		'a7': "abc",
		'a8': 1,
	}
	validate_json_data(valid_json_data, "valid_json_data", valid_schema, "valid_schema")	
	valid_json_data['a6'] = 42		# Optional and included
	validate_json_data(valid_json_data, "valid_json_data + optional", valid_schema, "valid_schema")	
	
	# Define and validate valid JSON data against valid schema.
	invalid_json_data = {
		'a1': ["abc", 11, 			
			   ["InvalidList",], 	# Invalid List member of List
			   {"x":"Invalid Dict"},# Invalid Dictionary member of List 
			   "def"],
		'a2': 2,					# Invalid value  (too small) 
		'a3': "1234567890123",		# Invalid Length (too long)
		'a4': "ABC",				# Invalid integer				
		'a5': {
			#'b1': 1,				# Invalid Missing value
			'b2': 43,				# Invalid value  (too big)
			'b3': -1,
			'b4': {'c1':1},		 	# Invalid Dict instead of List
			'b5': [ 
				[1, 'abc'],			# Invalid List instead of Dict
				{'c1': 2, 'c2': 'def'},
				{'c1': 3, 'c2': 'ghi'},
			],
			'b6': [1,2,3,4,5,6,7,8], # Invalid list length (too long)
		},
		'a7': "def",				# Invalid value not in list
		'a8': 4,					# Invalid value not in list
		'a99': "Invalid data"		# Invalid extra member of Dict.
	}
	validate_json_data(invalid_json_data, "invalid_json_data", valid_schema, "valid_schema")	
