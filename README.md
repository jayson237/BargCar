# BargCar

Barg Car is an online car rental company with several physical offices. Each office must have at least one
employee. Cars are parked in one of the offices.
To rent a car, a customer first register their information online on via an app. Then they choose a car
model, the pickup location (i.e., one of the offices), the start date, and the number of days they want to
rent the car.
For each car model, the company has a specific daily rent price as well as a fixed deposit price. To make
a booking, the customer will have to make a payment using a credit card. At this point, the booking is
made with a unique booking id and the booking date is also recorded.
If there is a car available at a particular location, Barg Car assigns a specific car with a specific license
plate number to the booking. A car is available if the car belongs to the location, it is not being rented
in the duration of the rent, and it is not damaged. A car is rented if between start date and (start date
+ number of day) there is a booking. However, a car may be returned early, in which case the car will be
available the following day. We will assume that the car will not be returned late. Once the available car
is assigned, the assigned car is guaranteed to be available at the pickup location on the given start date.
Additionally, given the booking id, the customer may also hire a driver. A driver is also an employee of
Barg Car. The driver need not be hired for the full duration of the booking but cannot be hired before
the start date or after the return date (i.e., after the start date + the number of days). For instance, if
the start date is 15/01/2024 and the booking is 5 days, the return date is 20/01/2024. For simplicity, a
driver can only be hired for consecutive days. As such, for the duration above, the customer cannot hire
a driver on 15/01/2024 and 17/01/2024, skipping 16/01/2024. However, the customer may hire a driver
from 16/01/2024 to 19/01/2024.
To guarantee that a specific car is available at the given location, each specific car belongs to only one
location. Although customers are allowed to return the car to any location, the company will move the
car to its correct location. This is done overnight with the guarantee that if a car is returned to a different
location on 20/01/2024, it will be available at the correct location by 21/01/2024. You do not havve to
worry about how Barg Car handles this.
On the start date of the rent, an employee of Barg Car at the pickup location will pass the key to the
customer. This has to be recorded in the database for tracking purposes. When the customer returns
the car at any location, another employee at the return location (which may be different from the pickup
location) will receive the key from the customer. If the total cost for the rent is lower than the deposit,
the difference is returned. Otherwise, additional payment is to be made by the customer using credit card.
Note that the total cost for the rent is the number of days times the daily rent price. Even if the car is
returned early, we will still charge for the entire booking duration.
Consider a car with a daily rent price of $200 and a deposit of $1500 is rented from 20/10/2024. If the car
is rented for 4 days but is returned on 22/02/2024, the total cost is $800. So $700 (i.e., $1500 - $800) from
the deposit is returned to the customer. On the other hand, if the car is rented for 10 days, the customer
must pay an additional $500.
