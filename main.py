import os
import time
import numpy as np

from multiprocessing import shared_memory, cpu_count
from multiprocessing import Process, current_process
from typing import Type
from brot_wrapper import mandelbrot

WID = 1024
HGT = 1024
SAMPLES = 4

X_MIN = -0.60
Y_MIN = 0.48
PITCH = (0.15) / WID


def write_image(buffer):
    with open("brot.ppm", "wb") as ppm:
        ppm.write(f"P6\n#Mandelbrot set\n{WID} {HGT}\n255\n".encode("ascii"))
        ppm.write(buffer.tobytes())
        # To flip the image 180 degrees
#        for i in range(HGT-1, -1, -1):
#            ppm.write(buffer[i].tobytes())


def single_threaded():
    # 2-dimensional array
    buffer = np.zeros((HGT, 3 * WID), dtype=np.uint8)

    brot = mandelbrot()

    start = time.time()
    # Generate the image
    for i in range(HGT):
        y = Y_MIN + i * PITCH
        brot.generate(X_MIN, y, PITCH, SAMPLES, WID, buffer[i])
    end = time.time()
    elapsed = end - start
    print(f"single threaded execution took {elapsed} seconds")

    brot.brot_delete()

    # Write out the generated image to file
    write_image(buffer)


def multi_threaded(brot: Type[mandelbrot]):
    pass


def generate(shm_name, shape, dtype, start):
    print(f"CPU: {current_process().name}, PID: {os.getpid()}")
    brot = mandelbrot()
    # Retrieve the reference to memory by name
    shm = shared_memory.SharedMemory(name=shm_name)
    # Cast the raw memory to usable shape
    np_array = np.ndarray(shape=shape, dtype=dtype, buffer=shm.buf)

    end = min(start+100, shape[0])
    for i in range(start, end):
        y = Y_MIN + i * PITCH
        brot.generate(X_MIN, y, PITCH, SAMPLES, WID, np_array[i])

    brot.brot_delete()
    # Release reference to memory
    shm.close()


def create_shared_memory_block():
    print("Creating shared multi process memory")
    # create a regular NumPy array in local process memory
    buffer = np.zeros((HGT, 3 * WID), dtype=np.uint8)
    # Allocate a raw shared memory block at the OS level
    shm = shared_memory.SharedMemory(create=True, size=buffer.nbytes)
    # Wrap the shared memory as a NumPy array
    np_array = np.ndarray(buffer.shape, dtype=np.uint8, buffer=shm.buf)
    # Copy initial data into shared memory
    np_array[:] = buffer[:]
    return shm, np_array


def multi_process():
    # Create a shared memory block
    shm, np_array = create_shared_memory_block()
    shape, dtype = np_array.shape, np_array.dtype

    processes = []
    start = 0
    s_time = time.time()

    for i in range(cpu_count()):
        _process = Process(target=generate, args=(shm.name, shape, dtype, start)) # noqa
        processes.append(_process)
        _process.start()
        start += 100

    for _process in processes:
        _process.join()

    e_time = time.time()
    elapsed_time = e_time - s_time
    print(f"Multiprocess execution took {elapsed_time} seconds")

    # Write out the generated image to file
    write_image(np_array)

    # Release reference to memory
    shm.close()
    # Free memory
    shm.unlink()


if __name__ == "__main__":
    try:
        single_threaded()
        multi_process()
    except Exception as e:
        print(f"Failed with error {e}")
