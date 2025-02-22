package errs

import (
	"errors"
	"fmt"
	"testing"
)

func TestWithLine_1(t *testing.T) {
	err1 := errors.New("error 1")
	err2 := New(err1)
	err3 := New(err2)

	fmt.Println(err3)
	fmt.Println(err3.RawError())
	fmt.Println(err3.StackTrace())
}
