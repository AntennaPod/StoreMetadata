#!/bin/python
import os
import subprocess
import platform
from pathlib import Path
import json

langs_and_fonts = {
    'ca': 'Sarabun-Bold',
    'de-DE': 'Sarabun-Bold',
    'en-US': 'Sarabun-Bold',
    'fr-FR': 'Sarabun-Bold',
    'he-IL': 'Arimo-Bold',
    'nl-NL': 'Sarabun-Bold',
    'it-IT': 'Sarabun-Bold',
    'es-ES': 'Sarabun-Bold'
}


def generate_text(text, font):
    print(text)
    os.system(
        "convert -size 1698x750 xc:none -gravity Center -pointsize 130 -fill '#167df0' -font "
        + font
        + ' -annotate 0 "'
        + text
        + '" /tmp/text.png')


def generate_tablet_text(text, font):
    print(text)
    os.system(
        "convert -size 1730x350 xc:none -gravity Center -pointsize 80 -fill '#167df0' -font "
        + font
        + ' -annotate 0 "'
        + text
        + '" /tmp/text.png')


def simple_phone(text, background_file, screenshotFile, outputFile, font):
    generate_text(text, font)
    os.system('convert templates/' + background_file
              + ' templates/phone.png -geometry +0+0 -composite '
              + screenshotFile + ' -geometry +306+992 -composite '
              + '/tmp/text.png -geometry +0+0 -composite '
              + outputFile)


def simple_tablet(text, screenshot_file, output_file, font):
    generate_tablet_text(text, font)
    os.system('convert ' + screenshot_file + ' -resize 1285 "/tmp/resized-image.png"')
    os.system('convert templates/tablet.png '
              + '/tmp/resized-image.png -geometry +224+459 -composite '
              + '/tmp/text.png -geometry +0+0 -composite '
              + output_file)


def two_phones(text, raw_screenshots_path, output_file, font):
    generate_text(text, font)
    os.system('convert templates/background2.png '
              + 'templates/twophones-a.png -geometry +0+10 -composite '
              + raw_screenshots_path + '/03a.png -geometry +119+992 -composite '
              + 'templates/twophones-b.png -geometry +0+0 -composite '
              + raw_screenshots_path + '/03b.png -geometry +479+1540 -composite '
              + '/tmp/text.png -geometry +0+0 -composite '
              + output_file)


def generate_screenshots(language, font):
    with open('strings/' + language + '.json') as textDefinitions:
        texts = json.load(textDefinitions)

    raw_screenshots_path = 'raw/' + language
    output_path = '../listings/' + language + "/graphics"
    Path(output_path + '/phone-screenshots').mkdir(parents=True, exist_ok=True)
    Path(output_path + '/large-tablet-screenshots').mkdir(parents=True, exist_ok=True)

    if not Path(raw_screenshots_path + '/00.png').is_file():
        raw_screenshots_path = 'raw/en-US'

    simple_phone(texts["00.png"], 'background1.png', raw_screenshots_path + '/00.png', output_path + '/phone-screenshots/00.png', font)
    two_phones(texts["01.png"], raw_screenshots_path, output_path + '/phone-screenshots/01.png', font)
    simple_phone(texts["02.png"], 'background1.png', raw_screenshots_path + '/01.png', output_path + '/phone-screenshots/02.png', font)
    simple_phone(texts["03.png"], 'background2.png', raw_screenshots_path + '/02.png', output_path + '/phone-screenshots/03.png', font)
    simple_phone(texts["04.png"], 'background1.png', raw_screenshots_path + '/04.png', output_path + '/phone-screenshots/04.png', font)
    simple_phone(texts["05.png"], 'background2.png', raw_screenshots_path + '/05.png', output_path + '/phone-screenshots/05.png', font)
    simple_tablet(texts["tablet.png"], raw_screenshots_path + '/tablet.png', output_path + '/large-tablet-screenshots/tablet.png', font)
    os.system('mogrify -resize 1120 "' + output_path + '/phone-screenshots/0*.png"')
    os.system('mogrify -resize 1120 "' + output_path + '/large-tablet-screenshots/tablet.png"')


def check_os():
    """Currently only working on Linux."""
    return platform.system() == 'Linux' or platform.system() == 'Darwin'


def check_packages():
    """ImageMagicks convert and morgify are required."""
    common = b'Version: ImageMagick'
    try:
        return common in subprocess.check_output(['convert', '-version']) and common in subprocess.check_output(
            ['mogrify', '-version'])
    except subprocess.CalledProcessError:
        return False


def check_fonts():
    """Check if required fonts are installed."""
    try:
        for font in langs_and_fonts.values():
            if bytes(font.encode()) not in subprocess.check_output(['fc-list', '-v']):
                return False
    except subprocess.CalledProcessError:
        return False
    return True


if __name__ == '__main__':
    assert (check_os())
    assert (check_packages())
    assert (check_fonts())
    for lang, font in langs_and_fonts.items():
        generate_screenshots(lang, font)
