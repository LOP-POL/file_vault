from math import log, pi
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
class experiment:
    """An elastic stiffness tensor represented in 6x6 Voigt notation."""

    def __init__(self, E=None, nu=None, no_values=5,for_chi=0):
        result = calculate_stiffness_conts(E, nu, no_values)[for_chi]
        chi, C11, C12, C11_mod = result[0], result[4], result[6], result[7]
        if E is None:
            E = 210 * 10**3
        if nu is None:
            nu = 0.3
        C44 = E / (2.0 * (1.0 + nu))
        self.stiffness = [
            [C11_mod, C12, C12, 0.0, 0.0, 0.0],
            [C12, C11, C12, 0.0, 0.0, 0.0],
            [C12, C12, C11, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, C44, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, C44, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, C44],
        ]

    
    def rotate(self, angle):
        """Rotate the stiffness tensor about the z axis by ``angle`` radians."""
        from math import cos, sin

        c, s = cos(angle), sin(angle)
        Q = [[c, -s, 0.0],
            [s, c, 0.0],
            [0.0, 0.0, 1.0]]
        pairs = ((0, 0), (1, 1), (2, 2), (1, 2), (0, 2), (0, 1)) # used to index the parts of the tensors that are needed to be changed
        tensor = [[[[0.0] * 3 for _ in range(3)] for _ in range(3)] for _ in range(3)] # creating a fourth order tensor with zeros
        """ copying the values from the stiffness into teh fourth order tensor """
        for a, (i, j) in enumerate(pairs):
            for b, (k, l) in enumerate(pairs):
                value = self.stiffness[a][b]
                tensor[i][j][k][l] = value
                tensor[j][i][k][l] = value
                tensor[i][j][l][k] = value
                tensor[j][i][l][k] = value
        rotated = [[0.0] * 6 for _ in range(6)] # making a second order tensor with zeros
        for a, (i, j) in enumerate(pairs):
            for b, (k, l) in enumerate(pairs):
                rotated[a][b] = sum(
                    Q[i][p] * Q[j][q] * Q[k][r] * Q[l][t] * tensor[p][q][r][t] # the tensor with the copied stiffness entries are then rotated using the standard method
                    for p in range(3) for q in range(3)
                    for r in range(3) for t in range(3)
                ) 
        self.stiffness = rotated
        return rotated

    def rotate_deg(self, angle):
            """ Rotate teh stiffness tensor by an angle, angle is given in dgerees """
            a = angle * pi/180
            return self.rotate(a)
            
        
    def get_component(self, i, j):
        """Return a component using 1-based Voigt notation."""
        if not (1 <= i <= 6 and 1 <= j <= 6):
            raise IndexError("Voigt indices must be between 1 and 6")
        return self.stiffness[i - 1][j - 1]

def degrees_to_radians(angle):
    return angle * pi/180

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
    Experiment = experiment(for_chi=1)
    component_before_rotation = Experiment.get_component(i=1,j=1)
    Experiment.rotate_deg(45)
    component = Experiment.get_component(i=1,j=1)
    print([round(i[0]) for i in calculate_stiffness_conts()])
    print([i[8] for i in calculate_stiffness_conts()])
    print([round(i[4]) for i in calculate_stiffness_conts()])
    print([round(i[7]) for i in calculate_stiffness_conts()])
    print(f'component11: {component}')
    print(f'component11 before rotation: {component_before_rotation}')
    

    #     print("\n-----------------------------")
    #     print(f'chi value: {result[0]} \n')
    #     print(f'sig_11 value: {result[1]} \n')
    #     print(f'sig_22 value: {result[2]}\n')
    #     print(f'sig_12 value: {result[3]} \n')
    #     print(f'C11 value: {round(result[4],2)} \n')
    #     print(f'C22 value: {round(result[5],2)} \n')
    #     print(f'C12 value: {round(result[6],2)} \n')
    #     print(f'C11_mod value: {round(result[7],2)} \n')
    #     print(f'step value: {round(result[8],2)} \n')
    #     print(f"renard series : {calculate_renard_series(ratio=3, step=2, decimal_places=4)}")

    
