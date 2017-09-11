# Required libraries
# (1) Nimfa, Site: http://nimfa.biolab.si/, Install: pip install nimfa
# (2) spaCy, Site: https://spacy.io/, Install: pip install spacy
# (3) Numpy and Scipy, Site: https://www.scipy.org/, Install: pip install --user numpy scipy

import time
import glob
import os

from nimfa_pmf import Nimfa
from spacy_meta import SpacyMeta


def OutputPOSTokenFiles(p_text_folder, p_counts_folder):

    for full_filepath in glob.glob(p_text_folder + "*.txt"):
        input_filename = os.path.basename(full_filepath)
        print "Input: {0}".format(input_filename)
        spacy_meta = SpacyMeta(os.path.dirname(full_filepath) + "/", input_filename)
        print "SpacyMeta created"
        spacy_meta.parse("latin1")
        print "POS Parsed"
        spacy_meta.output_pos_counts(p_counts_folder, "{0}_counts.json".format(os.path.splitext(input_filename)[0]))
        print "Count file output"


def ReadPOSTokenFiles(p_counts_folder):

    spacy_metas = []
    for full_filepath in glob.glob(p_counts_folder + "*.json"):
        spacy_metas.append(SpacyMeta.hydrated_instance(p_counts_folder, os.path.basename(full_filepath)))
    return spacy_metas


def GetNimfaInstance(p_vectors):

    row_count = len(p_vectors)
    col_count = len(p_vectors[0])
    np_instance = Nimfa(p_vectors, row_count, col_count)
    
    return np_instance


def main():   

    root_folder = "/Users/PeregrinePickle/Documents/School/New York University/Seminars/Melville/Presentation/"
    input_folder = root_folder + "text/split/bysection/"
    sentsplit_folder = root_folder + "text/split/bysection_bysentence/"
    output_folder = root_folder + "output/sentence_bysection_pos_counts/"
    pmf_output_folder = root_folder + "output/pmf_results/"


    # for full_filepath in glob.glob(input_folder + "*.txt"):
        
    #     spacy_meta = SpacyMeta(input_folder, os.path.basename(full_filepath))
    #     sentences = spacy_meta.get_sentences()

    #     # Sentences debug
    #     # lengths = []
    #     # for s in sentences:
    #     #     token_list = []
    #     #     for token in s:
    #     #         token_list.append(token.lower_)
    #     #     sent_len = len(token_list)
    #     #     lengths.append(sent_len)
    #     # lengths.sort()
    #     # print len(lengths)

    #     # a. Run only once
    #     # Split section text by sentences and output each into a separate txt file
    #     sentence_count = 1
    #     for s in sentences:
    #         new_filename = os.path.basename(full_filepath).strip(".txt")
    #         with open(sentsplit_folder + "md_{0}_{1}.txt".format(new_filename, sentence_count), "w") as output_file:
    #             output_file.write(s.text)
    #         sentence_count += 1

    # b. Run only once
    # OutputPOSTokenFiles(sentsplit_folder, output_folder)

    # 1. Reconstitutes POS count files output by Step 0
    spacy_metas = ReadPOSTokenFiles(output_folder)
    pos_vectors = []
    metas_order = []
    for sm in spacy_metas:
        metas_order.append(sm.filename())
        pos_vectors.append(sm.pos_counts())

    # Nimfa PMF Example
    np_instance = GetNimfaInstance(pos_vectors) 
    np_pmf = np_instance.pmf(2)
    fclusters = np_instance.pmf_clusters(np_pmf)

    # Output CSV file that matches sentences to clusters
    with open(pmf_output_folder + "mobydick_sentence_clusters_{0}.csv".format(long((time.time() + 0.5) * 1000)), "w") as pmf_results:
        for index in range(len(fclusters)):
            pmf_results.write("{0},{1}\n".format(metas_order[index], fclusters[index]))


if "__main__" == __name__:
    main()