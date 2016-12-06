# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import gensim, logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    
class my_model(object):

	def __init__(self, dirName):		
		self.dirName = dirName
		
   	def init_model(self):
		self.model = gensim.models.Word2Vec.load_word2vec_format(self.dirName, binary=True, unicode_errors='ignore')
		return self.model

