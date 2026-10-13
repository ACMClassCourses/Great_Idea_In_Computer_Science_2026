#ifndef BLOOM_FILTER_EXACT_BLACKLIST_HPP
#define BLOOM_FILTER_EXACT_BLACKLIST_HPP

#include <set>
#include <string>

class ExactBlacklist {
public:
    ExactBlacklist() : query_count_(0) {
    }

    void add_address(const std::string& email) {
        addresses_.insert(email);
    }

    void add_domain(const std::string& domain) {
        domains_.insert(domain);
    }

    bool contains(const std::string& email, const std::string& domain) {
        ++query_count_;
        return addresses_.count(email) > 0 || domains_.count(domain) > 0;
    }

    int query_count() const {
        return query_count_;
    }

private:
    std::set<std::string> addresses_;
    std::set<std::string> domains_;
    int query_count_;
};

#endif
