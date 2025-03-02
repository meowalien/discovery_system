package middleware

import (
	"bytes"
	"core/errs"
	"core/gincontext"
	"core/log"
	"errors"
	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
	"io"
	"math"
	"net/http"
	"os"
	"sync/atomic"
	"time"
)

type readCloser struct {
	ReadCloser io.ReadCloser
	buf        *bytes.Buffer
	read       atomic.Bool
}

func (r *readCloser) Read(p []byte) (n int, err error) {
	n, err = r.ReadCloser.Read(p)
	if n > 0 {
		// Write the read bytes into the buffer for later inspection.
		if _, err2 := r.buf.Write(p[:n]); err2 != nil {
			return n, err2
		}
	}
	if err == io.EOF {
		r.read.Store(true)
	}
	return n, err
}

func (r *readCloser) Close() error {
	// If the body hasn't been fully read yet, drain the remainder.
	if !r.read.Load() {
		if _, err := io.Copy(r.buf, r.ReadCloser); err != nil {
			return errs.New("failed to drain request body: %v", err)
		}
		r.read.Store(true)
	}
	return r.ReadCloser.Close()
}

func (r *readCloser) ReadIfNotRead() ([]byte, error) {
	if r.read.Load() {
		return r.buf.Bytes(), nil
	}
	_, err := io.Copy(r.buf, r.ReadCloser)
	if err != nil {
		if errors.Is(err, http.ErrBodyReadAfterClose) {
			r.read.Store(true)
		} else {
			return nil, errs.New("failed to read request body: %v", err)
		}
	}
	return r.buf.Bytes(), nil
}

func AccessLog(accessLogger log.Logger) gin.HandlerFunc {
	hostname, err := os.Hostname()
	if err != nil {
		hostname = "unknow"
	}
	return func(c *gin.Context) {

		// replace c.Request.Body with a reader that caches all the data
		// so that it can be read again later
		c.Request.Body = &readCloser{
			ReadCloser: c.Request.Body,
			buf:        new(bytes.Buffer),
		}

		c.Next()
		path := c.Request.URL.Path
		clientIP := c.ClientIP()
		method := c.Request.Method
		traceID := gincontext.TraceID.Get(c)
		start := gincontext.RequestStartTime.Get(c)
		stop := time.Since(start)
		latency := int(math.Ceil(float64(stop.Nanoseconds()) / 1000000.0))
		statusCode := c.Writer.Status()
		clientUserAgent := c.Request.UserAgent()
		referer := c.Request.Referer()
		responseLength := c.Writer.Size()
		if responseLength < 0 {
			responseLength = 0
		}

		entry := accessLogger.WithFields(logrus.Fields{
			"startTime":      start,
			"traceID":        traceID,
			"hostname":       hostname,
			"statusCode":     statusCode,
			"latency":        latency, // time to process
			"clientIP":       clientIP,
			"method":         method,
			"path":           path,
			"referer":        referer,
			"responseLength": responseLength,
			"userAgent":      clientUserAgent,
		})

		if len(c.Errors) > 0 {
			entry.Error(c.Errors.ByType(gin.ErrorTypePrivate).String())
		} else {
			body, e := c.Request.Body.(*readCloser).ReadIfNotRead()
			if e != nil {
				entry.Errorf("failed to read request body: %v", e)
			}

			msg := string(body)
			if statusCode >= http.StatusInternalServerError {
				entry.Error(msg)
			} else if statusCode >= http.StatusBadRequest {
				entry.Warn(msg)
			} else {
				entry.Info(msg)
			}
		}
	}
}
