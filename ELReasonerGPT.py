#!/usr/bin/python
import sys
from py4j.java_gateway import JavaGateway

class ELReasoner:
    def __init__(self):
        self.changed = True
        self.elements = []
        self.counter = 0

    class Element:
        def __init__(self, name, lst, connections):
            self.name = name
            self.list = []
            self.connections = []

    def conjunction1(self, concept, e):
        if concept.getClass().getSimpleName() == "ConceptConjunction":
            for conjunct in concept.getConjuncts():
                if conjunct not in e.list:
                    e.list.append(conjunct)
                    self.changed = True
        return e

    def subsume(self, concept, e):
        for axiom in gci:
            if axiom.lhs() == concept and axiom.rhs() not in e.list:
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
        if concept.getClass().getSimpleName() == "ExistentialRoleRestriction":
            filler = concept.filler()
            if any(element.list[0] == filler for element in elements):
                return elements

            d = self.Element(name=f"D:{self.counter}", list=[], connections=[])
            self.counter += 1
            e.connections.append(d)
            d.list.extend([filler, elFactory.getTop()])
            elements.append(d)
            self.changed = True
        return elements

    def existential2(self, concept, e):
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
        self.subsume(concept, e)
        self.conjunction1(concept, e)
        self.conjunction2(concept, e)
        self.existential1(concept, e, elements)
        self.existential2(concept, e)

    def equivalence(self, e):
        for axiom in equiv:
            concepts = axiom.getConcepts()
            for c in concepts:
                if c in e.list and c not in e.list:
                    e.list.append(c)
        return e

    def ELreasoner(self, classname):
        subsumer = []
        for concept in conceptNames:
            d = self.Element(name=classname, lst=[classname, elFactory.getTop()], connections=[])
            self.elements = [d]
            self.changed = True
            while self.changed:
                self.changed = False
                for e in self.elements:
                    for _ in e.list:
                        self.rules(_, e, self.elements)
            self.equivalence(d)
            if concept in d.list:
                subsumer.append(concept)
        return subsumer

# Connect to the java gateway of dl4python
gateway = JavaGateway()
elFactory = gateway.getELFactory()

# Check for command line input
if len(sys.argv) != 3:
    raise ValueError("The input should be in the form of PROGRAM_NAME ONTOLOGY_FILE CLASS_NAME")
else:
    ontologyfile = sys.argv[1]
    classname = elFactory.getConceptName(sys.argv[2])

# Get a parser from OWL files to DL ontologies
parser = gateway.getOWLParser()

# Get a formatter to print in nice DL format
formatter = gateway.getSimpleDLFormatter()

print("Loading the ontology...")

# Load an ontology from a file
ontology = parser.parseFile(ontologyfile)

print("Loaded the ontology!")

# The algorithm assumes conjunctions to always be over two concepts
# Ontologies in OWL can have conjunctions over an arbitrary number of concepts
# The following command changes all conjunctions so that they have at most two conjuncts
print("Converting to binary conjunctions")
gateway.convertToBinaryConjunctions(ontology)

# Get the TBox axioms
tbox = ontology.tbox()
axioms = tbox.getAxioms()

existentialrole = []
conjunctions = []
gci = []
equiv = []

print("These are the axioms in the TBox:")
for axiom in axioms:
    print(formatter.format(axiom))
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

# Get all concepts occurring in the ontology
allConcepts = ontology.getSubConcepts()
conceptNames = ontology.getConceptNames()

print("These are the concept names: ")
print([formatter.format(x) for x in conceptNames])

# Initialize reasoner and perform reasoning
subsumers = ELReasoner()
result = subsumers.ELreasoner(classname)
print(f"According to our reasoner, {classname} has the following subsumers: ")
for concept in result:
    print(" - ", formatter.format(concept))
