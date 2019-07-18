# Makefile for Sample Device Status Monitoring Application.
#
# AUTHOR(s): Sheetal Sahasrabudhe <sheesaha@cisco.com>
#

IMG = cat9kediag
PORT = 5000

docker:
	docker build -t $(IMG) .

.PHONY: docker

run:
	docker run --rm -it -p$(PORT):$(PORT) $(IMG)
