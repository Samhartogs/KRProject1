#! /usr/bin/python
import sys
from py4j.java_gateway import JavaGateway

# Check for command line input
if len(sys.argv) != 3:
    raise ValueError("The input should be in the form of PROGRAMM_NAME ONTOLOGY_FILE CLASS_NAME")
else:
    ontologyfile = sys.argv[1]
    classname = sys.argv[2]

# connect to the java gateway of dl4python
gateway = JavaGateway()

# get a parser from OWL files to DL ontologies
parser = gateway.getOWLParser()

# get a formatter to print in nice DL format
formatter = gateway.getSimpleDLFormatter()

print("Loading the ontology...")

# load an ontology from a file
ontology = parser.parseFile(ontologyfile)

print("Loaded the ontology!")

# IMPORTANT: the algorithm from the lecture assumes conjunctions to always be over two concepts
# Ontologies in OWL can however have conjunctions over an arbitrary number of concpets.
# The following command changes all conjunctions so that they have at most two conjuncts
print("Converting to binary conjunctions")
gateway.convertToBinaryConjunctions(ontology)



# get the TBox axioms
tbox = ontology.tbox()
axioms = tbox.getAxioms()
changed = False


print("These are the axioms in the TBox:")
for axiom in axioms:
    print(formatter.format(axiom))


# get all concepts occurring in the ontology
elFactory = gateway.getELFactory()
allConcepts = ontology.getSubConcepts()
conceptNames = ontology.getConceptNames()
print("These are the concept names: ")
print([formatter.format(x) for x in conceptNames])
test = elFactory.getConceptName(classname)


def conjunction1(concept):
    conceptType = concept.getClass().getSimpleName()
    if conceptType == "ConceptConjunction":
        for conjunct in concept.getConjuncts():
            concept.append(conjunct)
    changed = True
    return concept

def rules(concept):
    #Trule(concept)
    conjunction1(concept)
    #concept.append(conjunction2(concept))
    #existential1(concept)
    #existential2(concept)
    #subsume(concept)

def ELreasoner(classname):
    subsumer = []
    for concept in conceptNames:
        d = [classname]
        elements = [d]
        changed = True
        while changed == True:
            changed = False
            for e in elements:
                for _ in e:
                    rules(_)
        if concept in d:
            subsumer.append(concept)
    return subsumer

subsumers = ELreasoner(test)
print(f"According to our reasoner, {test} has the following subsumers: ")
for concept in subsumers:
    print(formatter.format(concept))





