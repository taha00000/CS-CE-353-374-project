build:
	docker build -t neeyazie/hss:0.0.2.RELEASE . 

run:
	docker container run -d -p 8000:8000 neeyazie/hss:0.0.2.RELEASE

push:
	docker push neeyazie/hss:0.0.2.RELEASE

tag:
	docker tag neeyazie/hss:0.0.2.RELEASE neeyazie/hss:latest