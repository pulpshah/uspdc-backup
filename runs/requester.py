from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from time import datetime
import openai
import time
import json
import os

class GPTConcurrentRequester:
    def __init__(self, df, open_ai_keys, input_file_path, scoreboard_calculator):
        self.df = df
        self.open_ai_keys = open_ai_keys
        self.lock1 = Lock()
        self.lock2 = Lock()
        self.lock3 = Lock()
        self.input_file_path = input_file_path
        self.scoreboard_calculator = scoreboard_calculator
        
    def prompt_epl(self, row):
        if not row['content']: 
            return "Error: A current sentence is required."

        content = f"Use your contextual awareness to evaluate the following debate snippet from the US Presidential debate for Ethos, Pathos, and Logos on a scale from 0.0 - 9.9. The snippet may be incomplete, in which case just return 0 values or empty strings. For all non-zero values for EPL, provide a 1 sentence explanation. When applicable, also tell me exactly which clauses correlate most strongly to Ethos/Pathos/Logos, otherwise empty string. [Snippet: \'{row['content']}\'] Return only a JSON object in this schema: {{E: x.x, P: y.y, L: z.z, E_Expl: string, P_Expl:, string L_Expl: string, E_Clauses: dict, P_Clauses: dict, L_Clauses: dict}}. If you cannot, simply return an empty JSON object."

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

    def get_epl(self, startturn=None, endturn=None, runcount=None):
        output_directory = os.path.join(os.path.dirname(self.input_file_path), "epl_scores")

        # Check if the output directory exists, if not create it
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            
        # Get the current date and create a new directory with it
        current_date = datetime.now().strftime("%m-%d")
        output_directory = os.path.join(output_directory, current_date)

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Create the 3 new folders
        full_responses_directory = os.path.join(output_directory, "full_responses")
        if not os.path.exists(full_responses_directory):
            os.makedirs(full_responses_directory)

        content_only_directory = os.path.join(output_directory, "content_only")
        if not os.path.exists(content_only_directory):
            os.makedirs(content_only_directory)

        errors_directory = os.path.join(output_directory, "errors")
        if not os.path.exists(errors_directory):
            os.makedirs(errors_directory)
        
        # Use the basename of the input file to create the output filename
        output_file_path = os.path.basename(self.input_file_path).replace('.txt', '_response')
        
        # Get unique filenames for the 3 output files
        _, response_file_path = self.get_unique_filename_json(full_responses_directory, output_file_path)
        _, content_key_file_path = self.get_unique_filename_json(content_only_directory, output_file_path + "_content")
        _, error_log_file_path = self.get_unique_filename_json(errors_directory, output_file_path + "_errors")

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

    def extract_and_parse_content(self, response):
        # Extract the content from the response
        content_str = response['choices'][0]['message']['content']

        # Parse the content string into JSON
        content_json = json.loads(content_str)

        # Return the JSON content
        return content_json
    
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

    def write_responses_to_file(self, response, output_file_path, idx):
        # Write the response to a file
        with self.lock1:
            with open(output_file_path, 'a') as file:
                file.write(f"{idx}: {response}\n")

        # Get the relative path from the absolute path
        relative_path = os.path.relpath(output_file_path)
        print(f"Wrote response for index {idx} to file: {relative_path}")
        
    def write_error_to_file(self, error_message, error_log_file_path):
        with self.lock3:
            with open(error_log_file_path, 'a') as file:
                file.write(f"{error_message}\n")
        print(f"\nWrote error to file: {os.path.relpath(error_log_file_path)}")

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