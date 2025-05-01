#!/usr/bin/env python3

# Requirement of the exercise
# An app that will help automate the writing of student feedback adhering to 
# formatting requirements. 
#
#	reqs:
#		- The feedback must be written to a .txt file with the file name 
#			including the students name. 
#		- The text in the file must have the headers 'General comments', 
#			'Punctuality and engagement' and 'further learning'. Each header will have
#			a short paragraph of text.
#		- All files to be written to a sub-folder named "feedback_files"
#		- The file should open automatically in a text editor for manual review.
#		- The user of the app should input students names.
#		- Inputs for marks/grades students receive for specific factors such    
#			as 'understanding_level', 'contribution_level' etc. 
#		- The marks should be used to format believable sentances to be written 
#			to the file.
#		- The feedback is expected to have correct grammar and appear to be 
#			written personally.
#		
#		
# example final format:
#	
# General comments
# Lyudmil worked hard in this module, completing all his labs to a good standard. 
# He picked up DevOps tooling quickly, demonstrating a good level of existing knowledge. 
# He contributed to class discussions and worked well independently.  
#
# Learner Punctuality and engagement 
# Lyudmil was always punctual throughout the module and engaged well. 
#
# Recommendations on further learning
# Continue to practice and explore good pipeline design and integrate docker and 
# monitoring into your projects. 
#
# Feedback will be given on Bud - (written by me manually!) Im looking for good and 
# extensible design, with comments/doc strings explaining decisions. 
# Deadline: end of module - must be emailed (in body of email not attatchment).
# spend 1 - 2 hours max! 

# Input: Student Name, the scores of understand level and contribution level.
# Output: A text file which contains comments.

# Define Script Name
codename = "GenerateComment"
__version__ = '1.0.0'

##### IMPORTS ######
#import requests								# Used for API calls to Jamf
import os									# Used to interact with the local filesystem
import getopt								# Used to parse command line arguments
#import shutil								# Used to copy files
import glob									# Used to search for files in a given location
import sys									# Used to get any arguments passed to script
import logging								# Used to log events to external file
import time									# Used to allow wait commands
import datetime								# Used to get the time and to convert seconds to HH:MM:SS time
#import mimetypes							# Used to get the icon file type
#import subprocess							# Used to run bash commands
import hashlib								# Used to get the local checksum of the package
import plistlib								# Used to read config details from a plist
#import urllib.parse							# Used to parse the auth when getting casper.jxml and quoting the package name
#import xml.etree.ElementTree as ET			# Used to search through XML data
from cryptography.fernet import Fernet		# Used to encrypt DB password
import mysql.connector						# Used to interact with a MySQL DB (python3 -m pip install mysql-connector)
import json									# Used to dump json for Zendesk ticket generation
import random

# https://stackoverflow.com/questions/11887762/how-do-i-compare-version-numbers-in-python
#from packaging.version import Version		# Used in sorted() as a key to sort versions in the array and parse version string for comparison

#from slack_webhook import Slack				# Used to send Slack Webhook to channel

#######################################
############# Variables ###############
#######################################

# Logging variable
BASE_DIR = "/Users/Shared/"
COMMENT_DIR = BASE_DIR + "feedback_files"

# Define the comments as dictionar㕙
general_comments = {
	5: [
		"Consistently demonstrates outstanding effort and enthusiasm in all areas.",
		"Exceeds expectations and shows strong leadership in class activities."
	],
	4: [
		"Performs very well with a strong understanding of material.",
		"Shows consistent effort and engages positively in class."
	],
	3: [
		"Performs satisfactorily and demonstrates understanding of most content.",
		"Contributes occasionally and completes most tasks on time."
	],
	2: [
		"Struggles to maintain consistent effort and requires occasional support.",
		"Participation is limited, and understanding of material is developing."
	],
	1: [
		"Often needs guidance and support to complete tasks.",
		"Rarely participates and shows limited engagement."
	],
	0: [
		"Does not demonstrate adequate effort or understanding at this time.",
		"Requires significant support and intervention to make progress."
	]
}

contribute_engagement_comments = {
	5: [
		"Highly engaged and consistently makes thoughtful contributions in class discussions.",
		"Demonstrates leadership and initiative, and actively supports peer learning."
	],
	4: [
		"Regularly participates and contributes relevant insights to group and class activities.",
		"Engaged in most lessons and interacts positively with both peers and teachers."
	],
	3: [
		"Participates when prompted and demonstrates a reasonable level of engagement.",
		"Involved in learning activities but could take more initiative independently."
	],
	2: [
		"Sometimes engaged but rarely initiates contributions without encouragement.",
		"Shows interest inconsistently and may be hesitant to participate in discussions."
	],
	1: [
		"Seldom participates and often appears disengaged during class activities.",
		"Requires regular prompting to contribute and stay focused."
	],
	0: [
		"Shows minimal engagement and contributes little to class or group work.",
		"Needs significant encouragement and support to participate meaningfully."
	]
}

