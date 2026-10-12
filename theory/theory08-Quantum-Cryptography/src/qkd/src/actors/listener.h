#ifndef LISTENER
#define LISTENER

#include <vector>
#include "quantum_lib/qubit.h"

class Listener{
    private:
        int key_length_;
        std::vector<char> bases_;
        std::vector<int> intercepted_bits_;
    public:
    Listener(int);
    std::vector<Qubit> eavesdrop(std::vector<Qubit> &);
    const std::vector<char> &GetBases() const;
    const std::vector<int> &GetInterceptedBits() const;
};

#endif