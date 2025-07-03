# num=int(input("enter rows : "))
# for i in range(1,num+1):
#     for j in range(0,i):
#         print("*",end="")
#     print()



def iseven(num):
    if num%2==0:
        return True
    else:
        return False

result=iseven(8)
if result==False:
    print("uneven")

else:
    print("Even")
    
