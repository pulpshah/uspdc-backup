# Base_Score: (CSC + WC + WC_bonus + NEC)
# complete sentences + 1
# words + 1 (incl. stopwords)
# defined words, unique + 1 (excl. stopwords)
# named entities, unique + 1

# EPL bonus: 
# [(E + P + L) / 30]

# Total Score = Base_Score * (1 + EPL_Bonus)



Turn	Speaker	Content	Total_Score Base_Score EPL_Multiplier Sentence_Count	Word_Count Word_Count_Bonus Named_Entity_Count E P L E_Expl P_Expl L_Expl Cumulative_Speaker_Score



Turn - what turn in the transcript is it
Speaker - who is speaking
Content - what are they saying

Total_Score - 0 (until scores are calculated) [equation = Base_Score * EPL_Multiplier]
Base_Score - sentence_count + word count + word count bonus + named entity count
EPL_Multiplier - [(E + P + L) / 30]
Sentence_Count - sentence count
Word_Count - word count of 'content'
Word_Count_Bonus - number of unique, defined words (found in an english dictionary) found in 'content'
Named_Entity_Count - number of named entities found in 'content'

E (0.0 - 9.9) returned by GPT
P (0.0 - 9.9) returned by GPT
L (0.0 - 9.9) returned by GPT

E_Expl
P_Expl
L_Expl

Cumulative_Speaker_Turn - how many times has the speaker spoken? (including current row)

Cumulative_Speaker_Base_Score - cumulative base points speaker has earned so far

Cumulative_Speaker_Total_Score - cumulative total points speaker has earned so far