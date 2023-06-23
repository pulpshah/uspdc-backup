import nltk
import textstat

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