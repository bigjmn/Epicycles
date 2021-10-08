import math
import numpy as np
import numpy.fft

def fourierdata(pointlist,samp):

    xs = []
    ys = []
    for i in pointlist:
        xs.append(i[0])
        xs.insert(0, i[0])
        ys.append(i[1])
        ys.insert(0,i[1])

    comp_array = np.array(xs, dtype = complex)
    comp_array.imag = np.array(ys)


    full_data = []

    get_fouriers = np.fft.fft(comp_array, samp)

    freqs = np.fft.fftfreq(samp)
    for j in range(samp):
        data_piece = []
        data_piece.append(np.abs(get_fouriers[j])/samp)
        data_piece.append(np.angle(get_fouriers[j]))
        data_piece.append(freqs[j])

        full_data.append(data_piece)

    print(full_data)

    return full_data
