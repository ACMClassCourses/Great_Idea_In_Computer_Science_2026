//simulate the receiver
#include "receiver.h"
#include<random>
#include<iostream>

Receiver::Receiver(int key_length):key_length_(key_length) {
    bases_.reserve(key_length_);
    measured_bits_.reserve(key_length_);
}


/**
 * @brief measure the received_qubits, the result should be stored in the class member measured_bits_
 * @param received_qubits the qubits you received
 */

void Receiver::measure_qubits(std::vector<Qubit> &received_qubits) {
    std::cout << "please input bases" << std::endl;
    for(int i = 0;i < key_length_; i++){
        char base;
        std::cin >> base;
        while(base != 'x' && base != '+') {
            std::cout << "please input x or +" << std::endl;
            std::cin >> base;

        }
        bases_.push_back(base);
        measured_bits_.push_back(QuantumUtils::measure_in_basis(received_qubits[i], bases_[i]));
    }
    //std::cout << std::endl;
}

const std::vector<char>& Receiver::GetBases() const {
    return bases_;
}

const std::vector<int>& Receiver::GetMeasuredBits() const {
    return measured_bits_;
}
