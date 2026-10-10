$ErrorActionPreference = "Stop"

$compiler = "g++"
$common = @("-std=c++17", "-O3", "-Wall", "-Wextra", "-Wpedantic", "-Isrc")

& $compiler @common src/lsh.cpp src/mnist.cpp test/test_lsh.cpp -o test/test_lsh.exe
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& test/test_lsh.exe test/data
$testExitCode = $LASTEXITCODE

Remove-Item -LiteralPath test/test_lsh.exe -Force -ErrorAction SilentlyContinue
exit $testExitCode