python_learning_recommendations = {
	5: [
		"To continue growing, focus on mastering advanced topics such as decorators, generators, and asynchronous programming.",
		"To enhance your skills further, consider working on larger projects or exploring areas like data science or web frameworks."
	],
	4: [
		"To reach an advanced level, improve your understanding of complex data structures and start exploring libraries like Pandas or Flask.",
		"You are doing well—next, challenge yourself with small projects and begin learning how to write clean, modular code."
	],
	3: [
		"To strengthen your skills, review functions, loops, and lists, and practice solving problems on platforms like LeetCode or HackerRank.",
		"You're on the right track—focus now on writing your own basic programs and understanding how to structure code logically."
	],
	2: [
		"To make progress, revisit Python fundamentals such as variables, conditionals, and loops with hands-on practice.",
		"You need to build more confidence with the basics—try structured tutorials and focus on writing short, simple programs."
	],
	1: [
		"To begin developing your skills, focus on understanding what programming is and how Python syntax works through guided exercises.",
		"Start by learning the most basic concepts like printing, data types, and simple if-statements using interactive resources."
	],
	0: [
		"Start with beginner-friendly, visual programming environments to build foundational thinking before tackling Python syntax.",
		"Focus on developing a basic understanding of what code does—work with simplified tools and one-on-one guidance to begin your journey."
	]
}

#######################################
############# Functions ###############
#######################################

def print_usage(error):
	""" Print the usage of the script itself
	"""	
	if error != None:
		print ("ERROR: " + error)
		
	print ('''usage: GenerateComment.py -g <general score 0-5> -c <contribution score 0-5> -n <student name> [-h]

required arguments:
-g, --general			pass the general score of the student
-c, --contribute		pass the contribution score of the student
-n, --name				pass the name of the student

optional arguments:
-h, --help			show this help message
''')
	
	
def check_arguments():
	''' Check and parse arguments into the script
	'''
	general = None
	contribute = None
	studentname = None
	
	# Remove 1st argument from the list of command line arguments 
	argument_list = sys.argv[1:]
	
	# Options (colon after a letter means a value is expected to be passed)
	options = "g:c:n:h"
	
	# Long options (equals means a value is expected to be passed)
	long_options = ["General =", "Contribute =", "Name =", "Help"]
	try: 
		# Parsing argument 
		arguments, values = getopt.getopt(argument_list, options, long_options) 
		
		# Checking each argument 
		for current_argument, current_value in arguments: 
			
			if current_argument in ("-h", "--help"): 
				print_usage(None)
				exit()
			elif current_argument in ("-g", "--general"): 
				general = current_value
			elif current_argument in ("-c", "--contribute"): 
				contribute = current_value
			elif current_argument in ("-n", "--name"):
				name = current_value
				
	except getopt.error as err: 
		# output error, and return with an error code 
		print_usage(str(err) + "\n==============================")
		exit()
		
	# If no error rasied above, then confirm we have a Cipher Key before continuing
	if general == None:
		print_usage("No general score provided.\n==============================")
		exit()
	elif contribute == None:
		print_usage("No contribution score provided.\n==============================")
		exit()
	elif name == None:
		print_usage("No student name provided.\n==============================")
		exit()
	
	# Validate general and contribute score
	try:
		general = int(general)
		contribute = int(contribute)
		
		# Check if the values are within the valid range
		if general < 0 or general > 5:
			print_usage("General score must be between 0 and 5.\n==============================")
			exit()
		if contribute < 0 or contribute >5:
			print_usage("Contribution score must be between 0 and 5.\n==============================")
			exit()
	except ValueError:
		print_usage("Scores must be integers.\n==============================")
		exit()
	
	
	else:
		return general, contribute, name


def get_comment(level, comments):
	'''Generate comment base on level
	'''
	return random.choice(comments.get(level, ["No comment available."]))


def generate_comment_as_file(name, overall_comment):
	
	# Replace any space with underscope in file naming
	file_name = f"{name.replace(' ', '_')}_comment.txt"
	
	# Create the folder if it does't exist
	os.makedirs(COMMENT_DIR, exist_ok=True)
	
	full_path = os.path.join(COMMENT_DIR, file_name)
	with open(full_path, "w") as file:
		file.write(overall_comment)


##############################################
############## MAIN APPLICATION ##############
##############################################
	
general, contribute, name = check_arguments()


# Construct the overall comment
overall_comment = 'General comments\n' + name + ' ' + get_comment(general, general_comments) + '\n\nLearner Punctuality and engagement\n'+ name + ' ' + get_comment(contribute, contribute_engagement_comments) + '\n\nRecommendations on further learning\n'+ get_comment(general, python_learning_recommendations)

generate_comment_as_file(name, overall_comment)

print("The overall comment has successfully been generated for student " + name + "\n\nThe overall comment:\n" + overall_comment + "\n\nThe file is in " + str(COMMENT_DIR))