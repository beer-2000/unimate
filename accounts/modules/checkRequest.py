

class CheckRequest:
    def __init__(self, data):
        self.university = data["university"]
        self.college = data["college"]
        self.major = data["major"]

    def univColMajor(self):
        if(
            (type(self.university) is int) &
            (type(self.college) is int) &
            (type(self.major) is int)) :
            return True
        return False
