## code up quick randomizer to run from persistent batch. 
import random


# first lets define all trials by ecc
colors = ['(1) Red', '(2) Green', '(3) Blue', '(4) Yellow']
eccentricities = [7, 10]
orientations = ['x', '+']


print('3 degrees, x orientation')
random.shuffle(colors)
print(colors)
print('\n')


# shuffle in-place
random.shuffle(eccentricities)


# lets do 'x' orientation first
print(f'{eccentricities[0]} degrees, {orientations[0]} orientation')
random.shuffle(colors)
print(colors)

print(f'{eccentricities[1]} degrees, {orientations[0]} orientation')
random.shuffle(colors)
print(colors)
print('\n')

# then do '+' orientation last
print(f'{eccentricities[0]} degrees, {orientations[1]} orientation')
random.shuffle(colors)
print(colors)

print(f'{eccentricities[1]} degrees, {orientations[1]} orientation')
random.shuffle(colors)
print(colors)