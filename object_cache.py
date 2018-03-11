from common.patterns import Singleton

class Cache(Singleton):

    def __init__(self):
        self.models = []
        self.objects_by_models = {}
        """dict[model,dict[k,model_instance]]"""
