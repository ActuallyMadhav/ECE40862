import random

def main():
    ans = random.randint(0, 10)
    win = False

    print(ans)

    for i in range(3):
        guess = int(input("Enter your guess: "))
        if guess == ans:
            win = True
            break

    if win:
        print("You win!")
    else:
        print("You lose!")

main()