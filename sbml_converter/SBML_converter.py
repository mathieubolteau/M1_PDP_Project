import xml.dom.minidom
import json
import os
from tkinter import *
from tkinter import filedialog


"""
Reads metabolites from the SBML file and returns a dictionnary
"""


def getMetabolites(doc):
    species = doc.getElementsByTagName("species")
    metabolites = []
    for sp in species:
        metabolite = {}
        metabolite["id"] = sp.getAttribute("id")
        metabolite["name"] = sp.getAttribute("name")
        metabolite["compartment"] = sp.getAttribute("compartment")
        metabolite["charge"] = sp.getAttribute("fbc:charge")
        metabolite["formula"] = sp.getAttribute("fbc:chemicalFormula")
        metabolites.append(metabolite)
    return metabolites


"""
Reads products from the SBML file and returns a dictionnary
"""


def getProducts(products_list):
    final_products = {}
    for prod in products_list:
        products = prod.getElementsByTagName("speciesReference")
        for p in products:
            final_products[p.getAttribute("species")] = float(
                p.getAttribute("stoichiometry")
            )
    return final_products


"""
Reads reactants from the SBML file and returns a dictionnary
"""


def getReactants(reactants_list):
    final_reactants = {}
    for react in reactants_list:
        reactants = react.getElementsByTagName("speciesReference")
        for r in reactants:
            stoichio = -float(r.getAttribute("stoichiometry"))
            final_reactants[r.getAttribute("species")] = stoichio
    return final_reactants

'''
Returns a list of the elements which are int list1 but not in list2
'''
def difference(list1,list2):
    return(list(set(list1)-set(list2)))

"""
Reads gene reaction rule from the SBML file and returns a string
"""

def getGeneReactionRules(reaction):
    geneReactionRule = ''
    genes = reaction.getElementsByTagName('fbc:geneProductRef')
    if (len(genes))== 0:
        return geneReactionRule
    elif (len(genes))== 1:
        geneReactionRule = genes[0].getAttribute("fbc:geneProduct")
    else:
        ors = reaction.getElementsByTagName("fbc:or")
        if len(ors)>0: 
            for i in range(len(ors)):
                ands = ors[i].getElementsByTagName("fbc:and")
                if len(ands)>0:  
                    for a in ands:
                        aGeneList = a.getElementsByTagName("fbc:geneProductRef")
                        for j in range(len(aGeneList)):
                            if j == 0 :
                                geneReactionRule = geneReactionRule + " ( " + aGeneList[j].getAttribute("fbc:geneProduct")
                            elif j == (len(aGeneList)-1):
                                geneReactionRule = geneReactionRule + " and " + aGeneList[j].getAttribute("fbc:geneProduct") + ")"
                            else : 
                                geneReactionRule = geneReactionRule + " and " + aGeneList[j].getAttribute("fbc:geneProduct")
                        if i<(len(ors)-1):
                            geneReactionRule = geneReactionRule + " or "
                    oGeneList = ors[i].getElementsByTagName("fbc:geneProductRef")
                    oGeneList = difference(oGeneList,aGeneList)
                    for j in range(len(oGeneList)):
                        if geneReactionRule == "":
                            geneReactionRule = geneReactionRule + oGeneList[j].getAttribute("fbc:geneProduct")
                        else : 
                            geneReactionRule = geneReactionRule + " or " + oGeneList[j].getAttribute("fbc:geneProduct")
                else : 
                    oGeneList = ors[i].getElementsByTagName("fbc:geneProductRef")
                    for j in range(len(oGeneList)):
                        if geneReactionRule == "":
                            geneReactionRule = geneReactionRule + oGeneList[j].getAttribute("fbc:geneProduct")
                        else : 
                            geneReactionRule = geneReactionRule + " or " + oGeneList[j].getAttribute("fbc:geneProduct")
        else : 
            ands = reaction.getElementsByTagName("fbc:and")
            for i in range(len(ands)):
                geneList = ands[i].getElementsByTagName("fbc:geneProductRef")
                for j in range (len(geneList)):
                    if geneReactionRule == "":
                            geneReactionRule = geneReactionRule + geneList[j].getAttribute("fbc:geneProduct")
                    else : 
                        geneReactionRule = geneReactionRule + " and " + geneList[j].getAttribute("fbc:geneProduct")

    
    return geneReactionRule

