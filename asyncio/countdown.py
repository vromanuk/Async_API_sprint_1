def countdown(n: int):
    print(f"Counting down from {n}")
    while n > 0:
        yield n
        n -= 1
    print("Done counting down")


if __name__ == "__main__":
    for i in countdown(10):
        print(i)
