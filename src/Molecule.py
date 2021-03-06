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
import os

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
	LATTICE=3
	
	###
	# Constructor
	# @todo Hay que crean una clase hija llamada QuantumMolecule, la cual tendrá parámetros como energías o orbitalEnergies
	##
	def __init__( this, name="Unknown", atomicNumbers=None, labels=None, xPos=None, yPos=None, zPos=None, charges=None ):
		this.name = name
		this.symmetryOperators = SymmetryOperatorsList()
		this.orbitalEnergies = []
		
		if( ( atomicNumbers!=None or labels!=None ) and ( xPos!=None and yPos!=None and zPos!=None ) and charges!=None ):
			for i in range(0,len(xPos)):
				if( atomicNumbers!=None ):
					this.append( Atom(xPos[i], yPos[i], zPos[i], atomicNumber=atomicNumbers[i], charge=charges[i]) )
				elif( labels!=None ):
					this.append( Atom(xPos[i], yPos[i], zPos[i], label=labels[i], charge=charges[i]) )
					
		this.nSymGrp = 0
		
	###
	# Constructor
	##
	@staticmethod
	def fromListOfAtoms( listOfAtoms ):
		mol = Molecule()
		
		mol.name = "From list of atoms"
		mol.symmetryOperators = SymmetryOperatorsList()
		mol.orbitalEnergies = []
		
		for atom in listOfAtoms:
			mol.append( atom )
			
		return mol
		
	###
	#
	##
	def __str__( this ):
		output = "Name = " + this.name +"\n"
		output += "Atoms List =\n"
		output += "%5s" % "p"
		output += "%5s" % "id"
		output += "%3s" % "IR"
		output += "%3s" % "SG"
		output += "%12s" % "label( Z)"
		output += "%15s" % "X"
		output += "%15s" % "Y"
		output += "%15s" % "Z"
		output += "%15s" % "Q"
		#output += "%15s" % "color"
		
		for i in range(len(this)):
			output += "\n"+"%5s"%i + str(this[i])
			
		if( len(this.symmetryOperators) > 0 ):
			output += "\n\n"
			output += "Symmetry Operators = \n"
			output += str(this.symmetryOperators)
		
		return output
		
	###
	#
	##
	def __copy__( this ):
		output = Molecule()
		
		output.name = this.name
		output.symmetryOperators = copy(this.symmetryOperators)
		output.orbitalEnergies = copy(output.orbitalEnergies)
		output.nSymGrp = this.nSymGrp
		
		for atom in this:
			output.append( atom, makeCopy=True, automaticId=False )
			
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
	def append( this, item, makeCopy=True, automaticId=True, check=True, debug=False, onlyTest=False ):
		if( not check ):
			if( makeCopy ):
				list.append( this, copy( item ) )
			else:
				list.append( this, item )
			
			if( automaticId ):
				this[-1].id = len(this)
				
			return True
			
		else:
			exist = False
			for atom in this:
				#if( atom == item ):
					#if( debug ):
						#print "This atoms are equal:"
						#print "  -> ", atom
						#print "  ->      ", item
						
					#exist = True
					#break
					
				if( atom.isInTheSamePositionWith(item) ):
					if( debug ):
						print "This atoms are in the same position:"
						print "  -> ", atom
						print "  ->      ", item
						
					exist = True
					break
			
			if( not exist ):
				if( not onlyTest ):
					if( makeCopy ):
						list.append( this, copy( item ) )
					else:
						list.append( this, item )
					
					if( automaticId ):
						this[-1].id = len(this)
					
				return True
			else:
				return False


	###
	# Sets the label of a type of atom
	##
	def setLabels( this, newLabel, label=None, id=None, pos=None ):
		if( label != None ):
			for atom in this:
				if( atom.label.upper() == label.upper() ):
					atom.label = newLabel.upper()
		elif( id != None ):
			for atom in this:
				if( atom.id == id ):
					atom.label = newLabel.upper()
		elif( pos != None ):
			for i in range(len(this)):
				if( i == pos ):
					this(i).label = newLabel.upper()
		else:
			for atom in this:
				atom.label = newLabel.upper()

								
	###
	# Sets the charge of a type of atom
	##
	def setCharges( this, charge, label=None, id=None, pos=None ):
		if( label != None ):
			for atom in this:
				if( atom.label.upper() == label.upper() ):
					atom.charge = charge
		elif( id != None ):
			for atom in this:
				if( atom.id == id ):
					atom.charge = charge
		elif( pos != None ):
			for i in range(len(this)):
				if( i == pos ):
					this(i).charge = charge
		else:
			for atom in this:
				atom.charge = charge
	
	###
	# Removes atoms from the molecule
	##
	def remove( this, idList=None, posList=None, atomList=None ):
		if( idList ):
			for id2 in idList:
				atom = this.getAtom( id=id2, makeCopy=False )
				list.remove( this, atom )
				
		elif( posList ):
			atomList = [] 
			for pos in posList:
				atomList.append( this.getAtom( pos=pos, makeCopy=False ) )
				
			for atom in atomList:
				list.remove( this, atom )
				
		elif( atomList ):
			for atom in atomList:
				list.remove( this, atom )
				
	###
	# @brief Returns the geometric center of the molecule
	##
	def center( this, hideIdList=None ):
		r = numpy.array( [ 0.0, 0.0, 0.0 ] )
		
		for atom in this:
			if( hideIdList != None ):
				if( not atom.id in hideIdList ):
					r += [ atom.x, atom.y, atom.z ]
			else:
				r += [ atom.x, atom.y, atom.z ]
		
		return r/len(this)
		
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
		
		this.symmetryOperators = SymmetryOperatorsList()
		
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
		print "APPLYING SYMMETRY OPERATORS"
		print "---------------------------"
		print ""
		print this.symmetryOperators
		print ""

		molecule=this[:]
		
		for p in this.symmetryOperators:
			for atom in molecule:
				xyz = atom.xyzMatrix()*p.rotation.transpose()+numpy.matrix( p.translation )
				this.append( Atom( xyz[0,0], xyz[0,1], xyz[0,2], label=atom.label, charge=atom.charge, real=False ) )
				
		print "   The applying of the symmetry operators has been successful !!"
		print ""
		sys.stdout.flush()
		
	###
	# Returns a list with the labels of the atoms
	##
	def getLabels( this ):
		labels = []
		
		for atom in this:
			if( not atom.label in labels ):
				labels.append( atom.label )
				
		return labels
		
	###
	# Returns a new molecule that includes only the atoms with the selected label
	##
	def filterByLabel( this, label ):
		mol = Molecule()
		mol.name = this.name+" filtered by "+label
		
		for atom in this:
			if( atom.label.upper() == label.upper() ):
				mol.append( atom )
				
		return mol
		
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
	# @todo Esta diferencia no debería retornar otra molecula, debería modificar la actual molecula
	##
	def difference( this, other, makeCopy=True, keepIds=False, tol=Atom.xyzThresholdComparison ):
		print "BUILDING THE MOLECULE DIFFERENCE"
		print "--------------------------------"
		print ""
		print "\""+this.name+"\""+" .DIFFERENCE. "+"\""+ other.name+"\""
		print ""

		outputMolecule = Molecule()
		
		outputMolecule.nSymGrp = this.nSymGrp
		
		initialTol = Atom.xyzThresholdComparison
		Atom.xyzThresholdComparison = tol
		
		for n in range(0,len(this)):
			located = False
			
			for m in range(0,len(other)):
				if( this[n] == other[m] ):
					print "   Equivalent atom located:"
					print "      ", this[n]
					print "      ", other[m]
					located = True
					break
					
			if( not located ):
				outputMolecule.append( this[n], makeCopy=makeCopy, automaticId=(not keepIds), check=False )
				
		#for n in range(0,len(this)):
			##norm = numpy.linalg.norm( atom.xyzArray() - centerAtom.xyzArray() )
			#norm = numpy.linalg.norm( this[n].xyzArray() )
			#located = False
			
			#if( norm < 15.0 ):
				#for m in range(0,len(other)):
					#if( this[n] == other[m] ):
						#print "   Equivalent atom located:"
						#print "      ", this[n]
						#print "      ", other[m]
						#located = True
						#break
					
			#if( not located ):
				#outputMolecule.append( this[n], makeCopy=makeCopy, automaticId=(not keepIds), check=False )
			
		Atom.xyzThresholdComparison = initialTol

		print ""
		return outputMolecule
		
	###
	# Return 
	##
	def mapPoints( this, pointsList, labels=None, maxScale=8.0 ):
		outputMap = {}
		
		for n in range( len(pointsList) ):
			scale = 1.0
			
			while ( scale <= maxScale ):
				options = {}
				
				for atom in this:
					norm = numpy.linalg.norm( numpy.array(pointsList[n]) - atom.xyzArray() )
					
					if( norm < scale*atom.covalentRadius() ):
						options[norm] = atom
						
				if( len( options ) == 0 ):
					scale += 1.0
					continue
				else:
					skeys = options.keys()
					skeys.sort()
					
					if( labels == None ):
						outputMap[n] = options[ skeys[0] ]
					else:
						outputMap[ labels[n] ] = options[ skeys[0] ]
					
					break
					
			if( scale == maxScale ):
				print "@@ WARNING @@ Element "+str(n)+" have not been assigned"
			
		return outputMap
		
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
		
		for n in range(len(this)):
			
			located = False
			
			for m in range(len(other)):
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
			print "               The two molecules don't have the same number of atoms ", len(molecule1), "!=", len(molecule2)
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
	
	###
	# 
	##
	def getNeighborhood( this, atom=None, id=None, pos=None, makeCopy=False, keepIds=False, debug=True ):
		if( debug and atom != None ):
			print "   Getting neighborhood for atom id=", "%5d"%(atom.id), " ... ",
		if( debug and id != None ):
			print "   Getting neighborhood for atom id=", "%5d"%id, " ... ",
		if( debug and pos != None ):
			print "   Getting neighborhood for atom pos=", "%5d"%pos, " ... ",
			
		if( atom != None ):
			centerAtom = atom
		elif( id != None ):
			centerAtom = this.getAtom( id )
		elif( pos != None ):
			centerAtom = this[ pos ]
			
		neighborhood = Molecule()
			
		for atom1 in this:
			if( centerAtom.isConnectedWith( atom1 ) ):
				if( makeCopy ):
					neighborhood.append( copy( atom1 ), automaticId=(not keepIds) )
				else:
					neighborhood.append( atom1, automaticId=(not keepIds) )
				
		if( debug ):
			print "OK --> [", 
			
			for atom1 in neighborhood:
				print atom.id,
				
			print "]"
			sys.stdout.flush()
			
		return neighborhood

	###
	# @return chemicalFormula:string
	##
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
		
	###
	# 
	##
	def centerAroundOf( this, atom=None, id=None, center=None, active=[True,True,True] ):
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
				
		if( center != None ):
			for atom1 in this:
				
				if( active[0] ):
					x=(atom1.x+center[0])
				if( active[1] ):
					y=(atom1.y+center[1])
				if( active[2] ):
					z=(atom1.z+center[2])
					
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
		elif( format==Molecule.LATTICE ):
			this.__saveInLatticeFormat( outputFileName )
		else:
			print "##Error##: in Molecule.save()"
			print "           Input file format for save geometry not Supported"
			exit
			
	###
	#
	##
	def load( this, inputFileName=STDIN, format=XYZ, check=False ):
		if( format==Molecule.XYZ ):
			this.__loadFromXYZFormat( inputFileName, check )
		else:
			print "##Error##: in Molecule.load()"
			print "           Input file format for load geometry not Supported"
			exit
			
	###
	#
	# @todo Hay que hacer una clase global que almacene todas las tolerancias, i.e. Atom.xyzThresholdComparison que no debería de estar en Atom
	##
	def checkSymmetry( this, tol=1e-1, force=False ):
		print "SYMMETRY CHECKING"
		print "-----------------"
		print "   TOLERANCE = ", tol
		print "   FORCE SYMMETRY = ", force
		
		if( len( this.symmetryOperators ) == 0 ):
			print "   Skipping check, because the molecule have not symmetry operators"
			return
			
		isSymmetric = True
		for atom in this:
			for p in this.symmetryOperators:
				xyz = atom.xyzMatrix()*p.rotation.transpose()+numpy.matrix( p.translation )
				proyectedAtom = Atom( xyz[0,0], xyz[0,1], xyz[0,2], label=atom.label, charge=atom.charge, id=atom.id )
				
				for atom2 in this:
					r = numpy.sqrt( sum( (atom2.xyzArray()-proyectedAtom.xyzArray())**2 ) )
					
					if( r < tol and r > Atom.xyzThresholdComparison ):
							print "   Is possible that this atoms are equivalent:"
							print "      "+str(atom2)
							print "      "+str(proyectedAtom)
							
							isSymmetric = False
							
							if( force ):
								print "      Forced to satisfy the symmetry !!!"
								atom2.set( x=proyectedAtom.x, y=proyectedAtom.y, z=proyectedAtom.z )
								
		if( force ):
			print "   The molecule now is according with the symmetry operators"
		else:
			if( isSymmetric ):
				print "   The molecule is according with the symmetry operators"
			else:
				print "   The molecule is not according with the symmetry operators"

	###
	# Find atoms related by symmetry operations. It changes the attribute symGrp in the Atom Class
	# @todo Cambiar el atributo de la clase atom "real" por "isReal"
	##
	def findRelatedBySym( this, tol=1e-1 ):
		print "FIND ATOMS RELATED BY SYMMETRY"
		print "------------------------------"
		print "   TOLERANCE = ", tol
		
		if( len( this.symmetryOperators ) == 0 ):
			print "   ## ERROR ##: The molecule have not symmetry operators"
			return
			
		print ""
		
		symGrp = 0
		for atom in this:
			if( atom.real ):
				atom.symGrp = symGrp
				print "   ", "%5d"%atom.id, "--> [",
				
				for p in this.symmetryOperators:
					xyz = atom.xyzMatrix()*p.rotation.transpose()+numpy.matrix( p.translation )
					proyectedAtom = Atom( xyz[0,0], xyz[0,1], xyz[0,2], label=atom.label, charge=atom.charge, id=atom.id )
					
					for atom2 in this:
						r = numpy.sqrt( sum( (atom2.xyzArray()-proyectedAtom.xyzArray())**2 ) )
						
						if( r < tol ):
							atom2.symGrp = symGrp
							print atom2.id,
							
				print "]"
				symGrp += 1
				
		this.nSymGrp = symGrp
		print ""
	
	###
	# Returns the list number "symGrp" with the atoms related by symmetry
	##
	def getSymRelatedGroups( this ):
		output = {}
		
		for i in range(this.nSymGrp):
			output[i]=[]
		
		for atom in this:
			output[atom.symGrp].append( atom )
		
		return output
		
	###
	# 
	##
	#def showSymGroup( this, symGrp=0 ):
		#for atom in this.getSymRelatedGroup( symGrp ):
			#print atom
								
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
	def radialShells( this, idCenter=-1, center=[0.0,0.0,0.0], stepSize=1.0, maxRadius=100.0, makeCopy=False ):
		print ""
		print "BUILDING RADIAL SHELLS"
		print "----------------------"
		
		if( idCenter != -1 ):
			centerEff = this[i].xyzArray()
		else:
			centerEff = center
		
		distAtomIDPair = []
		
		print "stepSize = ", stepSize
		print "center = ", centerEff
		print ""
		print "Building vector of distances ... ",
		for i in range(len(this)):
			dist = numpy.linalg.norm( this[i].xyzArray() - centerEff )
			
			if( dist <= maxRadius ):
				distAtomIDPair.append( ( dist, i ) )
		print "OK"
		sys.stdout.flush()
		
		print "Building radial shells ... ",
		hist={}
		outputMoleculeMap = {}
		
		for i in range(len(distAtomIDPair)):
			n = int( distAtomIDPair[i][0]/stepSize )
			rn = "%10.2f"%(n*stepSize)
			
			if( n in hist ):
				hist[n] += 1
				outputMoleculeMap[rn].append( this[distAtomIDPair[i][1]], automaticId=False, makeCopy=makeCopy, check=False )
			else:
				hist[n] = 1
				outputMoleculeMap[rn] = Molecule( "Radial shell"+rn )
				outputMoleculeMap[rn].append( this[distAtomIDPair[i][1]], automaticId=False, makeCopy=makeCopy, check=False )
				
		print "OK"
		sys.stdout.flush()
		
		print ""
		print "Radial distribution"
		print "%5s"%"r", "%8s"%"nAtoms", "%20s"%"ChemicalFormula"
		for key,value in hist.items():
			print "%5.2f"%(key*stepSize), "%8d"%value, "%20s"%outputMoleculeMap["%10.2f"%(key*stepSize)].chemicalFormula()
		print ""
		sys.stdout.flush()
		
		del hist
		del distAtomIDPair[:]
		return outputMoleculeMap
		
	###
	#
	##
	def neighborhoodCluster( this, idCenter=None, length=1, makeCopy=False, saturate=False, idCenterList=None, keepIds=False ):
		print "BUILDING NEIGHBORHOOD CLUSTER"
		print "------------------------------"
		if( idCenter != None ):
			print "   center   = ", idCenter
		elif( idCenterList != None ):
			print "   center   = ", idCenterList
		print "   length   = ", length
		print "   makeCopy = ", makeCopy
		print "   saturate = ", saturate
		print "   keepIds  = ", keepIds
		
		outputMolecule = Molecule()
		prevCenterList = []
		newCenterList = []
		processed = {}
			
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
					if( not processed.has_key(center.id) ):
						processed[center.id] = True
						neighborhood = this.getNeighborhood( id=center.id, keepIds=True )
						print "%5d"%(100*len(processed)/len(this)),"%"
						
						for newAtom in neighborhood:
							if( not processed.has_key(newAtom.id) ):
								newCenterList.append( newAtom )
								outputMolecule.append( newAtom, makeCopy=makeCopy, automaticId=False )
						
				prevCenterList = newCenterList[:]
				newCenterList = []
				
		if( saturate ):
			clusterExtended = this.__saturateWith( outputMolecule, "H" )
			
			if( not keepIds ):
				clusterExtended.normalizeIds()
				
			return clusterExtended
			
			
		if( not keepIds ):
			outputMolecule.normalizeIds()
			
		return outputMolecule
		
	#
	# @brief Calcula la energía de dispersión con esquemas tipo Grimme en unidades atómicas
	#
	def dispCorr( this, scheme="Grimme" ):
		Edisp = 0.0
		
		if( scheme == "Grimme" ):
			
			Htocm1 = 219474.63068
			unit_J_to_H = 2.2937128e17
			unit_nm_to_a0 = 18.89726134
			unit_pm_to_a0 = unit_nm_to_a0/1.0e3
			unit_mol_to_au = 6.0221417930e23
			unit_Ang_to_a0 = 1.0/0.529177208
			
			# C6 values and vdW radii from
			# S. Grimme, J Comput Chem 27 (2006) 1787-1799
			# Units c6=[J nm^6 mol^{-1}], r=[Angstrom]
			c6Table = {}
			c6Table["H"] = 0.14*unit_J_to_H*unit_nm_to_a0**6/unit_mol_to_au
			c6Table["He"] = 0.08*unit_J_to_H*unit_nm_to_a0**6/unit_mol_to_au
			c6Table["O"] = 0.70*unit_J_to_H*unit_nm_to_a0**6/unit_mol_to_au
			c6Table["Ti"] = 10.80*unit_J_to_H*unit_nm_to_a0**6/unit_mol_to_au
			
			rvdWTable = {}
			rvdWTable["H"] = 1.001*unit_Ang_to_a0
			rvdWTable["He"] = 1.012*unit_Ang_to_a0
			rvdWTable["O"] = 1.342*unit_Ang_to_a0
			rvdWTable["Ti"] = 1.562*unit_Ang_to_a0
			
			d = 20.0
			s6_PBE = 0.75
			
			rij = 0.0
			
			for atom1 in this:
				for atom2 in this:
					if( atom1 != atom2 ):
						if( ( atom1.label in c6Table ) and ( atom1.label in rvdWTable )
						     and ( atom2.label in c6Table ) and ( atom2.label in rvdWTable ) ):
							c6 = math.sqrt( c6Table[atom1.label]*c6Table[atom2.label] )
							rvdW = rvdWTable[atom1.label]+rvdWTable[atom2.label]
						else:
							print "### Error ###: in Molecule.dispCorr()"
							print "               Available atoms Ti,O,He,H"
							return 0.0
							
						rij = math.sqrt( (atom1.x-atom2.x)**2 + (atom1.y-atom2.y)**2
						    + (atom1.z-atom2.z)**2 )*unit_Ang_to_a0
						    
						dampF = 1.0/( 1.0+math.exp(-d*(rij/rvdW-1.0)) )
						Edisp += -s6_PBE*dampF*c6/rij**6
		else:
			print "### Error ###: in Molecule.dispCorr()"
			print "               Unknown scheme (", scheme, ")"
			return 0.0
			
		return Edisp/2.0 # @todo Estoy haciendo doble conteo en los ciclos anidados, por eso el 2.0
		
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
			print >> ofile, '%10.5f' % atom.z,
			print >> ofile, '%10.2f' % atom.charge
			
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
			
	def __saveInLatticeFormat( this, outputFileName ):
		if( outputFileName!=Molecule.STDOUT ):
			ofile = file(outputFileName, 'w')
		else:
			ofile = sys.stdout
			
		print >> ofile, ""
		print >> ofile, len(this)
		
		for atom in this:
			print >> ofile, "%10.5f"%atom.x, "%10.5f"%atom.y, "%10.5f"%atom.z, "%10.5f"%atom.charge, 0
		
		if( outputFileName!=Molecule.STDOUT ):
			ofile.close()
		
	###
	# Load the molecule geometry from XYZ format file
	##
	def __loadFromXYZFormat( this, inputFileName, check=False, debug=False ):
		if( debug ):
			print "LOADING MOLECULE FROM XYZ FILE"
			print "------------------------------"
			print "   INPUTFILENAME = ", inputFileName
			print "   CHECK         = ", check
		
		del this[:]
		
		if( inputFileName!=Molecule.STDIN ):
			ifile = file(inputFileName, 'r')
		else:
			ifile = sys.stdin
			
		nAtoms = 0
		i=0
		for line in ifile:
			if( i==0 ):
				nAtoms = int(line)
			if( i==1 ):
				this.name = line[0:len(line)-1]
				if( len(this.name) == 0 ):
					this.name = "from "+inputFileName
			if( i>=2 and i-1<=nAtoms ):
				tokens = line.split()
				this.append( Atom( float(tokens[1]), float(tokens[2]), float(tokens[3]), label=tokens[0] ), check )
			i+=1
			
		if( inputFileName!=Molecule.STDIN ):
			ifile.close()
			
		if( debug ):
			print "   Loading processes sucesfull !!"
			print ""
			sys.stdout.flush()
		
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
		cluster.save( "radialCluster.xyz", format=Molecule.XYZ )
		
		#cluster = mol1.neighborhoodCluster( 1, 2, saturate=True )
		#cluster.save( "neighborhoodCluster.xyz", format=Molecule.XYZ )
		#print "Cluster"
		#print cluster
		
		shells = mol1.radialShells( 1 )
		for shell in shells:
			shell.save( shell.name+".xyz", format=Molecule.XYZ )
		
		#newcluster = Molecule()
		#newcluster.load( PIAMOD_HOME+"/src/data/formats/XYZ", format=Molecule.XYZ )
		#print newcluster
		
		#newcluster.save( format=Molecule.POVRAY )
		
		
		
