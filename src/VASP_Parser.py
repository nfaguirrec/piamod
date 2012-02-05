# -*- coding: utf-8 -*-
############################################################################
#    Copyright (C) 2012 by Nestor Aguirre                                  #
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

class VASP_Parser( ParserTextBlock ):
	
	# Supported files type
	POSCAR=1
	
	# Specific flags for OUTPUT file type
	#ALL_ATOMS=0
	#IRREDUCIBLE_ATOMS=1
	
	###
	# 
	##
	def __init__( this, inputFile="" ):
		
		ParserTextBlock.__init__( this, inputFile )
		
		# variables for output type format
		#this.__atomsType = VASP_Parser.ALL_ATOMS
		this.__crystal = Crystal()
		
	###
	# 
	##
	def load( this, format=POSCAR ):
		del this.__crystal[:]
		
		if( format == VASP_Parser.POSCAR ):
			this.__loadPOSCAR()
			
		return this.__crystal
	###
	# 
	##
	#def setFlags( this, atomsType ):
		#if( atomsType == VASP_Parser.ALL_ATOMS or atomsType == VASP_Parser.IRREDUCIBLE_ATOMS ):
			#this.__atomsType = atomsType
		#else:
			#print "@@@ Warning @@@: in def setFlags(atomsType=",atomsType,")"
			#print "                 Wrong value"
			#print "                 the possible values are ALL_ATOMS(0) or IRREDUCIBLE_ATOMS(1)"
		
	###
	# 
	##
	def __loadPOSCAR( this ):
		
		this.__crystal = Crystal()
		
		this.extractLine( pos=1 )
		title = this.getBlock().content
		this.__crystal.name = title
		
		# Load the lattice vectors
		latticeConstant = float( this.extractLine( pos=2 ).content )
		
		latticeVectorsBlk = TextBlock( \
					this.extractLine( pos=3 ).content+"\n"+ \
					this.extractLine( pos=4 ).content+"\n"+ \
					this.extractLine( pos=5 ).content \
				 )
				 
		latticeVectors = latticeConstant*TextBlock.toMatrix( latticeVectorsBlk )
		this.__crystal.latticeVectors = latticeVectors
		
		labels = this.extractLine( pos=6 ).content.split()
		nAtomsByLabel = TextBlock.toArray( this.extractLine( pos=7 ), dtype='i' )
		
		# Check if selective dynamics is switched on
		sdyn = ( this.extractLine( pos=8 ).content == "Selective dynamics" )
		
		# Check if atom coordinates are cartesian or direct
		directCoordinates = ( this.extractLine( pos=9 ).content == "Direct" )
		
		print "nAtomsByLabel = ", nAtomsByLabel
		counterLabel = 0
		currentLabel = labels[0]
		for n in range( 0, sum(nAtomsByLabel) ):
			tokens = this.extractLine( pos=10+n ).content.split()
			
			x = float(tokens[0])*latticeVectors[0,0]
			y = float(tokens[1])*latticeVectors[1,1]
			z = float(tokens[2])*latticeVectors[2,2]
			
			if( n >= sum(nAtomsByLabel[0:min(counterLabel+1,len(nAtomsByLabel))]) ):
				counterLabel += 1
			
			this.__crystal.append( Atom( x, y, z, charge=0.0, label=labels[counterLabel] ) )
		
		##this.extractBlock( "^\sATOMS IN THE ASYMMETRIC UNIT.*", "^[\s]*$", "^[\s]{2,}[\d]+[\s]T.*", pos )
		##idsOfRealAtoms = TextBlock.toArray( this.getBlock().getColumn(1), dtype='i' )
		
		#this.extractBlock( "^\sATOMS IN THE ASYMMETRIC UNIT.*", "^\s*$", "^\s+\d+.*", pos )
		#labels = TextBlock.toArray( this.getBlock().getColumn( 4 ), dtype='a' )
		#isReal = TextBlock.toArray( this.getBlock().getColumn( 2 ), dtype='a' )
		#xPosition = TextBlock.toArray( this.getBlock().getColumn( 5 ), dtype='f' )
		#yPosition = TextBlock.toArray( this.getBlock().getColumn( 6 ), dtype='f' )
		#zPosition = TextBlock.toArray( this.getBlock().getColumn( 7 ), dtype='f' )
		
		#if( len(this.extractBlock( "^\sTOTAL ATOMIC CHARGES:$", "^\s[T]{29,29}.*" )) != 0 ):
			#charges = TextBlock.toArray( this.getBlock() )
		#else:
			#charges = []
		
		#for n in range(0,len(labels)):
			
			#if( this.__atomsType == VASP_Parser.IRREDUCIBLE_ATOMS ):
				#if( isReal[n] == "T" ):
					#lab = labels[n]
					#x = xPosition[n]*latticeParameters[0]
					#y = yPosition[n]*latticeParameters[1]

					#if( latticeParameters[2] != 500.0 ):
						#z = zPosition[n]*latticeParameters[2]
					#else:
						#z = zPosition[n]
					
					#if( len(charges) == len(labels) ):
						#q = Atom.labelToAtomicNumber(lab)-charges[n]
					#else:
						#q = 0.0
						
					#this.__crystal.append( Atom( x, y, z, charge=q, label=lab ) )
						
			#elif( this.__atomsType == VASP_Parser.ALL_ATOMS ):
				
				#lab = labels[n]
				#x = xPosition[n]*latticeParameters[0]
				#y = yPosition[n]*latticeParameters[1]
				
				#if( latticeParameters[2] != 500.0 ):
					#z = zPosition[n]*latticeParameters[2]
				#else:
					#z = zPosition[n]
				
				#if( len(charges) == len(labels) ):
					#q = Atom.labelToAtomicNumber(lab)-charges[n]
				#else:
					#q = 0.0
					
				#if( isReal[n] == "T" ):
					#this.__crystal.append( Atom( x, y, z, charge=q, label=lab, real=True ) )
				#else:
					#this.__crystal.append( Atom( x, y, z, charge=q, label=lab, real=False ) )
				
		#if( this.version == "CRYSTAL06" ):
			#this.extractBlock( ".*SYMMOPS - TRANSLATORS IN FRACTIONARY UNITS.*", "(^\s*$|^\sT{29,}.*$)", "^\s+\d+\s+\d+.*$" )
			#this.getBlock().removeColumns( [1,2] )
		#elif( this.version == "CRYSTAL09" ):
			#this.extractBlock( ".*SYMMOPS - TRANSLATORS IN FRACTIONAL UNITS.*", "(^\s*$|^\sT{29,}.*$)", "^\s+\d+\s+\d+.*$" )
			#this.getBlock().removeColumns( [1,2] )
		
		#for i in range(1,this.getBlock().nRows+1):
			#sym = numpy.fromstring( this.getBlock().getRow( i ), sep=' ', dtype='f' )
			#sym.shape = (4,3)
			#this.__crystal.addSymetryOperator( SymmetryOperator( sym ), apply=False )
		
	####
	## @warning no tiene implementado la contruccion de la supercelda leyendola desde el .gui
	###
	#def __loadGUI( this ):
		
		#this.__crystal = Crystal()
		
		## Se extraen los parametros de la celda
		#latticeParams = TextBlock.toMatrix( this.extractBlock( "^\s+\d+\s+\d+\s+\d+\s+E.*DE.*$", "^\s+\d+\s*$" ) )
		#this.__crystal.setLatticeVectors( latticeParams )
			
		## Se extraen las posiciones de los atomos irreducibles
		#this.extractBlock( "^\s+\d+\s*$" )
		#nAtoms = int(this.getBlock().header)
			
		#atomicNumber = TextBlock.toArray( this.getBlock().getColumn( 1 ), dtype='i' )
		#xPosition = TextBlock.toArray( this.getBlock().getColumn( 2 ) )
		#yPosition = TextBlock.toArray( this.getBlock().getColumn( 3 ) )
		#zPosition = TextBlock.toArray( this.getBlock().getColumn( 4 ) )
		
		#for n in range(0, nAtoms):
			#this.__crystal.append( Atom( xPosition[n], yPosition[n], zPosition[n], atomicNumber=atomicNumber[n] ) )
			
		## Se extraen los operadores de simetria
		#this.extractBlock( "^\s+\d+\s*$", "^\s+\d+\s*$" )
		
		#nOperators = int(this.getBlock().header)
			
		#for i in range(0, nOperators):
			#sym = SymmetryOperator( TextBlock.toMatrix( this.getBlock().getRows( range(4*i+1, 4*i+5) ) ) )
			#this.__crystal.addSymetryOperator( sym, apply=False )
			
		#this.__crystal.applySymmetry()
			
	###
	# 
	##
	@staticmethod
	def test():
		PIAMOD_HOME = os.getenv("PIAMOD_HOME")
		
		parser = VASP_Parser() ;
		crystal = Crystal() ;
		
		print ""
		print "Loading data from VASP POSCAR file"
		print "=================================="
		print ""
		parser.inputFile = PIAMOD_HOME+"/src/data/formats/VASP_POSCAR"
		crystal = parser.load( format=VASP_Parser.POSCAR )
		print crystal
		print crystal.chemicalFormula()
		crystal.save("salida.xyz")
		
