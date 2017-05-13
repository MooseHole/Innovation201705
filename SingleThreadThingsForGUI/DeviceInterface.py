from abc import ABCMeta, abstractmethod

class DeviceType(metaclass=ABCMeta):
    @abstractmethod
    def GetLabels(self):
        raise NotImplementedError

class DynamicDevice(DeviceType):
    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])
    def GetLabels(self):
        return vars(self)
