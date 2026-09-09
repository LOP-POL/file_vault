from math import log

def calculate_stiffness_conts(E=None,nu=None,no_values=5):

    if E is None:
        E = 210*10**3
    if nu is None:
        nu = 0.3

    lambda_ = E*nu/((1.0+nu)*(1.0-2.0*nu))
    mu = E/(2.0*(1.0+nu))

    eps11 = 0.0
    eps22 = 1.0e-2
    eps12 = 0.0

    results = []
    increment = 0.2
    for step in range(no_values):
        C11 = lambda_ + 2 * mu
        chi = C11 * increment
        C12 = lambda_
        C22 = lambda_ + 2 * mu
        C11_mod = C11 + chi

        C26 = 0.0
        C16 = 0.0 

        sigma11 = (C11*eps11 + C12*eps22 + 2* C26*eps12)


        sigma22 = (C12 * eps11 + C22 * eps22 + 2 *C26 * eps12)


        sigma12 = 2 * mu *eps12

        results.append([
            chi,
            sigma11,
            sigma22,
            sigma12,
            C11,
            C22,
            C12,
            C11_mod,
            increment,
        ])
        increment += 0.2
    return results

"""
Generate a Renard-style geometric progression.

@param ratio - optional geometric ratio between successive values.
@param series - optional Renard series (R5, R10, ...) to use.
@param no_values - number of values to generate.
@param decimal_places - number of decimal places in the result.
@param step - stride used in the exponent.
"""

def calculate_renard_series(ratio=None, series=None, decimal_places=2, no_values=4, step=1):
    if ratio is not None and series is not None:
        raise ValueError("Only provide either ratio or series, not both.")

    if ratio is not None:
        if ratio <= 0 or ratio == 1:
            raise ValueError("ratio must be greater than 0 and not equal to 1.")
        if step <= 0:
            raise ValueError("step must be greater than 0.")
        series = log(10) / log(ratio)
    elif series is None:
        series = 5

    if series <= 0:
        raise ValueError("series must be greater than 0.")

    return [
        round(10 ** ((i * step) / series), decimal_places)
        for i in range(no_values + 1)
    ]

if __name__ == '__main__':
    for result in calculate_stiffness_conts():
        print("\n-----------------------------")
        print(f'chi value: {result[0]} \n')
        print(f'sig_11 value: {result[1]} \n')
        print(f'sig_22 value: {result[2]}\n')
        print(f'sig_12 value: {result[3]} \n')
        print(f'C11 value: {round(result[4],2)} \n')
        print(f'C22 value: {round(result[5],2)} \n')
        print(f'C12 value: {round(result[6],2)} \n')
        print(f'C11_mod value: {round(result[7],2)} \n')
        print(f'step value: {round(result[8],2)} \n')
        print(f"renard series : {calculate_renard_series(ratio=3, step=2, decimal_places=4)}")

    
