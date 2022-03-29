### Chapter2 | 자료형

# 104p
# 2.
"""
split() : 문자열을 특정 문자로 자릅니다
upper() : 문자열을 대문자로 변환합니다.
lower() : 문자열을 소문자로 변환합니다.
strip() : 문자열 양옆의 공백을 제거합니다.
"""

# 105p
# 3.
a = input("> 1번째 숫자: ")
b = input("> 2번째 숫자: ")
print()

print("{} + {} = {}".format(int(a), int(b), int(a)+int(b)))

# 4.
string = "hello"

string.upper()
print("A 지점:", string)
#upper 함수를 실행한 결과를 저장하지 않았으므로 "hello"가 출력

print("B 지점:", string.upper())
#upper 함수 실행한 결과를 출력하므로 "HELLO"가 출력