from mopidyapi import MopidyAPI


class Mopidy(MopidyAPI):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.view = model.view
