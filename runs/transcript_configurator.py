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
from datetime import datetime

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

        'ethos_score': 0.0,
        'pathos_score': 0.0,
        'logos_score': 0.0,
        'E_Expl': 'empty',
        'E_Clauses': 'empty',
        'P_Expl': 'empty',
        'P_Clauses': 'empty',
        'L_Expl': 'empty',
        'L_Clauses': 'empty',
        
        'base_score': 0.0,
        'epl_multiplier': 0.0,
        'total_turn_score': 0.0,
        
        'cumulative_speaker_base_score': 0.0,
        'cumulative_speaker_total_score': 0.0,
        }

        for col, default_value in default_values.items():
            df[col] = default_value

        return df
    
class TranscriptConfigurator:
    def __init__(self):
        self.processor = TranscriptProcessor()

    def configure_transcript(self, original_transcript_path, known_speakers):
        output_file_name = original_transcript_path.split('/')[-1].replace('.txt', '_clean_.txt')
        output_file_path = os.path.join('clean', output_file_name)
        if not os.path.exists('clean/'):
            os.makedirs('clean/')
        processed_transcript, speaker_turns_dict = self.processor.process_transcript(original_transcript_path, known_speakers)
        self.processor.write_transcript_to_file(processed_transcript, output_file_path)

        transcript_df = self.processor.transcript_to_dataframe(processed_transcript)
        scoreboard_df = self.processor.configure_transcript_dataframe(transcript_df)

        return transcript_df, scoreboard_df
    
    def get_scoreboard_calculator(self, scoreboard_df):
        scoreboard_calculator = ScoreboardCalculator(scoreboard_df, self.processor.nlp, self.processor.english_vocab)
        return scoreboard_calculator
    
    def get_updated_scoreboard(self, original_transcript_path, known_speakers):
        transcript_df, scoreboard_df = self.configure_transcript(original_transcript_path, known_speakers)
        scoreboard_calculator = self.get_scoreboard_calculator(scoreboard_df)
        updated_scoreboard = scoreboard_calculator.update_scoreboard()
        return updated_scoreboard

class ScoreboardCalculator:
    def __init__(self, df, nlp, english_vocab):
        self.df = df
        self.nlp = nlp
        self.english_vocab = english_vocab

    def get_word_count_points(self, row):
        word_count = len(nltk.word_tokenize(row['content']))
        return word_count

    def get_sentence_count_points(self, row):
        sentence_count = len(nltk.sent_tokenize(row['content']))
        return sentence_count

    def get_named_entity_points(self, row):
        named_entity_count = len(self.nlp(row['content']).ents)
        return named_entity_count

    def get_named_entities(self, row):
        named_entities = self.nlp(row['content']).ents
        return named_entities

    def get_word_bonus_points(self, row):
        sentence_count = len(set(word.lower() for word in nltk.word_tokenize(row['content']) if word.lower() in self.english_vocab))
        return sentence_count

    def get_bonus_word_words(self, row):
        sentence_count = (set(word.lower() for word in nltk.word_tokenize(row['content']) if word.lower() in self.english_vocab))
        return sentence_count

    def calc_base_score(self, row):
        base_score = row['word_count_points'] + row['sentence_count_points'] + row['named_entity_count_points'] + row['bonus_word_points']
        return base_score
    
    def calc_epl_multiplier(self, row):
        epl_multiplier = (1 + ((row['ethos_score'] + row['pathos_score'] + row['logos_score']) / 30))
        return epl_multiplier
    
    def calc_total_turn_score(self, row):
        total_turn_score = row['base_score'] * row['epl_multiplier']
        return total_turn_score
    
    def calc_cumulative_speaker_base_score(self):
        self.df['cumulative_speaker_base_score'] = self.df.groupby('speaker')['base_score'].cumsum()
        return self.df
    
    def calc_cumulative_speaker_total_score(self):
        self.df['cumulative_speaker_total_score'] = self.df.groupby('speaker')['total_turn_score'].cumsum()
        return self.df

    def update_scoreboard(self):
        self.df['word_count_points'] = self.df.apply(self.get_word_count_points, axis=1)
        self.df['sentence_count_points'] = self.df.apply(self.get_sentence_count_points, axis=1)
        self.df['named_entity_count_points'] = self.df.apply(self.get_named_entity_points, axis=1)
        self.df['named_entities'] = self.df.apply(self.get_named_entities, axis=1)
        self.df['bonus_word_points'] = self.df.apply(self.get_word_bonus_points, axis=1)
        self.df['bonus_word_words'] = self.df.apply(self.get_bonus_word_words, axis=1)
        self.df['base_score'] = self.df.apply(self.calc_base_score, axis=1)
        self.df['epl_multiplier'] = self.df.apply(self.calc_epl_multiplier, axis=1)
        self.df['total_turn_score'] = self.df.apply(self.calc_total_turn_score, axis=1)
        
        self.calc_cumulative_speaker_base_score()
        self.calc_cumulative_speaker_total_score()

        return self.df

