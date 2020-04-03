#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from conans import ConanFile, CMake, tools

class CryptoAuthLib(ConanFile):
    name = 'cryptoauthlib'
    version = '2019.09.03'
    license = 'MIT'
    url = 'https://github.com/jens-totemic/conan-cryptoauthlib'
    homepage = 'https://github.com/MicrochipTech/cryptoauthlib'
    description = 'Library for interacting with the Crypto Authentication secure elements.'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {
        'shared': [True, False],
        'fPIC': [True, False],
        'halHID': [True, False], # Include the HID HAL Driver
        'halI2C': [True, False], # Include the I2C Hal Driver - Linux & MCU only
        'halCustom': [True, False], # Include support for Custom/Plug-in Hal Driver
        'pkcs11': [True, False], # Build PKCS11 Library
        'mbedtls': [True, False], # Integrate with mbedtls
        'debugOutput': [True, False], # Enable Debug print statements in library
        'debugOutputPkcs11': [True, False] # Enable PKCS11 Debug Output
    }
    default_options = {
        'shared': True,
        'fPIC': True, 
        'halHID': False,
        'halI2C': True,
        'halCustom': False,
        'pkcs11': False,
        'mbedtls': False,
        'debugOutput': False,
        'debugOutputPkcs11': False
    }
    exports_sources = ["01-support-osx.diff", "02-fix-install-location.diff"]
    generators = "cmake"

    scm = {
        'type': 'git',
        'url': 'https://github.com/MicrochipTech/cryptoauthlib.git',
        # January 15, 2020 in branch pkcs11
        'revision': "2df0eb145c7241263d07577394dd12f8b1e783f0"
        #'revision': version
    }

    def configure(self):
        if self.settings.os == 'Linux' and self.options['hal_kit_id']:
            raise Exception("Sorry - libudev isn't generally available in Conan yet so I can't build the library "
                            "with this configuration.")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ATCA_BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["ATCA_HAL_KIT_HID"] = self.options.halHID
        cmake.definitions["ATCA_HAL_I2C"] = self.options.halI2C
        cmake.definitions["ATCA_HAL_CUSTOM"] = self.options.halCustom
        cmake.definitions["ATCA_PRINTF"] = self.options.debugOutput
        cmake.definitions["ATCA_PKCS11"] = self.options.pkcs11
        cmake.definitions["ATCA_MBEDTLS"] = self.options.mbedtls
        cmake.definitions["PKCS11_DEBUG_ENABLE"] = self.options.debugOutputPkcs11
        #cmake.configure(source_folder=self._source_subfolder)
        # cmake.configure(source_folder=os.path.join(self.build_folder, 'lib'), build_folder=self.bin_dir)
        cmake.configure()
        return cmake

    def source(self):
        # Fix linker not finding malloc and free on OSX 
        tools.patch(patch_file="01-support-osx.diff")
        # Fix install directory hard-coded to / 
        tools.patch(patch_file="02-fix-install-location.diff")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        # self.copy('*.so' if self.options.shared else '*.a', src=os.path.join(self.bin_dir), dst='lib')
        # self.copy('*.h', src=os.path.join(self.build_folder, 'lib'), dst='include')
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ['cryptoauth']
        self.cpp_info.includedirs = [
            'include',
            os.path.join('include', 'hal'),
            os.path.join('include', 'basic'),
            os.path.join('include', 'crypto'),
            os.path.join('include', 'atcacert')
        ]

#################
    # @property
    # def cmake(self):
    #     cmake = CMake(self)
    #     cmake.definitions.update({
    #         'ATCA_HAL_KIT_HID': 'ON' if self.options.hal_kit_hid else 'OFF',
    #         'ATCA_HAL_I2C': 'ON' if self.options.hal_i2c else 'OFF',
    #         'ATCA_HAL_CUSTOM': 'ON' if self.options.hal_custom else 'OFF',
    #         'ATCA_PRINTF': 'ON' if self.options.printf else 'OFF',
    #         'ATCA_PKCS11': 'ON' if self.options.pkcs11 else 'OFF',
    #         'ATCA_MBEDTLS': 'ON' if self.options.mbedtls else 'OFF',
    #         'ATCA_BUILD_SHARED_LIBS': 'ON' if self.options.shared else 'OFF'
    #     })
    #     return cmake

    @property
    def bin_dir(self):
        return os.path.join(self.build_folder, 'build')