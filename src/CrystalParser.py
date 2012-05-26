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
from Crystal import *

class CrystalParser( ParserTextBlock ):
	
	# Supported files type
	INPUT=1
	OUTPUT=1
	D12=2
	GUI=3
	
	# Specific flags for OUTPUT file type
	ALL_ATOMS=0
	IRREDUCIBLE_ATOMS=1
	
	###
	# 
	##
	def __init__( this, inputFile="" ):
		
		ParserTextBlock.__init__( this, inputFile )
		
		# variables for output type format
		this.__atomsType = CrystalParser.ALL_ATOMS
		this.format = CrystalParser.OUTPUT
		this.version = "CRYSTAL09"
		this.__crystal = Crystal()
		
	###
	# 
	##
	def load( this, pos=-1 ):
		del this.__crystal[:]
		
		if( this.format == CrystalParser.OUTPUT ):
			this.__loadOutput( pos )
		elif( this.format == CrystalParser.D12 ):
			this.loadD12()
		elif( this.format == CrystalParser.GUI ):
			this.__loadGUI()
			
		return this.__crystal
	###
	# 
	##
	def setFlags( this, atomsType ):
		if( atomsType == CrystalParser.ALL_ATOMS or atomsType == CrystalParser.IRREDUCIBLE_ATOMS ):
			this.__atomsType = atomsType
		else:
			print "@@@ Warning @@@: in def setFlags(atomsType=",atomsType,")"
			print "                 Wrong value"
			print "                 the possible values are ALL_ATOMS(0) or IRREDUCIBLE_ATOMS(1)"
		
	###
	# 
	##
	def __loadOutput( this, pos=-1 ):
		
		this.__crystal = Crystal()
		
		this.extractLine( contains=".*CRYSTAL0\d.*", pos=1 )
		this.version = this.getBlock().getColumn(2)
		
		#print this.extractBlock( "^\s.*STARTING  DATE.*$", "^\s+$" )
		#latticeParameters = TextBlock.toArray( this.getBlock().getRow(1) )
		
		this.extractBlock( "^\sLATTICE PARAMETERS.*BOHR", "^\s[*]{20,}$", "^\s+\d+[.]\d+.*", pos )
		latticeParameters = TextBlock.toArray( this.getBlock().getRow(1) )
		
		# Esto es temporal, hay que ver en que parte se adiciona la infomación
		# de los ángulos de la celda unidad
		this.__crystal.latticeVectors[0,0] = latticeParameters[0]
		this.__crystal.latticeVectors[1,1] = latticeParameters[1]
		this.__crystal.latticeVectors[2,2] = latticeParameters[2]
		
		#this.extractBlock( "^\sATOMS IN THE ASYMMETRIC UNIT.*", "^[\s]*$", "^[\s]{2,}[\d]+[\s]T.*", pos )
		#idsOfRealAtoms = TextBlock.toArray( this.getBlock().getColumn(1), dtype='i' )
		
		this.extractBlock( "^\sATOMS IN THE ASYMMETRIC UNIT.*", "^\s*$", "^\s*\d+.*", pos )
		labels = TextBlock.toArray( this.getBlock().getColumn( 4 ), dtype='a' )
		isReal = TextBlock.toArray( this.getBlock().getColumn( 2 ), dtype='a' )
		xPosition = TextBlock.toArray( this.getBlock().getColumn( 5 ), dtype='f' )
		yPosition = TextBlock.toArray( this.getBlock().getColumn( 6 ), dtype='f' )
		zPosition = TextBlock.toArray( this.getBlock().getColumn( 7 ), dtype='f' )
		
		if( len(this.extractBlock( "^\sTOTAL ATOMIC CHARGES:$", "^\s[T]{29,29}.*" )) != 0 ):
			charges = TextBlock.toArray( this.getBlock() )
		else:
			charges = []
		
		for n in range(0,len(labels)):
			
			if( this.__atomsType == CrystalParser.IRREDUCIBLE_ATOMS ):
				if( isReal[n] == "T" ):
					lab = labels[n]
					x = xPosition[n]*latticeParameters[0]
					y = yPosition[n]*latticeParameters[1]

					if( latticeParameters[2] != 500.0 ):
						z = zPosition[n]*latticeParameters[2]
					else:
						z = zPosition[n]
					
					if( len(charges) == len(labels) ):
						q = Atom.labelToAtomicNumber(lab)-charges[n]
					else:
						q = 0.0
						
					this.__crystal.append( Atom( x, y, z, charge=q, label=lab ) )
						
			elif( this.__atomsType == CrystalParser.ALL_ATOMS ):
				
				lab = labels[n]
				x = xPosition[n]*latticeParameters[0]
				y = yPosition[n]*latticeParameters[1]
				
				if( latticeParameters[2] != 500.0 ):
					z = zPosition[n]*latticeParameters[2]
				else:
					z = zPosition[n]
				
				if( len(charges) == len(labels) ):
					q = Atom.labelToAtomicNumber(lab)-charges[n]
				else:
					q = 0.0
					
				if( isReal[n] == "T" ):
					this.__crystal.append( Atom( x, y, z, charge=q, label=lab, real=True ) )
				else:
					this.__crystal.append( Atom( x, y, z, charge=q, label=lab, real=False ) )
				
		if( this.version == "CRYSTAL06" ):
			this.extractBlock( ".*SYMMOPS - TRANSLATORS IN FRACTIONARY UNITS.*", "(^\s*$|^\sT{29,}.*$)", "^\s+\d+\s+\d+.*$" )
			this.getBlock().removeColumns( [1,2] )
		elif( this.version == "CRYSTAL09" ):
			this.extractBlock( ".*SYMMOPS - TRANSLATORS IN FRACTIONAL UNITS.*", "(^\s*$|^\sT{29,}.*$)", "^\s+\d+\s+\d+.*$" )
			this.getBlock().removeColumns( [1,2] )
		
		for i in range(1,this.getBlock().nRows+1):
			sym = numpy.fromstring( this.getBlock().getRow( i ), sep=' ', dtype='f' )
			sym.shape = (4,3)
			this.__crystal.addSymetryOperator( SymmetryOperator( sym ), apply=False )
		
	###
	# @warning no tiene implementado la contruccion de la supercelda leyendola desde el .gui
	##
	def __loadGUI( this ):
		
		this.__crystal = Crystal()
		
		# Se extraen los parametros de la celda
		latticeParams = TextBlock.toMatrix( this.extractBlock( "^\s+\d+\s+\d+\s+\d+\s+E.*DE.*$", "^\s+\d+\s*$" ) )
		this.__crystal.setLatticeVectors( latticeParams )
			
		# Se extraen las posiciones de los atomos irreducibles
		this.extractBlock( "^\s+\d+\s*$" )
		nAtoms = int(this.getBlock().header)
			
		atomicNumber = TextBlock.toArray( this.getBlock().getColumn( 1 ), dtype='i' )
		xPosition = TextBlock.toArray( this.getBlock().getColumn( 2 ) )
		yPosition = TextBlock.toArray( this.getBlock().getColumn( 3 ) )
		zPosition = TextBlock.toArray( this.getBlock().getColumn( 4 ) )
		
		for n in range(0, nAtoms):
			this.__crystal.append( Atom( xPosition[n], yPosition[n], zPosition[n], atomicNumber=atomicNumber[n] ) )
			
		# Se extraen los operadores de simetria
		this.extractBlock( "^\s+\d+\s*$", "^\s+\d+\s*$" )
		
		nOperators = int(this.getBlock().header)
			
		for i in range(0, nOperators):
			sym = SymmetryOperator( TextBlock.toMatrix( this.getBlock().getRows( range(4*i+1, 4*i+5) ) ) )
			this.__crystal.addSymetryOperator( sym, apply=False )
			
		this.__crystal.applySymmetry()
			
	###
	# 
	##
	@staticmethod
	def test():
		PIAMOD_HOME = os.getenv("PIAMOD_HOME")
		
		parser = CrystalParser() ;
		crystal = Crystal() ;
		
		print ""
		print "Loading data from CRYSTAL_OUTPUT file"
		print "====================================="
		print ""
		parser.inputFile = PIAMOD_HOME+"/src/data/formats/CRYSTAL_OUTPUT"
		parser.format = CrystalParser.OUTPUT
		
		print ""
		print "Loading all atoms"
		print "-----------------"
		print ""
		parser.setFlags( atomsType=CrystalParser.ALL_ATOMS )
		crystal = parser.load()
		crystal.save("crystal.xyz")
		print crystal
		
		print ""
		print "Loading only real atoms"
		print "-----------------------"
		print ""
		parser.setFlags( atomsType=CrystalParser.IRREDUCIBLE_ATOMS )
		parser.format = CrystalParser.OUTPUT
		crystal = parser.load()
		print crystal
		
		print ""
		print "Loading data from CRYSTAL_GUI file"
		print "=================================="
		print ""
		
		parser.inputFile = PIAMOD_HOME+"/src/data/formats/CRYSTAL_GUI"
		parser.format = CrystalParser.GUI
		crystal = parser.load()
		print crystal
		
