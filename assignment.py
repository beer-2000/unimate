list_num = list(range(1,10000+1))
result = list(range(1,10000+1))


for i in list_num:
    a = i // 10000
    num = i - (10000*a)
    b = num //1000
    num -= 1000*b
    c = num // 100
    num -= 100*c
    d = num // 10
    num -= 10*d
    e = num
    self_num = i + a + b + c + d + e
    if result.count(self_num) == 1:
        result.remove(self_num)

for self_num in result:
    print(self_num)

# list_num = list(range(1,100+1))
# result = list(range(1,100+1))


# for i in list_num:
#     print(f"number : {i}")
#     a = i // 100
#     print(a)
#     num = i - (100*a)
#     b = num //10
#     print(b)
#     num -= 10*b
#     c = num
#     print(c)
#     self_num = i + a + b + c
#     print(self_num)
#     if result.count(self_num) == 1:
#         print('ok')
#         result.remove(self_num)

# print("start")
# for self_num in result:
#     print(self_num)