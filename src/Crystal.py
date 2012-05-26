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

from Molecule import *
from CrystalParser import *

###
# Make a Crystal extending from Molecule
##
class Crystal(Molecule):
	
	###
	# Constructor
	##
	def __init__( this, name="Unknown", atomicNumbers=None, labels=None, xPos=None, yPos=None, zPos=None, charges=None ):
		Molecule.__init__( this, name, atomicNumbers, labels, xPos, yPos, zPos, charges )
		this.latticeVectors = -numpy.ones( (3,3) )
		this.numberOfReplicas = [1,1,1]
		
	###
	#
	##
	def __str__( this ):
		output = Molecule.__str__( this )+"\n\n"
		output += "Lattice Vectors ="
		
		for i in [0,1,2]:
			output += "\n"
			for j in [0,1,2]:
				output += "%15.7f" % this.latticeVectors[i,j]
				
		output += "\n\n"
		output += "Supercell Size = ["
		output += "%2d," % this.numberOfReplicas[0]
		output += "%2d," % this.numberOfReplicas[1]
		output += "%2d" % this.numberOfReplicas[2]
		output += " ]"
		
		return output
		
	###
	#
	##
	def __copy__( this ):
		output = Crystal()
		
		output.name = this.name
		output.symmetryOperators = copy(this.symmetryOperators)
		output.orbitalEnergies = copy(output.orbitalEnergies)
		
		for atom in this:
			output.append( atom, makeCopy=True, automaticId=False )
			
			#if( atom.real ):
				#this.realAtoms.append( this[-1] )
				
		output.latticeVectors = copy(this.latticeVectors)
		output.numberOfReplicas = copy(this.numberOfReplicas)
		
		return output
		
	###
	# Select the latticeVectors
	##
	def setLatticeVectors( this, latticeVectors ):
		
		# Checks if the lattice vectors have been chosen,
		# if these values have been chosen then the atomic
		# positions will be rescaled to the new values
		if( not ( this.latticeVectors+1.0 ).any() ):
			this.latticeVectors = numpy.matrix( latticeVectors )
		else:
			oldLatticeVectors = numpy.matrix( this.latticeVectors )
			this.latticeVectors = numpy.matrix( latticeVectors )
			
			for atom in this:
				atom.x = ( this.latticeVectors[0,0]/oldLatticeVectors[0,0] )*atom.x
				atom.y = ( this.latticeVectors[1,1]/oldLatticeVectors[1,1] )*atom.y
				atom.z = ( this.latticeVectors[2,2]/oldLatticeVectors[2,2] )*atom.z
		
	###
	# Select the supercell dimentions
	##
	def buildSuperCell( this, nx=1, ny=1, nz=0 ):
		print "BUILDING SUPERCELL"
		print "------------------"
		print "   NEW SIZE: "+"[ "+str(nx)+", "+str(ny)+", "+str(nz)+" ]"
		print ""

		this.numberOfReplicas[0] = nx
		this.numberOfReplicas[1] = ny
		this.numberOfReplicas[2] = nz
		
		molecule = this[:]
		c = this.latticeVectors
		
		#for ix in range(nx/2-nx+1, nx/2+1):
			#for iy in range(ny/2-ny+1, ny/2+1):
				#for iz in range(nz/2-nz+1, nz/2+1):
					
					#for atom in molecule:
						#x = atom.x+ix*c[0,0]+iy*c[0,1]+iz*c[0,2]
						#y = atom.y+ix*c[1,0]+iy*c[1,1]+iz*c[1,2]
						#z = atom.z+ix*c[2,0]+iy*c[2,1]+iz*c[2,2]
						
						#this.append( Atom( x, y, z, charge=atom.charge, label=atom.label, real=False, symGrp=atom.symGrp ), check=True )
						
						
		for ix in range(nx/2-nx+1, nx/2+1):
			for iy in range(ny/2-ny+1, ny/2+1):
				if( ix != 0 or iy != 0 ):
					for atom in molecule:
						x = atom.x+ix*c[0,0]
						y = atom.y+iy*c[1,1]
						z = atom.z
						
						this.append( Atom( x, y, z, charge=atom.charge, label=atom.label, real=False, symGrp=atom.symGrp ), check=False )
		
	###
	# Test method
	##
	@staticmethod
	def test():
		PIAMOD_HOME = os.getenv("PIAMOD_HOME")
		
		crystal = Crystal("Celda unidad de TiO2")
		
		crystal.append( Atom( 0.000000000000, 0.000000000000, 0.000000000000, label="Ti" ) )
		crystal.append( Atom( 1.419489652269, 1.419489652269, 0.000000000000, label="O"  ) )
		
		sym1 = [[-1.000,  0.000,  0.000],
			[ 0.000, -1.000,  0.000],
			[ 0.000,  0.000,  1.000],
			[ 0.000,  0.000,  0.000]]
		
		sym2 = [[ 0.100,  0.000,  0.000],
			[ 0.000, -0.100,  0.000],
			[ 0.000,  0.000, -0.100],
			[ 2.319,  2.319,  1.489]]
		
		sym3 = [[-1.000,  0.000,  0.000],
			[ 0.000,  1.000,  0.000],
			[ 0.000,  0.000, -1.000],
			[ 2.319,  2.319,  1.489]]
		
		sym4 = [[ 0.000, -1.000,  0.000],
			[-1.000,  0.000,  0.000],
			[ 0.000,  0.000, -1.000],
			[ 0.000,  0.000,  0.000]]
		
		sym5 = [[ 0.000,  1.000,  0.000],
			[ 1.000,  0.000,  0.000],
			[ 0.000,  0.000, -1.000],
			[ 0.000,  0.000,  0.000]]
		
		sym6 = [[ 0.000,  1.000,  0.000],
			[-1.000,  0.000,  0.000],
			[ 0.000,  0.000,  1.000],
			[ 2.319,  2.319,  1.489]]
		
		sym7 = [[ 0.000, -0.100,  0.000],
			[ 0.100,  0.000,  0.000],
			[ 0.000,  0.000,  0.100],
			[ 2.319,  2.319,  1.489]]
		
		sym8 = [[-0.100,  0.000,  0.000],
			[ 0.000, -0.100,  0.000],
			[ 0.000,  0.000, -0.100],
			[ 0.000,  0.000,  0.000]]
		
		sym9 = [[ 0.100,  0.000,  0.000],
			[ 0.000,  0.100,  0.000],
			[ 0.000,  0.000, -0.100],
			[ 0.000,  0.000,  0.000]]
		
		sym10= [[-0.100,  0.000,  0.000],
			[ 0.000,  0.100,  0.000],
			[ 0.000,  0.000,  0.100],
			[ 2.319,  2.319,  1.489]]
		
		sym11= [[ 0.100,  0.000,  0.000],
			[ 0.000, -0.100,  0.000],
			[ 0.000,  0.000,  0.100],
			[ 2.319,  2.319,  1.489]]
		
		sym12= [[ 0.000,  0.100,  0.000],
			[ 0.100,  0.000,  0.000],
			[ 0.000,  0.000,  0.100],
			[ 0.000,  0.000,  0.000]]
		
		sym13= [[ 0.000, -0.100,  0.000],
			[-0.100,  0.000,  0.000],
			[ 0.000,  0.000,  0.100],
			[ 0.000,  0.000,  0.000]]
		
		sym14= [[ 0.000, -0.100,  0.000],
			[ 0.100,  0.000,  0.000],
			[ 0.000,  0.000, -0.100],
			[ 2.319,  2.319,  1.489]]
		
		sym15= [[ 0.000,  0.100,  0.000],
			[-0.100,  0.000,  0.000],
			[ 0.000,  0.000, -0.100],
			[ 2.319,  2.319,  1.489]]
			
		latticeVectors = [[ 4.64, 0.00, 0.00],
				  [ 0.00, 4.64, 0.00],
				  [ 0.00, 0.00, 2.98]]
				  
		crystal.setSymetryOperators( [sym1, sym2, sym3, sym4, sym5, sym6, sym6, sym7, sym8, sym9, sym10, sym11, sym12, sym13, sym14, sym15] )
			
		crystal.setLatticeVectors( latticeVectors )
		crystal.buildSuperCell( 2, 2, 2 )
		crystal.save( "final.xyz", format=Molecule.XYZ )
		
		latticeVectors = [[ 1.2*4.64, 0.00, 0.00],
				  [ 0.00, 1.2*4.64, 0.00],
				  [ 0.00, 0.00, 1.2*2.98]]
				  
		crystal.setLatticeVectors( latticeVectors )
		crystal.save( "final2.xyz", format=Molecule.XYZ )
		
		print crystal
		