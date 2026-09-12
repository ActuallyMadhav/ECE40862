# Use this list in your program: [10, 20, 10, 40, 50, 60, 70]

def solve(nums: list, target: int):
    indices = {}
    for i in range(len(nums)):
        indices[nums[i]] = i

    for i in range(len(nums)):
        complement = target - nums[i]
        if (complement in indices) and indices[complement] != i:
            return [i, indices[complement]]
        
    return []

def main():
    nums = [10, 20, 10, 40, 50, 60, 70]
    target = int(input("What is your target number? "))
    index1, index2 = solve(nums, target)
    print(f"index1={index1}, index2={index2}")

main()