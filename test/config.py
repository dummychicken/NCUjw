class Config:
    __period = 40
    __limited = 60
    __threshold = 100

    @classmethod
    def get_period(cls):
        return cls.__period

    @classmethod
    def get_limited(cls):
        return cls.__limited

    @classmethod
    def get_threshold(cls):
        return cls.__threshold

