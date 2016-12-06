# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import json
import re
import unicodedata
import numpy as np
import operator
from my_model import my_model

import sys, getopt

__author__ = 'semantics_lab'

def mention_link_similarity(kb_graph_model, anchor_model, entity, surface_words, base_words, number_of_max_links):
	
	entity = entity.decode('utf8')
	
	# var
	total_similarity = np.dtype(float)
	total_similarity = 0.0

			
	if entity not in kb_graph_model.vocab:
		return total_similarity
	
	
	# get entity link from tuple 
	mention_links, mention_similarities = zip(*kb_graph_model.similar_by_word(entity, number_of_max_links))	
	
	
	# calculate entity link similarity 
	for n in range(0, len(mention_links)):

		try:
			surface_words_sim = np.dtype(float)
			base_words_sim = np.dtype(float)
			 
			surface_words_sim = 0.0
			base_words_sim = 0.0

			
			for m in range(0, len(surface_words)):
				if mention_links[n] in anchor_model.vocab and surface_words[m] in anchor_model.vocab:
					surface_words_sim = surface_words_sim + anchor_model.similarity(mention_links[n], surface_words[m])
			
			for m in range(0, len(base_words)):
				if mention_links[n] in anchor_model.vocab and base_words[m] in anchor_model.vocab:
					base_words_sim = base_words_sim +  anchor_model.similarity(mention_links[n], base_words[m])   	
			
			
			total_similarity = total_similarity + surface_words_sim + base_words_sim
		
		except ValueError:
			print "Oops!  That was no valid number.  Try again..."	
			
	
	return total_similarity		
	#return len(mention_links), total_similarity		


def mention_similarity(mention, babel_entity_file, surface_words, base_words, number_of_max_links):
			
	# instanciate anchorContext model 
	anchor_model_object = my_model('./jp_anchor_vec.bin')
	anchor_model = anchor_model_object.init_model()

	# instantiate kbGraph model	
	kb_graph_object = my_model('./jp_graph_vec.bin')
	kb_graph_model = kb_graph_object.init_model()

	
	# read babelnet entities 
	entity_in_babelnet = []
	
	with open(babel_entity_file) as f:
	
		for line in f:
			entity_in_babelnet.append(line.strip())

	f.close()

	
	# the similarity 
	entity_wise_sim = {} 
	entity_wise_linked_sim = {}

	for n in range(0, len(entity_in_babelnet)):

		try:
			
			similarity_count_surface_words = np.dtype(float)
			similarity_count_base_words = np.dtype(float)

			similarity_count_surface_words = 0.0
			similarity_count_base_words = 0.0

			current_babel_entity = entity_in_babelnet[n].decode('utf8')				
			
			# calculate surface word similarity 
			for word in surface_words:
				if current_babel_entity in anchor_model.vocab and word in anchor_model.vocab:					
					similarity_count_surface_words = similarity_count_surface_words + anchor_model.similarity(current_babel_entity, word)
				
			# calculate base word similarity 		
			for word in base_words:
				if current_babel_entity in anchor_model.vocab and word in anchor_model.vocab:					
					similarity_count_base_words = similarity_count_base_words +  anchor_model.similarity(current_babel_entity, word)   	
					
					
			# similarity without considering links
			entity_wise_sim[entity_in_babelnet[n]] = similarity_count_surface_words + similarity_count_base_words
			
			# similarity considering links
			entity_wise_linked_sim[entity_in_babelnet[n]] = similarity_count_surface_words + similarity_count_base_words + mention_link_similarity(kb_graph_model, anchor_model, entity_in_babelnet[n], surface_words, base_words, number_of_max_links)
					

		except ValueError:
			print "Oops!  That was no valid number.  Try again..."	


	dict_sorted_entity_wise_sim = sorted(entity_wise_sim.items(), key=operator.itemgetter(1))
	dict_sorted_entity_wise_linked_sim = sorted(entity_wise_linked_sim.items(), key=operator.itemgetter(1))
	
	print "without considering links "
	for word_score in dict_sorted_entity_wise_sim:
		print word_score[0], "-", word_score[1]
			
	
	print "considering links "
	for word_score in dict_sorted_entity_wise_linked_sim:
		print word_score[0], "-", word_score[1]


m_word=''
i_sentence=''

try:
    myopts, args = getopt.getopt(sys.argv[1:],"m:s:")
except getopt.GetoptError as e:
    print (str(e))
    print("Usage: %s -m mention_word -s input_sentence" % sys.argv[0])
    sys.exit(2)
 
for o, a in myopts:
    if o == '-m':
        m_word=a
    elif o == '-s':
        i_sentence=a

		

#mention = "タイタニック"
mention = m_word

headers = {'Content-Type': 'application/json'}

##get babelNet entities

#url_babel_net = 'http://127.0.0.1:8080/EntityRecognition/entity/recognize'
#payload_babel_net = {'sentence': mention}
#r_babel_net = requests.post(url_babel_net, data=json.dumps(payload_babel_net), headers=headers)

#print r_babel_net

#json_output_babel_net = json.loads(r_babel_net.text)


# get SRL data

url = 'http://52.68.8.19:5000'

# POST with JSON
sentence = i_sentence


payload = {'text': sentence}
r = requests.post(url, data=json.dumps(payload), headers=headers)

# Response, status etc
json_output = json.loads(r.text)
#print json_output['sentences'][0]['sentence']

parsed_data = json_output["sentences"][0]["tokens"]

# capture surface words and base word from parser (e.g., SRL)
surface_words = []
base_words = []


for token in parsed_data:
    
	if (re.match("VERB", token["pos"])!=None) or (re.match("NOUN", token["pos"])!=None) or (re.match("PRONOUN", token["pos"])!=None):
		surface_words.append(token["surface"])
				
		try:
			base_words.append(token["base_form"])
			
		except KeyError:
			print "Oops!  Key Not Found.  Try again..."	


# capture BabelNet API for BabelNet entity 
babel_entity_dir = './babelTitanic_jp.txt'

# call similarity function
number_of_max_links = 100 # number of links that we want to consider
mention_similarity(mention, babel_entity_dir, surface_words, base_words, number_of_max_links)			
