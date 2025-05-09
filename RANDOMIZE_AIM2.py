## code up quick randomizer to run from persistent batch. 
import random


# first lets define all trials by ecc
colors = ['(1) Red', '(2) Green', '(3) Blue', '(4) Yellow']

print('3 degrees, x orientation')
random.shuffle(colors)
colors.append('(0) Achromatic')
print(colors)
print('\n')