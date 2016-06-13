# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 18:24:31 2016

@author: Eddie
"""

import warnings

'''
List of all registered push instructions.
'''
registered_instructions = []


def register_instruction(instruction):
	'''
	Registers an instruction, excluding duplicates.
	'''   
	if len(list(filter(lambda x: x.name == instruction.name, registered_instructions))) > 0:
		warnings.warn('Duplicate instructions registered: ' + instruction.name + '. Duplicate ignored.')
	else:
		registered_instructions.append(instruction)