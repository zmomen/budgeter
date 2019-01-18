import csv
import re

from textblob.classifiers import NaiveBayesClassifier


class BankClassify():

    def __init__(self):
        """Load in the previous data (by default from AllData.csv) and initialise the classifier"""
        self.training_set = []
        self.accuracy = 0
        self.classifier = NaiveBayesClassifier(self.training_set, self.extractor)

    def get_accuracy(self):
        return self.accuracy

    def category_classify(self, item):
        # Guess a category using the classifier (only if there is data in the classifier)
        if len(self.classifier.train_set) > 1:
            guess = self.classifier.classify(item.lower())
        else:
            guess = ""
        new_entry = [(item.lower(), guess)]
        self.classifier.update(new_entry)
        self.training_set = self.training_set + new_entry
        self.accuracy = self.classifier.accuracy(self.training_set)
        return guess

    def read_bank_file(self, filename):
        """Read a csv file
        Returns a list with columns of 'desc' and 'category'."""
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            train = []
            for line in reader:
                train.append(tuple(line))
            self.training_set = self.training_set + train
            self.classifier.update(train)
            self.accuracy = self.classifier.accuracy(train)

        return True

    def update_training_set(self, new_data):
        """Update training data for the classifier, consisting of tuples of
        (text, category)"""
        train = []
        if len(new_data) > 0:
            for i in range(0, len(new_data)):
                row = new_data[i]
                new_desc = self.strip_numbers(row[0]).lower()
                train.append((new_desc, row[1]))
            self.training_set = self.training_set + train
            self.classifier.update(train)
            self.accuracy = self.classifier.accuracy(train)

        else:
            self.accuracy = 0
        return self.training_set

    def extractor(self, doc):
        """Extract tokens from a given string"""
        # TODO: Extend to extract words within words
        # For example, MUSICROOM should give MUSIC and ROOM
        tokens = self.split_by_multiple_delims(doc, [' ', '/'])

        features = {}

        for token in tokens:
            if token == "":
                continue
            features[token] = True

        return features

    def strip_numbers(self, s):
        """Strip numbers from the given string"""
        return re.sub("[^A-Z ]", "", s)

    def split_by_multiple_delims(self, string, delims):
        """Split the given string by the list of delimiters given"""
        regexp = "|".join(delims)

        return re.split(regexp, string)
