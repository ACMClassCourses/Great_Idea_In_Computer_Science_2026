//provide the function for quantum
#include "qubit.h"
#include <complex>
#include <ctime>
#include<iostream>
#include<cmath>
/**
 * @brief creat a new qubit with alpha and beta
 * @param alpha 
 * @param beta 
 * @return a new qubit
 */
Qubit::Qubit(std::complex<double> alpha, std::complex<double> beta) {
    state_.push_back(alpha);
    state_.push_back(beta);
	  normalize();
}

/**
 * @brief make the alpha and beta normalized i.e. alpha ^ 2 + beta ^ 2 = 1
 */
void Qubit::normalize() {
    double total_norm=std::norm(state_[0])+std::norm(state_[1]);
	  if(total_norm == 0) {
	      state_[0] = 1.0;
	      state_[1] = 0.0;
	      return;
	  }
   double sum=std::sqrt(total_norm);
	 state_[0]/=sum;
	 state_[1]/=sum;
}

/**
 * @brief measure the qubit and make the qubit collapse
 * @return the result of the measure,probability for 0 is alpha ^ 2, probability for 1 is beta ^ 2
 */
int Qubit::measure() {
	  static bool initialized = false;
	  if(!initialized){
	      std::srand(std::time(0));
	      initialized = true;
	  }
	  double pro0 = std::norm(state_[0]);
	  double r = static_cast<double>(std::rand()) / RAND_MAX;
	  if(r < pro0){
		    state_[0] = 1.0;
		    state_[1] = 0.0;
		    return 0;
	  }
	  else{
		    state_[0] = 0.0;
		    state_[1] = 1.0;
		    return 1;
	  }
}

/**
 * @brief set the state of the qubit
 * @param new_state the state you want the qubit to be
 */
void Qubit::SetState(std::complex<double> alpha, std::complex<double> beta) {
    state_[0] = alpha;
	  state_[1] = beta;
	  normalize();
}

std::vector<std::complex<double>> Qubit::GetState() {
  return state_;
}
namespace QuantumUtils {
    /**
     * @brief encode the bit to an qubit
     * @param bit the message you want to send
     * @param basis the wa you want to encode, only '+' and 'x', remember to handle for exception  
     */
    Qubit encode_bit(int bit, char basis) {
		    if(bit != 0 && bit != 1){
			      std::cout<<"bit must be 0 or 1";
		    }
		    if(basis != '+' && basis != 'x') {
			      std::cout<<"basis must be '+' or 'x'";
		    }
		    if(basis == '+') {
			      return bit == 0 ? Qubit(1.0,0.0) : Qubit(0.0,1.0);
		    }
		    else{
			      std::complex<double> c = 1.0 / std::sqrt(2.0);
			      return bit == 0 ? Qubit(c,c) : Qubit(-c,c);
		    }
    }
    /**
     * @brief measure the qubit in the way of the basis
     * @param qubit the qubit you want to measure
     * @param basis the way you want to measure
     * @return the result of the measure, only 0 or 1
     */
    int measure_in_basis(Qubit &qubit, char basis) {
        if(basis != '+' && basis != 'x') {
				    std::cout<<"basis must be '+' or 'x'";
		    }
		    if(basis == '+'){
				    return qubit.measure();
		    }
		    else {
            std::vector<std::complex<double>> state = qubit.GetState();
				    std::complex<double> alpha = state[0];
				    std::complex<double> beta = state[1];
				    std::complex<double> new_alpha = (alpha + beta) / std::sqrt(2.0);
				    std::complex<double> new_beta = (beta - alpha) / std::sqrt(2.0);
				    qubit.SetState(new_alpha, new_beta);
				    return qubit.measure(); 
        }
    }
 }