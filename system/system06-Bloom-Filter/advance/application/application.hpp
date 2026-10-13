#ifndef BLOOM_FILTER_APPLICATION_HPP
#define BLOOM_FILTER_APPLICATION_HPP

#include "../experiment/src.hpp"
#include "exact_blacklist.hpp"

#include <set>
#include <string>

inline bool is_spam(
    const std::string& email,
    const std::string& domain,
    const std::set<std::string>& trusted_addresses,
    const BloomFilter& bloom_filter,
    ExactBlacklist& exact_blacklist) {
    (void)email;
    (void)domain;
    (void)trusted_addresses;
    (void)bloom_filter;
    (void)exact_blacklist;
    // TODO: Check one email with Bloom filtering and exact lookup.
    return false;
}

#endif
