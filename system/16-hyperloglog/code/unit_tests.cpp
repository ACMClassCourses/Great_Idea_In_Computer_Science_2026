#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <string>
#include "hash.hpp"
#include "part0_naive.hpp"
#include "part1_dense.hpp"
#include "part2_sparse.hpp"

static int passed = 0;
static int failed = 0;

void check(bool ok, const char* name) {
    if (ok) {
        ++passed;
    } else {
        ++failed;
        std::printf("FAIL: %s\n", name);
    }
}

void checkNear(double a, double b, double tol, const char* name) {
    check(std::fabs(a - b) <= tol, name);
}

struct Rng {
    uint64_t state;

    explicit Rng(uint64_t seed) : state(seed) {}

    uint64_t next() {
        state += 0x9e3779b97f4a7c15ULL;
        return splitmix64(state);
    }
};

template <class T>
void feed(T& hll, uint64_t distinct, uint64_t repeats, uint64_t seed) {
    for (uint64_t i = 0; i < distinct; ++i) {
        hll.add("user_" + std::to_string(i));
    }

    Rng rng(seed);
    for (uint64_t i = 0; i < repeats; ++i) {
        hll.add("user_" + std::to_string(rng.next() % distinct));
    }
}

void testHash() {
    check(hash64("abc") == hash64("abc"), "hash is deterministic");
    check(hash64("abc") != hash64("abd"), "different strings usually hash differently");
    check(bucketIndex(0xA000000000000000ULL, 4) == 10, "bucket index");
    check(rho(0x0800000000000000ULL, 4) == 1, "rho 1");
    check(rho(0x0400000000000000ULL, 4) == 2, "rho 2");
    check(rho(0x0200000000000000ULL, 4) == 3, "rho 3");
    check(rho(0x0000000000000000ULL, 4) == 61, "rho all zero");
}

void testBasic() {
    HLL0 empty;
    check(empty.estimate() == 0.0, "empty basic HLL");

    HLL0 h;
    feed(h, 1000, 0, 1);
    double first = h.estimate();
    feed(h, 1000, 0, 1);
    check(h.estimate() == first, "duplicates do not change basic HLL");
    checkNear(h.estimate(), 1000.0, 100.0, "basic estimate near truth");

    HLL0 left;
    HLL0 right;
    HLL0 whole;
    Rng rng(7);

    for (int i = 0; i < 100000; ++i) {
        std::string value = "user_" + std::to_string(rng.next() % 50000);
        whole.add(value);
        if (i % 2 == 0) {
            left.add(value);
        } else {
            right.add(value);
        }
    }

    left.merge(right);
    check(left.estimate() == whole.estimate(), "basic merge matches whole stream");

    bool threw = false;
    try {
        HLL0 a(4);
        HLL0 b(5);
        a.merge(b);
    } catch (const std::invalid_argument&) {
        threw = true;
    }
    check(threw, "basic merge rejects different p");
}

void testDenseBits() {
    DenseHLL h(4);

    for (size_t i = 0; i < 16; ++i) {
        for (int value = 0; value < 64; ++value) {
            h.set(i, static_cast<uint8_t>(value));
            check(h.get(i) == value, "dense set/get");
        }
    }

    DenseHLL edge(4);
    edge.set(0, 63);
    edge.set(1, 17);
    edge.set(2, 31);
    check(edge.get(0) == 63, "dense neighbor 0");
    check(edge.get(1) == 17, "dense neighbor 1");
    check(edge.get(2) == 31, "dense neighbor 2");

    DenseHLL large;
    for (uint32_t i = 0; i < large.m(); ++i) {
        large.set(i, static_cast<uint8_t>((i * 7919) % 64));
    }
    for (uint32_t i = 0; i < large.m(); ++i) {
        check(large.get(i) == (i * 7919) % 64, "dense large table");
    }
}

