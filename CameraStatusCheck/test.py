from multiprocessing import Process

x, y, z, k = 1, 2, 0, 0


def reader(a, b, c):
    c = a + b
    k = [c]
    print(c)
    return c


if __name__ == '__main__':
    reader_p = Process(target=reader, args=(x, y, z))
    reader_p.start()
    reader_p.join()
    reader_p.close()
