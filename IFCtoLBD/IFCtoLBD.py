from datetime import datetime
import ifcopenshell as ios
import Namespace
import os
import re 

global baseURI 
inputFile = ""
targetFile = ""

includeBuildingElements = True
includeBuildingProperties = True
includeQuantities = True
includeGeometry = False

def convertIFCSPFtoTTL(inputFile, outputFile):
    inputFile = inputFile
    outputFile = outputFile
    now = datetime.now()
    current_time = now.strftime('%Y%m%d_%H%M%S')
	
    DEFAULT_PATH = "http://linkedbuildingdata.net/ifc/resources" + current_time + "/"
    global baseURI
    baseURI = DEFAULT_PATH

	#Enter the name of the ifc file behind pad between the " ". Just like the example. - reading file - IfcSpfReader
    pad = "Rijwoning_BM.ifc"
    model = ios.open(inputFile)

    f = open(outputFile, "w")
    writeTTLFileContent(model,f)    
    f.close()
    
def writeTTLFileContent(model, file):
    file.write(writeTTLHeader())
    file.write(writeLBDinstances(model,file))

def print_properties(properties, output):    
    for name, value in properties.items():   
        if name == "id":
            continue     
        name = cleanString(name)
        output += ";\n"
        if isinstance(value, int):          
            output += "\tprops:"+name+" \""+ str(value) +"\"^^xsd:int "
        elif isinstance(value, float):    
            output += "\tprops:"+name+" \""+ str(value) +"\"^^xsd:double "
        else:           
            output += "\tprops:"+name+" \""+ str(value) +"\"^^xsd:string "
    return output

""" def print_quantities(quantities, output):    
    for name, value in quantities.items():   
        if name == "id":
            continue     
        name = cleanString(name)
        output += ";\n"
        if isinstance(value, int):          
            output += "\tprops:"+name+" \""+ str(value) +"\"^^xsd:int "
        elif isinstance(value, float):    
            output += "\tprops:"+name+" \""+ str(value) +"\"^^xsd:double "
        else:           
            output += "\tprops:"+name+" \""+ str(value) +"\"^^xsd:string "
    return output """

def cleanString(name):
    name = ''.join(x for x in name.title() if not x.isspace())
    name = name.replace('\\', '')
    name = name.replace('/', '')
    return name



def writeTTLHeader():
    s = "# baseURI: " + baseURI + "\n"
    s+= "@prefix inst: <" + baseURI + "> .\n"
    s+= "@prefix rdf:  <" + Namespace.RDF + "> .\n"
    s+= "@prefix rdfs:  <" + Namespace.RDFS + "> .\n"
    s+= "@prefix xsd:  <" + Namespace.XSD + "> .\n"
    s+= "@prefix bot:  <" + Namespace.BOT + "> .\n"
    s+= "@prefix beo:  <" + Namespace.BEO + "> .\n"
    s+= "@prefix mep:  <" + Namespace.MEP + "> .\n"
    s+= "@prefix geom:  <" + Namespace.GEOM + "> .\n"
    s+= "@prefix props:  <" + Namespace.PROPS + "> .\n\n"

    s+= "inst: rdf:type <http://www.w3.org/2002/07/owl#Ontology> .\n\n"

    return s

def writeLBDinstances(model, f):
    output = ""
    output += writeSites(model,f)
    output += writeBuildings(model,f)
    output += writeStoreys(model,f)
    output += writeSpaces(model,f)
    output += writeElements(model,f)
    output += writeInterfaces(model,f)
    output += writeZones(model,f)
    return output

def writeSites(model,f):
    output = ""
    for s in model.by_type("IfcSite"):                
        output += "inst:site_"+str(s.id()) + "\n"
        output += "\ta bot:Site ;" + "\n"
        if(s.Name):
            output += "\trdfs:label \""+s.Name+"\"^^xsd:string ;" + "\n"
        if(s.Description):
            output += "\trdfs:comment \""+s.Description+"\"^^xsd:string ;" + "\n"        
        output += "\tbot:hasGuid \""+ ios.guid.expand(s.GlobalId) +"\"^^xsd:string ;" + "\n" # bot:hasGuid no such property in the bot ontology？
        output += "\tprops:hasCompressedGuid \""+ s.GlobalId +"\"^^xsd:string "
        for reldec in s.IsDecomposedBy:
            if reldec is not None:
                for b in reldec.RelatedObjects:
                    output += ";\n"
                    output += "\tbot:hasBuilding inst:building_"+ str(b.id()) + " "
        if(includeBuildingProperties):
            site_psets = ios.util.element.get_psets(s)
            for name, properties in site_psets.items():
                output = print_properties(properties, output)                             
                
        output += ". \n\n"
    return output

