# Dockerfile for Sample Device Status Monitoring Application.
#
# AUTHOR(s): Sheetal Sahasrabudhe <sheesaha@cisco.com>
#

FROM python:3.7
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000

CMD ["/app/run_server.sh"]
