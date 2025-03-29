package errorcode

type ErrorCode struct {
	ErrorMessage   string
	HTTPStatusCode int
}

var (
	ExampleErrorCode = ErrorCode{
		ErrorMessage:   "Example error message",
		HTTPStatusCode: 500,
	}
)
