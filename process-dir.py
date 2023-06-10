import os
import re
import json

def process_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), 'r') as file:
                lines = file.readlines()

            result = {
                'number_of_lines': len(lines),
                'number_of_blank_lines': len([i for i, line in enumerate(lines, start=1) if line.strip() == '']),
                'number_of_sentences': len(re.findall(r'[.!?]', ''.join(lines))),
                'number_of_words': len(''.join(lines).split()),
                'number_of_chars_excluding_spaces': len(''.join(lines).replace(' ', '')),
                'number_of_chars_including_spaces': len(''.join(lines)),
                'number_of_ellipses': len(re.findall(r'(\.\s*){2,}', ''.join(lines))),
                'number_of_dashes': len(re.findall(r'-', ''.join(lines))),
                'number_of_exclamation_marks': ''.join(lines).count('!'),
                'number_of_question_marks': ''.join(lines).count('?'),
                'number_of_words_in_brackets': len(re.findall(r'\[.*?\]|\(.*?\)', ''.join(lines))),
                'number_of_other_special_chars': len(re.findall(r'[^a-zA-Z0-9\s\.\-!?]', ''.join(lines))),
                'number_of_all_caps_words': len([word for word in ''.join(lines).split() if word.isupper()]),
            }

            attributes = {
                'number_of_blank_lines': [],
                'number_of_ellipses': [],
                'number_of_dashes': [],
                'number_of_words_in_brackets': [],
                'number_of_other_special_chars': [],
                'number_of_all_caps_words': [],
            }

            for i, line in enumerate(lines, start=1):
                if line.strip() == '':
                    attributes['number_of_blank_lines'].append(i)
                for match in re.finditer(r'(\.\s*){2,}', line):
                    attributes['number_of_ellipses'].append((i, match.start()))
                for match in re.finditer(r'-', line):
                    attributes['number_of_dashes'].append((i, match.start()))
                for match in re.finditer(r'\[.*?\]|\(.*?\)', line):
                    attributes['number_of_words_in_brackets'].append((i, match.start()))
                for match in re.finditer(r'[^a-zA-Z0-9\s\.\-!?]', line):
                    attributes['number_of_other_special_chars'].append((i, match.start()))
                for word in line.split():
                    if word.isupper():
                        attributes['number_of_all_caps_words'].append((i, line.find(word)))

            with open(os.path.join(directory, filename.replace('.txt', '.json')), 'w') as json_file:
                json.dump(result, json_file, indent=4)

            for attribute, values in attributes.items():
                attribute_directory = os.path.join(directory, attribute)
                os.makedirs(attribute_directory, exist_ok=True)
                with open(os.path.join(attribute_directory, filename.replace('.txt', f'-{attribute}.json')), 'w') as json_file:
                    json.dump(values, json_file, indent=4)