void testDenseBehavior() {
    HLL0 basic;
    DenseHLL dense;
    feed(basic, 10000, 40000, 5);
    feed(dense, 10000, 40000, 5);
    check(basic.estimate() == dense.estimate(), "dense matches basic");

    auto buf = dense.dump();
    check(buf.size() == 16 + 4096 * 6 / 8, "dense size");
    check(buf[0] == 'H' && buf[1] == 'L' && buf[2] == 'L' && buf[3] == '1', "dense magic");
    check(buf[5] == 1, "dense encoding byte");

    double before = dense.estimate();
    dense.set(0, static_cast<uint8_t>((dense.get(0) + 1) & 0x3F));
    check(dense.estimate() != before || dense.get(0) == 0, "dense recalculates after set");

    DenseHLL original;
    feed(original, 50000, 10000, 9);
    double estimate = original.estimate();
    auto saved = original.dump();
    DenseHLL restored = DenseHLL::load(saved);
    check(restored.dump() == saved, "dense dump/load bytes");
    check(restored.estimate() == estimate, "dense dump/load estimate");

    bool threw = false;
    auto bad_magic = saved;
    bad_magic[0] = 'X';
    try {
        DenseHLL::load(bad_magic);
    } catch (const std::runtime_error&) {
        threw = true;
    }
    check(threw, "dense rejects bad magic");

    threw = false;
    try {
        DenseHLL bad(3);
    } catch (const std::invalid_argument&) {
        threw = true;
    }
    check(threw, "dense rejects small p");

    threw = false;
    try {
        DenseHLL bad(15);
    } catch (const std::invalid_argument&) {
        threw = true;
    }
    check(threw, "dense rejects large p");
}

void testSparse() {
    HLL0 basic;
    SparseHLL sparse;
    feed(basic, 1000, 4000, 11);
    feed(sparse, 1000, 4000, 11);

    checkNear(sparse.estimate(), basic.estimate(), 1e-6, "sparse matches basic");
    check(!sparse.isDense(), "small sparse stays sparse");
    check(sparse.memBytes() < 16 + 4096 * 6 / 8, "small sparse uses less memory");

    double before = sparse.estimate();
    sparse.promote();
    check(sparse.isDense(), "promote changes state");
    checkNear(sparse.estimate(), before, 1e-9, "promote keeps estimate");
    check(sparse.memBytes() == 16 + 4096 * 6 / 8, "promoted size");

    SparseHLL automatic;
    feed(automatic, 100000, 0, 4);
    check(automatic.isDense(), "large sparse promotes automatically");

    SparseHLL saved_sparse;
    feed(saved_sparse, 500, 0, 3);
    auto sparse_buf = saved_sparse.dump();
    check(sparse_buf[5] == 0, "sparse encoding byte");
    SparseHLL loaded_sparse = SparseHLL::load(sparse_buf);
    checkNear(loaded_sparse.estimate(), saved_sparse.estimate(), 1e-12, "sparse dump/load");

    SparseHLL saved_dense;
    feed(saved_dense, 100000, 0, 3);
    auto dense_buf = saved_dense.dump();
    check(dense_buf[5] == 1, "sparse object can dump dense form");
    SparseHLL loaded_dense = SparseHLL::load(dense_buf);
    checkNear(loaded_dense.estimate(), saved_dense.estimate(), 1e-12, "dense form dump/load");
}

void testSparseMerge() {
    SparseHLL left;
    SparseHLL right;
    HLL0 whole;

    for (int i = 0; i < 2000; ++i) {
        std::string value = "user_" + std::to_string(i % 1000);
        whole.add(value);
        if (i % 2 == 0) {
            left.add(value);
        } else {
            right.add(value);
        }
    }

    SparseHLL right_copy = right;
    left.merge(right);
    checkNear(left.estimate(), whole.estimate(), 1e-6, "sparse plus sparse merge");
    checkNear(right.estimate(), right_copy.estimate(), 1e-12, "merge does not change source");

    SparseHLL dense_side;
    feed(dense_side, 100000, 0, 8);
    dense_side.merge(left);
    check(dense_side.isDense(), "dense plus sparse stays dense");

    SparseHLL small;
    feed(small, 100, 0, 2);
    SparseHLL dense_other;
    feed(dense_other, 100000, 0, 4);
    small.merge(dense_other);
    check(small.isDense(), "sparse plus dense promotes");
}

void testRandomConsistency() {
    for (int t = 0; t < 20; ++t) {
        uint64_t distinct = 1 + splitmix64(1000 + t) % 50000;
        uint64_t seed = splitmix64(2000 + t);

        HLL0 basic;
        DenseHLL dense;
        SparseHLL sparse;

        feed(basic, distinct, distinct, seed);
        feed(dense, distinct, distinct, seed);
        feed(sparse, distinct, distinct, seed);

        check(basic.estimate() == dense.estimate(), "random dense consistency");
        checkNear(sparse.estimate(), dense.estimate(), 1e-6, "random sparse consistency");
        checkNear(dense.estimate(), static_cast<double>(distinct),
                  0.12 * static_cast<double>(distinct) + 50.0,
                  "random estimate range");
    }
}

int main() {
    testHash();
    testBasic();
    testDenseBits();
    testDenseBehavior();
    testSparse();
    testSparseMerge();
    testRandomConsistency();

    std::printf("passed %d, failed %d\n", passed, failed);
    return failed == 0 ? 0 : 1;
}
