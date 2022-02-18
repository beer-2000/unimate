from ast import literal_eval



class RoomEnterPosible:
    
    def __init__(self, room, profile):
        self.room = room
        self.profile = profile
    
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

    def compare_interest(self):
        room_interest = self.room.interest
        profile_interest = literal_eval(self.profile.interest_list)
        print("interest 비교 결과")
        return room_interest in profile_interest
    
    def compare_college(self):
        room_college = self.room.college
        profile_college = str(self.profile.user.college)
        print("college 비교 결과")
        print(f"방:{room_college} 사용자:{profile_college}")
        return room_college == profile_college

    def compare_university(self):
        room_university = self.room.university
        profile_university = str(self.profile.user.university)
        print("college 비교 결과")
        print(f"방:{room_university} 사용자:{profile_university}")
        return room_university == profile_university
    
    def compare_grade(self):
        room_grade = self.room.grade_limit
        print("grade 비교 결과")
        if room_grade == None:
            print("방에 학년 제한이 없습니다.")
            return True
        profile_grade = self.profile.grade
        print(f"방:{room_grade} 사용자:{profile_grade}")
        return room_grade == profile_grade
    
    def compare_heads(self):
        room_heads_limit = self.room.heads_limit
        room_now_heads = len(self.room.owner.all())
        print("heads(인원)제한 확인 결과")
        print(f"수용 가능 인원: {room_heads_limit}, 현재 인원: {room_now_heads}")
        return room_now_heads < room_heads_limit
        
        


    
    
    





# MBTI 비교 (방 <--> 프로필)
# def compare_mbti(room_mbti, profile_mbti):
#     room = literal_eval(room_mbti)
#     profile = literal_eval(profile_mbti)
#     count_mbti = 0
#     for i in range(4):
#         if (room[i] == 'O') | (room[i] == profile[i]):
#             pass
#         else:
#             count_mbti = count_mbti+1
#     if count_mbti == 0:
#         return True
#     else:
#         return False

def compare_mbti(room, profile):
    room_mbti = literal_eval(room.mbti)
    profile_mbti = literal_eval(profile.mbti)
    count_mbti = 0
    for i in range(4):
        if (room_mbti[i] == 'O') | (room_mbti[i] == profile_mbti[i]):
            pass
        else:
            count_mbti = count_mbti+1
    if count_mbti == 0:
        return True
    else:
        return False





def compare_interest(room_interest, profile_interest):
    profile = literal_eval(profile_interest)
    if room_interest in profile:
        return True
    else:
        return False




# class RoomRecommendAPI(APIView):
#     def get(self, request, format=None):
#         allroom = Room.objects.all().order_by('-created_at')
#         room = allroom[1]
#         print(room)
#         profile = Profile.objects.get(user_id=request.user.id)
#         print(compare_mbti(room.mbti, profile.mbti))
#         return Response(status=status.HTTP_200_OK)