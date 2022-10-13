# A simple program to brute force APLL parameter values that will result in an output clock closest to the desired value
# Equation from section 3.2.7 (page 44) of:
# https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf

# Desired APLL output frequency
f_desired = 49.152E6

# Crystal oscillator frequency
f_xtal = 40E6


class APLL_Param():
    def __init__(self, f_xtal, sdm0, sdm1, sdm2, odiv):
        self.sdm0 = sdm0
        self.sdm1 = sdm1
        self.sdm2 = sdm2
        self.odiv = odiv
        self.f_out = self.calculate_Fout(f_xtal)
    
    def calculate_Fout(self, f_xtal):
        return (f_xtal * (self.sdm2 + self.sdm1/(2**8) + self.sdm0/(2**16) + 4))/(2 * (self.odiv + 2))


results = []

# Ranges 0 ~ N so to include ending value, range(N+1)
for sdm0 in range(255+1):
    if (sdm0 % 5 == 0):
        print("On sdm0 = ", sdm0)

    for sdm1 in range (255+1):
        for sdm2 in range(63+1):
            for odiv in range(31+1):
                param = APLL_Param(f_xtal, sdm0, sdm1, sdm2, odiv)
                # Only append if within 2.5% of desired value to reduce RAM usage
                if 0.975 < (param.f_out / f_desired) < 1.025:
                    results.append(param)

closest = min(results, key=lambda results:abs(results.f_out - f_desired))
print("Xtal Freq: ", f_xtal)
print("Desired Freq: ", f_desired)
print("Output Freq: ", closest.f_out)
print("sdm0: ", closest.sdm0)
print("sdm1: ", closest.sdm1)
print("sdm2: ", closest.sdm2)
print("odiv: ", closest.odiv)
