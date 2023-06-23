from collections import OrderedDict

debate_dict = OrderedDict([
    ("2020", {
        "info": "https://www.debates.org/debate-history/2020-debates/",
        "transcripts": [
            ("09-29", "https://www.debates.org/voter-education/debate-transcripts/september-29-2020-debate-transcript/"),
            ("10-07", "https://www.debates.org/voter-education/debate-transcripts/vice-presidential-debate-at-the-university-of-utah-in-salt-lake-city-utah/"),
            ("10-22", "https://www.debates.org/voter-education/debate-transcripts/october-22-2020-debate-transcript/")
        ]
    }),
    ("2016", {
        "info": "https://www.debates.org/debate-history/2016-debates/",
        "transcripts": [
            ("09-26", "https://www.debates.org/voter-education/debate-transcripts/september-26-2016-debate-transcript/"),
            ("10-04", "https://www.debates.org/voter-education/debate-transcripts/october-4-2016-debate-transcript/"),
            ("10-09", "https://www.debates.org/voter-education/debate-transcripts/october-9-2016-debate-transcript/"),
            ("10-19", "https://www.debates.org/voter-education/debate-transcripts/october-19-2016-debate-transcript/")
        ]
    }),
    ("2012", {
        "info": "https://www.debates.org/debate-history/2012-debates/",
        "transcripts": [
            ("10-03", "https://www.debates.org/voter-education/debate-transcripts/october-3-2012-debate-transcript/"),
            ("10-11", "https://www.debates.org/voter-education/debate-transcripts/october-11-2012-the-biden-romney-vice-presidential-debate/"),
            ("10-16", "https://www.debates.org/voter-education/debate-transcripts/october-16-2012-the-second-obama-romney-presidential-debate/"),
            ("10-22", "https://www.debates.org/voter-education/debate-transcripts/october-22-2012-the-third-obama-romney-presidential-debate/")
        ]
    }),
    ("2008", {
        "info": "https://www.debates.org/debate-history/2008-debates/",
        "transcripts": [
            ("09-26", "https://www.debates.org/voter-education/debate-transcripts/2008-debate-transcript/"),
            ("10-02", "https://www.debates.org/voter-education/debate-transcripts/2008-debate-transcript-2/"),
            ("10-07", "https://www.debates.org/voter-education/debate-transcripts/october-7-2008-debate-transcrip/"),
            ("10-15", "https://www.debates.org/voter-education/debate-transcripts/october-15-2008-debate-transcript/")
        ]
    }),
    ("2004", {
        "info": "https://www.debates.org/debate-history/2004-debates/",
        "transcripts": [
            ("09-30", "https://www.debates.org/voter-education/debate-transcripts/september-30-2004-debate-transcript/"),
            ("10-05", "https://www.debates.org/voter-education/debate-transcripts/october-5-2004-transcript/"),
            ("10-08", "https://www.debates.org/voter-education/debate-transcripts/october-8-2004-debate-transcript/"),
            ("10-13", "https://www.debates.org/voter-education/debate-transcripts/october-13-2004-debate-transcript/")
        ]
    }),
    ("2000", {
        "info": "https://www.debates.org/debate-history/2000-debates/",
        "transcripts": [
            ("10-03", "https://www.debates.org/voter-education/debate-transcripts/october-3-2000-transcript/"),
            ("10-05", "https://www.debates.org/voter-education/debate-transcripts/october-5-2000-debate-transcript/"),
            ("10-11", "https://www.debates.org/voter-education/debate-transcripts/october-11-2000-debate-transcript/"),
            ("10-17", "https://www.debates.org/voter-education/debate-transcripts/october-17-2000-debate-transcript/")
        ]
    }),
    ("1996", {
        "info": "https://www.debates.org/debate-history/1996-debates/",
        "transcripts": [
            ("10-06", "https://www.debates.org/voter-education/debate-transcripts/october-6-1996-debate-transcript/"),
            ("10-09", "https://www.debates.org/voter-education/debate-transcripts/october-9-1996-debate-transcript/"),
            ("10-16", "https://www.debates.org/voter-education/debate-transcripts/october-16-1996-debate-transcript/")
        ]
    }),
    ("1992", {
        "info": "https://www.debates.org/debate-history/1992-debates/",
        "transcripts": [
            ("10-11", "https://www.debates.org/voter-education/debate-transcripts/october-11-1992-first-half-debate-transcript/"),
            ("10-11", "https://www.debates.org/voter-education/debate-transcripts/october-11-1992-second-half-debate-transcript/"), # merge scraped conents in 1 file name actually 10-11 second half
            ("10-15", "https://www.debates.org/voter-education/debate-transcripts/october-15-1992-first-half-debate-transcript/"),
            ("10-15", "https://www.debates.org/voter-education/debate-transcripts/october-15-1992-second-half-debate-transcript/"), # merge scraped conents in 1 file name actually 10-15 second half
            ("10-13", "https://www.debates.org/voter-education/debate-transcripts/october-13-1992-debate-transcript/"),
            ("10-19", "https://www.debates.org/voter-education/debate-transcripts/october-19-1992-debate-transcript/")
        ]
    }),
    ("1988", {
        "info": "https://www.debates.org/debate-history/1988-debates/",
        "transcripts": [
            ("09-25", "https://www.debates.org/voter-education/debate-transcripts/september-25-1988-debate-transcript/"),
            ("10-05", "https://www.debates.org/voter-education/debate-transcripts/october-5-1988-debate-transcripts/"),
            ("10-13", "https://www.debates.org/voter-education/debate-transcripts/october-13-1988-debate-transcript/")
        ]
    }),
    ("1984", {
        "info": "https://www.debates.org/debate-history/1984-debates/",
        "transcripts": [
            ("10-07", "https://www.debates.org/voter-education/debate-transcripts/october-7-1984-debate-transcript/"),
            ("10-11", "https://www.debates.org/voter-education/debate-transcripts/october-11-1984-debate-transcript/"),
            ("10-21", "https://www.debates.org/voter-education/debate-transcripts/october-21-1984-debate-transcript/")
        ]
    }),
    ("1980", {
        "info": "https://www.debates.org/debate-history/1980-debates/",
        "transcripts": [
            ("09-21", "https://www.debates.org/voter-education/debate-transcripts/september-21-1980-debate-transcript/"),
            ("10-28", "https://www.debates.org/voter-education/debate-transcripts/october-28-1980-debate-transcript/")
        ]
    }),
    ("1976", {
        "info": "https://www.debates.org/debate-history/1976-debates/",
        "transcripts": [
            ("09-23", "https://www.debates.org/voter-education/debate-transcripts/september-23-1976-debate-transcript/"),
            ("10-06", "https://www.debates.org/voter-education/debate-transcripts/october-6-1976-debate-transcript/"),
            ("10-15", "Transcript not available."),
            ("10-22", "https://www.debates.org/voter-education/debate-transcripts/october-22-1976-debate-transcript/")
        ]
    }),
    ("1960", {
        "info": "https://www.debates.org/debate-history/1960-debates/",
        "transcripts": [
            ("09-26", "https://www.debates.org/voter-education/debate-transcripts/september-26-1960-debate-transcript/"),
            ("10-07", "https://www.debates.org/voter-education/debate-transcripts/october-7-1960-debate-transcript/"),
            ("10-13", "https://www.debates.org/voter-education/debate-transcripts/october-13-1960-debate-transcript/"),
            ("10-21", "https://www.debates.org/voter-education/debate-transcripts/october-21-1960-debate-transcript/")
        ]
    }),
    ("1956", {
        "info": "https://www.debates.org/debate-history/1956-debate/",
        "transcripts": [
            ("05-21", "Transcript not available.")
        ]
    }),
    ("1948", {
        "info": "https://www.debates.org/debate-history/1948-debate/",
        "transcripts": [
            ("05-17", "Transcript not available.")
        ]
    }),
    ("1858", {
        "info": "https://www.debates.org/debate-history/1858-debates/",
        "transcripts": [
            ("08-21", "Transcript not available."),
            ("08-27", "Transcript not available."),
            ("09-15", "Transcript not available."),
            ("09-18", "Transcript not available."),
            ("10-07", "Transcript not available."),
            ("10-13", "Transcript not available."),
            ("10-15", "Transcript not available.")
        ]
    })
])