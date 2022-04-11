import json

# import list of disambiguated authors in Econis
with open('../data/disambiguatedAuthors.json',encoding='utf-8') as authorsFile:
    disambAuthorsEconis = json.load(authorsFile)
authorsFile.close()

# disambiguation method for ambiguous bibliographic records
def matchAmbiguous(input, output, threshold):
    # import list of records to be disambiguated
    with open(input, encoding='utf-8') as econis:
        records = json.load(econis)
    econis.close()

    disambiguatedAuthors = []
    
    # disambiguation task
    for record in records:
        # preprocessing: extract all authors and all subjects (keywords) from the record
        referencesAll, referencesAmbiguous = getAuthors(record)
        subjectList = getSubjects(record)

        for author in referencesAmbiguous:
            # search for potential matches in the list of in Econis disambiguated authors
            potentialMatches, matchesIndex = findSameNames(author['name'])
            scores = []
            # calculate the similarity score for each potential match
            for match in potentialMatches:
                simScore = calculateSimilarityTopic(match['subjects'], subjectList)
                scores.append(simScore)
            if scores:
                # the GND-ID of the match with the highest similiarity score gets assigned to the author reference if the value matches the similarity threshold
                highestSimilarity = max(scores)
                if highestSimilarity >= threshold:
                    idx = scores.index(highestSimilarity)
                    matchingAuthor = potentialMatches[idx]
                    disambiguatedAuthors.append({'name': author['name'], 'econbiz_id': record['econbiz_id'], 'gnd_id': matchingAuthor['gnd_id'], 'similarity': highestSimilarity})
                    extendAuthors(matchesIndex[idx],getAllCoauthors(author['name'],referencesAll),subjectList)

    # write disambiguated authors in file
    with open(output,'w') as json_file:
        json.dump(disambiguatedAuthors, json_file, indent=2)
    json_file.close()

    # write extended list of in Econis disambiguated authors in file
    with open('../data/disambiguatedAuthors.json','w') as json_file:
        json.dump(disambAuthorsEconis, json_file, indent=2)
    json_file.close()

# extract all author references and author references without a GND-ID from a record
def getAuthors(record):
    personList = []
    noId = []
    if 'creator_personal' in record:
        for author in record['creator_personal']:
            personList.append(author)
            if 'gnd_id' not in author:
                noId.append(author)
    if 'contributor_personal' in record:
        for author in record['contributor_personal']:
            personList.append(author)
            if 'gnd_id' not in author:
                noId.append(author)
    return personList, noId

# extract all subjects (keywords) from a record
def getSubjects(record):
    subjectlist = []
    if 'subject_stw_added' in record:
        for subject in record['subject_stw_added']:
            subjectlist.append(subject['name_de'])
    if 'subject_gnd' in record:
        for subject in record['subject_gnd']:
            subjectlist.append(subject['name'])
    if 'subject' in record:
        subjectlist.extend(record['subject'])
    if 'subject_stw' in record:
        for subject in record['subject_stw']:
            subjectlist.append(subject['name_de'])
    if 'subject_fsw' in record:
        for subject in record['subject_fsw']:
            subjectlist.append(subject['name_de'])
    return subjectlist

# extract the co-authors of a specific author from the list of all authors
def getAllCoauthors(name,references):
    coauthorlist = []
    for ref in references:
        if ref['name'] != name:
            coauthorlist.append(ref)
    return coauthorlist

# similarity function to find possible matches for an ambiguous author reference
def findSameNames(name):
    sameNameList = []
    indexlist = []
    counter = 0
    for author in disambAuthorsEconis:
        if author['name'] == name:
            sameNameList.append(author)
            indexlist.append(counter)
        counter += 1
    return sameNameList, indexlist

# calculate the similarity of two authors by how often the first has written about the topics of the second
def calculateSimilarityTopic(topicsMatch,topicsReference):
    similarity = 0
    for topic in topicsReference:
        for topicMatch in topicsMatch:
            if topic == topicMatch:
                similarity += 1
    return similarity

# extend disambiguated author list by the values of the newly matched author reference
def extendAuthors(index,coauthors,subjects):
    disambAuthorsEconis[index]['coauthors'].extend(coauthors)
    disambAuthorsEconis[index]['subjects'].extend(subjects)

# example for calling the disambiguation function with a small, ambiguous dataset and different similarity thresholds
matchAmbiguous('../data/testsets/as_1author.json','../data/alg3_as_1author2.json',2)
matchAmbiguous('../data/testsets/as_1author.json','../data/alg3_as_1author15.json',15)
matchAmbiguous('../data/testsets/as_1author.json','../data/alg3_as_1author25.json',25)

# example for calling the disambiguation function with a small, ambiguous dataset and different similarity thresholds
matchAmbiguous('../data/testsets/as_2authors.json','../data/alg3_as_2authors2.json',2)
matchAmbiguous('../data/testsets/as_2authors.json','../data/alg3_as_2authors15.json',15)
matchAmbiguous('../data/testsets/as_2authors.json','../data/alg3_as_2authors25.json',25)

# example for calling the disambiguation function with a small, partly disambiguated dataset and different similarity thresholds
matchAmbiguous('../data/testsets/ps_2authors.json','../data/alg3_ps_2authors2.json',2)
matchAmbiguous('../data/testsets/ps_2authors.json','../data/alg3_ps_2authors15.json',15)
matchAmbiguous('../data/testsets/ps_2authors.json','../data/alg3_ps_2authors25.json',25)