def writeBuildings(model,f):
    output = ""
    for b in model.by_type("IfcBuilding"):                
        output += "inst:building_"+str(b.id()) + "\n"
        output += "\ta bot:Building ;" + "\n"
        if(b.Name):
            output += "\trdfs:label \""+b.Name+"\"^^xsd:string ;" + "\n"
        if(b.Description):
            output += "\trdfs:comment \""+b.Description+"\"^^xsd:string ;" + "\n"        
        output += "\tbot:hasGuid \""+ ios.guid.expand(b.GlobalId) +"\"^^xsd:string ;" + "\n"
        output += "\tprops:hasCompressedGuid \""+ b.GlobalId +"\"^^xsd:string "
        for reldec in b.IsDecomposedBy:
            if reldec is not None:
                for st in reldec.RelatedObjects:
                    output += ";\n"
                    output += "\tbot:hasStorey inst:storey_"+ str(st.id()) + " "
        if(includeBuildingProperties):
            psets = ios.util.element.get_psets(b)
            for name, properties in psets.items():
                output = print_properties(properties, output)                             
                
        output += ". \n\n"
    return output

def writeStoreys(model,f):
    output = ""
    for b in model.by_type("IfcBuildingStorey"):                
        output += "inst:storey_"+str(b.id()) + "\n"
        output += "\ta bot:Storey ;" + "\n"
        if(b.Name):
            output += "\trdfs:label \""+b.Name+"\"^^xsd:string ;" + "\n"
        if(b.Description):
            output += "\trdfs:comment \""+b.Description+"\"^^xsd:string ;" + "\n"        
        output += "\tbot:hasGuid \""+ ios.guid.expand(b.GlobalId) +"\"^^xsd:string ;" + "\n"
        output += "\tprops:hasCompressedGuid \""+ b.GlobalId +"\"^^xsd:string "
        for reldec in b.IsDecomposedBy:
            if reldec is not None:
                for st in reldec.RelatedObjects:
                    output += ";\n"
                    output += "\tbot:hasSpace inst:space_"+ str(st.id()) + " "
        for relcontains in b.ContainsElements:
            if relcontains is not None:
                for st in relcontains.RelatedElements:
                    output += ";\n"
                    output += "\tbot:containsElement inst:element_"+ str(st.id()) + " "

        if(includeBuildingProperties):
            psets = ios.util.element.get_psets(b)
            for name, properties in psets.items():
                output = print_properties(properties, output)                             
                
        output += ". \n\n"
    return output

def writeSpaces(model,f):
    output = ""
    for b in model.by_type("IfcSpace"):                
        output += "inst:space_"+str(b.id()) + "\n"
        output += "\ta bot:Space ;" + "\n"
        if(b.Name):
            output += "\trdfs:label \""+b.Name+"\"^^xsd:string ;" + "\n"
        if(b.Description):
            output += "\trdfs:comment \""+b.Description+"\"^^xsd:string ;" + "\n"        
        output += "\tbot:hasGuid \""+ ios.guid.expand(b.GlobalId) +"\"^^xsd:string ;" + "\n"
        output += "\tprops:hasCompressedGuid \""+ b.GlobalId +"\"^^xsd:string "
        for relbounded in b.BoundedBy:
            if relbounded is not None:
                st = relbounded.RelatedBuildingElement
                output += ";\n"
                output += "\tbot:adjacentElement inst:element_"+ str(st.id()) + " "
        for relcontains in b.ContainsElements:
            if relcontains is not None:
                counter = 0
                for st in relcontains.RelatedElements:
                    if counter == 0:
                        output += ";\n"
                        output += "\tbot:containsElement inst:element_"+ str(st.id()) + " "
                        counter+=1
                    else:
                        output += ", inst:element_"+ str(st.id()) + " "
                        counter+=1

        if(includeBuildingProperties):
            psets = ios.util.element.get_psets(b)
            for name, properties in psets.items():
                output = print_properties(properties, output)    

        #if(includeQuantities):
        #    qsets = ios.util.element.get_qsets(b)
        #    for name, quantities in qsets.items():
        #        output = print_quantities(quantities, output)                          
                
        output += ". \n\n"
    return output

