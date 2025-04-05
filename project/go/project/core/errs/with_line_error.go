package errs

import "strings"

type WithLineError interface {
	error
	RawError() error
	StackTrace() []string
}

type withLineError struct {
	error
	stackTrace []string
}

func (w *withLineError) Unwrap() error {
	return w.error
}

func (w *withLineError) RawError() error {
	return w.error
}

func (w *withLineError) StackTrace() []string {
	return w.stackTrace
}

func (w *withLineError) Error() string {
	stackTraceStr := strings.Join(w.stackTrace, " <= ")
	return stackTraceStr + ": " + w.error.Error()
}
