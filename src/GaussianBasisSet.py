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

import re
from UserDict import UserDict

from Atom import *
from ContractedGaussian import *
from ParserTextBlock import *

class GaussianBasisSet( UserDict ):
	
	CRYSTAL=0
	MOLPRO=1
	GAMESS=2
	
	def __init__( this ):
		UserDict.__init__( this )
		
	def __str__( this ):
		output = ""
		
		for key,value in this.items():
			output += "%3s\n" % key
			output += "-"*6 + "\n"
			
			for contraction in value:
				output += contraction.sType + "\n"
				
				for i in range(contraction.size()):
					output += "%15.10f" % contraction.primitives[i].exponent
					output += "%15.10f" % contraction.coefficients[i]
					output += "\n"
					
			output += "\n"
			
		return output[:-1]
		
	def load( this, inputFileName, format=CRYSTAL ):
		
		fileContent = open( inputFileName, "r" ).read()
		
		if( format == GaussianBasisSet.CRYSTAL ):
			__loadFromCystalFormat( fileContent )
		elif( format == GaussianBasisSet.MOLPRO ):
			__loadFromMoldenFormat( fileContent )
		else:
			print "## Error ## Basis set function in unknown format"
			
	def loadFromTextBlock( this, textBlock, format=CRYSTAL ):
		if( format == GaussianBasisSet.CRYSTAL ):
			this.__loadFromCystalFormat( textBlock )
		elif( format == GaussianBasisSet.GAMESS ):
			this.__loadFromGAMESSFormat( textBlock )
		elif( format == GaussianBasisSet.MOLPRO ):
			this.__loadFromMoldenFormat( textBlock )
		else:
			print "## Error ## Basis set function in unknown format"
		
	def __loadFromCystalFormat( this, textBlock ):
		
		lines = textBlock.content.splitlines()
		
		nLine = 0
		while( nLine < len(lines) ):
			tokens = lines[nLine].split()
			nLine += 1
			
			atomicNumber = int(tokens[0])
			label=""
			
			if( atomicNumber < 100 ):
				label = Atom.atomicNumberToLabel( atomicNumber )
			else:
				label = Atom.atomicNumberToLabel( atomicNumber%100 )
				label += str(int(atomicNumber/100))

			nContracted = int(tokens[1])
			
			currentBasis = []
			
			sType = 0
			nPrimitives = 0
			
			for i in range( 0, nContracted ):
				tokens = lines[nLine].split()
				nLine += 1
				
				sType = int(tokens[1])
				nPrimitives = int(tokens[2])
				
				if( sType == 0 ):
					currentBasis.append( ContractedGaussian( sType="S" ) )
				elif( sType == 1 ):
					currentBasis.append( ContractedGaussian( sType="S" ) )
					currentBasis.append( ContractedGaussian( sType="P" ) )
				elif( sType == 2 ):
					currentBasis.append( ContractedGaussian( sType="P" ) )
				elif( sType == 3 ):
					currentBasis.append( ContractedGaussian( sType="D" ) )
				elif( sType == 4 ):
					currentBasis.append( ContractedGaussian( sType="F" ) )
					
				for j in range( 0, nPrimitives ):
					tokens = lines[nLine].split()
					nLine += 1
					
					exponent = float(tokens[0])
					coefficient = float(tokens[1])
					
					gauss = PrimitiveGaussian( exponent=exponent )
					
					if( sType != 1 ):
						currentBasis[-1].append( coefficient, gauss )
					else:
						coefficient2 = float(tokens[2])
						
						currentBasis[-2].append( coefficient, gauss )
						currentBasis[-1].append( coefficient2, gauss )
						
				this[label] = currentBasis
				
		
	def __loadFromGAMESSFormat( this, textBlock ):
		
		lines = textBlock.content.splitlines()
		
		label = textBlock.header.replace( "$", "" )
		
		nContracted = 0
		nLine = 0
		while( nLine < len(lines) ):
			tokens = lines[nLine].split()
			nLine += 1
			
			if ( re.match( "^[A-Za-z]$", tokens[0] ) ):
				nContracted += 1
				
		nLine = 0
		while( nLine < len(lines) ):
			currentBasis = []
			
			sType = ""
			nPrimitives = 0
			
			for i in range( 0, nContracted ):
				tokens = lines[nLine].split()
				
				sType = tokens[0]
				nPrimitives = int(tokens[1])
				
				nLine += 1
				
				if( sType == "S" ):
					currentBasis.append( ContractedGaussian( sType="S" ) )
				elif( sType == "L" ):
					currentBasis.append( ContractedGaussian( sType="S" ) )
					currentBasis.append( ContractedGaussian( sType="P" ) )
				elif( sType == "P" ):
					currentBasis.append( ContractedGaussian( sType="P" ) )
				elif( sType == "D" ):
					currentBasis.append( ContractedGaussian( sType="D" ) )
				elif( sType == "F" ):
					currentBasis.append( ContractedGaussian( sType="F" ) )
					
				for j in range( 0, nPrimitives ):
					tokens = lines[nLine].split()
					nLine += 1
					
					exponent = float(tokens[1].replace("D","E"))
					coefficient = float(tokens[2].replace("D","E"))
					
					gauss = PrimitiveGaussian( exponent=exponent )
					
					if( sType != "L" ):
						currentBasis[-1].append( coefficient, gauss )
					else:
						coefficient2 = float(tokens[3].replace("D","E"))
						
						currentBasis[-2].append( coefficient, gauss )
						currentBasis[-1].append( coefficient2, gauss )
						
				this[label] = currentBasis
		
	def __loadFromMoldenFormat( this, textBlock ):
		pass
	
	def save( this, outputFileName=None, format=MOLPRO ):
		output =""
		
		output += "basis={\n"
		
		for label,currentBasis in this.items():
			labelNew = label[0]
			
			for i in range(1,len(label)):
				labelNew += label[i].lower()
			
			output += "\t"
			output += "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
			output += "\t! " + labelNew + "\n"
			
			for contracted in currentBasis:
				#output += "%10.7f" % contracted.constant + "\n"
				output += "\t"
				output += contracted.sType.lower() + "  " + labelNew
				
				for primitive in contracted.primitives:
					output += "  " + "%10.7f" % primitive.exponent
					
				output += "\n"
				output += "\t"
				output += "c  1."+ str(contracted.size())
					
				for coefficient in contracted.coefficients:
					output += "  " + "%10.7f" % coefficient
					
				output += "\n"
				
		output += "}"
		
		return output
		
	@staticmethod
	def test():
		gbs = GaussianBasisSet()
		
		heliumBasis = []
		
		contracted1 = ContractedGaussian( sType="S" )
		
		gauss1 = PrimitiveGaussian( exponent=0.1 )
		gauss2 = PrimitiveGaussian( exponent=0.2 )
		gauss3 = PrimitiveGaussian( exponent=0.3 )
		
		contracted1.append( 0.4, copy(gauss1) )
		contracted1.append( 0.1, copy(gauss2) )
		contracted1.append( 0.3, copy(gauss3) )
		
		heliumBasis.append( contracted1 )
		
		contracted2 = ContractedGaussian( sType="P" )
		
		gauss1 = PrimitiveGaussian( exponent=0.5 )
		gauss2 = PrimitiveGaussian( exponent=0.4 )
		gauss3 = PrimitiveGaussian( exponent=0.3 )
		
		contracted2.append( 0.2, copy(gauss1) )
		contracted2.append( 0.6, copy(gauss2) )
		contracted2.append( 0.8, copy(gauss3) )
		
		heliumBasis.append( contracted2 )
		
		gbs["He"] = heliumBasis
		
		print ""
		print gbs
		
		