def writeZones(model,f):
    output = ""
    for z in model.by_type("ifcZone"):
        output += "inst:space_" + str(z.id()) + "\n"
        output += "\ta bot:Zone ;" + "\n"
        if(z.Name):
            output += "\trdfs:label \""+z.Name+"\"^^xsd:string ;" + "\n"
        if(z.Description):
            output += "\trdfs:comment \""+z.Description+"\"^^xsd:string ;" + "\n"        
        output += "\tprops:hasGuid \""+ ios.guid.expand(z.GlobalId) +"\"^^xsd:string ;" + "\n"
        output += "\tprops:hasCompressedGuid \""+ z.GlobalId +"\"^^xsd:string "
        for reldec in z.IsDecomposedBy:
            if reldec is not None:
                for sp in reldec.RelatedObjects:
                    output += ";\n"
                    output += "\tbot:hasSpace inst:space_"+ str(sp.id()) + " "
        if(includeBuildingProperties):
            psets = ios.util.element.get_psets(z)
            for name, properties in psets.items():
                output = print_properties(properties, output)                             
                
        output += ". \n\n"
    return output 

def writeElements(model,f):
    output = ""
    for b in model.by_type("IfcElement"):                
        output += "inst:element_"+str(b.id()) + "\n"
        output += "\ta bot:Element ;" + "\n"
        if(b.Name):
            output += "\trdfs:label \""+b.Name+"\"^^xsd:string ;" + "\n"
        if(b.Description):
            output += "\trdfs:comment \""+b.Description+"\"^^xsd:string ;" + "\n"        
        output += "\tbot:hasGuid \""+ ios.guid.expand(b.GlobalId) +"\"^^xsd:string ;" + "\n"
        output += "\tprops:hasCompressedGuid \""+ b.GlobalId +"\"^^xsd:string "

        for relvoids in b.HasOpenings:
            if relvoids is not None:
                st = relvoids.RelatedOpeningElement
                for relfills in st.HasFillings:
                    if relfills is not None:
                        filler = relfills.RelatedBuildingElement
                        output += ";\n"
                        output += "\tbot:hostsElement inst:element_"+ str(filler.id()) + " "

        for relvoids in b.HasOpenings:
            if relvoids is not None:
                st = relvoids.RelatedOpeningElement
                for relfills in st.HasFillings:
                    if relfills is not None:
                        filler = relfills.RelatedBuildingElement
                        output += ";\n"
                        output += "\tbot:hostsElement inst:element_"+ str(filler.id()) + " "

        if(includeBuildingProperties):
            psets = ios.util.element.get_psets(b)
            for name, properties in psets.items():
                output = print_properties(properties, output)                             
                
        output += ". \n\n"
    return output

def writeInterfaces(model,f):
    output = ""
    for b in model.by_type("IfcRelSpaceBoundary"):                
        output += "inst:interface_"+str(b.id()) + "\n"
        output += "\ta bot:Interface ;" + "\n"
        if(b.Name):
            output += "\trdfs:label \""+b.Name+"\"^^xsd:string ;" + "\n"
        if(b.Description):
            output += "\trdfs:comment \""+b.Description+"\"^^xsd:string ;" + "\n"        
        output += "\tbot:hasGuid \""+ ios.guid.expand(b.GlobalId) +"\"^^xsd:string ;" + "\n"
        output += "\tprops:hasCompressedGuid \""+ b.GlobalId +"\"^^xsd:string "

        sp = b.RelatingSpace
        el = b.RelatedBuildingElement
        if sp is not None:
            output += ";\n"
            output += "\tbot:interfaceOf inst:space_"+ str(sp.id()) + " "
        if el is not None:
            output += ";\n"
            output += "\tbot:interfaceOf inst:element_"+ str(el.id()) + " "                
                
        output += ". \n\n"
    return output

#Enter the name of the ifc file behind fname between "". Enter the file name in which de document is saved in front. namefile\\
if __name__ == '__main__':
    fname = "files\\Rijwoning_BM.ifc"
    ofile = fname[:-4]+".ttl"
    convertIFCSPFtoTTL(fname, ofile)

#the converted file is saved in the same file as the ifc.                                