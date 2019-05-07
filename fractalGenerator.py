from cmath import log 
import math 
import numpy as np 
import time
from numba import jit
from PIL import Image 
import matplotlib.pyplot as plt
from sympy import Poly, symbols, sympify

def timeit(f):
    """decorator for timing functions. The decorated function
    returns a tuple (f(), time), since this is the format 
    useful for passing the elapsed time to the GUI."""
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        # print('took ' + str( te-ts) + ' seconds')
        return result, (te-ts)
    return timed

#dictionary for the colorschemes that the fractal can be rendered with.
colorschemes = { 
    "Plasma": plt.get_cmap("plasma") , 
    "Inferno" : plt.get_cmap("inferno"),
    "Spectral" :plt.get_cmap("nipy_spectral"),
    "Seismic":plt.get_cmap("seismic"),
    "HSV":plt.get_cmap("hsv"),
    "Prism" : plt.get_cmap("prism"),
    "Rainbow": plt.get_cmap("gist_rainbow"),
    "Flag" : plt.get_cmap("flag"),
    "Greys inverted": plt.get_cmap("gist_gray"),
    "Viridis": plt.get_cmap("viridis"),
    "Magma" : plt.get_cmap("magma"),
    "Cividis": plt.get_cmap("cividis"),
    "Greys" : plt.get_cmap("Greys"),
    "Blues" : plt.get_cmap("Blues"),
    "Reds" : plt.get_cmap("Reds"),
     "Copper" : plt.get_cmap("copper"),
     "Winter": plt.get_cmap("winter"),
      "Cool": plt.get_cmap("cool")
}

## Color interpolation functions, that 'squash' the color gradients in various ways. 
## all of them are of the type f:(0,1) -> (0,1)
def linear(x,maxiter):
    return x 
def sinus(x,maxiter):
    return np.sin(x*math.pi/2)
def autolog(x, maxiter):
    return (np.log(x*maxiter)/math.log(maxiter))
def logn(x,maxiter,n):
    return np.log(x*4**n + 1)/math.log(4**n + 1)
def gamma(x,maxiter, n ):
    return np.power(x,1/n)

#dict. for the interpolatoin functions
colorInterpolations = { 
    "Linear": linear , 
    "Sin": sinus , 
    "Autolog" : autolog,
    "Log 2": lambda x,m: logn(x,m,2),
    "Log 3": lambda x,m: logn(x,m,3),
    "Log 4": lambda x,m: logn(x,m,4),
    "Gamma 2": lambda x,m :gamma(x,m,2) ,
    "Gamma 3": lambda x,m :gamma(x,m, 3),
    "Gamma 4": lambda x,m :gamma(x,m, 4)  }



def get_poly_matrix(expression:str):
    """parses the given string into a polynomial and extracts the coefficient matrix.
    The argument has to be a valid polynomial in z and c, written in python syntax, 
    and where the letter I is used for the imaginary unit.
    
    returns a matrix of coefficients of z and c, as a numpy array.
    """

    z,c, H= symbols('z c H')
    poly = Poly(sympify(expression), z)
    zdeg=poly.degree() 
    zcoeffs = poly.all_coeffs() 
    cdeg = max([Poly(coef,c).degree() for coef in zcoeffs ])
    
    for n in range(zdeg+1):
        poly += H*z**n * c**cdeg 
    
    coefmatrix = [ Poly(coef,c).all_coeffs() for coef in poly.all_coeffs() ]
    coefmatrix = [ [ x.subs(H,0) for x in col ] for col in coefmatrix]
    return np.array( coefmatrix , dtype = np.complex ) 


def get_fractal_set(function:str,xmin:float,xmax:float,ymin:float,ymax:float,\
    width:int,height: int ,maxiter:int ) : 
    """
    The main function, that takes in the specifications of the fractal.
    Returns a tuple of (set, time) where set is a numpy array of shape (width,height) 
    with values between 0 and 1, and time is the time it took to generate the fractal. 
    """
    coefmatrix = get_poly_matrix(function)
    zdeg, cdeg = coefmatrix.shape 
    B = 5 #2**(1/(zdeg-2)) #B controls the divergence check; essentially needs to be picked large enough. 
    #for normal mandelbrot, the typical value is B=2. 

    convergence_lim=B**2 
    logzdeg = log(zdeg-1)
    logB = log(B)
    
    #parsing the given expression into a jit-function.
    lambdastr=f'lambda z,c:'+function.replace("I",'complex(0,1)')
    lambdafunc = eval(lambdastr)
    func = jit(nopython=True)(lambdafunc)

    #the function that computes the divergence of a point. 
    @jit(nopython=True)
    def fractal_test(z:complex):
        c = z 
        for n in range(maxiter):
            if z.real*z.real + z.imag*z.imag > convergence_lim: 
                sn = n - log( log (abs(z))/logB)/logzdeg
                return sn.real
            z = func(z,c)

        return (maxiter- log( log (abs(z))/logB)/logzdeg).real
    
    ##the function that loops over the lattice points, using the above function to compute the divergence for each one.
    @timeit
    @jit(nopython=True)
    def fractal_set():
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        fractal_set = [fractal_test(complex(r, i)) for r in r1 for i in r2]
        return fractal_set 
    
    set,time = fractal_set()
    #convert to a np.array and reshape into proper dimensions for generating an image
    set = np.array(set).reshape((width, height))
    set = set/maxiter

    return set,time



#the mandelbrot functions that I started with. 
# @jit
# def mandelbrot(z:complex,maxiter):
#     c = z
#     deg = 2.0
#     B = 2.0 
#     for n in range(maxiter):
#         # if abs(z) > 2:
#         if z.real*z.real + z.imag*z.imag > 4 : 
#             sn = n - log( log (abs(z))/log(B))/log(deg)
#             return sn.real
#         z = z*z + c
#     return (maxiter- log( log (abs(z))/log(B))/log(deg)).real

# @timeit
# @jit
# def mandelbrot_set(xmin,xmax,ymin,ymax,width,height,maxiter):
#     r1 = np.linspace(xmin, xmax, width)
#     r2 = np.linspace(ymin, ymax, height)
#     # return (r1,r2,[mandelbrot(complex(r, i),maxiter) for r in r1 for i in r2])
#     mandel = [mandelbrot(complex(r, i),maxiter) for r in r1 for i in r2]
#     man = np.array(mandel, dtype=float).reshape((width, height))
#     return man/maxiter 


def rescale(set: np.array,maxiter:int, interpolation:str):
    """Rescales the array representing the fractal according to the specified interpolation."""
    return colorInterpolations[interpolation](set,maxiter)

def save_image(set, filename:str, color:str):
    """Saves the given set as an image with the given filename, using the specified colormap to map 
    the array (with values between 0 and 1) to a nice color gradient. """
    colormap = colorschemes[color]
    img = Image.fromarray( np.uint8(colormap(set)*255)).transpose(Image.ROTATE_90)
    img.save(filename+".png",format="png")