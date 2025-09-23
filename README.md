# psc-timetable
Scrape the timetable from Peter Symonds College parent portal

## Building the docker image
docker build -t psc-timetable:latest .

## Running
docker run --rm -it -p 5000:5000/tcp -v $(pwd)/.env:/app/.env psc-timetable:latest
