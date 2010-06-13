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

import numpy

class TextBlock:
	
	def __init__( this, content="", header="", footer="" ):
		this.header = header
		this.footer = footer
		this.content = content
		this.nCols = 0
		this.nRows = 0
		
		if( content != "" ):
			this.__updateShape()
		
	def __str__( this ):
		output = ""
		output += "--\n"+this.header+"\n"
		output += "--\n"+this.content+"\n"
		output += "--\n"+this.footer+"\n"
		output += "--"
		
		return output
		
	###
	# Calcula el numero de filas y columnas del contenido del bloque
	# tomando como número de columnas el valor máximo encontrado
	##
	def __updateShape( this ):
		lines = this.content.splitlines()
		
		this.nCols = -1e1000
		this.nRows = len( lines )
		
		for line in lines:
			tokens = line.split()
			
			if( this.nCols < len(tokens) ):
				this.nCols = len(tokens)
				
	###
	# Attribute access control
	###
	def __setattr__( this, name, value ):
		this.__dict__[name] = value
		
		if( name == "content" ):
			this.__updateShape()
			
	###
	# Returns the row number "pos"
	##
	def getRow( this, pos ):
		return this.getRows( [pos] )
		
	###
	# Returns the rows contained in the list "listPos"
	##
	def getRows( this, listPos ):
		output = ""
		lines = this.content.splitlines()
		
		for i in listPos:
			output += lines[i-1]+"\n"
				
		output = output[:-1]
		return output
		
	###
	# Remueve la fila numero "pos"
	##
	def removeRow( this, pos ):
		return this.removeRows( [pos] )
		
	###
	# Remueve filas
	##
	def removeRows( this, listPos ):
		lines = this.content.splitlines()
		toKeep = list( set(range(1,len(lines)+1))-set(listPos) )
		this.content = this.getRows( toKeep )
		
	###
	# Filtra las filas utilizando una expresion regular
	##
	def filterRows( this, rex ):
		output = ""
		lines = this.content.splitlines()
		
		for line in lines:
			if( re.match( rex, line ) ):
				output += line+"\n"
				
		output = output[:-1]
		this.content = output
		
	###
	# Extrae la columna numero "pos"
	##
	def getColumn( this, pos ):
		return this.getColumns( [pos] )
		
	###
	# Extrae columnas desde un bloque dado
	##
	def getColumns( this, listPos ):
		output = ""
		lines = this.content.splitlines()
		
		maxCols = -1
		nRows = len(lines)
		
		# Se busca el numero maximo de columnas
		for i in range(0,nRows):
			line = lines[i]
			tokens = line.split()
			
			if( len(tokens) > maxCols ):
				maxCols = len(tokens)
				
		maxNCharInCol = [ -1e1000 ]*maxCols
				
		# Almacena el numero maximo de caracteres por columna
		for j in range(0,maxCols):
			for i in range(0,nRows):
				line = lines[i]
				tokens = line.split()
					
				if( j <= len(tokens) ):
					maxNCharInCol[j-1] = len(tokens[j-1])
			
		# Se contruye la columna con formato
		for i in range(0,nRows):
			line = lines[i]
			tokens = line.split()
			
			for j in listPos:
				if( j <= len(tokens) ):
					token = tokens[j-1]
					output += ("%"+str(maxNCharInCol[j-1])+"s") % token+" "
			
			output = output[:-1]
			output += "\n"
				
		output = output[:-1]
		return output
		
	###
	# Remueve la columna numero "pos"
	##
	def removeColumn( this, pos ):
		return this.removeColumns( [pos] )
		
	###
	# Remueve columnas
	##
	def removeColumns( this, listPos ):
		tokens = this.content.splitlines()[0].split()
		toKeep = list( set(range(1,len(tokens)+1))-set(listPos) )
		this.content = this.getColumns( toKeep )
	
	###
	# Filtra las columnas utilizando una expresion regular
	##
	def filterColumns( this, rex ):
		print "## Error ##: Funcion sin implementar"
		
	###
	# Convierte todos los valores a una matrix
	##
	@staticmethod
	def toMatrix( block, dtype='f' ):
		if( block.__class__.__name__ == "TextBlock" ):
			lines = block.content.splitlines()
		else:
			lines = block.splitlines()
		
		nCols = -1e1000
		nRows = len( lines )
		
		for line in lines:
			tokens = line.split()
			
			if( nCols < len(tokens) ):
				nCols = len(tokens)
				
			for token in tokens:
				if( re.match( "[abcdfghijklmnopqrstuvwxyzABCDFGHIJKLMNOPQRSTUVWXYZ]+", token ) != None ):
					print "## Error ##: El bloque que se desea convertir a matriz posee caracteres no numericos"
					return None
				
		if( block.__class__.__name__ == "TextBlock" ):
			return numpy.matrix( numpy.fromstring( block.content, sep=' ', dtype=dtype ).reshape( nRows, nCols ) )
		else:
			return numpy.matrix( numpy.fromstring( block, sep=' ', dtype=dtype ).reshape( nRows, nCols ) )
		
		
		
	###
	# Convierte todos los valores a un arreglo
	##
	@staticmethod
	def toArray( block, dtype='f' ):
		if( dtype=='S' or dtype=='a' ):
			
			if( block.__class__.__name__ == "TextBlock" ):
				tokens = block.content.split()
			else:
				tokens = block.split()
			
			output = numpy.array( ['XXXXXXXXXXXXXXXX']*len(tokens) )
			
			for i in range(0,len(tokens)):
				output[i] = tokens[i]
				
			return output
		else:
			if( block.__class__.__name__ == "TextBlock" ):
				return numpy.fromstring( block.content, sep=' ', dtype=dtype )
			else:
				return numpy.fromstring( block, sep=' ', dtype=dtype )
			
	###
	# Test method
	##
	@staticmethod
	def test():
		block = TextBlock()
		block.header = "ATOMS IN THE ASYMMETRIC UNIT   23 - ATOMS IN THE UNIT CELL:   72"
		block.footer = "END"
		block.content = \
		"     ATOM              X/A                 Y/B             Z(ANGSTROM) \n" \
		" *******************************************************************************\n" \
		"   1 T   8 O    -4.009694440315E-25  1.110232995006E-16  4.544119697405E+00\n" \
		"   2 T   8 O    -4.009694440315E-25 -5.000000000000E-01  4.544120404660E+00\n" \
		"   3 T   8 O     5.000000000000E-01  1.110232861188E-16  4.544120486632E+00\n" \
		"   4 T   8 O     5.000000000000E-01 -5.000000000000E-01  4.544120928429E+00\n" \
		"   5 T  22 TI   -4.009694440315E-25  2.499997137358E-01  3.273857166718E+00\n" \
		"   6 F  22 TI   -4.009694440315E-25 -2.499997137358E-01  3.273857166718E+00\n" \
		"   7 T  22 TI    5.000000000000E-01  2.499999291954E-01  3.273844068696E+00\n" \
		"   8 F  22 TI    5.000000000000E-01 -2.499999291954E-01  3.273844068696E+00\n" \
		"   9 T  22 TI   -2.500000257108E-01 -6.782250472326E-17  3.273899838083E+00\n" \
		"  10 T  22 TI   -2.499999008103E-01 -5.000000000000E-01  3.273900403448E+00\n" \
		"  11 F  22 TI    2.500000257108E-01 -6.782250472326E-17  3.273899838083E+00\n" \
		"  12 F  22 TI    2.499999008103E-01 -5.000000000000E-01  3.273900403448E+00\n" \
		"  13 T   8 O    -2.500002442782E-01 -1.530022276438E-01  3.273885314266E+00\n" \
		"  14 T   8 O    -2.499999388286E-01  3.469977940453E-01  3.273886547343E+00\n" \
		"  15 F   8 O     2.500002442782E-01 -1.530022276438E-01  3.273885314266E+00\n" \
		"  16 F   8 O     2.499999388286E-01  3.469977940453E-01  3.273886547343E+00\n" \
		"  17 F   8 O    -2.500002442782E-01  1.530022276438E-01  3.273885314266E+00\n" \
		"  18 F   8 O    -2.499999388286E-01 -3.469977940453E-01  3.273886547343E+00"
		
		print block
		
		print "Filtering Rows with ^\s{2,}\d+.*"
		print "================================"
		block.filterRows( "^\s{2,}\d+.*" )
		print block
		
		print "Column 4"
		print "========"
		print block.getColumn(4)
		
		print "Columns 2,5 and 6"
		print "================="
		print block.getColumns([2,5,6])
		
		print "Row 2"
		print "====="
		print block.getRow(2)
		
		print "Rows 4,6"
		print "========"
		print block.getRows([4,6])
		
		print "Columns 5, 6 and 7 to Matrix"
		print "============================"
		print TextBlock.toMatrix( block.getColumns([5,6,7]) )
		
		print "Columns 5, 6 and 7 to Array"
		print "==========================="
		print TextBlock.toArray( block.getColumns([5,6,7]) )
		
		print "Removing rows 1, 3 and 5"
		print "========================"
		block.removeRows([1,3,5])
		print block
		
		print "Removing columns 3, 5 and 7"
		print "==========================="
		block.removeColumns([3,5,7])
		print block
		
		