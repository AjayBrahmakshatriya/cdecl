import sys
base_types = ["int", "float", "double", "void", "char"]
special_tokens = ['*', '[', ']', '(', ')', ',']
ignore_tokens = [' ', ';', '\n']
decimal_constants = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

#Generic fail function with message
def fail_with(message):
	print message
	exit(-1)


#Fail function to indicate failure because of an unexpected character(s)
def fail(character):
	print_character = ""
	if isinstance(character, tuple):
		print_character = character[1]
	else:
		print_character = character
	fail_with("Syntax error: Invalid character - " + print_character)


#Classify a long token into T/I/N
# T = basic Type
# I = Identifier
# N = Numeral
def get_collect(collect):
	if collect in base_types:
			return ('T', collect)
	elif collect[0] not in decimal_constants:
		return ('I', collect)
	else:
		# For numeral we need to check if all the characters are numbers
		for j in collect:
			if j not in decimal_constants:
				fail(j)
		return ('N', collect)


#Take raw input and convert into a list of tokens
#Tokens are a single character for special symbols and a tuple with type and string for identifiers, types and constants
def tokenize(type_input):
	tokens = []
	#Collect unrecognized characters to match as a long token later
	collect = ""
	for i in type_input:
		if i in special_tokens or i in ignore_tokens:
			if collect != "":
				tokens += [get_collect(collect)]
				collect = ""
			#Skip whitespaces
			if i not in ignore_tokens:
				tokens += [i]
		else:
			collect += i
	if collect != "":
		tokens += [get_collect(collect)]
	return tokens

#Simple function to check if a token is a Numeral
def is_numeral(token):
	if isinstance(token , tuple) and token[0] == 'N':
		return True
	return False

#Simple function to check if a token is a basic Type
def is_basetype(token):
	if isinstance(token , tuple) and token[0] == 'T':
		return True
	return False

#Simple function to check if a token is an Identifier
def is_identifier(token):
	if isinstance(token , tuple) and token[0] == 'I':
		return True
	return False

#Identify where to start R-L from. It is obtained by finding the first token that can only be on the right side
def identify_start(type_input):
	start_pos = -1
	end_pos = -1
	for i in range(len(type_input)):	
		#tokens that only appear on the right side
		if is_identifier(type_input[i]) or type_input[i] == '[' or type_input[i] == ')':
			start_pos = i
			end_pos = i
			break

	# If a right side is not found, all the tokens are for left
	if start_pos == -1:
		start_pos = len(type_input)
		end_pos = len(type_input)
 	#if start_pos == -1:
	#	fail_with("Syntax error: Cannot figure type in " + str(type_input))


	return (type_input[:start_pos], type_input[end_pos:])


#Function identify the inner most bracket on both the sides and obtain the sub left and right tokens
def identify_limits(state):
	bracket_count = 1
	upper = []
	lower = []
	for i in state[2]:
		if i == '(':
			bracket_count += 1
		elif i == ')':
			bracket_count -= 1
		#Stop when the corresponding bracket is found
		if bracket_count == 0:
			break
		upper += [i]
	bracket_count = -1
	 
	for i in reversed(state[1]):
		if i == '(':
			bracket_count += 1
		elif i == ')':
			bracket_count -= 1
		#Stop when the corresponding bracket is found
		if bracket_count == 0:
			break
		lower = [i] + lower

	state = (state[0], state[1][:-len(lower)-1], state[2][len(upper)+1:], lower, upper)
	return state
		
	
#Pull a token from the right side 
def pull_right(upper):
	if len(upper) == 0:
		return (upper, None)
	character = upper[0]
	upper = upper[1:]
	return upper, character


#Pull a token from the left side
def pull_left(lower):
	if len(lower) == 0:
		return (lower, None)
	character = lower[-1]
	lower = lower[:-1]
	return lower, character

#A function to expract the argument types for a function from the right side
def extract_arguments(upper):
	arguments=[]
	curr_argument = []
	bracket_count = 1
	length_cut = 0
	
	#print upper	

	for i in upper:
		length_cut += 1
		if i == '(':
			bracket_count +=1 
		elif i == ')':
			bracket_count -=1
		#Separate arguments on comma
		elif i == ',' and bracket_count == 1:
			arguments += [curr_argument]
			curr_argument = []
			continue
		elif i == ';':
			fail(i)
		#Stop on matching bracket
		if bracket_count == 0:
			break
		curr_argument += [i]

	
	#Last argument if it exists
	if len(curr_argument) != 0:
		arguments += [curr_argument]
		

	return (upper[length_cut:], arguments)
		


def process_type(type_input):
	
	character = None
	
	#identify the starting point of parsing
	decl_name = identify_start(type_input)

	process_state = ("", decl_name[0], decl_name[1], [], [])

	done_first = 0

	while len(process_state[1]) > 0  or len(process_state[2]) > 0:
		process_state = identify_limits(process_state)	
		#spiral
		desc = process_state[0] 
		upper = process_state[4]
		lower = process_state[3]
				

		#Process right if exists
		while len(upper) > 0:
			upper, character = pull_right(upper)
			
			is_first = not done_first
			done_first = 1	
		
			#switch for right
			if character == None:
				break
			#Match for identifier
			if is_identifier(character) and is_first:
				desc += character[1] + " as "
			#Match for array type
			elif character == '[':
				upper, character = pull_right(upper)
				if character == ']':
					desc += "array of "
				elif is_numeral(character):
					number = character[1]
					upper, character = pull_right(upper)
					if character == ']':
						desc += "array [ " + number + " ] of "
					else:
						fail(character)
				else:
					fail(character)
			#Match for function type
			elif character == '(':
				upper, arguments = extract_arguments(upper)
				#print arguments		
				
				sub_type = "function ( " 
				if len(arguments) == 0:
					pass
				else:
					for i in range(len(arguments)):
						arg = arguments[i]
						sub_type += process_type(arg) 
						if i != len(arguments) - 1:
							sub_type += ", "				
					sub_type += " "
				desc += sub_type + ") returning "

			elif character == ';':
				pass
			else:
				fail(character)
	

		
	
		#Process left if exists
		while len(lower) > 0:
			lower, character = pull_left(lower)
			#switch for left
			if character == None:
				break
			#Match for pointer type
			if character == '*':
				desc += "pointer to "
			#Match for the final base type
			elif is_basetype(character) and len(process_state[1]) == 0 and len(process_state[2]) == 0 and len(lower) == 0:
				desc += character[1]
			else:
				fail(character)

		#Update state for parsing the next bracket
		process_state = (desc, process_state[1], process_state[2], [], [])

	#If the type doesn't end in a base type, it is incomplete	
	if not is_basetype(character):
		fail_with("Syntax error: No type name in declaration " + str(type_input))	

	#Final description created
	return process_state[0]


def main():
	for input_type in sys.stdin:
	#process a single input
		if input_type.strip() == "":
			continue
		tokens = tokenize(input_type)
		#Add declare to the destination only for the outmost type
		print "declare " + process_type(tokens)


if __name__ == "__main__":
	main()
