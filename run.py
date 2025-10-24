#!/usr/bin/env python3
"""
Cross-platform script to configure and run User Gaze Track
Usage: python run.py [--venv]
"""

import subprocess
import sys
import os
import platform
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import ipaddress


class GazeTrackRunner:
    def __init__(self):
        self.env_name = "user-gaze-track"
        self.venv_dir = ".venv"
        self.use_conda = False
        self.is_windows = platform.system() == "Windows"
        self.cert_file = "cert.pem"
        self.key_file = "key.pem"

    def print_step(self, message, emoji="🔧"):
        """Print a formatted message"""
        print(f"{emoji} {message}")

    def run_command(self, command, shell=True, check=True, capture_output=False):
        """Run a system command"""
        try:
            if capture_output:
                result = subprocess.run(
                    command, shell=shell, check=check, capture_output=True, text=True
                )
                return result.stdout.strip()
            else:
                subprocess.run(command, shell=shell, check=check)
                return True
        except subprocess.CalledProcessError as e:
            if capture_output:
                return None
            print(f"❌ Error running command: {command}")
            print(f"   {e}")
            return False

    def command_exists(self, command):
        """Check if a command is available"""
        return shutil.which(command) is not None

    def detect_environment_manager(self, force_venv=False):
        """Detects whether to use conda or venv"""
        if force_venv:
            self.print_step("Forcing use of Python venv...")
            self.use_conda = False
        elif self.command_exists("conda"):
            self.print_step(
                "Conda detected. Using conda for environment management...", "🐍"
            )
            self.use_conda = True
        else:
            self.print_step(
                "Conda not available. Using Python venv as fallback...", "⚠️"
            )
            self.use_conda = False

    def conda_env_exists(self):
        """Check if the conda environment exists"""
        try:
            output = self.run_command("conda env list", capture_output=True)
            if output:
                for line in output.split("\n"):
                    if line.strip().startswith(self.env_name):
                        return True
            return False
        except:
            return False

    def setup_conda_environment(self):
        """Set up the conda environment"""
        if self.conda_env_exists():
            self.print_step(
                f"Conda environment '{self.env_name}' already exists.", "✅"
            )
        else:
            self.print_step(
                f"Creating conda environment '{self.env_name}' from environment.yml...",
                "⚙️",
            )
            if not self.run_command(
                f"conda env create -n {self.env_name} -f environment.yml"
            ):
                return False
            self.print_step(f"Conda environment '{self.env_name}' created.", "✅")
        return True

    def get_conda_python(self):
        """Get the path to the Python executable inside the conda environment"""
        try:
            # Obtener la ruta base de conda
            conda_info = self.run_command("conda info --base", capture_output=True)
            if conda_info:
                if self.is_windows:
                    python_path = f"{conda_info}\\envs\\{self.env_name}\\python.exe"
                else:
                    python_path = f"{conda_info}/envs/{self.env_name}/bin/python"
                return python_path
            return None
        except:
            return None

    def setup_venv_environment(self):
        """Set up the venv-based environment"""
        venv_path = Path(self.venv_dir)
        venv_exists = venv_path.exists()

        if venv_exists:
            self.print_step(
                f"Virtual environment '{self.venv_dir}' already exists.", "✅"
            )
        else:
            self.print_step(
                f"Creating Python virtual environment '{self.venv_dir}'...", "⚙️"
            )
            if not self.run_command(f"python -m venv {self.venv_dir}"):
                return False
            self.print_step(f"Virtual environment '{self.venv_dir}' created.", "✅")

        return True, not venv_exists

    def get_venv_python(self):
        """Get the path to the Python executable inside the venv"""
        if self.is_windows:
            return str(Path(self.venv_dir) / "Scripts" / "python.exe")
        else:
            return str(Path(self.venv_dir) / "bin" / "python")

    def check_flask_installed(self, python_path):
        """Check if Flask is installed"""
        try:
            result = self.run_command(
                f'"{python_path}" -c "import flask"', capture_output=True
            )
            return result is not None
        except:
            return False

    def check_certificates_exist(self):
        """Check if SSL certificates exist"""
        cert_exists = Path(self.cert_file).exists()
        key_exists = Path(self.key_file).exists()

        if cert_exists and key_exists:
            self.print_step("SSL certificates found.", "🔐")
            # Mostrar información adicional sobre los certificados
            try:
                cert_stat = Path(self.cert_file).stat()
                cert_date = datetime.fromtimestamp(cert_stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                self.print_step(f"  - Certificate created: {cert_date}")
            except:
                pass
            return True
        elif cert_exists or key_exists:
            self.print_step(
                "Only one of the certificates exists. Both will be recreated.", "⚠️"
            )
            return False
        else:
            self.print_step("SSL certificates not found.", "❌")
            return False

    def install_cryptography(self, python_path):
        """Install the cryptography library if not available"""
        try:
            self.run_command(
                f'"{python_path}" -c "import cryptography"', capture_output=True
            )
            return True
        except:
            self.print_step("Installing cryptography to generate certificates...", "📦")
            return self.run_command(f'"{python_path}" -m pip install cryptography')

    def create_ssl_certificates(self, python_path):
        """Create self-signed SSL certificates using Python/cryptography"""
        if not self.install_cryptography(python_path):
            print("❌ Error installing cryptography")
            return False

        self.print_step("Generating self-signed SSL certificates...", "🔐")

        # Script Python para generar certificados
        cert_script = """
import os
import ipaddress
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta

# Generar clave privada
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Configure the certificate
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "Madrid"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "User Gaze Track"),
    x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Development"),
    x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
])

# Use timezone-aware datetime to avoid deprecation warning
try:
    # Python 3.12+
    now = datetime.now(datetime.UTC)
except AttributeError:
    # Python < 3.12
    from datetime import timezone
    now = datetime.now(timezone.utc)

# Create the certificate
cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    private_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    now
).not_valid_after(
    now + timedelta(days=365)
).add_extension(
    x509.SubjectAlternativeName([
        x509.DNSName("localhost"),
        x509.DNSName("127.0.0.1"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        x509.IPAddress(ipaddress.IPv6Address("::1")),
    ]),
    critical=False,
).sign(private_key, hashes.SHA256())

# Save the private key
with open("key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Save the certificate
with open("cert.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("Certificados generados exitosamente:")
print("- cert.pem (certificado)")
print("- key.pem (clave privada)")
"""

        # Escribir el script temporalmente y ejecutarlo
        script_path = "temp_cert_generator.py"
        try:
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(cert_script)

            if self.run_command(f'"{python_path}" {script_path}'):
                os.remove(script_path)
                self.print_step("SSL certificates created successfully.", "✅")
                self.print_step("  - cert.pem (public certificate)")
                self.print_step("  - key.pem (private key)")
                return True
            else:
                if os.path.exists(script_path):
                    os.remove(script_path)
                return False

        except Exception as e:
            print(f"❌ Error al crear certificados: {e}")
            if os.path.exists(script_path):
                os.remove(script_path)
            return False

    def setup_ssl_certificates(self, python_path):
        """Set up SSL certificates (detect or create if necessary)"""
        if not self.check_certificates_exist():
            try:
                create = input(
                    "Do you want to create self-signed SSL certificates? (y/n): "
                )
                if create.lower() in ["s", "sí", "si", "y", "yes"]:
                    if not self.create_ssl_certificates(python_path):
                        print("❌ Error creating SSL certificates")
                        print("   The application will run without HTTPS")
                        return False
                else:
                    self.print_step("SSL certificates not created.", "⚠️")
                    self.print_step("The application will run without HTTPS.", "⚠️")
                    return False
            except KeyboardInterrupt:
                print("\n❌ Cancelled by user")
                return False
        return True

    def install_dependencies(self, python_path):
        """Install project dependencies"""
        self.print_step("Installing dependencies...", "📦")

        requirements_file = Path("requirements.txt")
        if requirements_file.exists() and requirements_file.stat().st_size > 0:
            self.print_step("   From requirements.txt...")
            if not self.run_command(
                f'"{python_path}" -m pip install -r requirements.txt'
            ):
                return False
        else:
            self.print_step("   Installing core dependencies...")
            deps = [
                "flask==3.1.0",
                "flask-sqlalchemy==3.1.1",
                "flasgger==0.9.7.1",
                "numpy==1.26.4",
                "ttkbootstrap==1.10.1",
                "cryptography",
            ]
            for dep in deps:
                if not self.run_command(f'"{python_path}" -m pip install {dep}'):
                    return False

            self.print_step("Dependencies installed.", "✅")
            return True

    def ask_for_configuration(self, python_path):
        """Ask whether the user wants to configure the application"""
        print()
        try:
            choice = input(
                "Do you want to modify configurations before running the application? (y/n): "
            )
            if choice.lower() in ["s", "sí", "si", "y", "yes"]:
                self.print_step("Opening configurator...", "⚙️")
                if self.run_command(f'"{python_path}" src/config.py'):
                    self.print_step("Configuration completed.", "✅")
                else:
                    print("❌ Error opening configurator")
                    return False
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user")
            return False
        return True

    def run_application(self, python_path):
        """Run the main application"""
        self.print_step("Running the application...", "🚀")
        return self.run_command(f'"{python_path}" src/app.py')

    def run(self):
        """Main method that runs the full setup and execution flow"""
        # Detectar argumentos
        force_venv = "--venv" in sys.argv

        # Detectar gestor de entornos
        self.detect_environment_manager(force_venv)

        if self.use_conda:
            # Flujo conda
            if not self.setup_conda_environment():
                sys.exit(1)

            python_path = self.get_conda_python()
            if not python_path:
                print("❌ Could not get the conda Python path")
                sys.exit(1)

            # Verificar que cryptography esté disponible para conda
            self.install_cryptography(python_path)

        else:
            # Flujo venv
            success, is_new_env = self.setup_venv_environment()
            if not success:
                sys.exit(1)

            python_path = self.get_venv_python()

            # Instalar dependencias si es necesario
            if is_new_env or not self.check_flask_installed(python_path):
                if not self.install_dependencies(python_path):
                    sys.exit(1)
            else:
                self.print_step(
                    "Dependencies already installed, skipping installation.", "✅"
                )

        # Configurar certificados SSL
        self.setup_ssl_certificates(python_path)

        # Optional configuration
        if not self.ask_for_configuration(python_path):
            sys.exit(1)

        # Ejecutar aplicación
        if not self.run_application(python_path):
            sys.exit(1)


if __name__ == "__main__":
    try:
        runner = GazeTrackRunner()
        runner.run()
    except KeyboardInterrupt:
        print("\n❌ Execution cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
