import glob
import os

def main():

    root_folder = "/Users/PeregrinePickle/Documents/School/New York University/Seminars/Melville/Presentation/"
    input_folder = "text/split/bysection_bysentence/"
    names_of_interest = {"Bulkington":[], "Queequeg":[]}
    text_of_interest = {"Bulkington":[], "Queequeg":[]}
    for full_filepath in glob.glob(root_folder + input_folder + "*.txt"):
        with open(full_filepath, "r") as input_file:
            data = input_file.read()
            for name in names_of_interest.keys():
                if name in data:
                    names_of_interest[name].append(os.path.basename(full_filepath))
                    text_of_interest[name].append((os.path.basename(full_filepath), data.replace("\n", " ")))

    # Debug
    # for name in names_of_interest.keys():
    #     print "{0}({1}):".format(name, len(names_of_interest[name]))
    #     for fd_tuple in names_of_interest[name]:
    #         # print "{0} | {1}\n".format(fd_tuple[0], fd_tuple[1])
    #         print "{0}".format(fd_tuple[0])

    pmf_output_folder = "/output/pmf_results/"
    pmf_output_file = "mobydick_sentence_clusters_1490819354731.csv"
    sentence_to_group = {}
    bulkington_groups = []
    queequeg_groups = []
    groups_to_sentences = {}
    with open(root_folder + pmf_output_folder + pmf_output_file, "r") as pmf_file:
        csv_lines = pmf_file.readlines()
        for line in csv_lines:
            sent_filename,sent_group = line.strip().split(",")
            for name in names_of_interest:
                if sent_filename in names_of_interest[name]:
                    if "Bulkington" == name:
                        bulkington_groups.append(sent_group)
                    else:
                        queequeg_groups.append(sent_group)
                    if sent_filename in names_of_interest[name]:
                        sentence_to_group[sent_filename] = sent_group
                        if sent_group not in groups_to_sentences:
                            groups_to_sentences[sent_group] = []
                        groups_to_sentences[sent_group].append(sent_filename)

    # Debug
    # print sentence_to_group
    # print bulkington_groups
    # print queequeg_groups
    # print groups_to_sentences
    bset = set(bulkington_groups)
    qset = set(queequeg_groups)
    groups_in_both = list(bset.intersection(qset))
    # print "Groups in both: {0}".format(list(bset.intersection(qset)))
    # print "Groups only in Bulkington: {0}".format(list(bset - qset))
    # print "Groups only in Queequeg: {0}".format(list(qset - bset))

    # Queequeg-like Bulkington sentences
    qlb_sentences = []
    # print "Queequeg-like Bulkinton sentences"
    for group in groups_in_both:
        for filename in groups_to_sentences[group]:
            if filename in names_of_interest["Bulkington"]:
                # print filename
                qlb_sentences.append(filename)

    # print "======================================================"

    # Bulkington-like Queequeg sentences
    blq_sentences = []
    # print "Bulkington-like Queequeg sentences"
    for group in groups_in_both:
        for filename in groups_to_sentences[group]:
            if filename in names_of_interest["Queequeg"]:
                # print filename                
                blq_sentences.append(filename)

    # Show text of Queequeg-like Bulkington sentences
    for td_tuple in text_of_interest["Bulkington"]:
        if td_tuple[0] in qlb_sentences:
            print "Filename: {0}\nGroup: {1}\nSentence: {2}".format(td_tuple[0], sentence_to_group[td_tuple[0]], td_tuple[1].strip())
            print "======================================================"
    if True:
        return

    # Looking at groups 50, 230, 354
    looking_at = [50, 230, 354, 232]

    # for sentence in sentence_to_group:
    #     if sentence_to_group[sentence] == "50":
    #         print sentence
    # if True:
    #     return

    # Find Bulkington-like Queequeg sentences with these groups
    for td_tuple in text_of_interest["Queequeg"]:
        # print "group: {0} looking_at: {1}".format(sentence_to_group[td_tuple[0]], looking_at)
        if int(sentence_to_group[td_tuple[0]]) in looking_at:
            print "Filename: {0}\nGroup: {1}\nSentence: {2}".format(td_tuple[0], sentence_to_group[td_tuple[0]], td_tuple[1].strip())
            print "======================================================"






if __name__ == "__main__":
    main()