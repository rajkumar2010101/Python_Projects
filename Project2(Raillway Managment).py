# Program for railway management 
class Train:
    def __init__(self , name , fare , seats):
        self.name = name
        self.fare = fare
        self.seats = seats

    def getStatus(self):
        print(f"The Name of train is {self.name} ")
        print(f"The seats available in the trian are {self.seats}")

    def fareInfo(self):
        print(f"The price of the ticket is: Rs {self.fare}")

    def bookTicket(self):
        if(self.seats > 0):
            print(f"your ticket has been booked! Your seat number is {self.seats}")
            self.seats = self.seats - 1
        else:
            print("Train is full! kindly try in Tatkal")

    def cancleTicket(self, tiketno ):
        self.tiketno = tiketno
        for tiketno in [1,2,3,4,5,6,7,8,9]:
            self.seats = self.seats + 1
        print(f"Your seat no is {self.seats} is Cancle")

intercity = Train("Intercity Express : 14015",90,9)
intercity.getStatus()
intercity.bookTicket()
intercity.getStatus()
intercity.fareInfo()
intercity.cancleTicket(1)