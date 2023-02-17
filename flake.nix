{
  description = "A Python dev shell for a given package.";
  inputs = {
    nixpkgs.url = github:NixOS/nixpkgs/nixpkgs-unstable;
    flake-utils = {
      url = github:numtide/flake-utils;
    };
    pypi-deps-db = {
      url = "github:DavHau/pypi-deps-db";
      flake = false;
      # inputs.nixpkgs.follows = "nixpkgs";
      # inputs.mach-nix.follows = "mach-nix";
      # follows = "nixpkgs";
    };
    mach-nix = {
      url = "mach-nix";
      inputs.pypi-deps-db.follows = "pypi-deps-db";
      inputs.flake-utils.follows = "flake-utils";
      # inputs.nixpkgs.follows = "nixpkgs"; # causes issues with setuptools/distlib
    };
  };

  outputs = { self, nixpkgs, flake-utils, mach-nix, pypi-deps-db, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        machNix = mach-nix.lib."${system}";
        devEnvironment = machNix.mkPython {
            python="python39";
          requirements = builtins.readFile ./requirements.txt;
            # Fix some broken dependencies for python310
          _.rich.propagatedBuildInputs.mod = pySelf: self: oldVal: oldVal ++ [ pySelf.poetry ];
          _.jeepney.propagatedBuildInputs.mod = pySelf: self: oldVal: oldVal ++ [ pySelf.outcome pySelf.trio ];
        };
      in
      {
        devShell = pkgs.mkShell {
            name = "ptdpy";
          buildInputs = [
            devEnvironment
          ];
            shellHook = ''
              # Tells pip to put packages into $PIP_PREFIX instead of the usual locations.
              # See https://pip.pypa.io/en/stable/user_guide/#environment-variables.
              export PIP_PREFIX=$(pwd)/_build/pip_packages
              export PYTHONPATH="$PIP_PREFIX/${pkgs.python3.sitePackages}:$PYTHONPATH"
              export PYTHONPATH="$(pwd):$PYTHONPATH"
              export PATH="$(pwd):$PATH"
              export PATH="$PIP_PREFIX/bin:$PATH"
              unset SOURCE_DATE_EPOCH
            '';
        };
        packages.venv = devEnvironment;
      });
}
