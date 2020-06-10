DOCKERFILE_PATH=./executor/docker_image/
IMAGE_NAME = terminal_image

all: build-docker create-server

minify: minify-css minify-js

build-docker:
	docker build -t $(IMAGE_NAME):latest $(DOCKERFILE_PATH)

build-docker-wsl:
	docker.exe build -t $(IMAGE_NAME):latest $(DOCKERFILE_PATH)

create-server:
	python manage clean-db && python manage load-badges && python manage load-challenges

minify-js:
	curl -X POST -s --data-urlencode 'input@static/js/main.js' https://javascript-minifier.com/raw > static/js/main.min.js && \
	curl -X POST -s --data-urlencode 'input@static/js/report.js' https://javascript-minifier.com/raw > static/js/report.min.js && \
	curl -X POST -s --data-urlencode 'input@static/js/feedback.js' https://javascript-minifier.com/raw > static/js/feedback.min.js

minify-css:
	curl -X POST -s --data-urlencode 'input@static/css/main.css' https://cssminifier.com/raw > static/css/main.min.css && \
	curl -X POST -s --data-urlencode 'input@static/css/mvp.css' https://cssminifier.com/raw > static/css/mvp.min.css

html-file:
	cp static/_base.html static/$(name)

test:
	python ./manage test