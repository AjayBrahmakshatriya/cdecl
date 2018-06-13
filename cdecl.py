base_types = ["int", "float", "double", "void", "char"]
special_tokens = ['*', '[', ']', '(', ')', ',']
ignore_tokens = [' ', ';']
decimal_constants = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def fail_with(message):
	print message
	exit(-1)

def fail(character):
	print character
	print_character = ""
	if isinstance(character, tuple):
		print_character = character[1]
	else:
		print_character = character
	fail_with("Syntax error: Invalid character - " + print_character)

def get_collect(collect):
	if collect in base_types:
			return ('T', collect)
	elif collect[0] not in decimal_constants:
		return ('I', collect)
	else:
		for j in collect:
			if j not in decimal_constants:
				fail(j)
		return ('N', collect)

def tokenize(type_input):
	tokens = []
	collect = ""
	for i in type_input:
		if i in special_tokens or i in ignore_tokens:
			if collect != "":
				tokens += [get_collect(collect)]
				collect = ""
			if i not in ignore_tokens:
				tokens += [i]
		else:
			collect += i
	if collect != "":
		tokens += [get_collect(collect)]
	return tokens

def is_numeral(token):
	if isinstance(token , tuple) and token[0] == 'N':
		return True
	return False

def is_basetype(token):
	if isinstance(token , tuple) and token[0] == 'T':
		return True
	return False


def is_identifier(token):
	if isinstance(token , tuple) and token[0] == 'I':
		return True
	return False


def identify_start(type_input):
	start_pos = -1
	end_pos = -1
	for i in range(len(type_input)):	
		if is_identifier(type_input[i]) or type_input[i] == '[' or type_input[i] == ')':
			start_pos = i
			end_pos = i
			break

	if start_pos == -1:
		start_pos = len(type_input)
		end_pos = len(type_input)
 	#if start_pos == -1:
	#	fail_with("Syntax error: Cannot figure type in " + str(type_input))


	return (type_input[:start_pos], type_input[end_pos:])

def identify_limits(state):
	bracket_count = 1
	upper = []
	lower = []
	for i in state[2]:
		if i == '(':
			bracket_count += 1
		elif i == ')':
			bracket_count -= 1
		if bracket_count == 0:
			break
		upper += [i]
	bracket_count = -1
	 
	for i in reversed(state[1]):
		if i == '(':
			bracket_count += 1
		elif i == ')':
			bracket_count -= 1
		if bracket_count == 0:
			break
		lower = [i] + lower
	state = (state[0], state[1][:-len(lower)-1], state[2][len(upper)+1:], lower, upper)
	return state
		
	


def pull_right(upper):
	if len(upper) == 0:
		return (upper, None)
	character = upper[0]
	upper = upper[1:]
	return upper, character


def pull_left(lower):
	if len(lower) == 0:
		return (lower, None)
	character = lower[-1]
	lower = lower[:-1]
	return lower, character

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
		elif i == ',' and bracket_count == 1:
			arguments += [curr_argument]
			curr_argument = []
			continue
		elif i == ';':
			fail(i)
		if bracket_count == 0:
			break
		curr_argument += [i]


	if len(curr_argument) != 0:
		arguments += [curr_argument]
		

	return (upper[length_cut:], arguments)
		


def process_type(type_input):
	#identify DECL_NAME
	decl_name = identify_start(type_input)

	process_state = ("", decl_name[0], decl_name[1], [], [])


	while len(process_state[1]) > 0  or len(process_state[2]) > 0:
		process_state = identify_limits(process_state)	
		#spiral
		desc = process_state[0] 
		upper = process_state[4]
		lower = process_state[3]
		
		#Process right if exists
		while len(upper) > 0:
			upper, character = pull_right(upper)
			#switch for right
			if character == None:
				break
			if is_identifier(character):
				desc += character[1] + " as "
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
			elif character == '(':
				upper, arguments = extract_arguments(upper)
				#print arguments		
				
				sub_type = "function ( " 
				if len(arguments) == 0:
					pass
				elif len(arguments) == 1 and len(arguments[0]) == 1 and is_basetype(arguments[0][0]) and arguments[0][0][1] == "void":
					sub_type += "void "
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
			if character == '*':
				desc += "pointer to "
			else:
				if is_basetype(character) and len(process_state[1]) == 0 and len(process_state[2]) == 0 and len(lower) == 0:
					desc += character[1]
				else:
					fail(character)
			

		process_state = (desc, process_state[1], process_state[2], [], [])
	

	return process_state[0]




def main():

	#process a single input
	input_type = raw_input()
	tokens = tokenize(input_type)
	print "declare " + process_type(tokens)




if __name__ == "__main__":
	main()
