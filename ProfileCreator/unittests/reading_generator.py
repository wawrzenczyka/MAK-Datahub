import random
import json

def main():
    l = 50
    t = random.randint(0, 2000000000000)
    print("[")
    with open("data/sensor_config.json") as file:
        config = json.load(file)["limits"]
    for i in range(l):
        li = [[random.random()*v, random.random()*v, random.random()*v] for v in config.values()]
        args = (t, li[0], li[1], li[2], li[3], li[4], li[5])
        print("\t\t\t\tSensorReading%s" % str(args), end='')
        t += random.randint(100, 250)
        if i != l - 1:
            print(",")
        else:
            print("")
    print("\t\t\t]")
    
if __name__ == "__main__":
    main()
    #main2()