NEURON {
    SUFFIX extracellular_field
    NONSPECIFIC_CURRENT i
    RANGE amp, freq, phase, offset
}

PARAMETER {
    amp = 0 (nA)      : Field amplitude
    freq = 0 (Hz)     : Field frequency
    phase = 0 (deg)   : Phase (degrees)
    offset = 0 (nA)   : DC offset
    PI = 3.141592653589793
}

ASSIGNED {
    v (mV)
    i (nA)
}

BREAKPOINT {
    i = amp * sin(2 * PI * freq * t / 1000 + phase * PI / 180) + offset
}