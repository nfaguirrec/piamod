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
import numpy

###
# Make a Molecule extending from list of Atoms
##
class SymmetryOperator:
	
	###
	# Constructor
	# @error Hay que adicionar los casos para las distintas clases
	##
	def __init__( this, rotation=numpy.identity(3), translation=numpy.array([0.0,0.0,0.0]) ):
		if( numpy.matrix(rotation).shape == (4,3) ):
			if( rotation.__class__.__name__ == "list" ):
				this.rotation = numpy.matrix( rotation )[0:3,0:3]
				this.translation = numpy.array( [rotation[3][0],rotation[3][1],rotation[3][2]] )
			elif( rotation.__class__.__name__ == "ndarray" or rotation.__class__.__name__ == "matrix" ):
				this.rotation = numpy.matrix( rotation[0:3,0:3] )
				this.translation = numpy.array( rotation )[3,:]
		elif( numpy.matrix(rotation).shape == (3,4) ):
			if( rotation.__class__.__name__ == "list" ):
				this.rotation = numpy.matrix( rotation )[0:3,0:3]
				this.translation = numpy.array( [rotation[0][3],rotation[1][3],rotation[2][3]] )
			elif( rotation.__class__.__name__ == "ndarray" or rotation.__class__.__name__ == "matrix" ):
				this.rotation = numpy.matrix( rotation[0:3,0:3] )
				this.translation = numpy.array( rotation )[:,3]
		elif( numpy.matrix(rotation).shape == (3,3) ):
			this.rotation = numpy.matrix( rotation )
			this.translation = numpy.array( translation )
		
	###
	# Operador de impresion
	##
	def __str__( this ):
		output = ""
		
		for i in [0,1,2]:
			for j in [0,1,2]:
				output += "%7.3f" % this.rotation[i,j]
				
		output += "   "
			
		for i in [0,1,2]:
			output += "%7.3f" % this.translation[i]
		
		return output
	
	###
	# Test method
	##
	@staticmethod
	def test():
		sym1Raw = [[ 1.0,  0.0,  0.0 ],
			   [ 0.0,  1.0,  0.0 ],
			   [ 0.0,  0.0, -1.0 ]]
			
		sym1 = SymmetryOperator( sym1Raw )
		print "Operator 1"
		print "=========="
		print sym1
		
		sym2Raw = [[ 1.0,  0.0,  0.0 ],
			   [ 0.0,  1.0,  0.0 ],
			   [ 0.0,  0.0, -1.0 ],
			   [ 1.3,  4.2,  2.1 ]]
			
		sym2 = SymmetryOperator( sym2Raw )
		print "Operator 2"
		print "=========="
		print sym2
		
		sym3Raw = [[ 1.0,  0.0,  0.0,  1.3 ],
			   [ 0.0,  1.0,  0.0,  4.2 ],
			   [ 0.0,  0.0, -1.0,  2.1 ]]
			
		sym3 = SymmetryOperator( sym3Raw )
		print "Operator 3"
		print "=========="
		print sym3
		
import re
from UserList import UserList
		
class SymmetryOperatorsList( UserList ):
	
	###
	# Constructor
	##
	def __init__( this, initlist=None ):
		UserList.__init__( this, initlist )
		
	###
	# Constructor
	##
	def __str__( this, initlist=None ):
		output = ""
		
		for sym in this:
			output += str(sym) + "\n"
			
		output = output[:-1]
			
		return output
		
	###
	# Load from database
	##
	def loadFromDB( this, code=1 ):
		del this[:]
		
		PIAMOD_HOME = os.getenv("PIAMOD_HOME")
		if( PIAMOD_HOME == None ):
			print "### Error ###: Environment variable PIAMOD_HOME not found !!!"
			quit()
		
		ifile = file( PIAMOD_HOME+"/src/data/symDB/" + str(code)+".sym" , 'r')
		fileContent = ifile.read()
		ifile.close()
		
		lines = fileContent.splitlines()
		
		tmpArray = []
		i=0
		for line in lines:
			if( re.match( "^\s*$", line ) == None ):
				
				tokens = line.split()
				
				for token in tokens:
					
					if( re.match( "[-]{0,1}\d+/[-]{0,1}\d+", token ) ):
						oper = token.split('/')
						token = float(oper[0])/float(oper[1])
						
					tmpArray.append( float(token) )
					
				i += 1
				
				if( i==3 ):
					arr = numpy.array( tmpArray )
					arr.shape = (3,4)
					this.append( SymmetryOperator( arr ) )
					
					del tmpArray[:]
					i=0
		
	###
	# Test method
	##
	@staticmethod
	def test():
		sym1Raw = [[ 1.0,  0.0,  0.0 ],
			   [ 0.0,  1.0,  0.0 ],
			   [ 0.0,  0.0, -1.0 ]]
			
		sym2Raw = [[ 1.0,  0.0,  0.0 ],
			   [ 0.0,  1.0,  0.0 ],
			   [ 0.0,  0.0, -1.0 ],
			   [ 1.3,  4.2,  2.1 ]]
			
		sym3Raw = [[ 1.0,  0.0,  0.0,  1.3 ],
			   [ 0.0,  1.0,  0.0,  4.2 ],
			   [ 0.0,  0.0, -1.0,  2.1 ]]
			
		symOps = SymmetryOperatorsList()
		
		symOps.append( SymmetryOperator( sym1Raw ) )
		symOps.append( SymmetryOperator( sym2Raw ) )
		symOps.append( SymmetryOperator( sym3Raw ) )
		
		print "Operators"
		print "========="
		print symOps
		print
			
		print "Operators from Database"
		print "======================="
		for i in range(1,231):
			print "code = ", i
			print "----------"
			symOps.loadFromDB( i )
			print symOps
			print
		
