package errs

import (
	"errors"
	"fmt"
	"go-root/lib/runtime"
)

/*
New wraps an error or creates a new error with the caller's line number.
If an error is passed, it appends the caller's line number to the stack trace.
If a string is passed, it creates a new error with the caller's line number.
*/
func New(errOrMsg any, args ...any) WithLineError {
	var err error

	// If input is an error, wrap it
	if e, ok := errOrMsg.(error); ok {
		if e == nil {
			return nil
		}
		// If already a WithLineError, append stack trace
		var withLineErrorInst *withLineError
		if errors.As(e, &withLineErrorInst) {
			withLineErrorInst.stackTrace = append(withLineErrorInst.stackTrace, runtime.Caller(1, runtime.CALLER_FORMAT_SHORT))
			return withLineErrorInst
		}
		err = e
	} else if msg, ok := errOrMsg.(string); ok { // If input is a string, create a new error
		err = fmt.Errorf(msg, args...)
	} else {
		return nil
	}

	// Create a new WithLineError
	return &withLineError{
		error:      err,
		stackTrace: []string{runtime.Caller(1, runtime.CALLER_FORMAT_SHORT)},
	}
}
