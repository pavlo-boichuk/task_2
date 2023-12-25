import re
import sys
from pathlib import Path
import shutil


UKRAINIAN_SYMBOLS = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i", "ji", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")

TRANS_DICT = {}

archives_str = 'archives'
video_str = 'video'
audio_str = 'audio'
doc_str = 'documents'
images_str = 'images'
others_str = 'others'

archives_files = list()
video_files = list()
audio_files = list()
doc_files = list()
images_files = list()

folders = list()
others = list()

unknown_extensions = set()
known_extentions = {
    archives_str: set(),
    video_str: set(),
    audio_str: set(),
    doc_str: set(),
    images_str: set()
}

registered_extensions = {
    '/ZIP/GZ/TAR/': [archives_files, archives_str],
    '/AVI/MP4/MOV/MKV/': [video_files, video_str],
    '/MP3/OGG/WAV/AMR/': [audio_files, audio_str],
    '/DOC/DOCX/TXT/PDF/XLSX/PPTX/': [doc_files, doc_str],
    '/JPEG/PNG/JPG/SVG/': [images_files, images_str],
    'Not found': [others, others_str]
}


for key, value in zip(UKRAINIAN_SYMBOLS, TRANSLATION):
    
    TRANS_DICT[ord(key)] = value
    TRANS_DICT[ord(key.upper())] = value.upper()


def normalize(name):
    
    name, *extension = name.split('.')
    new_name = name.translate(TRANS_DICT)
    new_name = re.sub(r'\W', '_', new_name)
    
    return f"{new_name}.{'.'.join(extension)}"


def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()


def scan(folder):

    for item in folder.iterdir():

        if item.is_dir():
            if item.name not in ('archives', 'video', 'audio', 'documents', 'images', 'others'):
                folders.append(item)
                scan(item)
            continue

        extension = get_extensions(file_name=item.name)
        file_full_name = folder/item.name
        
        if not extension:
            others.append(file_full_name)
        else:
            try:
                find_extension = False

                for key_extension, container_list in registered_extensions.items():

                    if '/' + extension + '/' in key_extension:
                        
                        known_extentions[container_list[1]].add(extension)
                        container_list[0].append(file_full_name)

                        find_extension = True
                        break
                
                if not find_extension:
                    unknown_extensions.add(extension)
                    others.append(file_full_name)
                 
            except KeyError:
                unknown_extensions.add(extension)
                others.append(file_full_name)
                

def handle_files(folder_path, file_path, folder_name):

    if folder_name == archives_str:
        handle_archive(folder_path, file_path, folder_name)
    else:

        type_folder = folder_path/folder_name
        type_folder.mkdir(exist_ok=True)
        file_path.replace(type_folder/normalize(file_path.name))


def handle_archive(folder_path, file_path, archive_folder_name):

    archive_folder = folder_path / archive_folder_name
    archive_folder.mkdir(exist_ok=True)

    extention = Path(file_path.name).suffix
    archive_file_folder_name = normalize(file_path.name.replace(extention, '')) 

    archive_file_folder = archive_folder / archive_file_folder_name
    archive_file_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(file_path.resolve()), str(archive_file_folder.resolve()))
    except shutil.ReadError:
        archive_file_folder.rmdir()
        return
    except FileNotFoundError:
        archive_file_folder.rmdir()
        return
    
    file_path.unlink()


def remove_empty_folders(path):

    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass


def main():

    folder_path = Path(sys.argv[1]).resolve()

    scan(folder_path)

    for container_list in registered_extensions.values():
        for file in container_list[0]:
            handle_files(folder_path, file, container_list[1])
        
    remove_empty_folders(folder_path)


if __name__ == '__main__':

    main()