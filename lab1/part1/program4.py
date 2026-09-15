
def main():
    birthdays= {'Adam': '1/1/1',
                'Bob': '2/2/2',
                'Charlie': '3/3/3',
                'David': '4/4/4',
                'Eric': '5/5/5'}

    names = [name for name in birthdays]
    # print(names)
    print("We know the birthdays of: ")
    for name in names:
        print(name)

    request = input("Whose birthday do you want to look up?\n")
    #print(request)
    if request in names:
        print(f"{request}'s birthday is {birthdays[request]}")
    else:
        print("name not found. (check spelling or upper/lower case)")

main()