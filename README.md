# Terminal 
Browser based Terminal that executes commands in separate Docker containers.


# Setup

Build the docker image

````sh
$ make
````

or if you are using the Windows Subsystem for Linux:

````sh
$ make build-docker-wsl
````
 also you might need to set the DOCKER_BASE_URL and expose docker without TLS when using the WSL.
 
````sh
$ export DOCKER_BASE_URL="localhost:2375"
````


# TODO

- Check badges for completion [done]
- Serialize / Deserialize for commandline engine [done]
- Make challenges skipable [open]
- Welcome message
- data protection site
- about site