import pickle
import numpy as np

class Model():
    def __init__(self, model, features, labels):
        if not isinstance(features, list): raise("features must be a list!")
        if not isinstance(labels, list): raise("labels must be a list!")
        self.model = model
        self.features = features
        self.labels = labels

    @staticmethod
    def fit_create(model, X, y):
        return Model(model.fit(X,y), X.columns.tolist(), np.unique(y).tolist())

    def fit(self, X, y):
        self.model.fit(X,y)
        self.features = X.columns.tolist()
        self.labels = np.unique(y).tolist()
        return self

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)

    # EXPORT & IMPORT
    def dump(self, filename):
        with open(filename, 'w') as f:
            pickle.dump((
                pickle.dumps(self.model).encode('zlib'),
                self.features,
                self.labels
            ), f)

    @staticmethod
    def load(filename):
        with open(filename, 'r') as f:
            model, features, labels = pickle.load(f)
            model = pickle.loads(model.decode('zlib'))
        return Model(model, features, labels)
