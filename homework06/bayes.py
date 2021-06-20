import math
from collections import Counter


class NaiveBayesClassifier:
    def __init__(self, alpha: float = 1e-5):
        self.alpha = alpha
        self.model: dict = {
            "labels": {},
            "words": {},
        }

    def fit(self, X, y):
        """ Fit Naive Bayes classifier according to X, y."""
        dir = []
        for title, lable in zip(X, y):
            for word in title.split():
                pair = (word, lable)
                dir.append(pair)

        self.unique_words = Counter(dir)
        print("unique_words", self.unique_words)

        self.counted_dict = dict(Counter(y))
        print("counted_dict", self.counted_dict)

        words = [word for title in X for word in title.split()]
        self.counted_words = dict(Counter(words))
        print("counted_words", self.counted_words)

        self.model = {
            "labels": {},
            "words": {},
        }

        for edition in self.counted_dict:
            cast = 0
            for word, label_name in self.unique_words:
                if edition == label_name:
                    cast += self.unique_words[(word, edition)]
            params = {
                "label_count": cast,
                "probability": self.counted_dict[edition] / len(y),
            }
            self.model["labels"][edition] = params

        for word in self.counted_words:
            par = {}
            for edition in self.counted_dict:
                nc = self.model["labels"][edition]["label_count"]
                nic = self.unique_words.get((word, edition), 0)
                counted_len = len(self.counted_words)
                alpha = self.alpha
                smooth = (nic + alpha) / (nc + alpha * counted_len)
                par[edition] = smooth
            self.model["words"][word] = par

    def predict(self, X):
        """ Perform classification on an array of test vectors X. """
        words = X.split()
        prob = []
        for cur_label in self.model["labels"]:
            probability = self.model["labels"][cur_label]["probability"]
            total_grade = math.log(probability, math.e)
            for word in words:
                word_dict = self.model["words"].get(word, None)
                if word_dict:
                    total_grade += math.log(word_dict[cur_label], math.e)
            prob.append((total_grade, cur_label))
        _, prediction = max(prob)
        return prediction

    def score(self, X_test, y_test):
        """ Returns the mean accuracy on the given test data and labels. """
        reg = []
        for one in X_test:
            reg.append(self.predict(one))
        return sum(0 if reg[i] != y_test[i] else 1 for i in range(len(X_test))) / len(
            X_test
        )