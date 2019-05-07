# FractalGenerator
A fractal generator with a GUI.

The user can input functions f(z,c) and the program will generate pretty pictures of 
the fractals resulting from the convergence or divergence of the iterated evaluation
of z = f(z,c). In particular, f(z,c) = z**2 + c  generates the famous Mandelbrot set, 
and the generalizations f(z,c)= z**n + c gives the so called generalized Mandelbrots. 

The GUI is written in PyQt, and allows for intuitive zooming using the mouse, and a 
number of different color schemes and color interpolation options to experiment with. 
The fractal generation code uses the nice Numba library, which allows for just-in-time
compilation of numerical python functions to C code. This gives almost a factor of 100 
speed up, compared to just running pure python and numpy. 

I also use the Sympy package (a lightweight symbolic math python package) for extracting
the degree of the polynomial that the user can input. 

The required packages are listed in the requirements.txt file. 
