# shell.nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python313
    python313Packages.locust
    # 可选：如果你需要额外的 Python 包（如 requests、pyyaml 等）
    # python311Packages.requests
    # python311Packages.pytest
  ];

  # 设置 Python 环境变量（确保使用正确的 Python 和包路径）
  shellHook = ''
    export PYTHONPATH="${pkgs.python313Packages.locust}/${pkgs.python313.sitePackages}:$PYTHONPATH"
    echo "✅ Locust environment ready!"
    echo "   Run 'locust --help' to get started."
  '';
}