"""
Reads reactions from the SBML file 
Calls functions getProducts() and getReactants() 
to deal with stoichiometry
Returns a dictionnary
"""


def getReactions(doc):
    reacts = doc.getElementsByTagName("reaction")
    reactions = []
    for re in reacts:
        reaction = {}
        products_list = re.getElementsByTagName("listOfProducts")
        products = getProducts(products_list)
        reactants_list = re.getElementsByTagName("listOfReactants")
        reactants = getReactants(reactants_list)
        reactants.update(products)
        reaction["id"] = re.getAttribute("id")
        reaction["name"] = re.getAttribute("name")
        reaction["metabolites"] = reactants
        # reaction["lower_bound"]= re.getAttribute("fbc:lowerFluxBound")
        # reaction["upper_bound"]=re.getAttribute("fbc:upperFluxBound")
        reaction["gene_reaction_rule"]= getGeneReactionRules(re)
        # reaction["subsystem"]=
        reactions.append(reaction)
    return reactions




"""
Reads genes from the SBML file and returns a dictionnary
"""

def getGenes(doc):
    allGenes = doc.getElementsByTagName("fbc:geneProduct")
    genes = []
    for g in allGenes:
        gene = {}
        gene["id"] = g.getAttribute("fbc:id")
        gene["name"] = g.getAttribute("fbc:name")
        genes.append(gene)
    return genes

"""
Reads compartments from the SBML file and returns a dictionnary
"""


def getCompartments(doc):
    comparts = doc.getElementsByTagName("compartment")
    compartments = {}
    for comp in comparts:
        compartments[comp.getAttribute("id")] = comp.getAttribute("name")
    return compartments


"""
Calls all reading functions and builds a json type variable
"""


def createJSON(doc):
    json = {}
    json["metabolites"] = getMetabolites(doc)
    json["reactions"] = getReactions(doc)
    json["genes"] = getGenes(doc)
    json["id"] = doc.getElementsByTagName("model")[0].getAttribute("id")
    json["compartments"] = getCompartments(doc)
    json["version"] = "1"

    return json


"""
Checks SBML level
"""


def formatVerif(doc):
    level = doc.getElementsByTagName("sbml")
    level = level[0].getAttribute("level")
    if level == "3":
        return True
    else:
        return False


# -------  GRAPHIC PART --------#

class App(object):
    def __init__(self, root):
        self.root = root
        self.textframe = Frame(self.root, bg="#6ca7c9")
        self.textframe.pack(fill="both", expand=True)
        self.label1 = Label(
        self.textframe, text="Importez votre fichier SBML", font=("Helvetica", 18),bg="#6ca7c9")
        self.label1.pack()
        choice_button = Button(self.textframe, text="Choisir un fichier", font=("Helvetica", 15),command=self.upload)
        choice_button.pack()
        self.label2 = Label(self.textframe, text="", font=("Helvetica", 14),bg="#6ca7c9")
        self.label2.pack()

    """
    On click, allows the user to select a SBML file
    Creates a directory for the converted file (if it doesn't exist)
    Reads the SBML file and saves a JSON file in the directory.
    """

    def upload(self):
        filename = filedialog.askopenfilename()
        print("Selected:", filename)
        try:
            doc = xml.dom.minidom.parse(filename)
        except Exception:
            self.label2.config(text="Fichier invalide, format xml uniquement.")
        fileFormat = formatVerif(doc)
        if fileFormat:
            json_file = createJSON(doc)
            fileName = json_file["id"] + ".json"
            path = "converted_files"
            try:
                os.mkdir(path)
            except OSError:
                print("Creation of the directory failed, already exists")
            file_to_open = "converted_files/" + fileName
            with open(file_to_open, "w") as outfile:
                json.dump(json_file, outfile)
                self.label2.config(
                    text="Fichier converti, disponible dans le dossier converted_files"
                )

        else:
            print("Format error")
            self.label2.config(
                text="Fichier invalide, format trop ancien \n Le convertisseur ne fonctionne qu'avec des fichier level 3"
            )


root = Tk()
root.title("Convertisseur SBML vers JSON")
root.minsize(600, 300)
app = App(root)
root.mainloop()


# MAIN

