import subprocess
import platform
import os

def find_activemq_install_dir():
    # Assuming ActiveMQ installation directory is within the project directory
    project_dir = os.getcwd()  # Get the current working directory
    print(project_dir)
    activemq_dirs = [d for d in os.listdir(project_dir) if d.startswith("apache-activemq")]  # Filter directories
    print(activemq_dirs)
    if activemq_dirs:
        return os.path.abspath(os.path.join(project_dir, activemq_dirs[0]))
    else:
        return None
    
def start_activemq():
    activemq_install_dir = find_activemq_install_dir()
    if not activemq_install_dir:
        print("ActiveMQ installation directory not found.")
        return
    
    if platform.system() == "Windows":
        command = fr'"{activemq_install_dir}\bin\activemq" start'
    else:
        command = fr'{activemq_install_dir}/bin/activemq start'
    
    # Execute the command
    try:
        subprocess.run(command, shell=True, check=True)
        print("ActiveMQ started successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error starting ActiveMQ: {e}")

def stop_activemq():
    activemq_install_dir = find_activemq_install_dir()
    if not activemq_install_dir:
        print("ActiveMQ installation directory not found.")
        return
    
    if platform.system() == "Windows":
        command = fr'"{activemq_install_dir}\bin\activemq" stop'
    else:
        command = fr'{activemq_install_dir}/bin/activemq stop'
    
    # Execute the command
    try:
        subprocess.run(command, shell=True, check=True)
        print("ActiveMQ stoped successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error stopping ActiveMQ: {e}")

if __name__ == "__main__":
    start_activemq()
    #stop_activemq()
