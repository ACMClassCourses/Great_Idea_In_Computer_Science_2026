#include "application.hpp"

#include <algorithm>
#include <cstddef>
#include <iostream>
#include <set>
#include <string>

std::string normalize(std::string text) {
    for (std::size_t i = 0; i < text.size(); ++i) {
        if (text[i] >= 'A' && text[i] <= 'Z') {
            text[i] = static_cast<char>(text[i] - 'A' + 'a');
        }
    }
    return text;
}

std::string get_domain(const std::string& email) {
    std::size_t position = email.find('@');
    return email.substr(position + 1);
}

int main() {
    int address_count;
    int domain_count;
    int trusted_count;
    if (!(std::cin >> address_count >> domain_count >> trusted_count)) {
        return 0;
    }

    int blacklist_count = address_count + domain_count;
    std::size_t bit_count = std::max<std::size_t>(
        1, static_cast<std::size_t>(blacklist_count) * 8);
    BloomFilter bloom_filter(bit_count, 4);
    ExactBlacklist exact_blacklist;
    std::set<std::string> trusted_addresses;

    std::string text;
    for (int i = 0; i < address_count; ++i) {
        std::cin >> text;
        text = normalize(text);
        bloom_filter.add("address:" + text);
        exact_blacklist.add_address(text);
    }
    for (int i = 0; i < domain_count; ++i) {
        std::cin >> text;
        text = normalize(text);
        bloom_filter.add("domain:" + text);
        exact_blacklist.add_domain(text);
    }
    for (int i = 0; i < trusted_count; ++i) {
        std::cin >> text;
        trusted_addresses.insert(normalize(text));
    }

    int query_count;
    std::cin >> query_count;
    for (int i = 0; i < query_count; ++i) {
        std::cin >> text;
        std::string email = normalize(text);
        std::string domain = get_domain(email);
        if (is_spam(
                email,
                domain,
                trusted_addresses,
                bloom_filter,
                exact_blacklist)) {
            std::cout << "Spam\n";
        } else {
            std::cout << "Not Spam\n";
        }
    }

    std::cout << "Exact Queries: " << exact_blacklist.query_count() << '\n';
    return 0;
}
