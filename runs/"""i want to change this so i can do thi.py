"""i want to change this so i can do this:

ai_scores = get_epl(input_df, outputfile_name)
filled_scoreboard = load_scores(outputfile_name, input_df)

filled_scoreboard is now done


here's how it would look from the beginning:

step 1: load data

transcript = "../runs/2008-09-26-debate-preclean.txt"

step 2: get speaker turns and validated transcript:

def process_transcript(file_path, speakers_set):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Initialize an empty list to store the speakers and their speeches
    transcript = []

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
                
                transcript.append((current_speaker, speech))
            else:
                # If the line could not be split into a valid speaker and speech, append it to the last speaker's last speech
                transcript[-1] = (transcript[-1][0], transcript[-1][1] + ' ' + line)
        else:
            # If the line could not be split, append it to the last speaker's last speech
            transcript[-1] = (transcript[-1][0], transcript[-1][1] + ' ' + line)

    # Create a dictionary to count speaker turns
    speaker_turns = {speaker: sum(1 for t in transcript if t[0] == speaker) for speaker in speakers_set}

    return transcript, speaker_turns

def write_transcript_to_file(transcript, output_path):
    with open(output_path, 'w') as file:
        for speaker, speech in transcript:
            # Each line starts with the speaker name followed by their speech
            file.write(f'{speaker}: {speech}\n')

known_speakers = {'LEHRER', 'OBAMA', 'MCCAIN'}
new_transcript, speaker_turns = process_transcript(transcript, known_speakers)
write_transcript_to_file(new_transcript, '2008-9-29-clean-4.txt')

step 3: create the wireframe for the scoreboard:

# Create DataFrame from transcript
df = pd.DataFrame(new_transcript, columns=['Speaker', 'Content'])

# Add 'Turn' column (simply the index + 1)
df['Turn'] = df.index + 1

# Add 'Cumulative_Speaker_Turn' column
df['Cumulative_Speaker_Turn'] = df.groupby('Speaker').cumcount() + 1

# Initialize the rest of the columns with default values
default_values = {
    'Base_Score': 0.0,
    'EPL_Multiplier': 0.0,
    'Total_Score': 0.0,
    'Sentence_Count': 0,
    'Word_Count': 0,
    'Word_Count_Bonus': 0,
    'Named_Entity_Count': 0,
    'E': 0.0,
    'P': 0.0,
    'L': 0.0,
    'E_Expl': 'Empty',
    'P_Expl': 'Empty',
    'L_Expl': 'Empty',
    'Cumulative_Speaker_Base_Score': 0.0,
    'Cumulative_Speaker_Total_Score': 0.0
}

for col, default_value in default_values.items():
    df[col] = default_value

# Reorder the columns
empty_scoreboard = df[['Turn', 'Speaker', 'Content', 'Cumulative_Speaker_Turn', 'Base_Score', 'EPL_Multiplier', 'Total_Score', 
         'Sentence_Count', 'Word_Count', 'Word_Count_Bonus', 'Named_Entity_Count', 'E', 'P', 'L', 'E_Expl', 
         'P_Expl', 'L_Expl', 'Cumulative_Speaker_Base_Score', 'Cumulative_Speaker_Total_Score']]

step 4: get the initial scores calculated and placed:

def calculate_scores(df):
    df['Sentence_Count'] = df['Content'].apply(lambda x: len(nltk.sent_tokenize(x)))
    df['Word_Count'] = df['Content'].apply(lambda x: len(nltk.word_tokenize(x)))
    df['Word_Count_Bonus'] = df['Content'].apply(lambda x: len(set(w.lower() for w in nltk.word_tokenize(x) if w.lower() in english_vocab)))
    df['Named_Entity_Count'] = df['Content'].apply(lambda x: len(nlp(x).ents))
    
    df['Base_Score'] = df['Sentence_Count'] + df['Word_Count'] + df['Word_Count_Bonus'] + df['Named_Entity_Count']
    df['Total_Score'] = df['Base_Score']  # Initially Total_Score is the same as Base_Score

    # Calculate EPL Multiplier based on current E, P, L scores
    df['EPL_Multiplier'] = (df['E'].astype(float) + df['P'].astype(float) + df['L'].astype(float)) / 30
    
    df['Cumulative_Speaker_Base_Score'] = df.groupby('Speaker')['Base_Score'].cumsum()
    df['Cumulative_Speaker_Total_Score'] = df.groupby('Speaker')['Total_Score'].cumsum() 
    df['Cumulative_Speaker_Turn'] = df.groupby('Speaker').cumcount() + 1

    return df

# Calculate the initial scores
scoreboard = calculate_scores(empty_scoreboard)

then implement the changes i mentioned at the top of this message:

use concurrent processes to use 25 workers to iterate through the scoreboard from the previous step, and send requests to GPT using the prompt function:

def prompt_epl(row):
    if not row['Content']: # Ensure that there is a current sentence
        return "Error: A current sentence is required."

    # Initialize content with the current sentence
    content = f"Evaluate the following snippet for Ethos (E), Pathos (P), and Logos (L). (Scale: 0.0 - 9.9) For non-zero score only: provide a brief explanation, otherwise leave empty string. It should be equally difficult to score 0.0 as it would be to score 9.9. [Snippet: \'{row['Content']}\'] Return only a JSON object in this schema: {{E: x.x, P: y.y, L: z.z, E_Expl: string, P_Expl:, string L_Expl: string}}. Explanations must be 1 sentence long."

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

write the responses to a json

read and parse the json to find E, P, L, and the 3 corresponding explainer texts and do 2 things:

update the scoreboard dataframe with the new information and
write the parsed content to a new JSON file that contains the ORIGINAL speaker, turn, and content of the speakers speech"""