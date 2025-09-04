
Push-Location code/dep_external/src/binaural
git clone -b visr --single-branch https://github.com/ebu/bear.git visr --depth 1
git clone https://github.com/ebu/bear --depth 1
git clone https://github.com/resonance-audio/resonance-audio --depth 1
Push-Location bear
git submodule update --init --recursive --depth 1
Pop-Location
Push-Location resonance-audio/third_party
git clone https://bitbucket.org/jpommier/pffft.git pffft --depth 1
Pop-Location
Pop-Location

$config = "Debug"
$root = ((Get-Item .).FullName)
New-Item -Type Directory ./out -ErrorAction Ignore


New-Item -Type Directory ./out/visr -ErrorAction Ignore
cmake -B ./out/visr -S ./code/dep_external/src/binaural/visr `
    --install-prefix $root `
    -DCMAKE_TOOLCHAIN_FILE="$env:VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake" `
    -DVCPKG_MANIFEST_DIR="$root" `
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON `
    -DBUILD_SHARED_LIBS=OFF `
    -DBUILD_PYTHON_BINDINGS=OFF `
    -DBUILD_DOCUMENTATION=OFF `
    -DBUILD_AUDIOINTERFACES_PORTAUDIO=OFF `
    -DBUILD_AUDIOINTERFACES_JACK=OFF `
    -DBUILD_USE_SNDFILE_LIBRARY=OFF `
    -DBUILD_STANDALONE_APPLICATIONS=OFF `
    -DBUILD_TESTING=OFF `
    -DBUILD_INSTALL_SHARED_LIBRARIES=OFF `
    -DBUILD_INSTALL_STATIC_LIBRARIES=ON `
    -DBoost_USE_STATIC_LIBS=ON `
    -G "Visual Studio 17 2022"
cmake --build ./out/visr --parallel
cmake --install ./out/visr --prefix $root --config $config


New-Item -Type Directory ./out/bear -ErrorAction Ignore
cmake -B ./out/bear -S ./code/dep_external/src/binaural/bear/visr_bear `
    --install-prefix $root `
    -DCMAKE_TOOLCHAIN_FILE="$env:VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake" `
    -DVCPKG_MANIFEST_DIR="$root" `
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON `
    -DBUILD_SHARED_LIBS=OFF `
    -DBUILD_PYTHON_BINDINGS=OFF `
    -DEAR_USE_INTERNAL_EIGEN=OFF `
    -DBEAR_VISR_LIB_TYPE="static" `
    -DBEAR_DEMO=OFF `
    -DBEAR_UNIT_TESTS=OFF `
    -G "Visual Studio 17 2022"
cmake --build ./out/bear --parallel
cmake --install ./out/bear --prefix $root --config $config


New-Item -Type Directory ./out/iamf2bear -ErrorAction Ignore
cmake -B ./out/iamf2bear -S ./code/dep_external/src/binaural/iamf2bear `
    --install-prefix $root `
    -DCMAKE_TOOLCHAIN_FILE="$env:VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake" `
    -DVCPKG_MANIFEST_DIR="$root" `
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON `
    -DBUILD_SHARED_LIBS=OFF `
    -G "Visual Studio 17 2022"
cmake --build ./out/iamf2bear --parallel
cmake --install ./out/iamf2bear --prefix $root --config $config


New-Item -Type Directory ./out/resonance-audio -ErrorAction Ignore
cmake -B ./out/resonance-audio -S ./code/dep_external/src/binaural/resonance-audio `
    --install-prefix $root `
    -DCMAKE_TOOLCHAIN_FILE="$env:VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake" `
    -DVCPKG_MANIFEST_DIR="$root" `
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON `
    -DBUILD_SHARED_LIBS=OFF `
    -DBUILD_RESONANCE_AUDIO_API=ON `
    -DRA_USE_INTERNAL_EIGEN=OFF `
    -G "Visual Studio 17 2022"
cmake --build ./out/resonance-audio --parallel
cmake --install ./out/resonance-audio --prefix $root --config $config


New-Item -Type Directory ./out/iamf2resonance -ErrorAction Ignore
cmake -B ./out/iamf2resonance -S ./code/dep_external/src/binaural/iamf2resonance `
    --install-prefix $root `
    -DCMAKE_TOOLCHAIN_FILE="$env:VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake" `
    -DVCPKG_MANIFEST_DIR="$root" `
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON `
    -DBUILD_SHARED_LIBS=OFF `
    -DRESONANCE_LIB_TYPE="Static" `
    -G "Visual Studio 17 2022"
cmake --build ./out/iamf2resonance --parallel
cmake --install ./out/iamf2resonance --prefix $root --config $config


New-Item -Type Directory ./out/wavwriter -ErrorAction Ignore
cmake -B ./out/wavwriter -S ./code/dep_external/src/wav `
    --install-prefix $root `
    -DCMAKE_TOOLCHAIN_FILE="$env:VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake" `
    -DVCPKG_MANIFEST_DIR="$root" `
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON `
    -DBUILD_SHARED_LIBS=OFF `
    -G "Visual Studio 17 2022"
cmake --build ./out/wavwriter --parallel
cmake --install ./out/wavwriter --prefix $root --config $config


New-Item -Type Directory ./out/libiamf -ErrorAction Ignore
cmake -B ./out/libiamf -S ./code `
    --install-prefix $root `
    -DCMAKE_TOOLCHAIN_FILE="$env:VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake" `
    -DVCPKG_MANIFEST_DIR="$root" `
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON `
    -DBUILD_SHARED_LIBS=OFF `
    -DMULTICHANNEL_BINAURALIZER=ON `
    -DHOA_BINAURALIZER=ON `
    -G "Visual Studio 17 2022"
cmake --build ./out/libiamf --parallel
cmake --install ./out/libiamf --prefix $root --config $config


New-Item -Type Directory ./out/imafutil -ErrorAction Ignore
cmake -B ./out/imafutil -S ./code/test/tools/iamfdec `
    --install-prefix $root `
    -DCMAKE_TOOLCHAIN_FILE="$env:VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake" `
    -DVCPKG_MANIFEST_DIR="$root" `
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON `
    -DBUILD_SHARED_LIBS=OFF `
    -DMULTICHANNEL_BINAURALIZER=ON `
    -DHOA_BINAURALIZER=ON `
    -G "Visual Studio 17 2022"
cmake --build ./out/imafutil --parallel
cmake --install ./out/imafutil --prefix $root --config $config
