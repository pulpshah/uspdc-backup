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
        
        self.calc_cumulative_speaker_base_score()
        self.calc_cumulative_speaker_total_score()

        return self.df

class GPTConcurrentRequester:
    def __init__(self, df, open_ai_keys, input_file_path, scoreboard_calculator):
        self.df = df
        self.open_ai_keys = open_ai_keys
        self.lock1 = Lock()
        self.lock2 = Lock()
        self.input_file_path = input_file_path
        self.scoreboard_calculator = scoreboard_calculator

    def worker(self, idx, output_file_full):
        retries = 5
        for attempt in range(retries):
            try:
                row = self.df.loc[idx]
                api_key = self.open_ai_keys[idx % len(self.open_ai_keys)]
                openai.api_key = api_key
                response = self.prompt_epl(row)
                parsed_content = self.extract_and_parse_content(response)
                self.write_responses_to_file(response, output_file_full, idx)
                break
            except Exception as e:
                if attempt == retries - 1:
                    print(f'Error at index {idx} after {retries} attempts: {str(e)}')
                    print(f'Response content: {response["choices"][0]["message"]["content"]}')  
                else:
                    time.sleep(2 ** attempt)
        return idx, parsed_content
    
    def get_epl(self, startturn=None, endturn=None, runcount=None):
        output_directory = os.path.join(os.path.dirname(self.input_file_path), "epl-scores")
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        output_file_name = os.path.basename(self.input_file_path).replace('.txt', '_withEPL.txt')
        output_file_full = os.path.join(output_directory, output_file_name)
        
        start = startturn if startturn is not None else 0
        end = endturn if endturn is not None else len(self.df)

        if runcount is not None:
            end = min(start + runcount, len(self.df))

        if end > len(self.df):
            end = len(self.df)
            print(f"Warning: The end point exceeded the length of the dataframe. It has been adjusted to the last turn: {end}")

        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = [executor.submit(self.worker, i, output_file_full) for i in range(start, end)]
            for future in as_completed(futures):
                try:
                    original_index, parsed_content = future.result()
                    with self.lock2:
                        self.update_dataframe_with_parsed_content(parsed_content, original_index)
                except Exception as e:
                    print(f"Error in a thread: {str(e)}")
            
        # Change this line to use scoreboard_calculator's update_scoreboard method
        self.df = self.scoreboard_calculator.update_scoreboard()  # change this line

        self.df.sort_values('turn_number', inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        openai.api_key = None
        
        return self.df
        
    def prompt_epl(self, row):
        if not row['content']: 
            return "Error: A current sentence is required."

        content = f"Evaluate the following snippet for Ethos (E), Pathos (P), and Logos (L). (Scale: 0.0 - 9.9) For non-zero score only: provide a brief explanation, otherwise leave empty string. It should be equally difficult to score 0.0 as it would be to score 9.9. [Snippet: \'{row['content']}\'] Return only a JSON object in this schema: {{E: x.x, P: y.y, L: z.z, E_Expl: string, P_Expl:, string L_Expl: string}}. Explanations must be 1 sentence long."

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
        content = response['choices'][0]['message']['content']

        # Parse the content using json.loads and return the result
        parsed_content = json.loads(content)
        return parsed_content

    def write_responses_to_file(self, response, output_file_full, idx):
        # Write the response to a file
        with self.lock1:
            with open(output_file_full, 'a') as file:
                file.write(f"{idx}: {response}\n")

    def update_dataframe_with_parsed_content(self, parsed_content, idx):
        # Update the dataframe with the parsed content
        self.df.loc[idx, 'E_score'] = parsed_content['E']
        self.df.loc[idx, 'P_score'] = parsed_content['P']
        self.df.loc[idx, 'L_score'] = parsed_content['L']
        self.df.loc[idx, 'E_Expl'] = parsed_content['E_Expl']
        self.df.loc[idx, 'P_Expl'] = parsed_content['P_Expl']
        self.df.loc[idx, 'L_Expl'] = parsed_content['L_Expl']

