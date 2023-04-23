import xml.etree.ElementTree as ET

# Load the XML file
tree = ET.parse('output.xml')
root = tree.getroot()

# Find all redundant EXIF elements
for photo in root:
    for exif in photo:
        inner_exif_tag = exif.findall("EXIF")
        photo.append(inner_exif_tag[0])
        photo.remove(exif)
        break

# Save the modified XML tree to a file
tree.write('filename_modified.xml')
