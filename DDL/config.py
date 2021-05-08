class Config:
    __period = 40
    __limited = 60
    __threshold = 100
    __crRatio = 0.5
    __crEffective = 1
    __host = '123.60.11.177'
    __port = '3306'
    __user = 'root'
    __password = 'shwSjw1@j!kSl'
    __db = 'examArrange1'

    @classmethod
    def get_period(cls):
        return cls.__period

    @classmethod
    def get_limited(cls):
        return cls.__limited

    @classmethod
    def get_threshold(cls):
        return cls.__threshold

    @classmethod
    def get_crRatio(cls):
        return cls.__crRatio

    @classmethod
    def get_crEffective(cls):
        return cls.__crEffective

    @classmethod
    def get_port(cls):
        return cls.__port

    @classmethod
    def get_host(cls):
        return cls.__host

    @classmethod
    def get_user(cls):
        return cls.__user

    @classmethod
    def get_password(cls):
        return cls.__password

    @classmethod
    def get_db(cls):
        return cls.__db

