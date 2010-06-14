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

import fileinput
import re
import math
import sys

from copy import *
from collections import deque

from Atom import *
from SymmetryOperator import *

###
# Make a Molecule extending from list of Atoms
##
class Molecule(list):
	
	# Temporales mientras decido donde ponerlas
	STDIN="STDIN$$"
	STDOUT="STDOUT$$"
	
	# Available output file formats
	XYZ=0
	MOLDEN=1
	POVRAY=2
	
	###
	# Constructor
	##
	def __init__( this, name="Unknown", atomicNumbers=None, labels=None, xPos=None, yPos=None, zPos=None, charges=None ):
		this.name = name
		this.symmetryOperators = []
		this.orbitalEnergies = []
		this.realAtoms = []
		
		if( ( atomicNumbers!=None or labels!=None ) and ( xPos!=None and yPos!=None and zPos!=None ) and charges!=None ):
			for i in range(0,len(xPos)):
				if( atomicNumbers!=None ):
					this.append( Atom(xPos[i], yPos[i], zPos[i], atomicNumber=atomicNumbers[i], charge=charges[i]) )
				elif( labels!=None ):
					this.append( Atom(xPos[i], yPos[i], zPos[i], label=labels[i], charge=charges[i]) )
		
	###
	#
	##
	def __str__( this ):
		output = "Name = " + this.name +"\n"
		output += "Atoms List =\n"
		output += "%5s" % "id"
		output += "%12s" % "label( Z)"
		output += "%15s" % "X"
		output += "%15s" % "Y"
		output += "%15s" % "Z"
		#output += "%15s" % "q"
		#output += "%15s" % "color"
		
		for atom in this:
			output += "\n" + str(atom)
			
		if( len(this.symmetryOperators) > 0 ):
			output += "\n\n"
			output += "Symmetry Operators = \n"
				
			for sym in this.symmetryOperators:
				output +=  str(sym) + "\n"
		
		return output
		
	###
	#
	##
	def __copy__( this ):
		output = Molecule()
		
		output.name = this.name
		output.symmetryOperators = copy(this.symmetryOperators)
		output.orbitalEnergies = copy(output.orbitalEnergies)
		
		for atom in this:
			output.append( atom, makeCopy=True, automaticId=False )
			
			#if( atom.real ):
				#this.realAtoms.append( this[-1] )
				
		return output
			
	###
	#
	##
	def normalizeIds( this ):
		for i in range(0,len(this)):
			this[i].id = i+1
		
	###
	# Adds Atoms to the molecule
	##
	def append( this, item, makeCopy=True, automaticId=True ):
		exist = False
		for atom in this:
			if( atom == item ):
				exist = True
				break
		
		if( not exist ):
			if( makeCopy ):
				list.append( this, copy( item ) )
			else:
				list.append( this, item )
			
			if( automaticId ):
				this[-1].id = len(this)
				
			if( item.real ):
				this.realAtoms.append( this[-1] )
				
	###
	# Removes atoms from the molecule
	##
	def remove( this, idList=None, posList=None ):
		if( idList ):
			for id2 in idList:
				atom = this.getAtom( id=id2, makeCopy=False )
				#this.realAtoms.remove( atom )
				list.remove( this, atom )
				
		elif( posList ):
			atomList = [] 
			for pos in posList:
				atomList.append( this.getAtom( pos=pos, makeCopy=False ) )
				
			for atom in atomList:
				#this.realAtoms.remove( atom )
				list.remove( this, atom )
		
	###
	# @warning No tiene implementada la componente de translacion para el operador de simetria
	##
	def addSymetryOperator( this, operator, apply=True ):
		this.symmetryOperators.append( operator )
		
		if( apply ):
			molecule=this[:]
			
			for atom in molecule:
				xyz = atom.xyzMatrix()*this.symmetryOperators[-1].rotation.transpose()
				this.append( Atom( xyz[0,0], xyz[0,1], xyz[0,2], label=atom.label ) )
		
	###
	# Select the symmetry operators. The object symmetryOperators can be contain instances
	# of SymmetryOperator, npmatrix and list classes
	##
	def setSymetryOperators( this, symmetryOperators, apply=True ):
		
		this.symmetryOperators = []
		
		for operator in symmetryOperators:
			if( operator.__class__.__name__ == "SymmetryOperator" ):
				this.symmetryOperators.append( operator )
			elif( operator.__class__.__name__ == "npmatrix" ):
				this.symmetryOperators.append( SymmetryOperator( operator ) )
			elif( operator.__class__.__name__ == "list" ):
				this.symmetryOperators.append( SymmetryOperator( numpy.matrix(operator) ) )
			else:
				print "### Error ###: in Molecule.setSymetryOperators()"
				print "               Symmetry operators with unknown format"
		
		if( apply ):
			this.applySymmetry()
		
	###
	# Apply the symmetry operators on the all atoms
	##
	def applySymmetry( this ):
		molecule=this[:]
		
		for p in this.symmetryOperators:
			for atom in molecule:
				xyz = atom.xyzMatrix()*p.rotation.transpose()+numpy.matrix( p.translation )
				this.append( Atom( xyz[0,0], xyz[0,1], xyz[0,2], label=atom.label, charge=atom.charge, real=False ) )
					
	###
	# Return the Atom object using its id or position (pos), return
	# a copy or the reference to the original object using makeCopy flag
	##
	def getAtom( this, id=None, pos=None, makeCopy=True ):
		if( id != None ):
			for atom in this:
				if( atom.id == id ):
					if( makeCopy ):
						return copy( atom )
					else:
						return atom
						
			print "## Error ##: in Molecule.getAtom()"
			print "             The requiered atom id=", id , " has been not found !!!"
			
		elif( pos != None ):
			if( makeCopy ):
				return copy( this[pos] )
			else:
				return this[pos]
				
			print "## Error ##: in Molecule.getAtom()"
			print "             The requiered atom pos=", pos , " has been not found !!!"
				
	###
	# Return the diference between this molecule respect to other. Remember
	# that two atoms are equal only if them have the exact same xyz coordinates
	##
	def difference( this, other, makeCopy=True, keepIds=False, tol=Atom.xyzThresholdComparison ):
		outputMolecule = Molecule()
		
		initialTol = Atom.xyzThresholdComparison
		Atom.xyzThresholdComparison = tol
		
		for n in range(0,len(this)):
			
			located = False
			
			for m in range(0,len(other)):
				if( this[n] == other[m] ):
					located = True
					break
					
			if( not located ):
				outputMolecule.append( this[n], makeCopy=makeCopy, automaticId=(not keepIds) )
				
		Atom.xyzThresholdComparison = initialTol
				
		return outputMolecule
		
	###
	# Return the intersection between this molecule respect to other. Remember
	# that two atoms are equal only if the differences in xyz coordinates
	# is lower than tol. The atoms for the output molecule will be the same
	# than the molecule other. The ids will be take from other.
	##
	def intersection( this, other, makeCopy=True, keepIds=False, tol=Atom.xyzThresholdComparison  ):
		outputMolecule = Molecule()
		
		initialTol = Atom.xyzThresholdComparison
		Atom.xyzThresholdComparison = tol
		
		for n in range(0,len(this)):
			
			located = False
			
			for m in range(0,len(other)):
				if( this[n] == other[m] ):
					located = True
					break
				
			if( located ):
				outputMolecule.append( other[m], makeCopy=makeCopy, automaticId=(not keepIds) )
				outputMolecule[-1].id = this[n].id
				
		Atom.xyzThresholdComparison = initialTol
			
		return outputMolecule
	
	###
	# Return the xyz geometry diference between two molecules.
	# The diference will be performed element to element, preserving
	# the order in the two molecules using the id or pos flags
	# @returns: map using pos or id as key and [ xDiff, yDiff, zDiff ] as values
	##
	@staticmethod
	def geometryDifference( molecule1, molecule2, pos=True, id=False ):
		
		output = {}
		
		if( len(molecule1) != len(molecule2) ):
			print "### Error ###: in Molecule.geometryDifference()"
			print "               The two molecules don't have the same number of atoms"
			return
		
		for i in range(0,len(molecule1)):
			
			xDiff = 0.0
			yDiff = 0.0
			zDiff = 0.0
			
			if( pos ):
				xDiff = molecule1.getAtom( pos=i ).x - molecule2.getAtom( pos=i ).x
				yDiff = molecule1.getAtom( pos=i ).y - molecule2.getAtom( pos=i ).y
				zDiff = molecule1.getAtom( pos=i ).z - molecule2.getAtom( pos=i ).z
				
			elif( id ):
				xDiff = molecule1.getAtom( id=i ).x - molecule2.getAtom( id=i ).x
				yDiff = molecule1.getAtom( id=i ).y - molecule2.getAtom( id=i ).y
				zDiff = molecule1.getAtom( id=i ).z - molecule2.getAtom( id=i ).z
				
			output[i] = [ xDiff, yDiff, zDiff ]
				
		return output
		
	def getNeighborhood( this, atom=None, id=None, makeCopy=False, keepIds=False ):
		neighborhood = Molecule()
		
		if( atom != None ):
			for atom1 in this:
				if( atom.isConnectedWith( atom1 ) ):
					if( makeCopy ):
						neighborhood.append( copy( atom1 ), automaticId=(not keepIds) )
					else:
						neighborhood.append( atom1, automaticId=(not keepIds) )
					
		elif( id != None ):
			centerAtom = this.getAtom( id )
			
			for atom1 in this:
				if( centerAtom.isConnectedWith( atom1 ) ):
					neighborhood.append( atom1, makeCopy=makeCopy, automaticId=(not keepIds) )
				
		return neighborhood
		
	def chemicalFormula( this ):
		counter = {}
		output = ""
		
		for atom in this:
			if( counter.get( atom.label ) == None ):
				counter[atom.label] = 1
			else:
				counter[atom.label] += 1
				
		for key, value in counter.iteritems():
			output += str( key )+"_"+str(value)+" "
			
		return output
		
	def centerAroundOf( this, atom=None, id=None, active=[True,True,True] ):
		if( id != None ):
			atom = this.getAtom( id=id )
				
		if( atom != None ):
			for atom1 in this:
				
				x=atom1.x
				y=atom1.y
				z=atom1.z
				
				if( active[0] ):
					x=(atom1.x-atom.x)
				if( active[1] ):
					y=(atom1.y-atom.y)
				if( active[2] ):
					z=(atom1.z-atom.z)
					
				atom1.set( x=x, y=y, z=z )
		
	###
	#
	##
	def save( this, outputFileName=STDOUT, format=XYZ ):
		if( format==Molecule.XYZ ):
			this.__saveInXYZFormat( outputFileName )
		elif( format==Molecule.MOLDEN ):
			this.__saveInMoldenFormat( outputFileName )
		elif( format==Molecule.POVRAY ):
			this.__saveInPOVRayFormat( outputFileName )
		else:
			print "##Error##: in Molecule.save()"
			print "           Input file format for save geometry not Supported"
			exit
			
	###
	#
	##
	def load( this, inputFileName=STDIN, format=XYZ ):
		if( format==Molecule.XYZ ):
			this.__loadFromXYZFormat( inputFileName )
		else:
			print "##Error##: in Molecule.load()"
			print "           Input file format for load geometry not Supported"
			exit
			
	###
	#
	##
	def checkSymmetry( this, tol=1e-1, force=False ):
		for atom in this:
			for p in this.symmetryOperators:
				xyz = atom.xyzMatrix()*p.rotation.transpose()+numpy.matrix( p.translation )
				proyectedAtom = Atom( xyz[0,0], xyz[0,1], xyz[0,2], label=atom.label, charge=atom.charge, id=atom.id )
				
				for atom2 in this:
					r = numpy.sqrt( sum( (atom2.xyzArray()-proyectedAtom.xyzArray())**2 ) )
					
					if( r < tol and r > 1e-6 ):
							print "Is possible that this atoms are equivalent:"
							print "\t"+str(atom2)
							print "\t"+str(proyectedAtom)
							
							if( force ):
								print "\tForced to satisfy the symmetry !!!"
								atom2.set( x=proyectedAtom.x, y=proyectedAtom.y, z=proyectedAtom.z )
								
	###
	#
	##
	def radialCluster( this, idCenter, cutoff, makeCopy=False, saturate=False ):
		outputMolecule = Molecule()
		centerAtom = this.getAtom( id=idCenter )
			
		for atom in this:
			
			dist = numpy.linalg.norm( atom.xyzArray() - centerAtom.xyzArray() )
		
			if( dist < cutoff ):
				outputMolecule.append( atom, makeCopy=makeCopy, automaticId=False )
				
		if( saturate ):
			return this.__saturateWith( outputMolecule, "H" )
			
		return outputMolecule
		
	###
	#
	##
	def neighborhoodCluster( this, idCenter=None, length=1, makeCopy=False, saturate=False, idCenterList=None, keepIds=False ):
		outputMolecule = Molecule()
		prevCenterList = []
		newCenterList = []
			
		if( idCenterList != None ):
			for idItem in idCenterList:
				centerAtom = this.getAtom( id=idItem )
				prevCenterList.append( centerAtom )
				outputMolecule.append( centerAtom, makeCopy=makeCopy, automaticId=False )
			
		elif( idCenter != None ):
			centerAtom = this.getAtom( id=idCenter )
			prevCenterList.append( centerAtom )
			outputMolecule.append( centerAtom, makeCopy=makeCopy, automaticId=False )
		
		if( length != 0 ):
			for i in range(1,length+1):
				for center in prevCenterList:
					neighborhood = this.getNeighborhood( id=center.id, keepIds=True )
					
					for newAtom in neighborhood:
						
						newCenterList.append( newAtom )
						outputMolecule.append( newAtom, makeCopy=makeCopy, automaticId=False )
					
					
				prevCenterList = newCenterList[:]
				
		if( saturate ):
			clusterExtended = this.__saturateWith( outputMolecule, "H" )
			
			if( not keepIds ):
				clusterExtended.normalizeIds()
				
			return clusterExtended
			
			
		if( not keepIds ):
			outputMolecule.normalizeIds()
			
		return outputMolecule
		
		
	def __saturateWith( this, cluster, atomLabel="H" ):
		
		####################################################################1
		# Primero se extiende el cluster incluyendole los nuevos atomos
		# que despues se convertiran en H
		clusterExtended = Molecule()
		for atom in cluster:
			neighborhood = this.getNeighborhood( id=atom.id, keepIds=True )
			
			for atom2 in neighborhood:
				clusterExtended.append( atom2, automaticId=False )
			
		####################################################################1
		# Por diferencia con el clusters inicial se caturan los quienes
		# son los futuros hidrogenos
		hydrogens = clusterExtended.difference( cluster, makeCopy=False, keepIds=True )
		
		####################################################################1
		# Evaluando la vecindad de cada uno de los futuros hidrogenos
		# se calcula su nueva posicion y se transmutan a H, pero si hay
		# varios vecinos se crea directamente otro atomo de hidrogeno
		# en la posicion correcta
		clusterWithHydrogens = copy( clusterExtended )
		
		rp = 1.0
		for hydrogen in hydrogens:
			atomLeaves = clusterExtended.getNeighborhood( id=hydrogen.id, keepIds=True )
			
			i=0
			for atomLeaf in atomLeaves:
				xa = atomLeaf.x
				ya = atomLeaf.y
				za = atomLeaf.z
				
				xb = hydrogen.x
				yb = hydrogen.y
				zb = hydrogen.z
				
				r = numpy.linalg.norm( atomLeaf.xyzArray()-hydrogen.xyzArray() )
				
				xp = rp*((xb-xa)/r)+xa
				yp = rp*((yb-ya)/r)+ya
				zp = rp*((zb-za)/r)+za
				
				rp = ( atomLeaf.covalentRadius()+hydrogen.covalentRadius() )/2.0
				
				if( i==0 ):
					clusterWithHydrogens.getAtom( id=hydrogen.id, makeCopy=False ).set(label="H", x=xp, y=yp, z=zp)
				else:
					newHydrogen = copy( hydrogen )
					newHydrogen.set( label="H", x=xp, y=yp, z=zp )
					clusterWithHydrogens.append( newHydrogen )
				
				i+=1
			
		return clusterWithHydrogens
		
	
	###
	# Save the molecule geometry in XYZ format file
	##
	def __saveInXYZFormat( this, outputFileName ):
		
		if( outputFileName!=Molecule.STDOUT ):
			ofile = file(outputFileName, 'w')
		else:
			ofile = sys.stdout
			
		print >> ofile, '%5d' % len(this)
		print >> ofile, this.name
		
		for atom in this:
			print >> ofile, '%-5s' % atom.label,
			print >> ofile, '%10.5f' % atom.x,
			print >> ofile, '%10.5f' % atom.y,
			print >> ofile, '%10.5f' % atom.z
			
		if( outputFileName!=Molecule.STDOUT ):
			ofile.close()
			
	###
	# Save the molecule geometry in molden format file
	##
	def __saveInMoldenFormat( this, outputFileName ):
		
		if( outputFileName!=Molecule.STDOUT ):
			ofile = file(outputFileName, 'w')
		else:
			ofile = sys.stdout
			
		print >> ofile, "[Molden Format]"
		print >> ofile, "[Atoms] Angs"
		
		i=1
		for atom in this:
			print >> ofile, '%-5s' % atom.label,
			print >> ofile, '%5d' % i,
			print >> ofile, '%5d' % atom.atomicNumber,
			print >> ofile, '%10.7f' % atom.x,
			print >> ofile, '%10.7f' % atom.y,
			print >> ofile, '%10.7f' % atom.z
			
			i += 1
			
		if( outputFileName!=Molecule.STDOUT ):
			ofile.close()
			
	def __saveInPOVRayFormat( this, outputFileName ):
		if( outputFileName!=Molecule.STDOUT ):
			ofile = file(outputFileName, 'w')
		else:
			ofile = sys.stdout

		for atom in this:
			print >> ofile, atom.toPovray()
		
		if( outputFileName!=Molecule.STDOUT ):
			ofile.close()
		
	###
	# Save the molecule geometry in molden format file
	##
	def __loadFromXYZFormat( this, inputFileName ):
		
		del this[:]
		
		if( inputFileName!=Molecule.STDIN ):
			ifile = file(inputFileName, 'r')
		else:
			ifile = sys.stdin
			
		i=0
		for line in ifile:
			if( i==1 ):
				this.name = line[0:len(line)-1]
			if( i>=2 ):
				tokens = line.split()
				this.append( Atom( float(tokens[1]), float(tokens[2]), float(tokens[3]), label=tokens[0] ) )
			i+=1
			
		if( inputFileName!=Molecule.STDIN ):
			ifile.close()
		
	###
	# Test method
	##
	@staticmethod
	def test():
		PIAMOD_HOME = os.getenv("PIAMOD_HOME")
		
		mol1 = Molecule("Celda unidad de TiO2")
		
		mol1.append( Atom(  0.000000000000,   0.000000000000,  4.432457801093, label="O" ) )
		mol1.append( Atom(  2.954876407992,   0.000000000000,  4.432477313629, label="O" ) )
		mol1.append( Atom(  0.000000000000,   3.251532690144,  3.120904027079, label="Ti" ) )
		mol1.append( Atom(  2.954876407992,   3.251532690144,  3.120907233788, label="Ti" ) )
		mol1.append( Atom( -1.477443307323,   0.000000000000,  3.375470402770, label="Ti" ) )
		mol1.append( Atom( -1.477444073912,  -2.060340009799,  3.392188176100, label="O" ) )
		mol1.append( Atom(  0.000000000000,   0.000000000000,  1.937140741989, label="O" ) )
		mol1.append( Atom(  2.954876407992,   0.000000000000,  1.937190520821, label="O" ) )
		mol1.append( Atom(  0.000000000000,   3.251532690144,  1.269837359311, label="O" ) )
		mol1.append( Atom(  2.954876407992,   3.251532690144,  1.269826643925, label="O" ) )
		mol1.append( Atom(  0.000000000000,   0.000000000000,  0.000000000000, label="Ti" ) )
		mol1.append( Atom(  2.954876407992,   0.000000000000,  0.000000000000, label="Ti" ) )
		mol1.append( Atom( -1.477449064844,   3.251532690144,  0.000000000000, label="Ti" ) )
		mol1.append( Atom( -1.477465426449,   1.318586150097,  0.000000000000, label="O" ) )
			
		sym1 = [[ 1.0,  0.0,  0.0],
			[ 0.0, -1.0,  0.0],
			[ 0.0,  0.0, -1.0]]
			
		sym2 = [[-1.0,  0.0,  0.0],
			[ 0.0,  1.0,  0.0],
			[ 0.0,  0.0, -1.0]]
			
		sym3 = [[-1.0,  0.0,  0.0],
			[ 0.0, -1.0,  0.0],
			[ 0.0,  0.0,  1.0]]
			
		sym4 = [[-1.0,  0.0,  0.0],
			[ 0.0, -1.0,  0.0],
			[ 0.0,  0.0, -1.0]]
			
		sym5 = [[-1.0,  0.0,  0.0],
			[ 0.0,  1.0,  0.0],
			[ 0.0,  0.0,  1.0]]
			
		sym6 = [[ 1.0,  0.0,  0.0],
			[ 0.0, -1.0,  0.0],
			[ 0.0,  0.0,  1.0]]
			
		sym7 = [[ 1.0,  0.0,  0.0],
			[ 0.0,  1.0,  0.0],
			[ 0.0,  0.0, -1.0]]
			
		mol1.setSymetryOperators( [sym1, sym2, sym3, sym4, sym5, sym6, sym6, sym7] )
		mol1.save( "final.xyz", format=Molecule.XYZ )
		print mol1
		
		#mol1.save( format=Molecule.XYZ )
		#mol1.save( format=Molecule.MOLDEN )
		
		mol2 = Molecule("Fragment of the unit cell optimized")
		mol2.append( Atom(  0.00,   0.00,  4.43, label="O" ) )
		mol2.append( Atom(  2.95,   0.00,  4.43, label="O" ) )
		mol2.append( Atom(  2.95,   3.25,  3.12, label="Ti" ) )
		mol2.append( Atom( -1.47,   0.00,  3.37, label="Ti" ) )
		mol2.append( Atom( -1.47,  -2.06,  3.39, label="O" ) )
		mol2.save( "salida.xyz", format=Molecule.XYZ )
		
		moltmp = mol1.difference( mol2, keepIds=True, tol=1e-1 )
		moltmp.save( "difference.xyz", format=Molecule.XYZ )
		#print Molecule.geometryDifference( mol1, moltmp, id=True )
		#quit()
		mol1.intersection( mol2, keepIds=True, tol=1e-1 ).save( "intersection.xyz", format=Molecule.XYZ )
		
		cluster = mol1.radialCluster( 1, 4.0, saturate=True )
		cluster = mol1.neighborhoodCluster( 1, 2, saturate=True )
		#cluster.save( "cluster.xyz", format=Molecule.XYZ )
		print "Cluster"
		print cluster
		
		newcluster = Molecule()
		newcluster.load( PIAMOD_HOME+"/src/data/formats/XYZ", format=Molecule.XYZ )
		print newcluster
		
		newcluster.save( format=Molecule.POVRAY )
		
		
		