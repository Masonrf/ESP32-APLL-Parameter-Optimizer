# A simple program to brute force APLL parameter values that will result in an output clock closest to the desired value
# Equation from section 3.2.7 (page 44) of:
# https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf

# Desired APLL output frequency
f_desired = 49.152E6

# Crystal oscillator frequency
f_xtal = 40E6

from multiprocessing import Pool, Manager

# Class to store parameters
class APLL_Param():
    def __init__(self, f_xtal, sdm0, sdm1, sdm2, odiv):
        self.sdm0 = sdm0
        self.sdm1 = sdm1
        self.sdm2 = sdm2
        self.odiv = odiv
        self.f_out = self.calculate_Fout(f_xtal)
    
    # Equation from technical docs listed above
    def calculate_Fout(self, f_xtal):
        return (f_xtal * (self.sdm2 + self.sdm1/(2**8) + self.sdm0/(2**16) + 4))/(2 * (self.odiv + 2))

# Task for each thread
def threadTask(printLock, extendLock, results, sdm0):
    with printLock:
        print("Start thread sdm0: ", sdm0)
    
    tmpResults = []

    # Range is 0 ~ N+1
    for sdm1 in range(256):
        for sdm2 in range(64):
            for odiv in range(32):
                param = APLL_Param(f_xtal, sdm0, sdm1, sdm2, odiv)
                # Only append if within 1% of desired value to reduce RAM usage and CPU overhead later on
                if 0.99 < (param.f_out / f_desired) < 1.01:
                    tmpResults.append(param)

    with extendLock:
        # Extend with closest value in sdm0
        results.append(min(tmpResults, key=lambda tmpResults:abs(tmpResults.f_out - f_desired)))

# Error callback function
def custom_error_callback(error):
    print(error, flush=True)

if __name__ == '__main__':

    with Manager() as manager:
        extendLock = manager.Lock()
        printLock = manager.Lock()
        results = manager.list()

        with Pool() as p:
            poolDone = p.starmap_async(threadTask, [(printLock, extendLock, results, i) for i in range(256)], error_callback=custom_error_callback)
            poolDone.wait()
            print("Finished calculating.")

        print("Finding closest value.")
        closest = min(results, key=lambda results:abs(results.f_out - f_desired))
        
        print("\n-------- [Results] --------")
        print("Xtal Freq [Hz]:    ", f'{f_xtal:,}')
        print("Desired Freq [Hz]: ", f'{f_desired:,}')
        print("Output Freq [Hz]:  ", f'{closest.f_out:,}')
        print("sdm0: ", closest.sdm0)
        print("sdm1: ", closest.sdm1)
        print("sdm2: ", closest.sdm2)
        print("odiv: ", closest.odiv)
