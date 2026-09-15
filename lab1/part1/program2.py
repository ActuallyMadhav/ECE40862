import random

def main():
    a = [random.randint(1, 25) for i in range(10)]
    print(a)

    num = int(input("Enter number: "))
    b = [i for i in a if i < num]
    print("The new list is", b)
main()