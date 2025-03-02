# syntax=docker/dockerfile:1

##
# Stage 1: Build
##
FROM golang:1.24.0-alpine3.21 AS builder


ARG VERSION
RUN test -n "$VERSION" || (echo "ERROR: VERSION is not set!" && exit 1)


WORKDIR /app

COPY . .
RUN ls -R /app
RUN go work sync

RUN go build \
    -ldflags="-X main.Version=$VERSION" \
    -o myapp ./project/datacollector

FROM alpine:3.21
WORKDIR /app
COPY --from=builder /app/myapp .
ENTRYPOINT ["/app/myapp"]
