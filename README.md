# piamod
System based on Python for Interactive Analysis of Molecular data PIAMoD

# Loading data from VASP POSCAR file
```
parser = VASP_Parser()
crystal = Crystal()

parser.inputFile = "mydir/VASP_POSCAR"
crystal = parser.load( format=VASP_Parser.POSCAR )
print crystal
print crystal.chemicalFormula()
crystal.save("mycrystal.xyz")
```

# Using Contracted Gaussian Basis Sets
```
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
```

# Loading data from CRYSTAL output files
```
parser = CrystalParser() ;
crystal = Crystal() ;

print ""
print "Loading data from CRYSTAL_OUTPUT file"
print "====================================="
print ""
parser.inputFile = PIAMOD_HOME+"/src/data/formats/CRYSTAL_OUTPUT"
parser.format = CrystalParser.OUTPUT

print ""
print "Loading all atoms"
print "-----------------"
print ""
parser.setFlags( atomsType=CrystalParser.ALL_ATOMS )
crystal = parser.load()
crystal.save("crystal.xyz")
print crystal

print ""
print "Loading only real atoms"
print "-----------------------"
print ""
parser.setFlags( atomsType=CrystalParser.IRREDUCIBLE_ATOMS )
parser.format = CrystalParser.OUTPUT
crystal = parser.load()
print crystal

print ""
print "Loading data from CRYSTAL_GUI file"
print "=================================="
print ""

parser.inputFile = PIAMOD_HOME+"/src/data/formats/CRYSTAL_GUI"
parser.format = CrystalParser.GUI
crystal = parser.load()
print crystal
```

# Parsing CRYSTAL output files
```
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

```

# Crystals and symmetry operators
```
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
```
