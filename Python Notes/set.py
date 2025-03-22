# li = [1,2,3,4]

# def square(ele):
#     return ele * ele 

# result = map(square, li)
# print(result)
# print(list(result))

# li2 = ['10','20','30','40']
# new_li = list(map(int,li2))
# print(new_li)   #[10, 20, 30, 40]  type casting

li3 = [1, 2, 3, 4]
new_li = list(map(float,li3))
print(new_li)

print(list(map(bool,li3)))