# Bachelor thesis
The contents of this repository are part of the bachelor thesis "Examining concepts of author disambiguation: co-authorship as a disambiguation feature in EconBiz" by Swantje Wiechmann.

Directory algorithms contains:
  - algorithm1.py: the implementation of Algorithm 1 in the thesis
  - algorithm2.py: the implementation of Algorithm 2 in the thesis
  - algorithm3.py: the implementation of Algorithm 3 in the thesis

Directory data contains: 
  - disambiguatedAuthors.json: list of all disambiguated authors in Econis with their respective GND-ID, coauthors, and subjects they have written about. Because the complete file is too big for the disc the data were originally shared on, this is a smaller version with the subjects from the data fields 'subject_stw' and 'subject_fsw' missing.
  - testsets: 
    - directory containing all fourteen datasets used for testing the algorithms
    - naming convention:  
      - a/p for ambiguous/partly disambiguated bibliographic records
      - l/s for large (1000 bibliographic records)/small (100 bibliographic records) 
      - xAuthors for the amount of authors per bibliographic record = x
