import random 
def gamewin(comp , you):
# all possiblity of water(w)
    if comp == you:
        return None 
    elif comp == "w":
        if you == "g":
            return False
        elif you == "s":
            return True
#all possiblity of snake(s)
    elif comp == "s":
        if you == "w":
            return False
        elif you == "g":
            return True
# all possiblity of gun(g)
    elif comp == "g":
        if you == "w":
            return True
        elif you == "s":
            return False
print("computer trun: snake(s) , water(w) , gun(g)?")
randno = random.randint(1,3)
if randno == 1:
    comp = 's'
elif randno == 2:
    comp = 'w'
elif randno == 3:
    comp = 'g'
you = input("your turn: snake(s) , water(w) , gun(g)?   ")
a = gamewin(comp , you)
print(f"computer choice: {comp}")
print(f"Your choice: {you}")
if a == None:
    print("Game is Tie")
elif a:
    print("you win")
else :
    print("computer win")