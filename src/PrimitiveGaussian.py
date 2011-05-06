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

class PrimitiveGaussian:
	
	#**
	# Constructor
	#**
	def __init__( this, sType="XX", origin=[0.0,0.0,0.0], exponent=1.0, L=[-1,-1,-1] ):
		this.__blockAttributeAccess = True
		
		this.constant = 1.0

		this.origin = origin
		this.exponent = exponent
		
		this.center = this.origin
		
		this.__blockAttributeAccess = False
		
		# Automatically updated
		if( sType != "XX" ):
			this.sType = sType
		elif( L != [-1,-1,-1] ):
			this.L = L 
					
	#**
	# Convierte la gaussiana primitiva en un string
	#**
	def __str__( this ):
		output = ""
		output += "L = " + "(%2d" % this.L[0] + "%2d" % this.L[1] + "%2d" % this.L[2] + " ):%3s" % this.sType + "\n"
		output += "Origin = " + "(%10.5f" % this.origin[0]+ "%10.5f" % this.origin[1] + "%10.5f" % this.origin[2] + " )\n"
		output += "Exponent = " + "%10.5f" % this.exponent + "\n"
		output += "Normalization constant = " + "%10.5f" % this.constant
		return output
		
	#**
	# Attribute access control
	#**
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

	#**
	# Para ordenar de mayor a menor momento angular
	#**
	def __cmp__( this, other ):
		return -cmp( sum(this.L), sum(other.L) )
		
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
			
	def __updateL( this ):
		if(   this.sType == "S"   ): this.L = [0,0,0]
		elif( this.sType == "P"   ): this.L = [1,0,0]
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
		
	@staticmethod
	def test():
		gaussA = PrimitiveGaussian( sType="S", origin=[2.0,1.0,-5.0], exponent=0.1 )
		gaussB = PrimitiveGaussian( sType="S", origin=[-5.0,2.0,-1.0], exponent=0.2 )
		
		print gaussA
		print gaussB
				