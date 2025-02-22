# syntax=docker/dockerfile:1

##
# Stage 1: Build
##
FROM golang:1.23.2-alpine3.20 AS builder

# Define a required build argument
ARG VERSION

# Fail the build if VERSION is not set
RUN test -n "$VERSION" || (echo "ERROR: VERSION is not set!" && exit 1)

# Set the working directory inside the container
WORKDIR /app

# Copy go.mod and go.sum first to leverage caching
#COPY go.mod go.sum ./


# Copy the rest of the source code
COPY . .
RUN ls -R /app
RUN go work sync
# Build the application (embed VERSION via ldflags)
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-X main.Version=$VERSION" \
    -o myapp ./project/data_collector

##
# Stage 2: Final minimal image
##
FROM alpine:3.20

# Copy the compiled binary from the builder stage
COPY --from=builder /app/myapp /usr/local/bin/myapp

# Set an entrypoint (or CMD)
ENTRYPOINT ["/usr/local/bin/myapp"]