class GPTConcurrentRequester:
    def __init__(self, df, open_ai_keys, input_file_path, scoreboard_calculator):
        self.df = df
        self.open_ai_keys = open_ai_keys
        self.lock1 = Lock()
        self.lock2 = Lock()
        self.lock3 = Lock()
        self.input_file_path = input_file_path
        self.scoreboard_calculator = scoreboard_calculator
        
    def write_error_to_file(self, error_message, error_log_file_path):
        # Write the error message to the error log file
        with self.lock3:
            with open(error_log_file_path, 'a') as file:
                file.write(f"{error_message}\n")
        print(f"Wrote error to file: {os.path.relpath(error_log_file_path)}")

    def worker(self, idx, output_file_full, output_file_full_2, error_log_file_path):
        retries = 5
        parsed_content = None  # Initialize parsed_content here
        
        for attempt in range(retries):
            retry_temp = 1
            
            try:
                row = self.df.loc[idx]
                api_key = self.open_ai_keys[idx % len(self.open_ai_keys)]
                openai.api_key = api_key
                response = self.prompt_epl(row)
                parsed_content = self.extract_and_parse_content(response)
                self.write_responses_to_file(response, output_file_full, idx)
                self.write_responses_to_file(parsed_content, output_file_full_2, idx)
                break
            
            except Exception as e:
                error_message = ''
                if 'response' in locals() and response.get('choices') and len(response.get('choices')) > 0:
                    error_message = f'Error at index {idx} after {retry_temp} attempt(s): {str(e)}'
                    print(error_message)
                    error_message = f'Response content: {response["choices"][0]["message"]["content"]}'
                    print(error_message)
                    retry_temp += 1
                    
                else:
                    print(f'Error at index {idx} after {retry_temp} attempt(s): {str(e)}')
                
                self.write_error_to_file(error_message, error_log_file_path)
                retry_temp += 1
                
                time.sleep(1.5 ** attempt)
                
        return idx, parsed_content

    def get_unique_filename_json(self, output_directory, output_file_name_base):
        counter = 0
        while True:
            # Prepend the counter to the base file name
            output_file_name = f"{counter}_{output_file_name_base}.json" if counter != 0 else f"{output_file_name_base}.json"
            # Full path of the output file
            output_file_full = os.path.join(output_directory, output_file_name)
            # If this filename doesn't exist, we can use it
            if not os.path.exists(output_file_full):
                return output_file_name, output_file_full
            # Otherwise, increment the counter and try again
            counter += 1


    def get_epl(self, startturn=None, endturn=None, runcount=None):
        output_directory = os.path.join(os.path.dirname(self.input_file_path), "epl-scores")
    
        # Check if the output directory exists, if not create it
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            
        # Get the current date and create a new directory with it
        current_date = datetime.now().strftime("%m-%d")
        output_directory = os.path.join(output_directory, current_date)

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        # Use the basename of the input file to create the output filename
        output_file_path = os.path.basename(self.input_file_path).replace('.txt', '_response')
        
        # Get unique filenames for the 3 output files
        _, response_file_path = self.get_unique_filename_json(output_directory, output_file_path)
        _, content_key_file_path = self.get_unique_filename_json(output_directory, output_file_path + "_content")
        _, error_log_file_path = self.get_unique_filename_json(output_directory, output_file_path + "_errors")

        start = startturn if startturn is not None else 0
        end = endturn if endturn is not None else len(self.df)

        if runcount is not None:
            end = min(start + runcount, len(self.df))

        if end > len(self.df):
            end = len(self.df)
            print(f"Warning: The end point exceeded the length of the dataframe. It has been adjusted to the last turn: {end}")

        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = [executor.submit(self.worker, i, response_file_path, content_key_file_path, error_log_file_path) for i in range(start, end)]
            for future in as_completed(futures):
                try:
                    original_index, parsed_content = future.result()
                    with self.lock2:
                        self.update_dataframe_with_parsed_content(parsed_content, original_index)
                except Exception as e:
                    print(f"Error in a thread: {str(e)}")
                    

        self.df.sort_values('turn_number', inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        openai.api_key = None
        
        return self.df
        
    def prompt_epl(self, row):
        if not row['content']: 
            return "Error: A current sentence is required."

        content = f"Use your contextual awareness to evaluate the following debate snippet (may be incomplete) for Ethos, Pathos, and Logos on a scale from 0.0 - 9.9. For all non-zero values, provide a 1 sentence explanation, otherwise empty string. When applicable, also tell me exactly which clauses correlate most strongly to Ethos/Pathos/Logos, otherwise empty string. [Snippet: \'{row['content']}\'] Return only a JSON object in this schema: {{E: x.x, P: y.y, L: z.z, E_Expl: string, P_Expl:, string L_Expl: string, E_Clauses: dict, P_Clauses: dict, L_Clauses: dict}}."

        prompt = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a master debater and assistant to the judge of the US Presidential Debates."
                },
                {
                    "role": "user",
                    "content": content
                }
            ]
        )
        return prompt

    def extract_and_parse_content(self, response):
        # Extract the content from the response
        content_str = response['choices'][0]['message']['content']

        # Parse the content string into JSON
        content_json = json.loads(content_str)

        # Return the JSON content
        return content_json

    def write_responses_to_file(self, response, output_file_path, idx):
        # Write the response to a file
        with self.lock1:
            with open(output_file_path, 'a') as file:
                file.write(f"{idx}: {response}\n")

        # Get the relative path from the absolute path
        relative_path = os.path.relpath(output_file_path)
        print(f"Wrote response for index {idx} to file: {relative_path}")


    def update_dataframe_with_parsed_content(self, parsed_content, idx):
        if parsed_content:
            self.df.loc[idx, 'ethos_score'] = parsed_content['E']
            self.df.loc[idx, 'pathos_score'] = parsed_content['P']
            self.df.loc[idx, 'logos_score'] = parsed_content['L']
            self.df.loc[idx, 'E_Expl'] = parsed_content['E_Expl']
            self.df.loc[idx, 'E_Clauses'] = json.dumps(parsed_content['E_Clauses']) # Convert dict to string
            self.df.loc[idx, 'P_Expl'] = parsed_content['P_Expl']
            self.df.loc[idx, 'P_Clauses'] = json.dumps(parsed_content['P_Clauses']) # Convert dict to string
            self.df.loc[idx, 'L_Expl'] = parsed_content['L_Expl']
            self.df.loc[idx, 'L_Clauses'] = json.dumps(parsed_content['L_Clauses']) # Convert dict to string

            self.df.loc[idx, 'epl_multiplier'] = self.scoreboard_calculator.calc_epl_multiplier(self.df.loc[idx])
            self.df.loc[idx, 'total_turn_score'] = self.scoreboard_calculator.calc_total_turn_score(self.df.loc[idx])