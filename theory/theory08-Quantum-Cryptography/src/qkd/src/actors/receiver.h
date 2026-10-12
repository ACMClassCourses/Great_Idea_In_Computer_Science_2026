#ifndef RECEIVER
#define RECEIVER

#include <vector>
#include "quantum_lib/qubit.h"

class Receiver {
    private:
        int key_length_;
        std::vector<char> bases_;
        std::vector<int> measured_bits_;
    public:
        Receiver(int);
        void measure_qubits(std::vector<Qubit> &);
        const std::vector<char> &GetBases() const;
        const std::vector<int> &GetMeasuredBits() const;
};

#endif
