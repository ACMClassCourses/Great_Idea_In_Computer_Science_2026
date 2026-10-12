#pragma once

#include <string>

class GitObject {
public:
    virtual ~GitObject() {}

    virtual std::string serialize() const = 0;
};

class Blob : public GitObject {
    // TODO: Design the Blob data and behavior.
};

class Tree : public GitObject {
    // TODO: Design the Tree data and behavior.
};

class Commit : public GitObject {
    // TODO: Design the Commit data and behavior.
};
