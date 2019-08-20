from Bio import SeqIO
import os


class DataPreprocessor:
    seq_ids = []
    error_ids = []
    data = []  # non duplicate data list
    preprocessed_data = []  # pre processed data list
    file_types = {"fasta": "fasta", "fas": "fasta"}  # accepted data input file types
    type_id = {"DNA": [], "AA": []}  # dictionary to keep ids and types
    valid_DNA = "ACGT"
    valid_AA = "ARNDBCEQZGHILKMFPSTWYV"
    data_type = ""
    dna_count = 0  # no of dna sequences
    aa_count = 0  # no of aa sequences
    seq_count = 0  # no of sequences
    valid_SC = "_?-"

    def findSeqType(self, seq, length):
        dna_c = 0
        aa_c = 0
        sequence = seq.upper()

        for char in sequence:
            if char in self.valid_DNA:
                dna_c += 1
            if char in self.valid_AA:
                aa_c += 1
            if char in self.valid_SC:
                length = length - 1
        if dna_c == length:  # check valid dna sequence or not
            self.dna_count += 1
            self.seq_count += 1
            self.data_type = 'DNA'
        elif aa_c == length:  # check valid aa sequence or not
            self.aa_count += 1
            self.seq_count += 1
            self.data_type = 'AA'
        else:
            self.data_type = 'UNDEFINED'

    # check the data type of the complete data set
    def findDataSetType(self):
        if (self.dna_count / self.seq_count) > 0.85:
            self.data_type = 'DNA'
            if self.dna_count != self.seq_count:
                self.error_ids = self.type_id['AA']  # identifying  irrelevant AA sequences
                # print("DNA data set")

        elif (self.aa_count / self.seq_count) > 0.85:
            self.data_type = 'AA'
            if self.aa_count != self.seq_count:
                self.error_ids = self.type_id['DNA']  # identifying  irrelevant DNA sequences

        else:
            print("incompatible sequence  records found")  # ambiguous data set

    def processData(self, file):
        in_file = file
        file_type = in_file.split(".")[1]  # extract file type
        if file_type in self.file_types.keys():  # check the relevancy of file type
            file_type = self.file_types[file_type]  # normalize file type
            dataset = SeqIO.parse(in_file, file_type)  # Type parser
            for seq in dataset:
                if seq.id not in self.seq_ids:  # handle duplicate records
                    self.findSeqType(seq.seq, len(seq))
                    if self.data_type != 'UNDEFINED' or self.data_type != '':  # to ignore incorrect sequences
                        self.type_id[self.data_type].append(seq.id)  # add to dictionary to keep track of dna or aa
                        self.seq_ids.append(seq.id)
                        self.data.append(seq)
                    else:
                        print("Incorrect sequence")
                else:
                    print("Duplicate record found", seq.id)

            self.findDataSetType()  # data type of complete data set
            # print(self.error_ids)
            for seq in self.data:  # to catch correct sequences after type check
                if seq.id not in self.error_ids:
                    self.preprocessed_data.append(seq)

        out_file = '{}_processed.fasta'.format(
            os.path.splitext(in_file)[0])  # write the preprocessed data to a temporary file
        with open(out_file, 'w') as f:
            SeqIO.write(self.preprocessed_data, f, 'fasta')
        return out_file


""" start = time.time()
preprocessor = DataPreprocessor()
output_file = preprocessor.handleInput("SequenceTestSet_GenomeLab.fasta")
print(output_file)
end = time.time()
print(end-start)"""
