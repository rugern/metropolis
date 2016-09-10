# Metropolis

### Requirements
* Python 3.4<

### Installation

```bash
# Create virtual environment (and new folder with that name)
pyvenv <env_name>

# Activate virtual environment
pyvenv <env_name>/bin/activate

# Install project as a development module
pip install -e .
```

### Usage
You need to enter (and exit) the virtual environment for each work session:
```bash
# Start
pyvenv <env_name>/bin/activate

# End
pyvenv deactivate
```

Running the server:
```bash
pserve development.ini --reload
```
