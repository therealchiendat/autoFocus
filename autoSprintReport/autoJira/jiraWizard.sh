#!/bin/bash -eo pipefail

script_name="jiraWizard.sh"

echo "Current Python version is: $(python --version)"
# Get the version of Python installed on the system
python_version=$(python --version 2>&1)

# Extract the major and minor version numbers
major_version=$(echo $python_version | cut -d' ' -f2 | cut -d'.' -f1)
minor_version=$(echo $python_version | cut -d' ' -f2 | cut -d'.' -f2)
python_command="python${major_version}.${minor_version}"

# Check that the selected Python version meets the minimum requirements
if "$python_command" -c 'import sys; assert sys.version_info >= (3, 7)' 2>&1 >/dev/null; then
    echo "$script_name: Python $python_version is installed."
else
    echo "$script_name: Python version greater than or equal to 3.7 is not installed."
    echo "$script_name: This project requires Python version greater than or equal to 3.7."
    echo "$script_name: Exiting..."
    exit 1
fi

# Create virtual environment
echo "$script_name: Creating virtual environment"
$python_command -m venv venv --copies
. venv/bin/activate

# Upgrade pip
echo "$script_name: Upgrading pip"
pip install --upgrade pip

# Install package in development mode
echo "$script_name: Installing Packages"
pip install -r requirements.txt

echo "$script_name: Installation Done!"

### HERE COMES THE MAGIC!

# First, delete all csv files in the directory
echo "$script_name: Deleting all csv files in the directory"
rm -f *.csv

echo "$script_name: delete sprintgoal.txt if it exists"
rm -f sprintgoal.txt

# Run the autoJira script
echo "$script_name: Running autoJira script"
$python_command autoJira.py

# Check for `Jira.csv` file
if [ -f "Jira.csv" ]; then
    echo "$script_name: Jira.csv file created successfully!"
else
    echo "$script_name: Jira.csv file not found!"
    echo "$script_name: Exiting..."
    exit 1
fi

# run autoCalc.py to parse the Jira.csv file
echo "$script_name: Running autoCalc script"
$python_command autoCalc.py

# Check for `SprintHealth.csv` file
if [ -f "SprintHealth.csv" ]; then
    echo "$script_name: SprintHealth.csv file created successfully!"
    # run autoSlides.py to update the slides
    echo "$script_name: Running autoSlides script"
    $python_command autoSlides.py
else
    echo "$script_name: SprintHealth.csv file not found!"
    echo "$script_name: Exiting..."
    exit 1
fi


