//simulate the listener,where define the class Listener
#include "listener.h"
#include <iostream>

Listener::Listener(int key_length):key_length_(key_length) {
    bases_.reserve(key_length_);
    intercepted_bits_.reserve(key_length_);
}

/**
 * @brief measure the qubits and resend the qubits for length key_length_
 * @param original_qubits the intercepted qubits
 * @return the qubits to resend
 */
std::vector<Qubit> Listener::eavesdrop(std::vector<Qubit> &original_qubits) {
    std::cout << "please input bases" << std::endl;
    for(int i = 0;i < key_length_; i++){
        char base_;
        std::cin >> base_;
        bases_.push_back(base_);
        intercepted_bits_.push_back(QuantumUtils::measure_in_basis(original_qubits[i], bases_[i]));
        //decode the intercepted_bits_
    }
    for(int i = 0;i < key_length_; i++){
        std::cout << intercepted_bits_[i];
    }
    std::cout << std::endl;
    std::vector<Qubit> out_Qubit;
    for(int i = 0;i < key_length_; i++){
        out_Qubit.push_back(QuantumUtils::encode_bit(intercepted_bits_[i], bases_[i]));
    }
    return out_Qubit;
}

const std::vector<char>& Listener::GetBases() const {
    return bases_;
}

const std::vector<int>& Listener::GetInterceptedBits() const {
    return intercepted_bits_;
}
