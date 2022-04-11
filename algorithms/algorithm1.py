import json

# import list of disambiguated authors in Econis
with open('../data/disambiguatedAuthors.json',encoding='utf-8') as authorsFile:
    disambAuthorsEconis = json.load(authorsFile)
authorsFile.close()

# disambiguate partly disambiguated bibliographic records
def matchPartlyDisamb(input, output, threshold):
    # import list of records to be disambiguated
    with open(input, encoding='utf-8') as econisData:
        records = json.load(econisData)
    econisData.close()

    disambiguatedAuthors = []

    #disambiguate the records
    for record in records:
        # preprocessing: extract all authors and all subjects (keywords) from the record
        referencesAll, referencesGnd, referencesNoId = getAuthors(record)
        subjectList = getSubjects(record)

        # disambiguation task
        for author in referencesNoId:
            # search for potential matches in the list of in Econis disambiguated authors
            potentialMatches, matchesIndex = findSameNames(author['name'])
            scores = []
            # calculate the similarity score for each potential match
            for match in potentialMatches:
                simScore = calculateSimilarity(match['coauthors'],referencesGnd)
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

# extract all author references from a record and divide them by the factor if they have a GND-ID
def getAuthors(record):
    personList = []
    noId = []
    withId = []
    if 'creator_personal' in record:
        for author in record['creator_personal']:
            personList.append(author)
            if 'gnd_id' in author:
                withId.append(author)
            else:
                noId.append(author)
    if 'contributor_personal' in record:
        for author in record['contributor_personal']:
            personList.append(author)
            if 'gnd_id' in author:
                withId.append(author)
            else:
                noId.append(author)
    return personList, withId, noId

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

# calculate the similarity of two authors by how often the first has written together with the co-authors of the second
def calculateSimilarity(coauthorsMatch,coauthorsReference):
    similarity = 0
    for coauthor in coauthorsReference:
        for coauthorMatch in coauthorsMatch:
            if 'gnd_id' in coauthorMatch and coauthor['gnd_id'] == coauthorMatch['gnd_id']:
                similarity += 1
    return similarity

# extend disambiguated author list by the values of the newly matched author reference
def extendAuthors(index,coauthors,subjects):
    disambAuthorsEconis[index]['coauthors'].extend(coauthors)
    disambAuthorsEconis[index]['subjects'].extend(subjects)

# example for calling the disambiguation function with a small, partly disambiguated dataset and different similarity thresholds
matchPartlyDisamb('../data/testsets/ps_2authors.json','../data/alg1_ps_2authors1.json',1)
matchPartlyDisamb('../data/testsets/ps_2authors.json','../data/alg1_ps_2authors5.json',5)
matchPartlyDisamb('../data/testsets/ps_2authors.json','../data/alg1_ps_2authors10.json',10)
