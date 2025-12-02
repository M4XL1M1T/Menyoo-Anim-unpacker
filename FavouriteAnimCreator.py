#!/usr/bin/env python3
import os
import re
import time
import zipfile
import rarfile
from pathlib import Path

rarfile.UNRAR_TOOL = r"C:\Program Files\WinRAR\UnRAR.exe"

XML_CONTENT = '''<?xml version="1.0"?>
<PedAnims>

</PedAnims>
'''

PROMPT_TEXT_XML = (
    "The file 'FavouriteAnims.xml' does not exist.\n"
    "Do you want to create it with the default template? (Y/n): "
)

PROMPT_TEXT_DIR = (
    "The directory 'put your packed anims here' does not exist.\n"
    "Do you want to create it? (Y/n): "
)


def find_existing(path_name: str = 'FavouriteAnims.xml') -> Path | None:
    cwd = Path.cwd() / path_name
    if cwd.exists():
        return cwd
    script_dir = Path(__file__).resolve().parent / path_name
    if script_dir.exists():
        return script_dir
    return None


def ensure_directory(dir_name: str) -> Path:
    """Create directory if it doesn't exist."""
    target = Path.cwd() / dir_name
    target.mkdir(parents=True, exist_ok=True)
    return target


def create_file(target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('w', encoding='utf-8', newline='\n') as f:
        f.write(XML_CONTENT)


def add_anims_to_xml(xml_path: Path, anim_lines: list[str]) -> None:
    """Add animation lines to FavouriteAnims.xml before </PedAnims>."""
    if not anim_lines:
        print("No animations to add.")
        return
    
    try:
        with open(xml_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        formatted_lines = [f"\t{line}" for line in anim_lines]
        anim_content = '\n'.join(formatted_lines)
        new_content = content.replace('</PedAnims>', f'{anim_content}\n</PedAnims>')
        
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Added {len(anim_lines)} animation(s) to {xml_path.name}")
    except Exception as e:
        print(f"Error updating XML: {e}")


def ask_yes(prompt_text: str, default_yes: bool = True) -> bool:
    try:
        resp = input(prompt_text).strip()
    except EOFError:
        return default_yes
    if resp == '':
        return default_yes
    return resp.lower() in ('j', 'ja', 'y', 'yes')


def extract_zip(zip_path: Path, extract_to: Path) -> bool:
    """Extract a ZIP file to the target directory."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Extracted: {zip_path.name} → {extract_to}")
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"Error extracting {zip_path.name}: {e}")
        return False


def extract_rar(rar_path: Path, extract_to: Path) -> bool:
    """Extract a RAR file to the target directory using rarfile."""
    try:
        with rarfile.RarFile(str(rar_path)) as rar_ref:
            rar_ref.extractall(str(extract_to))
        print(f"Extracted: {rar_path.name} → {extract_to}")
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"Error extracting {rar_path.name}: {e}")
        return False


def extract_archives(anims_dir: Path) -> None:
    """Extract all ZIP and RAR files in the directory."""
    archives = list(anims_dir.glob('*.zip')) + list(anims_dir.glob('*.rar'))
    
    if not archives:
        print("No ZIP or RAR files found.")
        return
    
    print(f"Found {len(archives)} archive(s) to extract.")
    
    for archive in archives:
        extract_dir = anims_dir / archive.stem
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        if archive.suffix.lower() == '.zip':
            extract_zip(archive, extract_dir)
        elif archive.suffix.lower() == '.rar':
            extract_rar(archive, extract_dir)


def search_anim_dicts(search_dir: Path) -> list[str]:
    """Search for <Anim dict=" in all files recursively and return matching lines."""
    print("\nSearching for animation dictionaries...\n")
    
    found_lines = []
    found_count = 0
    
    for file_path in search_dir.rglob('*'):
        if file_path.is_file():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        if '<Anim' in line and 'dict=' in line:
                            stripped_line = line.strip()
                            if stripped_line and stripped_line not in found_lines:
                                found_lines.append(stripped_line)
                                print(f"Found: {stripped_line}")
                                found_count += 1
            except Exception as e:
                pass
    
    if found_count == 0:
        print("No animation dictionaries found.")
    else:
        print(f"\nTotal found: {found_count} animation dictionary entries.")
    
    return found_lines


def main() -> None:
    existing = find_existing()
    if existing:
        print(f"Found: '{existing}'")
    else:
        target = Path.cwd() / 'FavouriteAnims.xml'
        if ask_yes(PROMPT_TEXT_XML):
            create_file(target)
            print(f"File created: '{target}'")
        else:
            print('Cancelled. File was not created.')
            return
    
    anims_dir = Path.cwd() / 'put your packed anims here'
    if anims_dir.exists():
        print(f"Directory exists: '{anims_dir}'")
    else:
        if ask_yes(PROMPT_TEXT_DIR):
            anims_dir.mkdir(parents=True, exist_ok=True)
            print(f"Directory created: '{anims_dir}'")
        else:
            print('Cancelled. Directory was not created.')
            return
    
    extract_archives(anims_dir)
    
    anim_lines = search_anim_dicts(anims_dir)
    
    xml_path = Path.cwd() / 'FavouriteAnims.xml'
    if anim_lines:
        add_anims_to_xml(xml_path, anim_lines)


if __name__ == '__main__':
    main()
