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

import math
import re
from itertools import *

import numpy

###
#  @brief Make an Atom
##
class Atom:
	
	# GLobal variables
	X=0
	Y=1
	Z=2
	
	xyzThresholdComparison = 1e-6
	
	__labelToAtomicNumber={
		"X":0, "XX":0, "H":1, "HE":2, "LI":3, "BE":4, "B":5, "C":6, "N":7, "O":8,
		"F":9, "NE":10, "NA":11, "MG":12, "AL":13, "SI":14, "P":15, "S":16, "CL":17, "AR":18,
		"K":19, "CA":20, "SC":21, "TI":22, "V":23, "CR":24, "MN":25, "FE":26, "CO":27, "NI":28,
		"CU":29, "ZN":30, "GA":31, "GE":32, "AS":33, "SE":34, "BR":35, "KR":36, "RB":37, "SR":38,
		"Y":39, "ZR":40, "NB":41, "MO":42, "TC":43, "RU":44, "RH":45, "PD":46, "AG":47, "CD":48,
		"IN":49, "SN":50, "SB":51, "TE":52, "I":53, "XE":54, "CS":55, "BA":56, "LA":57, "CE":58,
		"PR":59, "ND":60, "PM":61, "SM":62, "EU":63, "GD":64, "TB":65, "DY":66, "HO":67, "ER":68,
		"TM":69, "YB":70, "LU":71, "HF":72, "TA":73, "W":74, "RE":75, "OS":76, "IR":77, "PT":78,
		"AU":79, "HG":80, "TL":81, "PB":82, "BI":83, "PO":84, "AT":85, "RN":86, "FR":87, "RA":88,
		"AC":89, "TH":90, "PA":91, "U":92, "NP":93, "PU":94, "AM":95, "CM":96, "BK":97, "CF":98,
		"ES":99, "FM":100, "MD":101, "NO":102, "LR":103
	}
	
	__labelToCovalentRadius={
		"X":0.000000, "XX":0.000000, "H":0.370000, "HE":0.700000, "LI":1.230000, "BE":0.890000, "B":0.900000, "C":0.850000,
		"N":0.740000, "O":0.740000, "F":0.720000, "NE":0.700000, "NA":1.000000, "MG":1.360000, "AL":1.250000, "SI":1.170000,
		"P":1.100000, "S":1.100000, "CL":0.990000, "AR":0.700000, "K":2.030000, "CA":1.740000, "SC":1.440000, "TI":1.420000,
		"V":1.220000, "CR":0.000000, "MN":1.160000, "FE":0.000000, "CO":1.150000, "NI":1.170000, "CU":1.250000, "ZN":1.250000,
		"GA":1.200000, "GE":1.210000, "AS":1.160000, "SE":0.700000, "BR":1.240000, "KR":1.910000, "RB":1.620000, "SR":1.450000,
		"Y":1.340000, "ZR":1.290000, "NB":1.290000, "MO":1.240000, "TC":1.250000, "RU":0.000000, "RH":1.340000, "PD":1.410000,
		"AG":1.500000, "CD":1.400000, "IN":1.410000, "SN":1.370000, "SB":1.330000, "TE":0.700000, "I":1.330000, "XE":1.980000,
		"CS":1.690000, "BA":1.690000, "LA":0.000000, "CE":1.690000, "PR":1.690000, "ND":1.690000, "PM":1.690000, "SM":1.690000,
		"EU":1.690000, "GD":1.690000, "TB":1.690000, "DY":1.690000, "HO":1.690000, "ER":1.690000, "TM":1.690000, "YB":1.690000,
		"LU":1.690000, "HF":1.440000, "TA":1.340000, "W":1.300000, "RE":1.280000, "OS":1.260000, "IR":1.290000, "PT":1.340000,
		"AU":1.440000, "HG":1.550000, "TL":1.540000, "PB":1.520000, "BI":1.520000, "PO":1.400000, "AT":0.700000, "RN":2.400000,
		"FR":2.000000, "RA":1.900000, "AC":1.900000, "TH":1.900000, "PA":1.900000, "U":1.900000, "NP":2.000000, "PU":2.000000,
		"AM":2.000000, "CM":2.000000, "BK":2.000000, "CF":2.000000, "ES":2.000000, "FM":2.000000, "MD":2.000000, "NO":2.000000,
		"LR":2.000000
	}
	
	__labelToVanDerWallsRadius={
		"X":0.750000, "XX":0.750000, "H":1.200000, "HE":1.700000, "LI":1.700000, "BE":1.700000, "B":1.700000, "C":1.700000,
		"N":1.550000, "O":1.520000, "F":1.470000, "NE":1.700000, "NA":1.700000, "MG":1.700000, "AL":1.940000, "SI":2.100000,
		"P":1.800000, "S":1.800000, "CL":1.750000, "AR":1.700000, "K":1.700000, "CA":1.700000, "SC":1.700000, "TI":1.700000, 
		"V":1.980000, "CR":1.940000, "MN":1.930000, "FE":1.930000, "CO":1.920000, "NI":1.700000, "CU":1.700000, "ZN":1.700000,
		"GA":2.020000, "GE":1.700000, "AS":1.960000, "SE":1.700000, "BR":2.100000, "KR":1.700000, "RB":1.700000, "SR":1.700000,
		"Y":1.700000, "ZR":2.210000, "NB":1.700000, "MO":2.060000, "TC":1.700000, "RU":2.010000, "RH":2.010000, "PD":2.040000,
		"AG":1.700000, "CD":1.700000, "IN":1.700000, "SN":1.700000, "SB":1.700000, "TE":1.700000, "I":2.150000, "XE":1.700000,
		"CS":1.700000, "BA":1.700000, "LA":0.800000, "CE":1.700000, "PR":1.700000, "ND":1.700000, "PM":1.700000, "SM":1.700000,
		"EU":1.700000, "GD":1.700000, "TB":1.700000, "DY":1.700000, "HO":1.700000, "ER":1.700000, "TM":1.700000, "YB":1.700000,
		"LU":1.700000, "HF":1.700000, "TA":1.700000, "W":1.700000, "RE":1.700000, "OS":2.020000, "IR":2.030000, "PT":1.700000,
		"AU":1.700000, "HG":1.700000, "TL":1.700000, "PB":1.700000, "BI":1.700000, "PO":1.700000, "AT":1.700000, "RN":1.700000,
		"FR":1.700000, "RA":1.700000, "AC":1.700000, "TH":1.700000, "PA":1.700000, "U":1.700000, "NP":2.000000, "PU":2.000000,
		"AM":2.000000, "CM":2.000000, "BK":2.000000, "CF":2.000000, "ES":2.000000, "FM":2.000000, "MD":2.000000, "NO":2.000000,
		"LR":2.000000
	}
	
	__labelToColor={
		"X":"#ffffff", "TI":"#bfc2c7", "O":"#ff0c0c", "HE":"#1bb100", "H":"#ffffff", "C":"#914915"
	}
	
	###
	#  @brief Constructor
	##
	def __init__( this, x=0.0, y=0.0, z=0.0, charge=0.0, label="X", atomicNumber=0, id=-1, real=True, symGrp=0 ):
		
		this.__blockAttributeAccess = True
		
		this.x = x
		this.y = y
		this.z = z
		
		this.label = label
		this.atomicNumber = atomicNumber
		
		this.charge = charge
		this.id = id
		this.symGrp = symGrp
		
		this.real = real
		
		this.__blockAttributeAccess = False
		
		if( atomicNumber == 0 ):
			this.__blockAttributeAccess = True
			this.atomicNumber = this.labelToAtomicNumber( Atom.__filterLabel( label ) )
			this.__blockAttributeAccess = False
		elif( label == "X" ):
			this.__blockAttributeAccess = True
			this.label = this.atomicNumberToLabel( atomicNumber )
			this.__blockAttributeAccess = False
		
	###
	#
	##
	def __str__( this ):
		output = ""
		
		if( this.id != -1 ):
			output += "%5s" % str(this.id)
			
		if( this.real ):
			output += "%3s" % "T"
		else:
			output += "%3s" % " "
			
		output += "%3d" % this.symGrp
			
		output += "%8s" % this.label
		output += "(%2s)" % str(this.atomicNumber)
		output += "%15.7f" % this.x
		output += "%15.7f" % this.y
		output += "%15.7f" % this.z
		
		output += "%15.5f" % this.charge
		#output += "%15s" % this.labelToColor( this.label )
		
		return output
		
	###
	#
	##
	def __eq__( this, other ):
		
		if( ( abs(this.x-other.x) < Atom.xyzThresholdComparison and
		      abs(this.y-other.y) < Atom.xyzThresholdComparison and
		      abs(this.z-other.z) < Atom.xyzThresholdComparison ) and
		      ( this.label == other.label or this.atomicNumber == other.atomicNumber ) ):
			return True
		else:
			return False
		
	#**
	# Filter the label i.e. Ti12 --> Ti used in molpro
	#**
	@staticmethod
	def __filterLabel( label ):
		if( re.match( ".*\d+.*", label ) ):
			pos=re.compile("\d+").search( label ).start()
			return label[0:pos]
		else:
			return label
		
	#**
	# Attribute access control
	#**
	def __setattr__( this, name, value ):
		this.__dict__[name] = value
		
		if( not this.__blockAttributeAccess ):
			if( name == "label" ):
				this.__blockAttributeAccess = True
				
				this.atomicNumber = this.labelToAtomicNumber( Atom.__filterLabel( value ) )

				this.__blockAttributeAccess = False
				
			if( name == "atomicNumber" ):
				this.__blockAttributeAccess = True
				
				this.label = this.atomicNumberToLabel( value )
				
				this.__blockAttributeAccess = False
				
	def set( this, x=None, y=None, z=None, charge=None, label=None, atomicNumber=None, id=None, real=None ):
		if( x != None ):
			this.x = x
		if( y != None ):
			this.y = y
		if( z != None ):
			this.z = z
		if( charge != None ):
			this.charge = charge
		if( label != None ):
			this.label = label
			this.atomicNumber = this.labelToAtomicNumber( label )
		if( atomicNumber != None ):
			this.atomicNumber = atomicNumber
			this.label = this.atomicNumberToLabel( atomicNumber )
		if( id != None ):
			this.id = id
		if( real != None ):
			this.real = real
		
	###
	# Returns a numpy array with the coordinates x,y,z
	##
	def xyzArray( this ):
		return numpy.array([this.x, this.y, this.z])
		
	###
	# Returns a numpy matrix 1x3 with the coordinates x,y,z
	##
	def xyzMatrix( this ):
		return numpy.matrix([this.x, this.y, this.z]).reshape(1,3)
		
	###
	#
	##
	def isConnectedWith( this, atom ):
		return Atom.areConnected( this, atom )
		
	###
	#
	##
	def covalentRadius( this ):
		return Atom.labelToCovalentRadius( this.label )
	
	###
	#
	##
	def toPovray( this ):
		
		label = Atom.__filterLabel( this.label )
		
		output = ""
		
		output += "sphere {\n"
		output += "\t<"
		output += "%7.3f," % this.x
		output += "%7.3f," % this.y
		output += "%7.3f" % this.z
		output += "> , // position\n"
		output += "\t%7.3f" % this.covalentRadius()#*0.5
		output += " // radius\n"
		output += "\ttexture{\n"
		output += "\t\tpigment {\n"
		output += "\t\t\tcolor rgb < "
		output += "%2.3f," % ( int( Atom.labelToColor(label)[1:3], 16 )/255.0 )
		output += "%2.3f," % ( int( Atom.labelToColor(label)[3:5], 16 )/255.0 )
		output += "%2.3f"  % ( int( Atom.labelToColor(label)[5:7], 16 )/255.0 )
		output += " >\n"
		
		output += "\t\t}\n" ;
		output += "\t}\n" ;
		output += "\tfinish { phong 0.8 }\n" ;
		output += "}" ;
		output += "\n" ;

		
		return output
		
	###
	#
	##
	@staticmethod
	def areConnected( atom1, atom2 ):
		
		label1 = Atom.__filterLabel( atom1.label )
		label2 = Atom.__filterLabel( atom2.label )
		
		diff = atom1.xyzArray() - atom2.xyzArray()
		dist = math.sqrt( numpy.dot( diff, diff ) )
		cutoff = Atom.labelToCovalentRadius( label1 ) + Atom.labelToCovalentRadius( label2 )
		
		#print "atom(", atom1.id , ") = ", atom1.xyzArray()
		#print "atom(", atom2.id , ") = ", atom2.xyzArray()
		#print "diff = ", diff
		#print "dist = ", dist
		#print "cutoff = ", cutoff
		
		if( dist <  cutoff and dist > 0.001 ):
			return True
		else:
			return False
		
	###
	# Translate from the label of one atom to the respective atomic number
	##
	@staticmethod
	def labelToAtomicNumber( label ):
		return Atom.__labelToAtomicNumber[ Atom.__filterLabel( label ).upper() ]
		
	###
	# Translate from the atomic number of one atom to the respective label
	##
	@staticmethod
	def atomicNumberToLabel( atomicNumber ):
		for (key, value) in izip( Atom.__labelToAtomicNumber.keys(), Atom.__labelToAtomicNumber.values() ):
			if( value == atomicNumber ):
				return key.upper()
		
	###
	#
	##
	@staticmethod
	def labelToCovalentRadius( label ):
		return Atom.__labelToCovalentRadius[ Atom.__filterLabel( label ).upper() ]
		
	###
	#
	##
	@staticmethod
	def labelToColor( label ):
		return Atom.__labelToColor[ Atom.__filterLabel( label ).upper() ]
		
	###
	# Test method
	##
	@staticmethod
	def test():
		atom1 = Atom( 2.9548764, 3.2515328, 3.120907, label="Ti1" )
		atom2 = Atom( 2.9548764, 6.5030656, 4.432477, label="O1" )
		atom3 = Atom( 2.9548764, 3.2515328, 1.269827, label="O" )
		atom4 = Atom( 2.96, 3.26, 3.13, label="Ti" )
		
		print " Atoms"
		print "======="
		print "Atom1) ", atom1
		print "Atom2) ", atom2
		print "Atom3) ", atom3
		print "Atom4) ", atom4
		print ""
		
		print "Position Array of Atom1 = ", atom1.xyzArray()
		print "Position Matrix  of Atom1 = ", atom1.xyzMatrix()
		print ""
		
		print "Atom1 is equal than Atom4 ( tol =", Atom.xyzThresholdComparison, ") ? = ", ( atom1 == atom4 )
		Atom.xyzThresholdComparison = 1e-1
		print "Atom1 is equal than Atom4 ( tol =", Atom.xyzThresholdComparison, ") ? = ", ( atom1 == atom4 )
		print ""
		
		print "Atom1 are connected with Atom2 ? = ", atom1.isConnectedWith( atom2 )
		print "Atom1 are connected with Atom3 ? = ", atom1.isConnectedWith( atom3 )
		print "Atom1 are connected with Atom2 ? = ", atom2.isConnectedWith( atom3 )
		print ""
		
		print "Covalent Radius for Atom1 = ", atom1.covalentRadius()
		print "Covalent Radius for Atom3 = ", atom3.covalentRadius()
		
		