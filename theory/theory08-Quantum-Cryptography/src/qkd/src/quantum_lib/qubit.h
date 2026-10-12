#ifndef QUBIT
#define QUBIT

#include<complex>
#include<vector>

class Qubit {
    private:
        std::vector<std::complex<double>> state_;
        void normalize();
    public:
        Qubit(std::complex<double>, std::complex<double>);
        int measure();
        void SetState(std::complex<double>, std::complex<double>);
        std::vector<std::complex<double>> GetState();
};

namespace QuantumUtils {
    Qubit encode_bit(int bit, char basis);
    int measure_in_basis(Qubit &qubit, char basis);
}
#endif