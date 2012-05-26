# -*- coding: utf-8 -*-
############################################################################
#    Copyright (C) 2010 by Nestor Aguirre                                  #
#    nfaguirre@imaff.cfmac.csic.es                                         #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

import os
import sys
import atexit
#from optparse import OptionParser

from TextBlock import *
from ParserTextBlock import *
from CrystalParser import *
from VASP_Parser import *
from MolproParser import *
from PrimitiveGaussian import *
from ContractedGaussian import *
from GaussianBasisSet import *
from Atom import *
from Molecule import *
from Crystal import *
from QuantumMolecule import *
from SymmetryOperator import *

class PIAMoD:
	
	HISTORY_FILE = os.path.expanduser("~/.piamod_history")
	
	###
	# Actualiza el archivo history
	##
	def saveHistory( this ):
		try:
			import readline
			readline.write_history_file( PIAMoD.HISTORY_FILE )
		except ImportError:
			print "Module readline not available."
			
		del readline
		
	###
	# Lee el archivo history
	##
	def readHistory( this ):
		try:
			import readline
			if( os.path.exists( PIAMoD.HISTORY_FILE ) ):
				readline.read_history_file( PIAMoD.HISTORY_FILE )
		except ImportError:
			print "Module readline not available."
			
		del readline
		
	###
	# Carga el componente de completado de codigo
	##
	def loadCompleter( this ):
		try:
			import readline
			import rlcompleter
			readline.parse_and_bind("tab: complete")
		except ImportError:
			print "Module rlcompleter not available."
			
		del readline, rlcompleter
		
	###
	# Muestra el mensaje de bienvenida
	##
	def showWelcomeMessage( this ):
		print "==================================================="
		print "                 WELCOME TO PIAMOD"
		print "       System based on Python for Interactive"
		print "             Analysis of Molecular data"
		print ""
		print "         Author: Nestor Aguirre (2009-2011)"
		print ""
		print "      Departamento de Fisica Atomica Molecular"
		print "                y de Agregados (CSIC)"
		print "                    Madrid, Spain"
		print "==================================================="
		
	###
	# Principal function
	##
	@staticmethod
	def run():
		#parser = OptionParser()
		
		#parser.add_option(
			#"-i", "--ifile",
			#action="store", type="string", dest="inputFileName",
			#help="Crystal input filename", metavar="FILE"
		#)
		
		#parser.add_option(
			#"-o", "--ofile",
			#action="store", type="string", dest="outputFile", default="screen",
			#help="Write output data to FILE", metavar="FILE"
		#)
		
		#(options, args) = parser.parse_args()
		
		sys.ps1="piamod> "
		
		principal = PIAMoD()
		#principal.showWelcomeMessage()
		principal.loadCompleter()
		principal.readHistory()
		atexit.register( principal.saveHistory )
		
	###
	# Principal function
	##
	@staticmethod
	def runScript( scriptFileName ):
		#parser = OptionParser()
		
		#parser.add_option(
			#"-i", "--ifile",
			#action="store", type="string", dest="inputFileName",
			#help="Crystal input filename", metavar="FILE"
		#)
		
		#parser.add_option(
			#"-o", "--ofile",
			#action="store", type="string", dest="outputFile", default="screen",
			#help="Write output data to FILE", metavar="FILE"
		#)
		
		#(options, args) = parser.parse_args()
		
		sys.ps1="piamod> "
		
		principal = PIAMoD()
		#principal.showWelcomeMessage()
		#principal.loadCompleter()
		#principal.readHistory()
		#atexit.register( principal.saveHistory )
		
		if os.path.isfile( scriptFileName ):
			execfile( scriptFileName )
		