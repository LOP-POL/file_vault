E = 210*10**3
nu = 0.3

lambda_ = E*nu/((1.0+nu)*(1.0-2.0*nu))
mu = E/(2.0*(1.0+nu))

eps11 = 0.0
eps22 = 1.0e-2
eps12 = 0.0

chi_values = [0,1000,2000,6000,16000]

results = []

for chi in chi_values:
    C11 = lambda_ + 2 * mu + chi
    C12 = lambda_
    C22 = lambda_ + 2 * mu

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
        C12
    ])

if __name__ == '__main__':
    for result in results:
        print("\n-----------------------------")
        print(f'chi value: {result[0]} \n')
        print(f'sig_11 value: {result[1]} \n')
        print(f'sig_22 value: {result[2]}\n')
        print(f'sig_12 value: {result[3]} \n')
        print(f'C11 value: {round(result[4],2)} \n')
        print(f'C22 value: {round(result[5],2)} \n')
        print(f'C12 value: {round(result[6],2)} \n')
        

    
