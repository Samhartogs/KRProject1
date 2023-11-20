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

existentialrole = []
conjunctions = []
gci = []
equiv = []
print("These are the axioms in the TBox:")
for axiom in axioms:
    axiomType = axiom.getClass().getSimpleName()
    if axiomType == "GeneralConceptInclusion":
        gci.append(axiom)
        conceptType = axiom.rhs().getClass().getSimpleName()
        if conceptType == "ExistentialRoleRestriction":
            existentialrole.append(axiom.rhs())
        elif conceptType == "ConceptConjunction":
            conjunctions.append(axiom.rhs())
    elif axiomType == "EquivalenceAxiom":
        equiv.append(axiom)



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

    class Element:
        def __init__(self, name, list, connections):
            self.name = name
            self.list = []
            self.connections = []

    def conjunction1(self, concept, e):
        conceptType = concept.getClass().getSimpleName()
        if conceptType == "ConceptConjunction":
            for conjunct in concept.getConjuncts():
                if conjunct not in e.list:
                    e.list.append(conjunct)
                    self.changed = True
        return e

    def subsume(self, concept, e):
        for axiom in gci:
            if axiom.lhs() == concept:
                if axiom.rhs() not in e.list:
                    e.list.append(axiom.rhs())
                    self.changed = True

        return e

    def conjunction2(self, concept, e):
        for axiom in conjunctions:
            conjunct = axiom.getConjuncts()
            if all(element in conjunct for element in e.list):
                e.list.append(elFactory.getConjunction(conjunct[0], conjunct[1]))
                self.changed = True
        return e

    def existential1(self, concept, e, elements):

        conceptType = concept.getClass().getSimpleName()
        if conceptType == "ExistentialRoleRestriction":
            for element in elements:
                if concept.filler() == element.list[0]:
                    return elements
                
            d = self.Element(name=f"D:{self.counter}", list=[], connections=[])
            e.connections.append(d)
            d.list.append(concept.filler())
            elements.append(d)
            self.changed = True
        return elements

    def existential2(self, concept, e):
        #make sure concept type is atomic C
        if len(e.connections) > 0:
            for successor in e.connections:
                for concept in successor.list:
                    for axiom in existentialrole:
                        filler = axiom.filler()
                        if concept == filler and axiom not in e.list:
                            role = elFactory.getRole("hasIngredient")
                            existential = elFactory.getExistentialRoleRestriction(role, filler)
                            e.list.append(existential)
                            self.changed = True
        return e



    def rules(self, concept, e, elements):
        #Trule(concept)
        self.subsume(concept, e)
        self.conjunction1(concept, e)
        self.conjunction2(concept, e)
        self.existential1(concept, e, elements)
        self.existential2(concept, e)

    def equivalence(self, e):
        for axiom in equiv:
            concepts = axiom.getConcepts()
            if concepts[0] in e.list and concepts[1] not in e.list:
                e.list.append(concepts[1])
            if concepts[1] in e.list and concepts[0] not in e.list:
                e.list.append(concepts[0])
        return e




    def ELreasoner(self, classname):
        subsumer = []
        for concept in conceptNames:
            d = self.Element(name=classname, list=[], connections=[])
            d.list.append(classname)
            self.elements = [d]
            self.changed = True
            while self.changed == True:
                self.changed = False
                for e in self.elements:
                    for _ in e.list:
                        self.rules(_, e, self.elements)
            self.equivalence(d)
            if concept in d.list:
                subsumer.append(concept)
        return subsumer

subsumers = reasoner()
result = subsumers.ELreasoner(test)
print(f"According to our reasoner, {test} has the following subsumers: ")
for concept in result:
    print(" - ", formatter.format(concept))





