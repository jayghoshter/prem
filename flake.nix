{
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
  flake-utils.lib.eachDefaultSystem (system:
  let 
    pkgs = nixpkgs.legacyPackages.${system}; 
    # dir = ''/home/jayghoshter/dev/tools/ptdpy/'';

    mach-nix = import (builtins.fetchGit {
      url = "https://github.com/DavHau/mach-nix";
      ref = "refs/tags/3.5.0";
    }) {};


    in 
    {

      defaultPackage = pkgs.python3Packages.buildPythonPackage{
        pname = "ptdpy";
        version = "0.1";

        src = ./.;

        mnpyreq = mach-nix.mkPython {
          requirements = builtins.readFile ./requirements.txt;
        };

        propagatedBuildInputs = with pkgs; [
          mnpyreq
        ];

        doCheck = false;
      };


      devShell = pkgs.mkShell rec {
            name = "ptdpy";

            mnpyreq = mach-nix.mkPython {
              requirements = builtins.readFile ./requirements.txt;
            };

            buildInputs = with pkgs; [
              mnpyreq
            ];

            shellHook = ''
              # Tells pip to put packages into $PIP_PREFIX instead of the usual locations.
              # See https://pip.pypa.io/en/stable/user_guide/#environment-variables.
              export PYTHONPATH="$(pwd):$PYTHONPATH"
              export PATH="$(pwd)/bin:$PATH"
              unset SOURCE_DATE_EPOCH
            '';

        };
      });
}
