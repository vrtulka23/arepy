import arepy as apy
import numpy as np

class frequencyBins:
    def __init__(self):
        
        # initial settings
        self.bins = np.array([11.2, 13.6, 15.2, 24.6, 136],dtype=np.float128) * apy.const.eV2Hz
        
        # H2 piecewise values
        self.sxSigmaPW = [ # in [cm^2]
            0.09e-18, 1.15e-18, 3.0e-18, 5.0e-18, 
            6.75e-18, 8.0e-18, 9.0e-18, 9.5e-18, 
            9.8e-18, 10.1e-18, 9.8e-18
        ]
        self.sxEnergyPW = [ # in [Hz]
            3.675345566117e+15, 3.735795328717e+15, 3.796245091318e+15, 3.856694853919e+15,
            3.917144616519e+15, 3.9655044266e+15, 4.0259541892e+15, 4.074313999281e+15, 
            4.110583856841e+15, 4.158943666922e+15, 4.267753239603e+15, 4.376562812284e+15
        ] 

    # calculate cross sections
    def getSigma(self,freq,T=1e3):
        sigma = np.array([
            np.where((self.bins[0]<freq)&(freq<self.bins[2]), 2.47e-18, 0 ),
            np.where(freq<self.bins[1], 0, self.sx_topCrossSectionH(freq,T)/self.sx_bottomCrossSection(freq,T)),
            np.where(freq<self.sxEnergyPW[-1], 0, self.sx_topCrossSectionH2(freq,T)/self.sx_bottomCrossSection(freq,T)),
            np.where(freq<self.bins[3], 0, self.sx_topCrossSectionHe(freq,T)/self.sx_bottomCrossSection(freq,T)),
        ])
        for f in range(len(self.sxEnergyPW)-1):
            ids = (self.sxEnergyPW[f]<freq) & (freq<self.sxEnergyPW[f+1])
            sigma[2][ids] = self.sxSigmaPW[f]
        return sigma

    # crossection integrals
    def sx_topCrossSectionH( self, freq, T ):
        return 2.23938132e29 / ( freq * ( np.exp( apy.const.h * freq / ( apy.const.k_B * T ) ) - 1.0 ) )

    def sx_topCrossSectionH2( self, freq, T ):
        return 8.17342552e29 / ( freq * ( np.exp( apy.const.h * freq / ( apy.const.k_B * T ) ) - 1.0 ) )

    def sx_topCrossSectionHe( self, freq, T ):
        return 9.492e-16 * (4.15752 + ( 1.4434 - 3.038699e-16 * freq)**2) * \
            (1.0 + 0.825067 * (4.5625 + ( 0.4434 - 3.038699e-16 * freq)**2.0)**0.25)**-3.188 * \
            (4.5625 + ( 0.4434 - 3.038699e-16 * freq)**2.0)**-1.953 * \
            freq * freq / ( np.exp( apy.const.h * freq / ( apy.const.k_B * T ) ) - 1.0 )
             
    def sx_bottomCrossSection( self, freq, T ):
        return freq * freq / ( np.exp( apy.const.h * freq / ( apy.const.k_B * T ) ) - 1.0 )
