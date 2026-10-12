// src/main.cpp

#include <iostream>   
#include <vector>    
#include <string>     
#include <numeric>    
#include <algorithm>  
#include <random>     
#include <iomanip>    
#include<memory>


#include "actors/listener.h"
#include "actors/receiver.h"
#include "actors/sender.h"


/**
 * @brief print the vector
 * @tparam T the type of the vector
 * @param name the title for the print
 * @param vec the vector you want to print
 */
template<typename T>
void print_vector(const std::string& title, const std::vector<T>& vec) {
    std::cout << title;
    for (const auto& item : vec) {
        std::cout << item;
    }
    std::cout << std::endl;
}

/**
 * @brief simulation the BB84
 * @param key_length the length for the key
 * @param eavesdrop if there is a eavesdrop
 * @param check_sample_ratio the ratio for check
 */
void run_simulation(int key_length, bool eavesdrop, double check_sample_ratio = 0.5) {

    std::cout << "--- BB84 Simulation Start ---" << std::endl;
    std::cout << "Configuration -> Key Length: " << key_length 
              << ", Eavesdropping: " << (eavesdrop ? "Yes" : "No") << std::endl << std::endl;

    // 1.initialize the role
    Sender sender(key_length);
    Receiver receiver(key_length);
    std::unique_ptr<Listener> listener = nullptr; 
    if (eavesdrop) {
        listener = std::make_unique<Listener>(key_length);
    }

    // 2.sender send the key
    std::cout << "Step 1: Alice generates and sends qubits..." << std::endl;
    std::vector<Qubit> qubits = sender.GenerateBits();
    print_vector("  Alice's original bits:  ", sender.GetBits());
    print_vector("  Alice's original bases: ", sender.GetBases());

    // 3.listener intercept(if there is a listener)
    if (listener) {
        std::cout << "\nStep 2: Eve intercepts, measures, and resends..." << std::endl;
        qubits = listener->eavesdrop(qubits); 
    }
    
    // 4.receiver receive the key
    std::cout << "\nStep " << (eavesdrop ? "3" : "2") << ": Bob receives and measures qubits..." << std::endl;
    receiver.measure_qubits(qubits);
    print_vector("  Bob's measured bases:   ", receiver.GetBases());
    print_vector("  Bob's measured results: ", receiver.GetMeasuredBits());

    // 5. check the bases
    std::cout << "\nStep " << (eavesdrop ? "4" : "3") << ": Alice and Bob compare bases..." << std::endl;
    std::vector<int> matching_indices;
    for (int i = 0; i < key_length; ++i) {
        if (sender.GetBases()[i] == receiver.GetBases()[i]) {
            matching_indices.push_back(i);
        }
    }
    std::cout << "  Bases match at " << matching_indices.size() << " positions (approx. 50%)." << std::endl;
    for(auto key : matching_indices) {
      std::cout << key << " ";
    }
    std::cout << std::endl;
    if (matching_indices.empty()) {
        std::cout << "\nProtocol failed: No matching bases found." << std::endl;
        return;
    }

    // 6. select the key
    std::vector<int> alice_key;
    std::vector<int> bob_key;
    alice_key.reserve(matching_indices.size());
    bob_key.reserve(matching_indices.size());
    for (int index : matching_indices) {
        alice_key.push_back(sender.GetBits()[index]);
        bob_key.push_back(receiver.GetMeasuredBits()[index]);
    }
    print_vector("  Alice's sifted key: ", alice_key);
    print_vector("  Bob's sifted key:   ", bob_key);

    // 7. test
    std::cout << "\nStep " << (eavesdrop ? "5" : "4") << ": Security Check by comparing a sample..." << std::endl;
    int sifted_key_length = alice_key.size();
    int num_check_bits = static_cast<int>(sifted_key_length * check_sample_ratio);
    
    // make sure we have at least 1 key
    if (sifted_key_length > 0 && num_check_bits == 0) {
        num_check_bits = 1;
    }

    // make the list 0, 1, 2,...
    std::vector<int> indices(sifted_key_length);
    std::iota(indices.begin(), indices.end(), 0);

    // randomly permute
    std::random_device rd;
    std::mt19937 g(rd());
    std::shuffle(indices.begin(), indices.end(), g);

    // sample
    int errors = 0;
    for (int i = 0; i < num_check_bits; ++i) {
        int check_index = indices[i];
        if (alice_key[check_index] != bob_key[check_index]) {
            errors++;
        }
    }

    double error_rate = (num_check_bits > 0) ? static_cast<double>(errors) / num_check_bits : 0.0;
    std::cout << "  Comparing " << num_check_bits << " sample bits..." << std::endl;
    std::cout << "  Found " << errors << " errors." << std::endl;
    std::cout << "  Quantum Bit Error Rate (QBER): " << std::fixed << std::setprecision(2) << error_rate * 100.0 << "%" << std::endl;

    // 8. conclusion
    const double EAVES_DROPPING_THRESHOLD = 0.10; // the ratio for the check
    if (error_rate > EAVES_DROPPING_THRESHOLD) {
        std::cout << "\nRESULT: High error rate detected! EAVESDROPPING SUSPECTED. Key is discarded." << std::endl;
    } else {
        // (可选实现) 从密钥中移除已公开的样本比特
        std::cout << "\nRESULT: Security check passed. A secure key can be established." << std::endl;
        // 实际应用中，剩下的密钥会经过错误纠正和保密增强，这里我们简化处理
        std::cout << "  (After removing sample bits, the final key would be derived from the rest)" << std::endl;
    }
    
    std::cout << "\n--- Simulation End ---" << std::endl;
}


// -----------------------------------------------------------------------------
// 程序入口 (Main Entry Point)
// -----------------------------------------------------------------------------
int main() {
    std::cout << "choose ythe key length : ";
    int key_length;
    std::cin >> key_length;

    // --- 场景一：安全信道，无窃听 ---
    std::cout << "SCENARIO 1: Secure Channel (No Eavesdropper)" << std::endl;
    std::cout << "===========================================" << std::endl;
    run_simulation(key_length, false);

    std::cout << "\n\n";

    // --- 场景二：不安全信道，有窃听 ---
    std::cout << "SCENARIO 2: Insecure Channel (With Eavesdropper)" << std::endl;
    std::cout << "==============================================" << std::endl;
    run_simulation(key_length, true);

    return 0;
}