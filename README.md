# Mandelbrot Fractal Image renderer with a C++ core and a Python Multi-Process and shared memory execution architecture

This project is intended to explore a hybrid Python and C++ architecture for high-performance numerical computing using a distributed framework.

A compute intensive Mandelbrot fractal image generator is written in C++ and shared with the Python framework which calls the shared libary over a muti-processor architecture using a shared memory object across processors working on different sections of the fractal image.

I explore the performance in three ways:

1. Native C++ single threaded operation
2. C++ library called via Python using a single threaded operation
3. C++ library called via Python using a muti-processor architecture using a shared memory coordination

## Key Features

🚀 **C++ Shared Library Acceleration**
The Mandelbrot computation is implemented in C++ and exposed to Python via a shared library (libbrot.so).
This ensures the most performance-critical code runs at native speed.

🧠 **Multi-Processor Execution**
The workload is split across multiple processes using Python’s multiprocessing module, enabling full utilization of all available CPU cores.

🧩 **Shared Memory Data Model**
A single image buffer is allocated using OS-level shared memory (multiprocessing.shared_memory) and safely accessed by all worker processes without copying.

🖼️ **Deterministic Image Output**
Each worker process computes a fixed range of image rows and writes results directly into the shared image buffer.

## Architecture

### High-Level Flow

1. Python initializes shared memory

2. Multiple worker processes are spawned

3. Each worker:

    a) Attaches to the shared memory block

    b) Calls into the C++ Mandelbrot generator

    c) Writes directly into its assigned region

4. The final image is written to disk from shared memory

### Single-Threaded Execution

The single_threaded() path serves as a baseline:

1. Uses a single Python process

2. Calls the C++ library sequentially

3. Useful for correctness verification and performance comparison

This highlights the raw performance of the C++ kernel without parallelism.

### Multi-Process Execution

The multi_process() path demonstrates true parallel computation:

1. One process per CPU core (cpu_count())

2. Each process:

    - Instantiates its own C++ Mandelbrot object

    - Operates on a slice of the image

3. No locks or synchronization primitives are required because:

    - Each process writes to a distinct memory region

This design scales efficiently with available CPU cores.

### Shared Memory Strategy

Instead of copying NumPy arrays between processes, the project uses:

`multiprocessing.shared_memory.SharedMemory`

#### Benefits:

✅ Zero-copy data sharing

✅ Reduced memory overhead

✅ High throughput between processes

✅ Clean separation of computation domains

✅ Inter-Process communication is non-existant due to shared memory

The shared raw memory buffer is wrapped as a NumPy array, enabling seamless integration with Python numerical workflows.

### Why Use Multi-Process Instead of Multi-Thread?

Python threads are constrained by the Global Interpreter Lock (GIL), so even if we multi-threaded the computation, we will not be able to truly utilize the parallelization due to the GIL lock having a single instance. 

Multi-process execution bypasses the GIL entirely as each process independently invokes the C++ shared library. This results in true parallel execution on multiple CPU cores.

## Output

The final result is a binary PPM image (brot.ppm) representing the Mandelbrot fractal set:

![Mandelbrot image](/Images/brot.png)

## Summary

This project demonstrates an effective pattern for high-performance computing in Python:

> Python for orchestration, C++ for computation, shared memory for scalability.

It is particularly well-suited for:

1. Scientific computing

2. Image generation

3. Numerical simulations

4. CPU-bound workloads

## Usage:

To compile and link an executable for the core C++ code:

`g++ -O3 brot.cpp -o brot`

The executable can then be run the following way:

`./brot`

To compile just the object code with out linking:

`g++ -O3 -fPIC brot.cpp -o brot.o`

To link object file and create shared library for use by the Python wrapper:

`g++ -shared -o libbrot.so brot.o`

This creates a shared library called `libbrot.so` which is loaded by the Python code.

> Note: The project provides a pre-compiled shared library. The library needs to be re-compiled only in the case of changes.

## Results:

> Native C++ execution took 69 seconds

> Python single threaded execution took 70.69 seconds

> Python Multiprocess execution took 17.66 seconds
