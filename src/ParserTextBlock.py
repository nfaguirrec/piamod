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

from TextBlock import *

class ParserTextBlock:
	
	EOF="EOF$$"
	
	###
	# Constructor
	##
	def __init__( this, inputFile="" ):
		this.inputFile = inputFile
		this.numberOfBlocks=-1
		this.__principalBlock=TextBlock()
		this.__currentBlock=TextBlock()
		
	###
	# Return the block number "pos" (-1 for the last), that your begin
	# matched with the regular expression "begin" and the end matched with
	# the regular expression "end", besides filetering the content with
	# the regular expression "lineFilter". This function load the block
	# from file and save this in this.__principalBlock
	##
	def extractBlock( this, begin, end=EOF, lineFilter=".*", pos=-1 ):
		
		inputFile = file( this.inputFile, "r" )
		fileContent = inputFile.read()
		inputFile.close()
		
		(this.__currentBlock, this.numberOfBlocks) = \
			this.getBlockFrom( fileContent, begin, end, lineFilter, pos )
		this.__principalBlock = this.__currentBlock
		
		return this.__principalBlock
		
	###
	# Return the line number "pos" (-1 for the last)
	##
	def extractLine( this, pos=-1, contains=None ):
		
		inputFile = file( this.inputFile, "r" )
		lines = inputFile.read().splitlines()
		inputFile.close()
		
		output = ""
		
		if( contains == None ):
			if( pos != -1 ):
				output = lines[pos-1]
			else:
				output = lines[-1]
			
		if( contains != None ):
			matchedLines = []
			
			for line in lines:
				if( re.match( contains, line ) ):
					matchedLines.append( line )
					
			this.numberOfBlocks = len(matchedLines)
			
			if( len(matchedLines) == 0 ):
				print "### Error ###, Not found lines that do match with ", contains
				return
			
			if( pos >= 1 ):
				output = matchedLines[pos-1]
			else:
				output = matchedLines[-1]
			
		this.__currentBlock = TextBlock( output )
		this.__principalBlock = this.__currentBlock
		
		return this.__principalBlock
	
	###
	# Igual que extractBlock pero realiza todas las operaciones sobre this.__principalBlock
	# sin modificarlas y almacenandolas en this.__currentBlock
	##
	def getBlock( this, begin=None, end=None, lineFilter=".*", pos=-1 ):
		
		if( len(this.__principalBlock.content) != 0 ):
			if( begin != None and end != None ):
				(this.__currentBlock, this.numberOfBlocks) = \
					this.getBlockFrom( this.__principalBlock.content, begin, end, lineFilter, pos )
		else:
			print "### Error ###, You need call first extractBlock function"
			
		return this.__currentBlock
		
	###
	# Extract a block from the raw block "block", actualizando los atributos
	# __currentBlock, header, footer y numberOfBlocks, este ultimo solo
	# si la funcion se llama por primera vez sin una posicion (pos) definida
	##
	@staticmethod
	def getBlockFrom( text, begin, end=EOF, lineFilter=".*", pos=-1 ):
		locatedBegin=False
		locatedEnd=False
		
		previousBlock = ""
		previousHeader = ""
		previousFooter = ""
		
		selectedBlock = ""
		selectedHeader = ""
		footer = ""
		
		lines = text.splitlines()
		
		nBlock=0
		nLine=0
		for line in lines:
			
			if( locatedBegin==True ):
				
				if( end == ParserTextBlock.EOF and nLine+1 == len(lines) ):
					selectedBlock = selectedBlock+line
					
					footer = ""
						
					locatedBegin = False
					locatedEnd = True
						
					break
				
				elif( re.match( end, line ) ):
					# Esta linea lo que busca es quitar el ultimo
					# cambio de linea adicionado por el comando
					# selectedBlock = selectedBlock+line+"\n"
					# que esta mas abajo
					selectedBlock = selectedBlock[:-1]
					footer = line
					
					locatedBegin = False
					locatedEnd = True
					
					if( pos == nBlock  ):
						break
					else:
						nBlock += 1
				else:
					if( re.match( lineFilter, line ) ):
						selectedBlock = selectedBlock+line+"\n"
				
			if( re.match( begin, line ) ):
				locatedBegin = True
				locatedEnd = False
				previousBlock = selectedBlock
				previousHeader = selectedHeader
				selectedHeader = line
				selectedBlock = ""
				
			nLine += 1
			
		# Solo para el caso en que no se solicite una posicion especifica del bloque
		# se actualizara el numero de bloques
		if( pos == -1 ):
			numberOfBlocks = nBlock
		else:
			numberOfBlocks = -1
			
		if( locatedEnd ):
			return ( TextBlock(selectedBlock, selectedHeader, footer), numberOfBlocks )
		else:
			return ( TextBlock(previousBlock, previousHeader, footer), numberOfBlocks )
			
	@staticmethod
	def test():
		parser = ParserTextBlock()
		parser.inputFile = "src/data/formats/CRYSTAL_OUTPUT"
		
		print "Second line"
		print "==========="
		print parser.extractLine( 2 ).content+"\n"
		
		print "All Atoms"
		print "========="
		print parser.extractBlock( "^\sATOMS IN THE ASYMMETRIC UNIT.*", "^[\s]*$", "^[\s]{2,}[\d]+.*" )
		
		print "Real Atoms"
		print "=========="
		print parser.extractBlock( "^\sATOMS IN THE ASYMMETRIC UNIT.*", "^[\s]*$", "^[\s]{2,}[\d]+[\s]T.*" )
		
		print "Titanium Atoms"
		print "=============="
		print parser.extractBlock( "^\sATOMS IN THE ASYMMETRIC UNIT.*", "^[\s]*$", ".*22 TI.*" )
		
		print "Charges"
		print "======="
		print parser.extractBlock( ".*TOTAL ATOMIC CHARGES:.*", ".*T{30,30}.*" )
		
		print "Column 4 to matrix"
		print "=================="
		print TextBlock.toMatrix( parser.getBlock().getColumn(4) )
		
		print "Row 2 to matrix"
		print "==============="
		print TextBlock.toMatrix( parser.getBlock().getRow(2) )
		
		print "All to array"
		print "============"
		print TextBlock.toArray( parser.getBlock() )
		
		print "All to matrix"
		print "============="
		print "Is necessary to remove the last row for it to be square,"
		parser.getBlock().removeRow(10)
		print parser.getBlock()
		print "To Matrix,"
		print TextBlock.toMatrix( parser.getBlock() )
		
		print "Columns 2,5, and 6 to matrix"
		print "============================"
		print TextBlock.toMatrix( parser.getBlock().getColumns([2,5,6]) )
		
		print "Rows 4,6 to matrix"
		print "=================="
		print TextBlock.toMatrix( parser.getBlock().getRows([4,6]) )
		
		print "SCF history block"
		print "================="
		parser.extractBlock( ".*ATOMIC WAVEFUNCTION.*", ".*SCF ENDED - CONVERGENCE.*", "^\sCYC.*" )
		x=TextBlock.toArray( parser.getBlock().getColumn(4) )
		print x
		#import matplotlib.pyplot as plt
		#plt.plot( x[10:], 'bo-' )
		#plt.show()
		#import Gnuplot
		#gp = Gnuplot.Gnuplot(persist = 0)
		#plot1 = Gnuplot.PlotItems.Data( x[10:], with_="linespoints 1 6", title="HF-SCF CONVERGENCE" )
		#gp.plot( plot1 )
		
		print "Column 2 and 4 to matrix"
		print "======================="
		print TextBlock.toMatrix( parser.getBlock().getColumns([2,4]) )
		
		
		parser.inputFile = "src/data/formats/CRYSTAL_OPTGEOM_OUTPUT"
		
		print "OPT history block, with real atoms"
		print "=================================="
		parser.extractBlock( ".*STARTING GEOMETRY OPTIMIZATION.*", ".*OPT END.*" )
		print "Cycle 0"
		parser.getBlock( ".*ATOMS IN THE ASYMMETRIC UNIT.*", "^[\s]*$", "^[\s]{2,}[\d]+[\s]T.*", 0 )
		print parser.getBlock().getColumns([4,5,6,7])
		print "Last Cycle"
		parser.getBlock( ".*ATOMS IN THE ASYMMETRIC UNIT.*", "^[\s]*$", "^[\s]{2,}[\d]+[\s]T.*", -1 )
		print parser.getBlock().getColumns([4,5,6,7])
		
		
