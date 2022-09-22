with open("a.txt") as f:
    for line in f:
        a="".join(line.split(" "))
        with open("b.txt","a") as f2:
            f2.write(a)