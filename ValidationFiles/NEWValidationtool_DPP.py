from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # Importeer getSampleStyleSheet
from pyshacl import validate
from rdflib import Graph, Namespace
import re


# URI ontology
dpp = Namespace("http://www.semanticweb.org/janneke.bosma/DPP#")   

# Loads shacl and ontology 
sg = Graph().parse(r"files\\SHACL1.0.ttl", format="turtle")
# ont = Graph().parse(r"files\\DPP_Ont.ttl", format="turtle")

# Load the data graphs to check (save these files in the python environment and put the filename below in case it is saved in a file)
folder_name = "files\\"

# In the file_names below write down the name of the turtle file you want to validate
file_names = [
         "TestfileX.ttl",
]
data_files = [folder_name + s for s in file_names]


# Name of Validation report in PDF (text between "titel" can be altered)
pdf_file = "validation_results.pdf"

# Create PDF
pdf_doc = SimpleDocTemplate(pdf_file, pagesize=letter)
styles = getSampleStyleSheet()

# Title
title_style = ParagraphStyle('Title', parent=styles['Normal'])
title_style.alignment = 0  # text is linked out on the left side 

pdf_content = []

# List to check missing words
missing_words = {}

for data_file in data_files:
    data_graph = Graph().parse(data_file, format="turtle")
    
    # Classes to check
    words_to_check = ['dpp:log', 'dpp:classificationCode', 'bmp:manufacturer', 'dpp:owner', 
                      'dpp:origin', 'dpp:conditionAssessment', 'dpp:futureFunction', 
                      'dpp:reusabilityPotential', 'dpp:recyclingPotential', 'dpp:proofOfReuse', 
                      'dpp:externalParty', 'dpp:disassemblyPotential']
    
    # Checks classes and add missing classes in PDF
    missing_words[data_file] = []
    for word in words_to_check:
        if word not in data_graph.serialize(format="turtle"):
            missing_words[data_file].append(word)

if missing_words:
    pdf_content.append(Paragraph("Validation Report", styles['Title']))  # add titel
    for file, words in missing_words.items():
        pdf_content.append(Paragraph(file, styles['Heading2']))  # bold file name
        pdf_content.append(Paragraph("- " + "\n- ".join(words), styles['Normal']))
    pdf_content.append(Paragraph("-----------------------------------------------------------------------------------------", styles['Normal']))

# SHACL validation
for data_file in data_files:
    data_graph = Graph().parse(data_file, format="turtle")

    r = validate(data_graph,                 
                 shacl_graph=sg,
               #  ont_graph=ont,
              #   inference=None,
                 #   abort_on_first=False,
                 #   allow_infos=False,
                 #   allow_warnings=False,
                 #   meta_shacl=False,
                 #   advanced=False,
                 #   js=False,
                 #   debug=False
                 )
    conforms, results_graph, results_text = r

    val_results_str = f"Validation results for {data_file}:\n"
    append_file_name = val_results_str + results_text
    parts = append_file_name.split("message:")

    if parts:
        # For each index in the total list
        for index, part in enumerate(parts):
            # Search file in which the validation results belong
            for file_name in file_names:
                # het validation_results bestand heeft alleen de naam van het bestand erin staan, dus ik moet die lostrekken van de map
                if file_name in part:
                    # File found in which we search for the GUID

                    # Search for compressed GUID beloning to the focus node 
                    data_graph = Graph().parse(folder_name+file_name, format="turtle")
                    full_file_in_memory = data_graph.serialize(format="turtle")

                    # Extract data from input_string
                    pattern = r'Focus Node:(.*?)\n'
                    matches = re.findall(pattern, part, re.DOTALL)

                    # Store data in a list
                    data_list = [match.strip() for match in matches]

                    # Assume that one inst can only have one GUID
                    data_list = list(set(data_list))

                    guid_value = []
                    # Search in another string using entries from data_list
                    for entry in data_list:
                        entry_index = full_file_in_memory.find(entry)
                        if entry_index != -1:
                            # Look for the first occurrence of "props:hasCompressedGuid"
                            guid_pattern = r'props:hasCompressedGuid "(.*?)"'
                            search_substring = full_file_in_memory[entry_index:]
                        guid_match = re.search(guid_pattern, search_substring)
                        if guid_match:
                            # Now add the GUID after the inst
                            parts[index] = part.replace(f"Focus Node: {entry}", f"Focus Node: {entry}"+f"\n\tCompressed GUID: {guid_match.group(1)}")

        # Results in text file and terminal
        with open("validation_results.txt", "a") as output_file:
            for part in parts:
                output_file.write("message:" + part.strip() + "\n\n")

    # Results in PDF
    pdf_content.append(Paragraph(f"Validation results for {data_file}:", styles['Heading1']))
    
    # Format in PDF
    if parts:
        for part in parts:
            # Marker voor Constraint Violation
            if "Constraint Violation" in part:  
                part = part.replace("Constraint Violation", "<br/><br/><b>Constraint Violation</b>")
            # Marker voor de compressed GUIDs (Compressed GUID: ...)
            part = re.sub(r'(Compressed GUID: .*?)\n', r'<b>\1</b>\n', part)
            pdf_content.append(Paragraph(part.strip(), styles['Normal']))
            pdf_content.append(Paragraph("\n", styles['Normal']))
    else:
        pdf_content.append(Paragraph("No validation results found.", styles['Normal']))  # Add message if no results found
        
pdf_doc.build(pdf_content)

print('done')