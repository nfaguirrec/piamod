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

from copy import *
from PrimitiveGaussian import *

class ContractedGaussian:
	
	###
	# Constructor
	##
	def __init__( this, sType="XX", origin=[0.0,0.0,0.0], exponent=1.0, L=[-1,-1,-1] ):
		this.__blockAttributeAccess = True
		
		this.constant = 1.0

		this.origin = origin
		
		this.coefficients = []
		this.primitives = []
		
		this.__blockAttributeAccess = False
		
		# Automatically updated
		if( sType != "XX" ):
			this.sType = sType
		elif( L != [-1,-1,-1] ):
			this.L = L
			
	###
	# Returns the number of primitive gaussians
	##
	def __len__( this ):
		return len( this.coefficients )
	
	###
	# Returns the number of primitive gaussians
	##
	def size( this ):
		return len( this.coefficients )
			
	###
	# Convierte la gaussiana primitiva en un string
	##
	def __str__( this ):
		output = ""
		output += "Angular moment = " + "(%3d" % this.L[0] + "%3d" % this.L[1] + "%3d" % this.L[2] + " ) :%3s" % this.sType + "\n"
		output += "Origin = " + "(%10.5f" % this.origin[0]+ "%10.5f" % this.origin[1] + "%10.5f" % this.origin[2] + " )\n"
		output += "Normalization constant = %10.5f" % this.constant + "\n"
		output += "Composition = \n"
		
		for i in range(this.size()):
			output += "%3d" % i
			output += "%10.5f" % this.coefficients[i]
			output += ", "
			output += "%10.5f" % this.primitives[i].constant
			output += "%10.5f" % this.primitives[i].exponent
			output += "  :  "  + this.primitives[i].sType + "\n"
			
		output += ""
		return output
	
	###
	# 
	##
	def append( this, coefficient, primitive, makeCopy=True ):
		
		this.coefficients.append( coefficient )
		
		if( makeCopy ):
			this.primitives.append( copy(primitive) )
		else:
			this.primitives.append( primitive )
		
		for gauss in this.primitives:
			gauss.sType = this.sType
			gauss.origin = this.origin
		
	###
	# Para ordenar de menor a mayor momento angular
	##
	def __cmp__( this, other ):
		return cmp( sum(this.L), sum(other.L) )
	
	###
	# Attribute access control
	##
	def __setattr__( this, name, value ):
		this.__dict__[name] = value
		
		if( not this.__blockAttributeAccess ):
			if( name == "L" ):
				this.__blockAttributeAccess = True
				this.__updateSType()
				this.__blockAttributeAccess = False
				
			if( name == "sType" ):
				this.__blockAttributeAccess = True
				this.__updateL()
				this.__blockAttributeAccess = False
								
	def __updateSType( this ):
		if(   this.L == [0,0,0] ): this.sType = "S"
		elif( this.L == [1,0,0] ): this.sType = "Px"
		elif( this.L == [0,1,0] ): this.sType = "Py"
		elif( this.L == [0,0,1] ): this.sType = "Pz"
		elif( this.L == [2,0,0] ): this.sType = "Dxx"
		elif( this.L == [0,2,0] ): this.sType = "Dyy"
		elif( this.L == [0,0,2] ): this.sType = "Dzz"
		elif( this.L == [1,1,0] ): this.sType = "Dxy"
		elif( this.L == [1,0,1] ): this.sType = "Dxz"
		elif( this.L == [0,1,1] ): this.sType = "Dyz"
		
		for gauss in this.primitives:
			gauss.sType = this.sType
			
	def __updateL( this ):
		if(   this.sType == "S"   ): this.L = [0,0,0]
		elif( this.sType == "P"  ):  this.L = [1,0,0]
		elif( this.sType == "Px"  ): this.L = [1,0,0]
		elif( this.sType == "Py"  ): this.L = [0,1,0]
		elif( this.sType == "Pz"  ): this.L = [0,0,1]
		elif( this.sType == "D"   ): this.L = [2,0,0]
		elif( this.sType == "Dxx" ): this.L = [2,0,0]
		elif( this.sType == "Dyy" ): this.L = [0,2,0]
		elif( this.sType == "Dzz" ): this.L = [0,0,2]
		elif( this.sType == "Dxy" ): this.L = [1,1,0]
		elif( this.sType == "Dxz" ): this.L = [1,0,1]
		elif( this.sType == "Dyz" ): this.L = [0,1,1]
		elif( this.sType == "F"   ): this.L = [3,0,0]
		
		for gauss in this.primitives:
			gauss.L = this.L
					
	@staticmethod
	def test():
		gaussA = PrimitiveGaussian( exponent=6.168856 )
		gaussB = PrimitiveGaussian( exponent=1.623913 )
		gaussC = PrimitiveGaussian( exponent=0.425250 )
		
		contractedA = ContractedGaussian( sType="S", origin=[0.0,0.0,0.0] )
		contractedB = ContractedGaussian( sType="Pz", origin=[0.0,0.0,0.5] )
		
		contractedA.append( 1.444635, gaussA )
		contractedA.append( 0.535328, gaussB )
		contractedA.append( 4.154329, gaussC )
		
		contractedB.append( 2.444635, gaussA )
		contractedB.append( 1.535328, gaussB )
		contractedB.append( 0.154329, gaussC )
		
		print contractedA
		print contractedB
				