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

###
# Make a QuntumMolecule extending from Molecule
##
class QuantumMolecule( Molecule ):

	###
	# Constructor
	##
	def __init__( this, name="Unknown", atomicNumbers=None, labels=None, xPos=None, yPos=None, zPos=None, charges=None ):
		Molecule.__init__( this, name, atomicNumbers, labels, xPos, yPos, zPos, charges )
		this.orbitalEnergies = []
		
        ###
        #
        ##
        def __str__( this ):
                output = Molecule.__str__( this )+"\n\n"
                output += "Orbital Energies = \n"
                
                output += "   "
                for i in range(len(this.orbitalEnergies)):
			output += "%8.5f" % this.orbitalEnergies[i]
			
			if( (i+1)%10 == 0 or i == len(this.orbitalEnergies) ):
				output += "\n   "
			elif( i < len(this.orbitalEnergies)-1 ):
				output += ", "
                                
                output += "\n"
                
                return output
                
        ###
        #
        ##
        def __copy__( this ):
                output = copy( this )
                output.orbitalEnergies = copy(this.orbitalEnergies)
                return output
                
        ###
        #
        ##
        @staticmethod
        def orbitalEnergiesToGnuplot( orbEnerList, labels, fileName ):
		ofile = file( fileName, 'w' )
		ofileDens = file( "dens.dat", 'w' )
		
		print >> ofile, "set termopt enhanced"
		print >> ofile, "unset key"
		print >> ofile, "unset xtics"
		
		print >> ofile, "set multiplot"
		
		print >> ofile, "set border 15"
		print >> ofile, "set format y \"%5.2f\""
		print >> ofile, "set ytics nomirror out"
		print >> ofile, "set style arrow 1 nohead ls 1 lw 2"
		print >> ofile, "set ylabel \"Relative energy\""
		print >> ofile, "set xlabel \"N\""
		print >> ofile, "set xtics out nomirror border in scale 0,0"
		print >> ofile, "set size 0.5,0.8"
		print >> ofile, "set xrange [0.0:",len(orbEnerList),"]"
		
		print >> ofile, "set xtics ( ",
		for i in range(len(labels)):
			print >> ofile, "\"", labels[i] ,"\" ", 0.5+i,
			if( i!= len(labels)-1 ):
				print >> ofile, ", ",
		print >> ofile, ")"
		
		emin = 1e10
		emax = -1e10
		for i in range(len(orbEnerList)):
			for j in range(len(orbEnerList[i])):
				y=orbEnerList[i][j]-min(orbEnerList[i])
				print >> ofile, "set arrow from ",i,"+0.2,", y, " to ",i,"+0.8,", y, " as 1"
				
				if( y < emin ):
					emin = y
					
				if( y > emax ):
					emax = y
					
			dens=len(orbEnerList[i])/(max(orbEnerList[i])-min(orbEnerList[i]))
			print >> ofileDens, 0.5+i, dens
			
		print >> ofile, "set yrange [",emin-0.1*(emax-emin),":",emax+0.1*(emax-emin),"]"
		print >> ofile, "plot ",10.0*emax
		
		print >> ofile, "unset arrow"
		print >> ofile, "set ylabel \"\""
		print >> ofile, "unset xlabel"
		print >> ofile, "set border 0"
		print >> ofile, "set size 0.39,0.2"
		print >> ofile, "set origin 0.112,0.76"
		print >> ofile, "unset xtics"
		print >> ofile, "unset ytics"
		print >> ofile, "set style fill solid 1.00 border -1"
		print >> ofile, "set style data histograms"
		print >> ofile, "set style histogram cluster gap 0.5"
		print >> ofile, "set boxwidth 0.4 absolute"
		print >> ofile, "plot [] [2:10] \"./dens.dat\" u 2 ls 3"
		
		print >> ofile, "unset multiplot"
		
		print >> ofile, "pause -1"
		ofile.close()
                
        ###
        # Test method
        ##
        @staticmethod
        def test():
		qmol = QuantumMolecule("My Molecule")

		qmol.append( Atom( 0.000000000000, 0.000000000000, 0.000000000000, label="Ti" ) )
		qmol.append( Atom( 1.419489652269, 1.419489652269, 0.000000000000, label="O"  ) )
		
		# 1 bosons
		n1 = [ -16.16, -16.08, -15.21, -15.13, -14.86, -13.54 ]
		# 2 bosons
		n2 = [ -32.42, -31.56, -31.11, -32.00, -31.48, -30.66, -32.03, -30.50, -30.26, -31.63, -30.33, -31.55, -30.33 ]
		# 3 bosons
		n3 = [ -48.58, -48.06, -47.69, -46.98, -47.76, -47.68, -47.58, -47.69, -47.13, -46.15, -48.13, -47.75, -46.84, -47.72, -46.39, -47.75, -46.99 ]
		# 4 bosons
		n4 = [ -64.49, -63.57, -62.76, -64.55, -63.73, -63.11 ]
		
		QuantumMolecule.orbitalEnergiesToGnuplot( [n1,n2,n3,n4], ["1", "2", "3", "4"], "salida.gnu" )
		os.system("gnuplot salida.gnu; rm salida.gnu")

		print qmol
		

