#ifndef SENDER
#define SENDER

#include <vector>
#include "quantum_lib/qubit.h"

class Sender {
    private:
        std::vector<int> bits_;
        std::vector<char> bases_;
        int key_length_;

    public:
        Sender(int);
        std::vector<Qubit> GenerateBits();
        const std::vector<int> &GetBits() const;
        const std::vector<char> &GetBases() const;
        
};

#endif