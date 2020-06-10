import multiprocessing as m
import time

def do_something():
    print("started sleeping")
    time.sleep(1)
    print("done sleeping")

if __name__=="__main__":
    start = time.perf_counter()
    p = []
    for _ in range(0, 4):
        pp = m.Process(target=do_something)
        pp.start()
        p += [pp]

    for i in range(4):
        p[i].join()

    print(time.perf_counter() - start)

    do_something()
