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

class reasoner:
    def __init__(self):
        self.changed = True
        self.elements = []
        self.counter = 0

    def conjunction1(self, concept, e):
        conceptType = concept.getClass().getSimpleName()
        if conceptType == "ConceptConjunction":
            for conjunct in concept.getConjuncts():
                e.append(conjunct)
            self.changed = True
        return e

    def subsume(self, concept, e):
        for axiom in axioms:
            axiomType = axiom.getClass().getSimpleName()
            if axiomType == "GeneralConceptInclusion" and axiom.lhs() == concept:
                if axiom.rhs() not in e:
                    e.append(axiom.rhs())
                    self.changed = True
        return e

    def conjunction2(self, concept, e):
        for axiom in axioms:
            axiomType = axiom.getClass().getSimpleName()
            if axiomType == "GeneralConceptInclusion":
                conceptType = axiom.rhs().getClass().getSimpleName()
                if conceptType == "ConceptConjunction":
                    conjunct = axiom.rhs().getConjuncts()
                    print(conjunct)
                    if all(element in conjunct for element in e):
                        e.append(elFactory.getConjunction(conjuct[0], conjunct[1]))
                        self.changed = True
        return e

    def existential1(self, concept, elements):
        conceptType = concept.getClass().getSimpleName()
        if conceptType == "ExistentialRoleRestriction":
            for element in elements:
                if concept.filler() in element[0]:
                    return elements
            d = []
            d.append(concept.filler())
            elements.append(d)
        return elements

    def existential2(self, elements):
        conceptType = concept.getClass().getSimpleName()
        if conceptType == "ExistentialRoleRestriction":







    def rules(self, concept, e, elements):
        #Trule(concept)
        #self.conjunction1(concept, e)
        #self.conjunction2(concept, e)
        #self.existential1(concept, elements)
        self.existential2(concept, e)
        #self.subsume(concept, e)

    def ELreasoner(self, classname):
        subsumer = []
        for concept in conceptNames:
            d = [classname]
            self.elements = [d]
            self.changed = True
            while self.changed == True:
                self.changed = False
                for e in self.elements:
                    for _ in e:
                        self.rules(_, e, self.elements)
            if concept in d:
                subsumer.append(concept)
        return subsumer

subsumers = reasoner()
result = subsumers.ELreasoner(test)
print(f"According to our reasoner, {test} has the following subsumers: ")
for concept in result:
    print(formatter.format(concept))





