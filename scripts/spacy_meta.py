import json
import sys
from spacy.en import English


spacy_pos_order = [
    "PROPN",
    "PUNCT",
    "DET",
    "ADJ",
    "NOUN",
    "ADV",
    "SPACE",
    "CONJ",
    "VERB",
    "PART",
    "ADP",
    "NUM",
    "PRON",
    "INTJ",
    "X",
    "SYM"
]    


class SpacyMeta:

    __s_parser = None

    def __init__(self, p_folder, p_filename, p_save_text=True):

        if "/" != p_folder.strip()[len(p_folder) - 1]:
            p_folder += "/"
        self.__m_folder = p_folder
        self.__m_filename = p_filename
        self.__m_parser = None
        self.__m_pos_counts = [0] * len(spacy_pos_order)
        self.__m_pos_counts_dict = {}
        self.__m_token_counts = {}

        # Optional save of full text
        self.__m_full_text = None
        if p_save_text:
            with open(p_folder + p_filename, "rU") as text_file:
                self.__m_full_text = text_file.read()

        # Static member initialization of spaCy English parser
        if None == SpacyMeta.__s_parser:
            SpacyMeta.__s_parser = English()

    @staticmethod
    def hydrated_instance(p_count_file_folder, p_count_file):

        spacy_counts = SpacyMeta.read_count_file(p_count_file_folder, p_count_file)
        hydrated_instance = SpacyMeta(spacy_counts["folder"], spacy_counts["filename"])
        if "pos" in spacy_counts:
            for pos_index in range(len(spacy_pos_order)):
                hydrated_instance.__m_pos_counts[pos_index] = spacy_counts["pos"][spacy_pos_order[pos_index]]
                hydrated_instance.__m_pos_counts_dict[spacy_pos_order[pos_index]] = spacy_counts["pos"][spacy_pos_order[pos_index]]
        if "tokens" in spacy_counts:
            hydrated_instance.__m_token_counts = spacy_counts["tokens"]
        return hydrated_instance

    def filename(self):
        return self.__m_filename

    def folder(self):
        return self.__m_folder

    def parser(self):
        return self.__m_parser

    def pos_counts(self):
        return self.__m_pos_counts

    def pos_counts_dict(self):
        return self.__m_pos_counts_dict

    def token_counts(self):
        return self.__m_token_counts


    def change_encoding(self, p_encoding):

        if "latin1" == p_encoding:
            reload(sys)  
            sys.setdefaultencoding("latin1")
        elif "ascii" == p_encoding:
            reload(sys)
            sys.setdefaultencoding("ascii")


    def parse(self, p_encoding=None):

        # spaCy parser
        # parser = English()

        # Set encoding if requested
        if p_encoding:
            self.change_encoding(p_encoding)

        with open(self.__m_folder + self.__m_filename, "rU") as input_file:

            # Run spaCy parser
            data = unicode(input_file.read())
            self.__m_parser = SpacyMeta.__s_parser(data) 

            # Save tokens, token counts, and POS counts
            for span in self.__m_parser.sents:
                
                sent = [self.__m_parser[i] for i in range(span.start, span.end)]
                for token in sent:

                    # Save tokens and token counts
                    if token.lower_ not in self.__m_token_counts:
                        self.__m_token_counts[token.lower_] = 1
                    else:
                        self.__m_token_counts[token.lower_] += 1

                    # Save POS counts
                    self.__m_pos_counts[spacy_pos_order.index(token.pos_)] += 1
                    if token.pos_ not in self.__m_pos_counts_dict:
                        self.__m_pos_counts_dict[token.pos_] = 1
                    else:
                        self.__m_pos_counts_dict[token.pos_] += 1

        # print "Parsed sentences"


    def parse_by_pos(self, p_pos, p_encoding=None):

        # Set encoding if requested
        if p_encoding:
            self.change_encoding(p_encoding)

        pos_token_dict = {}
        myverbs = ["love", "appear", "sacrifice", "show", "pieced", "thought"]

        with open(self.__m_folder + self.__m_filename, "rU") as input_file:

            # Run spaCy parser
            data = unicode(input_file.read())
            self.__m_parser = SpacyMeta.__s_parser(data) 

            # Save tokens, token counts, and POS counts
            for span in self.__m_parser.sents:
                
                sent = [self.__m_parser[i] for i in range(span.start, span.end)]
                for token in sent:

                    # Retrieve requested POS tokens only
                    if token.pos_ == p_pos:
                        if token.lemma_ not in pos_token_dict:
                            pos_token_dict[token.lemma_] = 0
                        pos_token_dict[token.lemma_] += 1
                    else:
                        if token.lower_ in myverbs:
                            print "{0}: {1}".format(token.lower_, token.pos_)

        return pos_token_dict


    def get_sentences(self, p_encoding="utf-8"):

         # spaCy parser
        parser = English()

        # Set encoding if requested
        if p_encoding:
            self.change_encoding(p_encoding)

        with open(self.__m_folder + self.__m_filename, "rU") as input_file:

            # Run spaCy parser
            data = input_file.read()
            self.__m_parser = parser(data.decode(p_encoding)) 

        # Return list of sentences
        return self.__m_parser.sents


    def get_pos_count(self, p_pos_name):

        pos_count = 0
        if p_pos_name in spacy_pos_order:
            pos_count = self.__m_pos_counts[spacy_pos_order.index(p_pos_name)]
        return pos_count

    def has_token(self, p_token):

        return p_token in self.__m_token_counts

    def get_token_count(self, p_token):

        token_count = 0
        if self.has_token(p_token):
            token_count = self.__m_token_counts[p_token]
        return token_count


    def output_pos_counts(self, p_output_folder, p_output_filename):

        with open(p_output_folder + p_output_filename, "w") as output_file:
            json_output = {}
            json_output["folder"] = self.__m_folder
            json_output["filename"] = self.__m_filename
            json_output["pos"] = {}
            if None != self.__m_full_text:
                json_output["full_text"] = self.__m_full_text
            for pos_index in range(len(spacy_pos_order)):
                json_output["pos"][spacy_pos_order[pos_index]] = self.__m_pos_counts[pos_index]
            json.dump(json_output, output_file)

    def output_token_counts(self, p_output_folder, p_output_filename):

        with open(p_output_folder + p_output_filename, "w") as output_file:
            json_output = {}
            json_output["folder"] = self.__m_folder
            json_output["filename"] = self.__m_filename
            json_output["tokens"] = {}
            for token in self.__m_token_counts:
                json_output["tokens"][token] = self.__m_pos_counts[token]
            json.dump(json_output, output_file)

    def output_pos_and_token_counts(self, p_output_folder, p_output_filename):

        with open(p_output_folder + p_output_filename, "w") as output_file:
            json_output = {}
            json_output["folder"] = self.__m_folder
            json_output["filename"] = self.__m_filename
            json_output["pos"] = {}
            for pos_index in range(len(spacy_pos_order)):
                json_output["pos"][spacy_pos_order[pos_index]] = self.__m_pos_counts[pos_index]            
            json_output["tokens"] = {}
            for token in self.__m_token_counts:
                json_output["tokens"][token] = self.__m_pos_counts[token]
            json.dump(json_output, output_file)

    @staticmethod
    def read_count_file(p_count_file_folder, p_count_file):

        with open(p_count_file_folder + p_count_file, "rU") as json_file:
            count_json = json.load(json_file)
        return count_json

    @staticmethod
    def get_pos_index(p_pos_name):
        for index in range(len(spacy_pos_order)):
            if p_pos_name == spacy_pos_order[index]:
                return index
        return -1

