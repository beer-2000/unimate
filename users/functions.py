from ast import literal_eval


# MBTI 비교 (방 <--> 프로필)
def compare_mbti(room_mbti, profile_mbti):
    room = literal_eval(room_mbti)
    profile = literal_eval(profile_mbti)
    count_mbti = 0
    for i in range(4):
        if (room[i] == 'O') | (room[i] == profile[i]):
            pass
        else:
            count_mbti = count_mbti+1
    if count_mbti == 0:
        return True
    else:
        return False