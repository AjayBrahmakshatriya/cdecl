

base_types = ["int", "float", "double", "void", "char"]
special_tokens = ['*', '[', ']', '(', ')', ',']
ignore_tokens = [' ', ';']
decimal_constants = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def fail_with(message):
	print message
	exit(-1)

def fail(character):
	fail_with("Syntax error: Invalid character - " + character)

def get_collect(collect):
	if collect in base_types:
			return 'T'
	elif collect[0] not in decimal_constants:
		return 'I'
	else:
		for j in collect:
			if j not in decimal_constants:
				fail(j)
		return 'N'

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

def identify_decl_name(type_input):
	name_collected = ""
	start_pos = -1
	end_post = -1
	for pos in range(len(type_input)):
		character = type_input[pos]

		if character in special_tokens or character in ignore_tokens:
			if len(name_collected) != 0:
				if name_collected not in base_types and (name_collected[0] not in decimal_constants):
					break
				else:
					name_collected = ""
			start_pos = pos + 1
		else:
			name_collected += character
			end_pos = pos + 1
	if name_collected != "" and name_collected not in base_types and (name_collected[0] not in decimal_constants):
		pass
	else:
		name_collected = ""

 	if name_collected == "":
		fail_with("Syntax error: Identifier not found in " + type_input)

	return (name_collected, type_input[:start_pos], type_input[end_pos:])

def identify_limits(state):
	bracket_count = 1
	upper = ""
	lower = ""
	for i in state[2]:
		if i == '(':
			bracket_count += 1
		elif i == ')':
			bracket_count -= 1
		if bracket_count == 0:
			break
		upper += i
	bracket_count = -1
	 
	for i in reversed(state[1]):
		if i == '(':
			bracket_count += 1
		elif i == ')':
			bracket_count -= 1
		if bracket_count == 0:
			break
		lower = i + lower
	state = (state[0], state[1][:-len(lower)-1], state[2][len(upper)+1:], lower, upper)
	return state
		
	


def pull_right(upper):
	character = ' '
	while character == ' ':
		if upper == "":
			return (upper, None)
		character = upper[0]
		upper = upper[1:]
	return upper, character


def pull_left(lower):
	character = ' '
	while character == ' ':
		if lower == "":
			return (lower, None)
		character = lower[-1]
		lower = lower[:-1]
	return lower, character

def extract_arguments(upper):
	arguments=[]
	curr_argument = ""
	bracket_count = 1
	length_cut = 0
	for i in upper:
		length_cut += 1
		if i == '(':
			bracket_count +=1 
		elif i == ')':
			bracket_count -=1
		elif i == ',':
			arguments += [curr_argument]
			curr_argument = ""
			continue
		elif i == ';':
			fail(i)
		if bracket_count == 0:
			break
		curr_argument += i

	if not (curr_argument.strip() == "" and len(arguments) == 0):
		arguments += [curr_argument]
		

	return (upper[length_cut:], arguments)
		


def process_type(type_input):
	#identify DECL_NAME
	decl_name = identify_decl_name(type_input)

	#print decl_name

	process_state = (decl_name[0] + " as ", decl_name[1], decl_name[2], "", "")


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
			
			if character == '[':
				upper, character = pull_right(upper)
				if character != ']':
					fail(character)
				desc += "array of "
			elif character == '(':
				upper, arguments = extract_arguments(upper)
				
				sub_type = "function ( " 
				if len(arguments) == 0:
					pass
				elif len(arguments) == 1 and arguments[0].strip() == "void":
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
				character = lower + character
				lower = ""
				if character.strip() in base_types and process_state[1] == "" and process_state[2] == "":
					desc += character.strip()
				else:
					fail(character)
			

		process_state = (desc, process_state[1], process_state[2], "", "")
	

	return process_state[0]




def main():

	#process a single input
	input_type = raw_input()
	print tokenize(input_type)
	print "declare " + process_type(input_type)




if __name__ == "__main__":
	main()
