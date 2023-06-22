from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    df = pd.read_csv("sep-29-2008-final-scoreboard-csv-2.csv")
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Removing 'Unnamed' columns
    df['row_attr'] = df['speaker'].apply(lambda x: f'data-speaker="{x.upper()}"')
    return render_template('table.html', df=df)

if __name__ == '__main__':
    app.run(debug=True)
    
    