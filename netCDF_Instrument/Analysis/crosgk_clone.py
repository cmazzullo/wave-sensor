import numpy as np

def make_test_data():
    T = 300  # total time in seconds
    f = 4  # sample frequency in Hz
    t = np.arange(T * f) / f
    periods = (3, 10)  # wave periods in seconds
    amps = (.5, 1)  # amplitudes in meters
    noise = np.random.normal(.5, .03, (len(t),))
    Pwave = sum([amp * np.sin(2 * np.pi * t / period)
                 for amp, period in zip(amps, periods)]) + noise
    return Pwave

def crosgk(X, Y, N, M, DT, DW, stats):
    df = 1 / (N * DT)
    if DW == 1:
        # Hann window
        w = np.hanning(N)
        dj = N / 2
    else:
        w = np.ones(N, 1)
        dj = N

    varw = sum(w**2) / N

    nx = len(X)
    ny = len(Y)
    avgx = sum(X) / nx
    avgy = sum(Y) / ny
    px = np.zeros(len(w))
    py = np.zeros(len(w))
    Pxx = np.zeros(len(w))
    Pxy = np.zeros(len(w))
    Pyy = np.zeros(len(w))
    ns = 0

    ns += 1

    px = X - avgx;
    px = w * px
    px = np.fft.fft(px)

    py = Y - avgy
    py = w * py
    py = np.fft.fft(py)

    Pxx = Pxx + px * np.conj(px)
    Pyy = Pyy + py * np.conj(py)
    Pxy = Pxy + py * np.conj(px)
    
    Pxx = (2 / (ns * (N**2) * varw * df)) * Pxx
    Pyy = (2 / (ns * (N**2) * varw * df)) * Pyy
    Pxy = (2 / (ns * (N**2) * varw * df)) * Pxy

    if M > 1:
        w = []
        w = np.hamming(M)
        w = w / sum(w)
        w1 = np.array(w[np.ceil((M + 1) / 2) : M])
        w2 = np.zeros(N - M)
        w3 = np.array(w[0 : np.ceil((M + 1) / 2)])
        w = np.hstack((w1, w2, w3))
        w = np.fft.fft(w)
        Pxx = np.fft.fft(Pxx)
        Pyy = np.fft.fft(Pyy)
        Pxy = np.fft.fft(Pxy)
        Pxx = np.fft.ifft (w * Pxx)
        Pyy = np.fft.ifft(w * Pyy)
        Pxy = np.fft.ifft (w * Pxy)

    Pxx = Pxx[0 : N / 2]
    Pyy = Pyy[0 : N / 2]
    Pxy = Pxy[0 : N / 2]

    F = []
    F = (np.arange(1, N / 2) -  1) * df

    if DW == 1:
        nn = (ns + 1) * N / 2
    else:
        nn = ns * N

    avgx = sum(X[0:nn]) / nn
    varx = sum((X[0 : nn] - avgx)**2) / (nn - 1)

    avgy = sum(Y[0:nn]) / nn
    vary = sum((Y[0 : nn] - avgy)**2) / (nn - 1)
    covxy = sum((X[0 : nn] - avgx) * (Y[0 : nn] - avgy)) / (nn - 1)


    m0xx = (0.5 * Pxx[0] + sum(Pxx[1 : N / 2 - 1]) +
            0.5 * Pxx[N / 2 - 1]) * df

    m0yy = (0.5 * Pyy[0] + sum(Pyy[1 : N / 2 - 1]) +
            0.5 * Pyy[N / 2 - 1]) * df
    m0xy = (0.5 * Pxy[0] + sum(Pxy[1 : N / 2 - 1]) +
            0.5 * Pxy[N / 2 - 1]) * df

    Pxx = Pxx * (varx / m0xx)
    Pyy = Pyy * (vary / m0yy)
    Pxy = Pxy * (covxy / np.real(m0xy))

    P = [Pxx, Pyy, Pxy]

    return P, F

p = make_test_data()
P, F = crosgk(p, p, len(p), 50, .25, 1, 0)
