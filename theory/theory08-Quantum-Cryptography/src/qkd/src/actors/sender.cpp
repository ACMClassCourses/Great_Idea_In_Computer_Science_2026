//simulate sender
#include "sender.h"
#include<random>
#include<iostream>


Sender::Sender(int key_length):key_length_(key_length) {
    bases_.reserve(key_length_);
    bits_.reserve(key_length_);
}


/**
 * @brief generate qubits as the key
 * @return the key
 */
std::vector<Qubit> Sender::GenerateBits() {
    std::vector<Qubit> generated_qubit;
    std::cout << "please input bases(x or +) :" << std::endl;
    for(int i = 0;i < key_length_; i++){
        char base;
        std::cin >> base;
        while(base != 'x' && base != '+') {
            std::cout << "please input x or +" << std::endl;
            std::cin >> base;
        }
        bases_.push_back(base);  
    }
    std::cout << "please input bit(0 or 1) :" << std::endl;
    for(int i = 0; i < key_length_; i++){
        int bit;
        std::cin >> bit;
        while(bit != 0 && bit != 1) {
            std::cout << "please input 0 or 1" << std::endl;
            std::cin >> bit;
        }
        bits_.push_back(bit);  
        generated_qubit.push_back(QuantumUtils::encode_bit(bits_[i], bases_[i]));
    }
    return generated_qubit;
}

const std::vector<int> &Sender::GetBits() const {
    return bits_;
}

const std::vector<char> &Sender::GetBases() const {
    return bases_;
}