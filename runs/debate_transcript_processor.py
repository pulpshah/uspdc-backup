from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import openai
import json
from threading import Lock
import pandas as pd
import re
import time
import nltk
import spacy
import numpy as np
from collections import Counter
from threading import local

class TranscriptProcessor:
    def __init__(self):
        # Load English tokenizer, POS tagger, parser, NER, and word vectors
        self.nlp = spacy.load("en_core_web_sm")

        # Define a word list using nltk corpus
        self.english_vocab = set(w.lower() for w in nltk.corpus.words.words())

        self.open_ai_keys = [os.getenv(f"OPENAI_KEY_{i}") for i in range(1, 26)]
    
    def process_transcript(self, file_path, speakers_set):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Initialize an empty list to store the speakers and their speeches
        processed_transcript = []

        # Initialize an empty string to store the current speaker
        current_speaker = ''

        for line in lines:
            # Remove leading and trailing whitespaces
            line = line.strip()

            if not line:
                continue

            # Split the line into speaker and speech, the maxsplit parameter is set to 1
            split_line = line.split(':', 1)

            # Check if the line could be split into speaker and speech
            if len(split_line) == 2:
                # Potential speaker
                potential_speaker = split_line[0].strip().upper()
                
                # If the potential speaker is in our known speakers set
                if potential_speaker in speakers_set:
                    # Update the current speaker and append the speech to the transcript
                    current_speaker, speech = split_line
                    current_speaker = current_speaker.strip().upper()
                    speech = speech.strip()
                    
                    processed_transcript.append((current_speaker, speech))
                else:
                    # If the line could not be split into a valid speaker and speech, append it to the last speaker's last speech
                    processed_transcript[-1] = (processed_transcript[-1][0], processed_transcript[-1][1] + ' ' + line)
            else:
                # If the line could not be split, append it to the last speaker's last speech
                processed_transcript[-1] = (processed_transcript[-1][0], processed_transcript[-1][1] + ' ' + line)

        # Create a dictionary to count speaker turns
        speaker_turns_dict = {speaker: sum(1 for t in processed_transcript if t[0] == speaker) for speaker in speakers_set}

        return processed_transcript, speaker_turns_dict

    def write_transcript_to_file(self, transcript, output_path):
        with open(output_path, 'w') as file:
            for speaker_name, speaker_content in transcript:
                # Each line starts with the speaker name followed by their speech
                file.write(f'{speaker_name}: {speaker_content}\n')


    def transcript_to_dataframe(self, processed_transcript):
        df = pd.DataFrame(processed_transcript, columns=['speaker', 'content'])
        return df

    def configure_transcript_dataframe(self, df):
        df['turn_number'] = df.index + 1
        df['cumulative_speaker_turn_number'] = df.groupby('speaker').cumcount() + 1

        default_values = {
        'relevancy': 0,
        'turn_topic': 'empty',
        'word_count_points': 0,
        'sentence_count_points': 0,
        'named_entity_count_points': 0,
        'named_entities': 'empty',
        'bonus_word_points': 0,
        'bonus_word_words': 'empty',
        'base_score': 0.0,
        'E': 0.0, # change
        'P': 0.0, # change
        'L': 0.0, # change
        'E_expl': 'empty',
        'P_expl': 'empty',
        'L_expl': 'empty',
        'epl_multiplier': 0.0,
        'total_turn_score': 0.0,
        'cumulative_speaker_base_score': 0.0,
        'cumulative_speaker_total_score': 0.0,
        }

        for col, default_value in default_values.items():
            df[col] = default_value

        return df