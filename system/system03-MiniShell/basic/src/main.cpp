#include <iostream>
#include <map>
#include <string>

int main() {
    // State: file name -> content. The virtual root "/" always exists and is
    // not stored here; Basic has no sub-directories.
    std::map<std::string, std::string> files;
    (void)files;

    // TODO: read commands line by line from std::cin until "exit" or EOF,
    //       split each line into words, and implement the Basic Mini Shell.
    //       See README.md for the command table and the ERROR format.

    return 0;
}
