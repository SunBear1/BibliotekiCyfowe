import os
from xml.etree.ElementTree import Element, SubElement, ElementTree

import exifread
import piexif
import cloudmersive_image_api_client as cloudmersive
from PIL import Image

configuration = cloudmersive.Configuration()
configuration.api_key['Apikey'] = 'fd34710b-605f-464b-95c9-71c136b1cc0f'
cloudmersive_client = cloudmersive.RecognizeApi(cloudmersive.ApiClient(configuration))


def get_exif_data(image_path: str, element) -> str:
    """
    Extracts all EXIF metadata from an image file.
    :param image_path: path to image
    :return: list of exif metadata
    """
    f = open(image_path, 'rb')
    tags = exifread.process_file(f)
    f.close()
    exif = SubElement(element, 'EXIF')

    for tag, value in tags.items():
        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            tag_name = tag.replace(' ', '').replace('', '')
            tag_element = SubElement(exif, tag_name)
            tag_element.text = str(value)
    return exif


def reduce_image_size(image_path: str):
    """
    Loads an image, reduces its size and saves the smaller version as a new image. Returns new image path.
    :param image_path: path to image
    :return:
    """
    with Image.open(image_path) as image:
        width, height = image.size
        if width > 1000 or height > 1000:

            if width > height:
                new_width = 1000
                new_height = int(height * (new_width / width))
            else:
                new_height = 1000
                new_width = int(width * (new_height / height))

            image = image.resize((new_width, new_height))
            exif_dict = piexif.load(image.info['exif'])
            image.save(image_path, exif=piexif.dump(exif_dict))


def get_image_description(image_path: str) -> str:
    """
    Fetches auto generated image description
    :param image_path: path to image
    :return: auto generated image description
    """
    response = cloudmersive_client.recognize_describe(image_file=image_path)
    return response.best_outcome.description


if __name__ == "__main__":
    IMAGES_DIR = "images"
    photo_id = 0
    xml_root = Element('photos')

    for image_name in os.listdir(IMAGES_DIR):
        image_path = os.path.join(IMAGES_DIR, image_name)
        photo = Element('photo', {'id': str(photo_id), 'name': image_name})

        exif_tag = SubElement(photo, 'EXIF')
        exif_tag = get_exif_data(image_path=image_path, element=exif_tag)

        reduce_image_size(image_path=image_path)
        description_tag = SubElement(photo, 'description')
        description_tag.text = get_image_description(image_path=image_path)

        improved_description_tag = SubElement(photo, 'improved_description')
        improved_description_tag.text = "PLACEHOLDER"

        print(f"photo with ID {photo_id} processed.")
        photo_id += 1
        xml_root.append(photo)

    ElementTree(xml_root).write("output.xml")
