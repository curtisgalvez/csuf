import maze
import sys

if len(sys.argv) > 1:
    runs = int(sys.argv[1])
else:
    print('\nUsage: python simulation.py <number_of_runs>\n')
    sys.exit(1)

captured = 0
min = 1000
max = 0
avg = []

for i in range(0, runs):
    result = maze.main()
    if result[1] == False:
        if result[0] < min:
            min = result[0]
        elif result[0] > max:
            max = result[0]
        avg.append(result[0])
    else:
        captured += 1
print('\n# of steps with {0} runs\nMinimum: {1}\nMaximum: {2}\nAverage: {3}\nCaptured: {4}'.format(runs, min, max, sum(avg)/runs, captured))