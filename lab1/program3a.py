def main():
    num = int(input("How many fibonacci numbers would you like to generate? "))
    fibNums = fibonacci(num)
    print("The Fibonacci Sequence is: ", end='')
    print(*fibNums, sep=', ')



def fibonacci(x: int) -> list:
    a = 0
    b = 1
    count = 0

    fibNums = []
    while count < x:
        fibNums.append(a)
        next = a + b
        a = b
        b = next
        count += 1

    return fibNums

main()