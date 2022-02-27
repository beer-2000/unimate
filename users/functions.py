from ast import literal_eval
from rest_framework import status
from rest_framework.response import Response


#방 입장 조건 비교 (각각 True or False 반환)
class RoomEnterPosible:
    #초기값 세팅
    def __init__(self, room, profile):
        self.room = room
        self.profile = profile
    #logic1
    def compare_university(self):
        room_university = self.room.university
        profile_university = str(self.profile.user.university)
        print("university 비교 결과")
        print(f"방:{room_university} 사용자:{profile_university}")
        return room_university == profile_university
    #logic2
    def compare_open(self):
        return self.room.room_open == 'open'
    #logic3
    def compare_heads(self):
        room_heads_limit = self.room.heads_limit
        room_now_heads = len(self.room.owner.all())
        print("heads(인원)제한 확인 결과")
        print(f"수용 가능 인원: {room_heads_limit}, 현재 인원: {room_now_heads}")
        return room_now_heads < room_heads_limit
    #logic4
    def compare_grade(self):
        room_grade = self.room.grade_limit
        print("grade 비교 결과")
        if room_grade == None:
            print("방에 학년 제한이 없습니다.")
            return True
        profile_grade = self.profile.grade
        print(f"방:{room_grade} 사용자:{profile_grade}")
        return room_grade == profile_grade
    #logic5
    def compare_gender(self):
        room_gender = self.room.gender_limit
        print("gender 비교 결과")
        if room_gender == "N":
            print("방에 성별 제한이 없습니다.")
            return True
        profile_gender = self.profile.gender
        print(f"방:{room_gender} 사용자:{profile_gender}")
        return room_gender == profile_gender
    #logic6-1
    def compare_mbti(self):
        room_mbti = literal_eval(self.room.mbti)
        profile_mbti = literal_eval(self.profile.mbti)
        count_mbti = 0
        print("mbti 비교 결과")
        for i in range(4):
            if (room_mbti[i] == 'O') | (room_mbti[i] == profile_mbti[i]):
                print(f"방:{room_mbti[i]} 사용자:{profile_mbti[i]}")
                #pass
            else:
                print(f"방:{room_mbti[i]} 사용자:{profile_mbti[i]} 이므로 입장 불가")
                count_mbti = count_mbti+1
        return count_mbti == 0
    #logic6-2
    def compare_interest(self):
        room_interest = self.room.interest
        profile_interest = literal_eval(self.profile.interest_list)
        print("interest 비교 결과")
        print(f"방:{room_interest} 사용자:{profile_interest}")
        return room_interest in profile_interest
    #logic6-3
    def compare_college(self):
        room_college = self.room.college
        profile_college = str(self.profile.user.college)
        print("college 비교 결과")
        print(f"방:{room_college} 사용자:{profile_college}")
        return room_college == profile_college

#방 입장 가능 여부 확인
#True or False, message(body) 반환
def compare_total(room, profile):
    var = RoomEnterPosible(room, profile)
    if not var.compare_university():
        body = {"message": "Different university"}
        return False, body
    elif not var.compare_open():
        body = {"message": "Not open"}
        return False, body
    elif not var.compare_heads():
        body = {"message": "The room is already full"}
        return False, body
    elif not var.compare_grade():
        body = {"message": "Grade limit"}
        return False, body
    elif not var.compare_gender():
        body = {"message": "Gender limit"}
        return False, body
    elif room.common == '':
        print("common is blank")
        body = {"message": "Entrance OK"}
        return True, body
    elif room.common == 'mbti':
        if not var.compare_mbti():
            body = {"message": "Common-MBTI limit"}
            return False, body
        else:
            print("common OK")
            body = {"message": "Entrance OK"}
            return True, body
    elif room.common == 'interest':
        if not var.compare_interest():
            body = {"message": "Common-Interest limit"}
            return False, body
        else:
            print("common OK")
            body = {"message": "Entrance OK"}
            return True, body
    elif room.common == 'college':
        if not var.compare_college():
            body = {"message": "Common-College limit"}
            return False, body


#mbti만 비교 (리스트 형태의 텍스트로 입력)
def mbti_check(mbti1, mbti2):
    room_mbti = literal_eval(mbti1)
    profile_mbti = literal_eval(mbti2)
    count_mbti = 0
    print("mbti 비교 결과")
    for i in range(4):
        if (room_mbti[i] == 'O') | (room_mbti[i] == profile_mbti[i]):
            print(f"방:{room_mbti[i]} 사용자:{profile_mbti[i]}")
            #pass
        else:
            print(f"방:{room_mbti[i]} 사용자:{profile_mbti[i]} 이므로 입장 불가")
            count_mbti = count_mbti+1
    return count_mbti == 0