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

from ParserTextBlock import *
from Molecule import *

class MolproParser( ParserTextBlock ):
	
	# Supported files type
	INPUT=0
	OUTPUT=1
	
	###
	# 
	##
	def __init__( this, inputFile="" ):
		
		ParserTextBlock.__init__( this, inputFile )
		
		# variables for output type format
		this.format = MolproParser.OUTPUT
		this.version = "2009.1"
		this.__molecule = Molecule()
		
	###
	# 
	##
	def load( this ):
		del this.__molecule[:]
		
		if( this.format == MolproParser.INPUT ):
			this.__loadInput()
		elif( this.format == MolproParser.OUTPUT ):
			this.__loadOutput()
			
		return this.__molecule
		
	###
	# 
	##
	def __loadInput( this ):
		pass
		
	###
	# 
	##
	def __loadOutput( this ):
		
		this.__molecule = Molecule()
		
		this.extractLine( contains=".*Version .* linked.*", pos=1 )
		this.version = this.getBlock().getColumn(2)
		
		this.extractLine( contains=".*LABEL \*.*", pos=1 )
		this.__molecule.name = this.getBlock().content[11:]
		
		this.extractBlock( ".*ATOMIC COORDINATES.*", ".*Bond lengths.*", ".*\s+\d+\s+[A-Z,a-z]{1,2}\d{0,1}.\d{0,1}.*" )
		labels = TextBlock.toArray( this.getBlock().getColumn( 2 ), dtype='a' )
		xPosition = TextBlock.toArray( this.getBlock().getColumn( 4 ), dtype='f' )
		yPosition = TextBlock.toArray( this.getBlock().getColumn( 5 ), dtype='f' )
		zPosition = TextBlock.toArray( this.getBlock().getColumn( 6 ), dtype='f' )
		
		#this.extractBlock( "^\sTOTAL ATOMIC CHARGES:$", "^\s[T]{29,29}.*" )
		#charges = TextBlock.toArray( this.getBlock() )
		charges = []
		
		# Esta linea sirve para extrer energías de orbitales, sin haber utilizado la opción ORBPRINT
		#this.extractBlock( ".*Orbital energies:.*", ".*[*]{10,}.*", "\s+[-]{0,1}\d+.\d{3,}\s+" )
		#this.__molecule.orbitalEnergies = TextBlock.toArray( this.getBlock() )
		
		this.extractBlock( ".*ELECTRON ORBITALS.*", ".*[*]{10,}.*", "\s+\d+.\d{0,3}\s+\d\s+" )
		this.__molecule.orbitalEnergies = sorted( TextBlock.toArray( this.getBlock().getColumn(3) ) )
		
		for n in range(0,len(labels)):
			
			if( len(charges) == len(labels) ):
				q = charges[n]
			else:
				q = 0.0
				
			this.__molecule.append( Atom( xPosition[n], yPosition[n], zPosition[n], charge=q, label=labels[n] ) )
			
	###
	# 
	##
	@staticmethod
	def test():
		parser = MolproParser() ;
		molecule = Molecule() ;
		
		print ""
		print "Loading data from MOLPRO_OUTPUT file"
		print "====================================="
		print ""
		
		parser.inputFile = "src/data/formats/MOLPRO_OUTPUT"
		parser.format = MolproParser.OUTPUT
		
		print ""
		print "Loading Molecule"
		print "----------------"
		print ""
		molecule = parser.load()
		print molecule
		
		