
























### 171~173p

# # 1번
# print("1-1")
# dict_a = {}
# dict_a['name'] = '구름'
# print(dict_a)

# print("1-2")
# dict_a = {"name": "구름"}
# del dict_a['name']
# print(dict_a)


# # 2번
# pets = [
#     {"name": "구름", "age": 5},
#     {"name": "초코", "age": 3},
#     {"name": "아지", "age": 1},
#     {"name": "호랑이", "age": 1}
# ]

# print("# 우리 동네 애완 동물들")
# for pet in pets:
#     print(f"{pet['name']} {pet['age']}살")


# 3번
# numbers = [1,2,6,8,4,3,2,1,9,5,4,9,7,2,1,3,5,4,8,9,7,2,3]
# counter = {}

# for number in numbers:
#     if number in counter:
#         counter[number] += 1
#     else:
#         counter[number] = 1

# print(counter)


# 4번
# character = {
#     "name": "기사",
#     "level": 12,
#     "items": {
#         "sword": "불꽃의 검",
#         "armor": "풀플레이트"
#         },
#     "skill": ["베기", "세게 베기", "아주 세게 베기"]
#     }

# for key in character:
#     if type(character[key]) is dict:
#         for i in character[key]:
#             print(f"{i}: {character[key][i]}")
#     elif type(character[key]) is list:
#         for i in character[key]:
#             print(f"{key}: {i}")
#     else:
#         print(f"{key}: {character[key]}")


### 187~189p

# 1번
# """
# range(5) -> [0, 1, 2, 3, 4]
# range(4,6) -> [4, 5]
# range(7,0,-1) -> [7, 6, 5, 4, 3, 2, 1]
# range(3,8) -> [3, 4, 5, 6, 7]
# range(3,10,3) -> [3, 6, 9]
# """

# 2번
# key_list = ["name", "hp", "mp", "level"]
# value_list = ["기사", 200, 30, 5]
# character = {}

# for i in range(len(key_list)):
#     character[key_list[i]] = value_list[i]

# print(character)

# 3번
# limit = 10000
# i = 1
# sum_value = 0
# while sum_value < 10000:
#     sum_value += i
#     print(i)
#     i += 1
#     print(sum_value)
    

# print("{}를 더할 때 {}을 넘으며 그때의 값은 {}입니다.".format(i-1, limit, sum_value))

# 4번
max_value = 0
a = 0
b = 0

for i in range(101):
    j = 100 - i
    if i*j > max_value:
        max_value = i*j
        a = i
        b = j

print("최대가 되는 경우: {} * {} = {}".format(a, b, max_value))